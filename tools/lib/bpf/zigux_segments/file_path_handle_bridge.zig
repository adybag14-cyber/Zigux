const std = @import("std");

pub const bpf_obj_name_len: usize = 16;

pub const FdInfoMapInfo = struct {
    map_id: u32 = 0,
    map_type: u32,
    key_size: u32,
    value_size: u32,
    max_entries: u32,
    map_flags: u32,
    map_extra: u64 = 0,
};

pub const default_bpf_fs_path = "/sys/fs/bpf";
pub const bpf_map_type_devmap: u32 = 14;
pub const bpf_map_type_devmap_hash: u32 = 25;
pub const bpf_f_rdonly_prog: u32 = 1 << 7;

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

pub const ReusePinnedMapOpenDisposition = enum {
    prevented,
    optional_probe,
};

pub const ReusePinnedMapOpenPlan = struct {
    disposition: ReusePinnedMapOpenDisposition,
    pin_path: []const u8,

    pub fn requiresPinnedMapOpen(self: ReusePinnedMapOpenPlan) bool {
        return self.disposition == .optional_probe;
    }
};

pub const ReusePinnedMapOpenFailureDisposition = enum {
    skip_missing_pinned_map,
    fail,
};

pub const ReusePinnedMapOpenFailurePlan = struct {
    disposition: ReusePinnedMapOpenFailureDisposition,
    log_level: TokenPreparationLogLevel,

    pub fn shouldContinueWithoutReuse(self: ReusePinnedMapOpenFailurePlan) bool {
        return self.disposition == .skip_missing_pinned_map;
    }
};

pub const ReusePinnedMapResolutionDisposition = enum {
    reused,
    incompatible_map,
    reuse_fd_failed,
};

