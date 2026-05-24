const std = @import("std");

pub const bpf_obj_name_len: usize = 16;
pub const default_bpf_fs_path = "/sys/fs/bpf";
pub const bpf_map_type_devmap: u32 = 14;
pub const bpf_map_type_devmap_hash: u32 = 25;
pub const bpf_f_rdonly_prog: u32 = 1 << 7;

pub const FilePathHandleBridgeError = error{
    PathTooLong,
    InvalidPid,
    InvalidFd,
    InvalidValue,
    MissingSeparator,
};

pub const FdinfoField = struct {
    key: []const u8,
    value: []const u8,
};

pub const FdinfoMapInfo = struct {
    map_type: ?u32 = null,
    key_size: ?u32 = null,
    value_size: ?u32 = null,
    max_entries: ?u32 = null,
    map_flags: ?u32 = null,
    map_extra: ?u64 = null,
};

pub const FdinfoMapInfoSummary = struct {
    parsed_field_count: usize,
    has_complete_legacy_fields: bool,
};

pub const MapReuseObservation = struct {
    map_name: []const u8,
    map_type: ?u32,
    key_size: ?u32,
    value_size: ?u32,
    max_entries: ?u32,
    map_flags: ?u32,
    map_extra: ?u64,
};

pub const MapReuseCompatibilitySummary = struct {
    map_type_matches: bool,
    key_size_matches: bool,
    value_size_matches: bool,
    max_entries_matches: bool,
    map_flags_matches: bool,
    map_extra_matches: bool,

    pub fn isCompatible(self: MapReuseCompatibilitySummary) bool {
        return self.map_type_matches and
            self.key_size_matches and
            self.value_size_matches and
            self.max_entries_matches and
            self.map_flags_matches and
            self.map_extra_matches;
    }
};

pub const ReusePinnedMapAttemptDisposition = enum {
    prevented,
    optional_probe,
    mandatory_probe,
};

pub const ReusePinnedMapAttempt = struct {
    disposition: ReusePinnedMapAttemptDisposition,
    bpffs_path: []const u8,
    requested_map_name: []const u8,

    pub fn requiresBpffsOpen(self: ReusePinnedMapAttempt) bool {
        return self.disposition != .prevented;
    }
};

pub const TokenPreparationDisposition = enum {
    prevented,
    optional_probe,
    mandatory_probe,
};

pub const TokenPreparationLogLevel = enum {
    debug,
    warn,
};

pub const TokenPreparationFailureStage = enum {
    bpffs_open,
    token_create,
};

pub const TokenPreparationFailureDisposition = enum {
    fail,
    skip_optional,
    skip_optional_missing_delegation,
};

pub const TokenPreparationFailurePlan = struct {
    disposition: TokenPreparationFailureDisposition,
    log_level: TokenPreparationLogLevel,
    message_suffix: []const u8,

    pub fn shouldContinueWithoutToken(self: TokenPreparationFailurePlan) bool {
        return self.disposition != .fail;
    }
};

pub const TokenPreparationPlan = struct {
    disposition: TokenPreparationDisposition,
    bpffs_path: []const u8,
    log_level: ?TokenPreparationLogLevel,

    pub fn requiresBpffsOpen(self: TokenPreparationPlan) bool {
        return self.disposition != .prevented;
    }

    pub fn requiresTokenCreate(self: TokenPreparationPlan) bool {
        return self.disposition != .prevented;
    }
};

const linux_errno = std.os.linux.E;

fn noSpaceToPathTooLong(err: anyerror) FilePathHandleBridgeError {
    return switch (err) {
        error.NoSpaceLeft => error.PathTooLong,
        else => unreachable,
    };
}

fn fieldValue(line: []const u8, key: []const u8) ?[]const u8 {
    if (!std.mem.startsWith(u8, line, key)) return null;
    if (line.len <= key.len or line[key.len] != ':') return null;
    return std.mem.trim(u8, line[key.len + 1 ..], " \t");
}

fn parseDecimalField(
    line: []const u8,
    key: []const u8,
    destination: *?u32,
) FilePathHandleBridgeError!bool {
    const value_text = fieldValue(line, key) orelse return false;
    destination.* = std.fmt.parseUnsigned(u32, value_text, 10) catch return error.InvalidValue;
    return true;
}

fn parseFlagField(line: []const u8, destination: *?u32) FilePathHandleBridgeError!bool {
    const value_text = fieldValue(line, "map_flags") orelse return false;
    const parsed = std.fmt.parseInt(i64, value_text, 0) catch return error.InvalidValue;
    if (parsed < 0) return error.InvalidValue;
    destination.* = std.math.cast(u32, parsed) orelse return error.InvalidValue;
    return true;
}

fn parseExtendedField(
    line: []const u8,
    key: []const u8,
    destination: *?u64,
) FilePathHandleBridgeError!bool {
    const value_text = fieldValue(line, key) orelse return false;
    destination.* = std.fmt.parseUnsigned(u64, value_text, 0) catch return error.InvalidValue;
    return true;
}

pub fn buildFdinfoPath(buffer: []u8, pid: u32, fd: i32) FilePathHandleBridgeError![]u8 {
    if (pid == 0) return error.InvalidPid;
    if (fd < 0) return error.InvalidFd;
    return std.fmt.bufPrint(buffer, "/proc/{d}/fdinfo/{d}", .{ pid, fd }) catch |err| noSpaceToPathTooLong(err);
}

pub fn buildProcFdinfoPath(buffer: []u8, pid: u32, fd: i32) FilePathHandleBridgeError![]u8 {
    return buildFdinfoPath(buffer, pid, fd);
}

pub fn buildCurrentProcessFdinfoPath(buffer: []u8, fd: i32) FilePathHandleBridgeError![]u8 {
    const pid = std.math.cast(u32, std.os.linux.getpid()) orelse return error.InvalidPid;
    return buildFdinfoPath(buffer, pid, fd);
}

pub fn parseFdinfoLine(line: []const u8) FilePathHandleBridgeError!FdinfoField {
    const separator = std.mem.indexOfScalar(u8, line, ':') orelse return error.MissingSeparator;
    return .{
        .key = std.mem.trim(u8, line[0..separator], " \t"),
        .value = std.mem.trim(u8, line[separator + 1 ..], " \t"),
    };
}

pub fn applyFdinfoMapInfoLine(info: *FdinfoMapInfo, line: []const u8) FilePathHandleBridgeError!void {
    if (try parseDecimalField(line, "map_type", &info.map_type)) return;
    if (try parseDecimalField(line, "key_size", &info.key_size)) return;
    if (try parseDecimalField(line, "value_size", &info.value_size)) return;
    if (try parseDecimalField(line, "max_entries", &info.max_entries)) return;
    if (try parseFlagField(line, &info.map_flags)) return;
    if (try parseExtendedField(line, "map_extra", &info.map_extra)) return;
}

pub fn parseMapInfoFromFdinfo(input: []const u8) FilePathHandleBridgeError!FdinfoMapInfo {
    return parseFdinfoMapInfo(input);
}

pub fn parseFdinfoMapInfo(input: []const u8) FilePathHandleBridgeError!FdinfoMapInfo {
    var info = FdinfoMapInfo{};
    var lines = std.mem.tokenizeAny(u8, input, "\r\n");
    while (lines.next()) |line| {
        try applyFdinfoMapInfoLine(&info, line);
    }
    return info;
}

pub fn summarizeFdinfoMapInfo(info: FdinfoMapInfo) FdinfoMapInfoSummary {
    var parsed_field_count: usize = 0;
    if (info.map_type != null) parsed_field_count += 1;
    if (info.key_size != null) parsed_field_count += 1;
    if (info.value_size != null) parsed_field_count += 1;
    if (info.max_entries != null) parsed_field_count += 1;
    if (info.map_flags != null) parsed_field_count += 1;
    if (info.map_extra != null) parsed_field_count += 1;

    return .{
        .parsed_field_count = parsed_field_count,
        .has_complete_legacy_fields = info.map_type != null and
            info.key_size != null and
            info.value_size != null and
            info.max_entries != null and
            info.map_flags != null,
    };
}

pub fn chooseReusedMapName(requested_name: []const u8, info_name: []const u8) []const u8 {
    if (info_name.len == bpf_obj_name_len - 1 and
        requested_name.len >= info_name.len and
        std.mem.eql(u8, requested_name[0..info_name.len], info_name))
    {
        return requested_name;
    }
    return info_name;
}

pub fn resolveReusedMapName(requested_name: []const u8, info_name: []const u8) []const u8 {
    return chooseReusedMapName(requested_name, info_name);
}

pub fn mapReuseObservationFromFdinfo(map_name: []const u8, info: FdinfoMapInfo) MapReuseObservation {
    return .{
        .map_name = map_name,
        .map_type = info.map_type,
        .key_size = info.key_size,
        .value_size = info.value_size,
        .max_entries = info.max_entries,
        .map_flags = info.map_flags,
        .map_extra = info.map_extra,
    };
}

pub fn normalizeReuseCompatibilityMapFlags(expected_map_type: u32, actual_map_flags: u32) u32 {
    if (expected_map_type == bpf_map_type_devmap or expected_map_type == bpf_map_type_devmap_hash) {
        return actual_map_flags & ~bpf_f_rdonly_prog;
    }
    return actual_map_flags;
}