pub const ReusePinnedMapResolution = struct {
    disposition: ReusePinnedMapResolutionDisposition,
    result_code: i32,
    should_close_pin_fd: bool,
    should_mark_map_pinned: bool,

    pub fn succeeded(self: ReusePinnedMapResolution) bool {
        return self.result_code == 0;
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

pub const TokenPreparationAcquisitionDisposition = enum {
    prepared,
    cache_allocation_failed,
};

pub const TokenPreparationAcquisition = struct {
    disposition: TokenPreparationAcquisitionDisposition,
    result_code: i32,
    should_close_token_fd: bool,
    should_store_token_fd: bool,
    should_store_feat_cache_token_fd: bool,

    pub fn succeeded(self: TokenPreparationAcquisition) bool {
        return self.result_code == 0;
    }
};

pub const FilePathHandleBridgeError = error{
    PathTooLong,
    InvalidPid,
    InvalidFd,
    InvalidValue,
};

const linux_errno = std.os.linux.E;

fn noSpaceToPathTooLong(err: anyerror) FilePathHandleBridgeError {
    return switch (err) {
        error.NoSpaceLeft => error.PathTooLong,
        else => unreachable,
    };
}

fn fieldValue(line: []const u8, key: []const u8) ?[]const u8 {
    if (!std.mem.startsWith(u8, line, key)) {
        return null;
    }
    if (line.len <= key.len or line[key.len] != ':') {
        return null;
    }

    return std.mem.trim(u8, line[key.len + 1 ..], " \t");
}

fn parseDecimalField(
    line: []const u8,
    key: []const u8,
    destination: *u32,
) FilePathHandleBridgeError!bool {
    const value_text = fieldValue(line, key) orelse return false;
    destination.* = std.fmt.parseUnsigned(u32, value_text, 10) catch return error.InvalidValue;
    return true;
}

fn parseFlagField(line: []const u8, destination: *u32) FilePathHandleBridgeError!bool {
    const value_text = fieldValue(line, "map_flags") orelse return false;
    const digits = if (std.mem.startsWith(u8, value_text, "0x") or std.mem.startsWith(u8, value_text, "0X"))
        value_text[2..]
    else
        value_text;
    const base: u8 = if (digits.ptr != value_text.ptr)
        16
    else if (value_text.len > 1 and value_text[0] == '0')
        8
    else
        10;
    destination.* = std.fmt.parseUnsigned(u32, digits, base) catch return error.InvalidValue;
    return true;
}

fn parseMapExtraField(line: []const u8, destination: *u64) FilePathHandleBridgeError!bool {
    const value_text = fieldValue(line, "map_extra") orelse return false;
    const trimmed_value = if (std.mem.startsWith(u8, value_text, "0x") or std.mem.startsWith(u8, value_text, "0X"))
        value_text[2..]
    else
        value_text;
    const base: u8 = if (trimmed_value.ptr == value_text.ptr) 10 else 16;
    destination.* = std.fmt.parseUnsigned(u64, trimmed_value, base) catch return error.InvalidValue;
    return true;
}

pub fn buildFdinfoPath(buffer: []u8, pid: u32, fd: i32) FilePathHandleBridgeError![]u8 {
    if (pid == 0) {
        return error.InvalidPid;
    }
    if (fd < 0) {
        return error.InvalidFd;
    }

    return std.fmt.bufPrint(buffer, "/proc/{d}/fdinfo/{d}", .{ pid, fd }) catch |err| noSpaceToPathTooLong(err);
}

pub fn buildCurrentProcessFdinfoPath(buffer: []u8, fd: i32) FilePathHandleBridgeError![]u8 {
    const pid = std.math.cast(u32, std.os.linux.getpid()) orelse return error.InvalidPid;
    return buildFdinfoPath(buffer, pid, fd);
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

pub fn resolveTokenPreparationAcquisition(has_feat_cache: bool) TokenPreparationAcquisition {
    if (!has_feat_cache) {
        return .{
            .disposition = .cache_allocation_failed,
            .result_code = -@as(i32, @intFromEnum(linux_errno.NOMEM)),
            .should_close_token_fd = true,
            .should_store_token_fd = false,
            .should_store_feat_cache_token_fd = false,
        };
    }

    return .{
        .disposition = .prepared,
        .result_code = 0,
        .should_close_token_fd = false,
        .should_store_token_fd = true,
        .should_store_feat_cache_token_fd = true,
    };
}

pub fn planReusePinnedMapOpen(pin_path: ?[]const u8) ReusePinnedMapOpenPlan {
    const path = pin_path orelse return .{
        .disposition = .prevented,
        .pin_path = "",
    };
    if (path.len == 0) {
        return .{
            .disposition = .prevented,
            .pin_path = "",
        };
    }
    return .{
        .disposition = .optional_probe,
        .pin_path = path,
    };
}

pub fn classifyReusePinnedMapOpenFailure(err_code: i32) ReusePinnedMapOpenFailurePlan {
    if (err_code == -@as(i32, @intFromEnum(linux_errno.NOENT))) {
        return .{
            .disposition = .skip_missing_pinned_map,
            .log_level = .debug,
        };
    }

    return .{
        .disposition = .fail,
        .log_level = .warn,
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

pub fn resolveReusePinnedMapAttempt(is_compatible: bool, reuse_fd_result: i32) ReusePinnedMapResolution {
    if (!is_compatible) {
        return .{
            .disposition = .incompatible_map,
            .result_code = -@as(i32, @intFromEnum(linux_errno.INVAL)),
            .should_close_pin_fd = true,
            .should_mark_map_pinned = false,
        };
    }

    if (reuse_fd_result != 0) {
        return .{
            .disposition = .reuse_fd_failed,
            .result_code = reuse_fd_result,
            .should_close_pin_fd = true,
            .should_mark_map_pinned = false,
        };
    }

    return .{
        .disposition = .reused,
        .result_code = 0,
        .should_close_pin_fd = true,
        .should_mark_map_pinned = true,
    };
}

pub fn parseMapInfoFromFdinfo(input: []const u8) FilePathHandleBridgeError!FdInfoMapInfo {
    var info = FdInfoMapInfo{
        .map_id = 0,
        .map_type = 0,
        .key_size = 0,
        .value_size = 0,
        .max_entries = 0,
        .map_flags = 0,
    };

    var lines = std.mem.tokenizeAny(u8, input, "\r\n");
    while (lines.next()) |line| {
        if (try parseDecimalField(line, "map_id", &info.map_id)) continue;
        if (try parseDecimalField(line, "map_type", &info.map_type)) continue;
        if (try parseDecimalField(line, "key_size", &info.key_size)) continue;
        if (try parseDecimalField(line, "value_size", &info.value_size)) continue;
        if (try parseDecimalField(line, "max_entries", &info.max_entries)) continue;
        if (try parseFlagField(line, &info.map_flags)) continue;
        if (try parseMapExtraField(line, &info.map_extra)) continue;
    }

    return info;
}

pub fn normalizeReuseCompatibilityMapFlags(expected_map_type: u32, actual_map_flags: u32) u32 {
    if (expected_map_type == bpf_map_type_devmap or expected_map_type == bpf_map_type_devmap_hash) {
        return actual_map_flags & ~bpf_f_rdonly_prog;
    }

    return actual_map_flags;
}

pub fn isMapReuseCompatible(expected: FdInfoMapInfo, actual: FdInfoMapInfo) bool {
    return actual.map_type == expected.map_type and
        actual.key_size == expected.key_size and
        actual.value_size == expected.value_size and
        actual.max_entries == expected.max_entries and
        normalizeReuseCompatibilityMapFlags(expected.map_type, actual.map_flags) == expected.map_flags and
        actual.map_extra == expected.map_extra;
}

test "buildFdinfoPath keeps the proc fdinfo pathname helper explicit" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/proc/321/fdinfo/7",
        try buildFdinfoPath(&buffer, 321, 7),
    );
    try std.testing.expectEqualStrings(
        "/proc/9999/fdinfo/42",
        try buildFdinfoPath(&buffer, 9999, 42),
    );
}

test "buildFdinfoPath keeps invalid pid fd and buffer exhaustion explicit" {
    var short_buffer: [8]u8 = undefined;

    try std.testing.expectError(error.InvalidPid, buildFdinfoPath(&short_buffer, 0, 4));
    try std.testing.expectError(error.InvalidFd, buildFdinfoPath(&short_buffer, 7, -1));
    try std.testing.expectError(error.PathTooLong, buildFdinfoPath(&short_buffer, 1234, 56));
}

test "buildCurrentProcessFdinfoPath matches the live libbpf current-process anchor" {
    var actual: [64]u8 = undefined;
    var expected: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        try std.fmt.bufPrint(&expected, "/proc/{d}/fdinfo/{d}", .{ std.os.linux.getpid(), 11 }),
        try buildCurrentProcessFdinfoPath(&actual, 11),
    );
    try std.testing.expectError(error.InvalidFd, buildCurrentProcessFdinfoPath(&actual, -1));
}

test "planTokenPreparation keeps token-path intent explicit without claiming io parity" {
    const prevented = planTokenPreparation("");
    try std.testing.expectEqual(TokenPreparationDisposition.prevented, prevented.disposition);
    try std.testing.expectEqualStrings("", prevented.bpffs_path);
    try std.testing.expectEqual(@as(?TokenPreparationLogLevel, null), prevented.log_level);
    try std.testing.expect(!prevented.requiresBpffsOpen());
    try std.testing.expect(!prevented.requiresTokenCreate());

    const optional = planTokenPreparation(null);
    try std.testing.expectEqual(TokenPreparationDisposition.optional_probe, optional.disposition);
    try std.testing.expectEqualStrings(default_bpf_fs_path, optional.bpffs_path);
    try std.testing.expectEqual(TokenPreparationLogLevel.debug, optional.log_level.?);
    try std.testing.expect(optional.requiresBpffsOpen());
    try std.testing.expect(optional.requiresTokenCreate());

    const mandatory = planTokenPreparation("/custom/bpffs");
    try std.testing.expectEqual(TokenPreparationDisposition.mandatory_probe, mandatory.disposition);
    try std.testing.expectEqualStrings("/custom/bpffs", mandatory.bpffs_path);
    try std.testing.expectEqual(TokenPreparationLogLevel.warn, mandatory.log_level.?);
    try std.testing.expect(mandatory.requiresBpffsOpen());
    try std.testing.expect(mandatory.requiresTokenCreate());
}

test "classifyTokenPreparationFailure keeps optional and mandatory recovery discipline explicit" {
    const prevented = classifyTokenPreparationFailure(planTokenPreparation(""), .bpffs_open, -@as(i32, @intFromEnum(linux_errno.ACCES)));
    try std.testing.expectEqual(TokenPreparationFailureDisposition.skip_optional, prevented.disposition);
    try std.testing.expectEqual(TokenPreparationLogLevel.debug, prevented.log_level);
    try std.testing.expectEqualStrings(", skipping optional step...", prevented.message_suffix);
    try std.testing.expect(prevented.shouldContinueWithoutToken());

    const optional_open = classifyTokenPreparationFailure(planTokenPreparation(null), .bpffs_open, -@as(i32, @intFromEnum(linux_errno.PERM)));
    try std.testing.expectEqual(TokenPreparationFailureDisposition.skip_optional, optional_open.disposition);
    try std.testing.expectEqual(TokenPreparationLogLevel.debug, optional_open.log_level);
    try std.testing.expectEqualStrings(", skipping optional step...", optional_open.message_suffix);
    try std.testing.expect(optional_open.shouldContinueWithoutToken());

    const optional_missing_delegation = classifyTokenPreparationFailure(planTokenPreparation(null), .token_create, -@as(i32, @intFromEnum(linux_errno.NOENT)));
    try std.testing.expectEqual(TokenPreparationFailureDisposition.skip_optional_missing_delegation, optional_missing_delegation.disposition);
    try std.testing.expectEqual(TokenPreparationLogLevel.debug, optional_missing_delegation.log_level);
    try std.testing.expectEqualStrings("", optional_missing_delegation.message_suffix);
    try std.testing.expect(optional_missing_delegation.shouldContinueWithoutToken());

    const mandatory_create = classifyTokenPreparationFailure(planTokenPreparation("/custom/bpffs"), .token_create, -@as(i32, @intFromEnum(linux_errno.PERM)));
    try std.testing.expectEqual(TokenPreparationFailureDisposition.fail, mandatory_create.disposition);
    try std.testing.expectEqual(TokenPreparationLogLevel.warn, mandatory_create.log_level);
    try std.testing.expectEqualStrings("", mandatory_create.message_suffix);
    try std.testing.expect(!mandatory_create.shouldContinueWithoutToken());
}

test "resolveTokenPreparationAcquisition keeps token-fd ownership explicit after creation" {
    const no_cache = resolveTokenPreparationAcquisition(false);
    try std.testing.expectEqual(
        TokenPreparationAcquisitionDisposition.cache_allocation_failed,
        no_cache.disposition,
    );
    try std.testing.expectEqual(-@as(i32, @intFromEnum(linux_errno.NOMEM)), no_cache.result_code);
    try std.testing.expect(no_cache.should_close_token_fd);
    try std.testing.expect(!no_cache.should_store_token_fd);
    try std.testing.expect(!no_cache.should_store_feat_cache_token_fd);
    try std.testing.expect(!no_cache.succeeded());

    const prepared = resolveTokenPreparationAcquisition(true);
    try std.testing.expectEqual(TokenPreparationAcquisitionDisposition.prepared, prepared.disposition);
    try std.testing.expectEqual(@as(i32, 0), prepared.result_code);
    try std.testing.expect(!prepared.should_close_token_fd);
    try std.testing.expect(prepared.should_store_token_fd);
    try std.testing.expect(prepared.should_store_feat_cache_token_fd);
    try std.testing.expect(prepared.succeeded());
}

test "planReusePinnedMapOpen keeps pinned-map preflight explicit without claiming reopen io" {
    const prevented_null = planReusePinnedMapOpen(null);
    try std.testing.expectEqual(ReusePinnedMapOpenDisposition.prevented, prevented_null.disposition);
    try std.testing.expectEqualStrings("", prevented_null.pin_path);
    try std.testing.expect(!prevented_null.requiresPinnedMapOpen());

    const prevented_empty = planReusePinnedMapOpen("");
    try std.testing.expectEqual(ReusePinnedMapOpenDisposition.prevented, prevented_empty.disposition);
    try std.testing.expectEqualStrings("", prevented_empty.pin_path);
    try std.testing.expect(!prevented_empty.requiresPinnedMapOpen());

    const planned = planReusePinnedMapOpen("/sys/fs/bpf/reused_map");
    try std.testing.expectEqual(ReusePinnedMapOpenDisposition.optional_probe, planned.disposition);
    try std.testing.expectEqualStrings("/sys/fs/bpf/reused_map", planned.pin_path);
    try std.testing.expect(planned.requiresPinnedMapOpen());
}

test "classifyReusePinnedMapOpenFailure keeps missing pinned-map lookup distinct from hard failures" {
    const missing_pinned_map = classifyReusePinnedMapOpenFailure(-@as(i32, @intFromEnum(linux_errno.NOENT)));
    try std.testing.expectEqual(ReusePinnedMapOpenFailureDisposition.skip_missing_pinned_map, missing_pinned_map.disposition);
    try std.testing.expectEqual(TokenPreparationLogLevel.debug, missing_pinned_map.log_level);
    try std.testing.expect(missing_pinned_map.shouldContinueWithoutReuse());

    const denied = classifyReusePinnedMapOpenFailure(-@as(i32, @intFromEnum(linux_errno.PERM)));
    try std.testing.expectEqual(ReusePinnedMapOpenFailureDisposition.fail, denied.disposition);
    try std.testing.expectEqual(TokenPreparationLogLevel.warn, denied.log_level);
    try std.testing.expect(!denied.shouldContinueWithoutReuse());
}

test "chooseReusedMapName preserves the requested name when the kernel-truncated prefix matches" {
    try std.testing.expectEqualStrings(
        "process_pinned_map",
        chooseReusedMapName("process_pinned_map", "process_pinned_"),
    );
}

test "chooseReusedMapName falls back to the kernel info name when truncation rules do not match" {
    try std.testing.expectEqualStrings(
        "ringbuf_map",
        chooseReusedMapName("ringbuf_map_local", "ringbuf_map"),
    );
    try std.testing.expectEqualStrings(
        "different_prefix",
        chooseReusedMapName("process_pinned_map", "different_prefix"),
    );
    try std.testing.expectEqualStrings(
        "",
        chooseReusedMapName("process_pinned_map", ""),
    );
}

test "resolveReusePinnedMapAttempt keeps mismatch, reuse failure, and success ownership explicit" {
    const incompatible = resolveReusePinnedMapAttempt(false, 0);
    try std.testing.expectEqual(ReusePinnedMapResolutionDisposition.incompatible_map, incompatible.disposition);
    try std.testing.expectEqual(-@as(i32, @intFromEnum(linux_errno.INVAL)), incompatible.result_code);
    try std.testing.expect(incompatible.should_close_pin_fd);
    try std.testing.expect(!incompatible.should_mark_map_pinned);
    try std.testing.expect(!incompatible.succeeded());

    const reuse_failed = resolveReusePinnedMapAttempt(true, -@as(i32, @intFromEnum(linux_errno.PERM)));
    try std.testing.expectEqual(ReusePinnedMapResolutionDisposition.reuse_fd_failed, reuse_failed.disposition);
    try std.testing.expectEqual(-@as(i32, @intFromEnum(linux_errno.PERM)), reuse_failed.result_code);
    try std.testing.expect(reuse_failed.should_close_pin_fd);
    try std.testing.expect(!reuse_failed.should_mark_map_pinned);
    try std.testing.expect(!reuse_failed.succeeded());

    const reused = resolveReusePinnedMapAttempt(true, 0);
    try std.testing.expectEqual(ReusePinnedMapResolutionDisposition.reused, reused.disposition);
    try std.testing.expectEqual(@as(i32, 0), reused.result_code);
    try std.testing.expect(reused.should_close_pin_fd);
    try std.testing.expect(reused.should_mark_map_pinned);
    try std.testing.expect(reused.succeeded());
}

test "parseMapInfoFromFdinfo keeps the bounded key-value parsing behavior" {
    const info = try parseMapInfoFromFdinfo(
        "pos:\t0\n" ++
            "flags:\t02000002\n" ++
            "mnt_id:\t27\n" ++
            "map_id:\t27\n" ++
            "map_type:\t2\n" ++
            "key_size:\t8\n" ++
            "value_size:\t16\n" ++
            "max_entries:\t64\n" ++
            "map_flags:\t0x400\n" ++
            "map_extra:\t17\n",
    );

    try std.testing.expectEqual(@as(u32, 27), info.map_id);
    try std.testing.expectEqual(@as(u32, 2), info.map_type);
    try std.testing.expectEqual(@as(u32, 8), info.key_size);
    try std.testing.expectEqual(@as(u32, 16), info.value_size);
    try std.testing.expectEqual(@as(u32, 64), info.max_entries);
    try std.testing.expectEqual(@as(u32, 0x400), info.map_flags);
    try std.testing.expectEqual(@as(u64, 17), info.map_extra);
}

test "parseMapInfoFromFdinfo tolerates reordered fields and surrounding whitespace" {
    const info = try parseMapInfoFromFdinfo(
        "map_flags:   512\r\n" ++
            "map_id:\t44\r\n" ++
            "map_extra:\t0x20\r\n" ++
            "max_entries:\t128\r\n" ++
            "value_size:\t4\r\n" ++
            "key_size:\t 4\r\n" ++
            "map_type:\t1\r\n",
    );

    try std.testing.expectEqual(@as(u32, 44), info.map_id);
    try std.testing.expectEqual(@as(u32, 1), info.map_type);
    try std.testing.expectEqual(@as(u32, 4), info.key_size);
    try std.testing.expectEqual(@as(u32, 4), info.value_size);
    try std.testing.expectEqual(@as(u32, 128), info.max_entries);
    try std.testing.expectEqual(@as(u32, 512), info.map_flags);
    try std.testing.expectEqual(@as(u64, 0x20), info.map_extra);
}

test "parseMapInfoFromFdinfo keeps libbpf-style numeric bases explicit" {
    const info = try parseMapInfoFromFdinfo(
        "map_id:\t3\r\n" ++
            "map_type:\t1\r\n" ++
            "key_size:\t4\r\n" ++
            "value_size:\t8\r\n" ++
            "max_entries:\t16\r\n" ++
            "map_flags:\t010\r\n" ++
            "map_extra:\t0X2A\r\n",
    );

    try std.testing.expectEqual(@as(u32, 3), info.map_id);
    try std.testing.expectEqual(@as(u32, 8), info.map_flags);
    try std.testing.expectEqual(@as(u64, 42), info.map_extra);
}

test "parseMapInfoFromFdinfo mirrors libbpf's zero-init and last-field-wins fallback" {
    const info = try parseMapInfoFromFdinfo(
        "map_id:\t5\n" ++
            "map_type:\t1\n" ++
            "key_size:\t4\n" ++
            "map_extra:\t5\n" ++
            "map_id:\t9\n" ++
            "map_type:\t2\n" ++
            "map_extra:\t9\n" ++
            "value_size:\t8\n",
    );

    try std.testing.expectEqual(@as(u32, 9), info.map_id);
    try std.testing.expectEqual(@as(u32, 2), info.map_type);
    try std.testing.expectEqual(@as(u32, 4), info.key_size);
    try std.testing.expectEqual(@as(u32, 8), info.value_size);
    try std.testing.expectEqual(@as(u32, 0), info.max_entries);
    try std.testing.expectEqual(@as(u32, 0), info.map_flags);
    try std.testing.expectEqual(@as(u64, 9), info.map_extra);
}

test "parseMapInfoFromFdinfo keeps malformed values explicit" {
    try std.testing.expectError(error.InvalidValue, parseMapInfoFromFdinfo(
        "map_type:\t1\n" ++
            "key_size:\tfour\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t16\n" ++
            "map_flags:\t32\n",
    ));
    try std.testing.expectError(error.InvalidValue, parseMapInfoFromFdinfo(
        "map_id:\tbad\n" ++
            "map_type:\t1\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t16\n" ++
            "map_flags:\t32\n",
    ));
    try std.testing.expectError(error.InvalidValue, parseMapInfoFromFdinfo(
        "map_type:\t1\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t16\n" ++
            "map_extra:\tnope\n",
    ));
}

test "normalizeReuseCompatibilityMapFlags mirrors libbpf's DEVMAP readonly-prog exception" {
    try std.testing.expectEqual(
        @as(u32, 0),
        normalizeReuseCompatibilityMapFlags(bpf_map_type_devmap, bpf_f_rdonly_prog),
    );
    try std.testing.expectEqual(
        @as(u32, 0x20),
        normalizeReuseCompatibilityMapFlags(bpf_map_type_devmap_hash, bpf_f_rdonly_prog | 0x20),
    );
    try std.testing.expectEqual(
        @as(u32, bpf_f_rdonly_prog),
        normalizeReuseCompatibilityMapFlags(1, bpf_f_rdonly_prog),
    );
}

test "isMapReuseCompatible accepts DEVMAP info when only readonly-prog was injected by the kernel" {
    const expected = FdInfoMapInfo{
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = 0,
        .map_extra = 9,
    };
    const actual = FdInfoMapInfo{
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = bpf_f_rdonly_prog,
        .map_extra = 9,
    };

    try std.testing.expect(isMapReuseCompatible(expected, actual));
}

test "isMapReuseCompatible keeps exact field mismatches explicit outside the DEVMAP exception" {
    const expected = FdInfoMapInfo{
        .map_type = 1,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = 0,
        .map_extra = 9,
    };

    try std.testing.expect(!isMapReuseCompatible(expected, .{
        .map_type = 1,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = bpf_f_rdonly_prog,
        .map_extra = 9,
    }));
    try std.testing.expect(!isMapReuseCompatible(expected, .{
        .map_type = 1,
        .key_size = 4,
        .value_size = 16,
        .max_entries = 32,
        .map_flags = 0,
        .map_extra = 9,
    }));
    try std.testing.expect(!isMapReuseCompatible(expected, .{
        .map_type = 1,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = 0,
        .map_extra = 10,
    }));
}