pub fn summarizeMapReuseCompatibility(expected: FdinfoMapInfo, actual: FdinfoMapInfo) MapReuseCompatibilitySummary {
    return .{
        .map_type_matches = actual.map_type == expected.map_type,
        .key_size_matches = actual.key_size == expected.key_size,
        .value_size_matches = actual.value_size == expected.value_size,
        .max_entries_matches = actual.max_entries == expected.max_entries,
        .map_flags_matches = if (expected.map_type != null and actual.map_flags != null and expected.map_flags != null)
            normalizeReuseCompatibilityMapFlags(expected.map_type.?, actual.map_flags.?) == expected.map_flags.?
        else
            actual.map_flags == expected.map_flags,
        .map_extra_matches = actual.map_extra == expected.map_extra,
    };
}

pub fn isMapReuseCompatible(expected: FdinfoMapInfo, actual: FdinfoMapInfo) bool {
    return summarizeMapReuseCompatibility(expected, actual).isCompatible();
}

pub fn resolveReusePinnedMapAttempt(token_path: ?[]const u8, requested_map_name: []const u8) ReusePinnedMapAttempt {
    if (token_path) |path| {
        if (path.len == 0) {
            return .{
                .disposition = .prevented,
                .bpffs_path = "",
                .requested_map_name = requested_map_name,
            };
        }
        return .{
            .disposition = .mandatory_probe,
            .bpffs_path = path,
            .requested_map_name = requested_map_name,
        };
    }

    return .{
        .disposition = .optional_probe,
        .bpffs_path = default_bpf_fs_path,
        .requested_map_name = requested_map_name,
    };
}

pub fn planTokenPreparation(token_path: ?[]const u8) TokenPreparationPlan {
    if (token_path) |path| {
        if (path.len == 0) {
            return .{
                .disposition = .prevented,
                .bpffs_path = "",
                .log_level = null,
            };
        }

        return .{
            .disposition = .mandatory_probe,
            .bpffs_path = path,
            .log_level = .warn,
        };
    }

    return .{
        .disposition = .optional_probe,
        .bpffs_path = default_bpf_fs_path,
        .log_level = .debug,
    };
}

pub fn classifyTokenPreparationFailure(
    plan: TokenPreparationPlan,
    stage: TokenPreparationFailureStage,
    err_code: i32,
) TokenPreparationFailurePlan {
    const log_level = plan.log_level orelse .debug;
    if (plan.disposition == .mandatory_probe) {
        return .{
            .disposition = .fail,
            .log_level = log_level,
            .message_suffix = "",
        };
    }

    if (stage == .token_create and err_code == -@as(i32, @intFromEnum(linux_errno.NOENT))) {
        return .{
            .disposition = .skip_optional_missing_delegation,
            .log_level = log_level,
            .message_suffix = "",
        };
    }

    return .{
        .disposition = .skip_optional,
        .log_level = log_level,
        .message_suffix = ", skipping optional step...",
    };
}

test "buildProcFdinfoPath keeps proc fdinfo formatting explicit" {
    var buffer: [64]u8 = undefined;
    try std.testing.expectEqualStrings(
        "/proc/777/fdinfo/9",
        try buildProcFdinfoPath(&buffer, 777, 9),
    );
}

test "parseFdinfoMapInfo and summary keep bounded parsing explicit" {
    const parsed = try parseFdinfoMapInfo(
        \\map_type: 5
        \\key_size: 8
        \\value_size: 16
        \\max_entries: 1024
        \\map_flags: 0x20
    );
    const summary = summarizeFdinfoMapInfo(parsed);

    try std.testing.expectEqual(@as(?u32, 5), parsed.map_type);
    try std.testing.expectEqual(@as(?u32, 0x20), parsed.map_flags);
    try std.testing.expectEqual(@as(usize, 5), summary.parsed_field_count);
    try std.testing.expect(summary.has_complete_legacy_fields);
}

test "applyFdinfoMapInfoLine and parseFdinfoLine keep malformed inputs explicit" {
    var info = FdinfoMapInfo{};
    try std.testing.expectError(error.InvalidValue, applyFdinfoMapInfoLine(&info, "map_flags:\t-1"));
    try std.testing.expectError(error.MissingSeparator, parseFdinfoLine("map_type"));
}

test "planTokenPreparation keeps optional and mandatory probes explicit" {
    const optional = planTokenPreparation(null);
    try std.testing.expect(optional.requiresBpffsOpen());
    try std.testing.expect(optional.requiresTokenCreate());

    const mandatory = planTokenPreparation("/custom/bpffs");
    try std.testing.expectEqual(TokenPreparationDisposition.mandatory_probe, mandatory.disposition);

    const prevented = planTokenPreparation("");
    try std.testing.expect(!prevented.requiresBpffsOpen());
}

test "isMapReuseCompatible keeps devmap readonly-prog exception explicit" {
    const expected = FdinfoMapInfo{
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = 0,
        .map_extra = 9,
    };
    const actual = FdinfoMapInfo{
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = bpf_f_rdonly_prog,
        .map_extra = 9,
    };

    try std.testing.expect(isMapReuseCompatible(expected, actual));
}
