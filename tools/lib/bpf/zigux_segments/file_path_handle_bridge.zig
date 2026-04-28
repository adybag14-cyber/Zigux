const std = @import("std");

pub const FdInfoMapInfo = struct {
    map_type: u32,
    key_size: u32,
    value_size: u32,
    max_entries: u32,
    map_flags: u32,
};

pub const default_bpf_fs_path = "/sys/fs/bpf";

pub const TokenPreparationDisposition = enum {
    prevented,
    optional_probe,
    mandatory_probe,
};

pub const TokenPreparationLogLevel = enum {
    debug,
    warn,
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

pub const FilePathHandleBridgeError = error{
    PathTooLong,
    InvalidPid,
    InvalidFd,
    DuplicateField,
    InvalidValue,
    MissingMapType,
    MissingKeySize,
    MissingValueSize,
    MissingMaxEntries,
    MissingMapFlags,
};

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
    seen: *bool,
    destination: *u32,
) FilePathHandleBridgeError!bool {
    const value_text = fieldValue(line, key) orelse return false;
    if (seen.*) {
        return error.DuplicateField;
    }

    destination.* = std.fmt.parseUnsigned(u32, value_text, 10) catch return error.InvalidValue;
    seen.* = true;
    return true;
}

fn parseFlagField(
    line: []const u8,
    seen: *bool,
    destination: *u32,
) FilePathHandleBridgeError!bool {
    const value_text = fieldValue(line, "map_flags") orelse return false;
    if (seen.*) {
        return error.DuplicateField;
    }

    const parsed = std.fmt.parseInt(i64, value_text, 0) catch return error.InvalidValue;
    if (parsed < 0) {
        return error.InvalidValue;
    }

    destination.* = std.math.cast(u32, parsed) orelse return error.InvalidValue;
    seen.* = true;
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

pub fn parseMapInfoFromFdinfo(input: []const u8) FilePathHandleBridgeError!FdInfoMapInfo {
    var info = FdInfoMapInfo{
        .map_type = 0,
        .key_size = 0,
        .value_size = 0,
        .max_entries = 0,
        .map_flags = 0,
    };

    var saw_map_type = false;
    var saw_key_size = false;
    var saw_value_size = false;
    var saw_max_entries = false;
    var saw_map_flags = false;

    var lines = std.mem.tokenizeAny(u8, input, "\r\n");
    while (lines.next()) |line| {
        if (try parseDecimalField(line, "map_type", &saw_map_type, &info.map_type)) continue;
        if (try parseDecimalField(line, "key_size", &saw_key_size, &info.key_size)) continue;
        if (try parseDecimalField(line, "value_size", &saw_value_size, &info.value_size)) continue;
        if (try parseDecimalField(line, "max_entries", &saw_max_entries, &info.max_entries)) continue;
        if (try parseFlagField(line, &saw_map_flags, &info.map_flags)) continue;
    }

    if (!saw_map_type) return error.MissingMapType;
    if (!saw_key_size) return error.MissingKeySize;
    if (!saw_value_size) return error.MissingValueSize;
    if (!saw_max_entries) return error.MissingMaxEntries;
    if (!saw_map_flags) return error.MissingMapFlags;

    return info;
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

test "parseMapInfoFromFdinfo keeps the bounded key-value parsing behavior" {
    const info = try parseMapInfoFromFdinfo(
        "pos:\t0\n" ++
            "flags:\t02000002\n" ++
            "mnt_id:\t27\n" ++
            "map_type:\t2\n" ++
            "key_size:\t8\n" ++
            "value_size:\t16\n" ++
            "max_entries:\t64\n" ++
            "map_flags:\t0x400\n",
    );

    try std.testing.expectEqual(@as(u32, 2), info.map_type);
    try std.testing.expectEqual(@as(u32, 8), info.key_size);
    try std.testing.expectEqual(@as(u32, 16), info.value_size);
    try std.testing.expectEqual(@as(u32, 64), info.max_entries);
    try std.testing.expectEqual(@as(u32, 0x400), info.map_flags);
}

test "parseMapInfoFromFdinfo tolerates reordered fields and surrounding whitespace" {
    const info = try parseMapInfoFromFdinfo(
        "map_flags:   512\r\n" ++
            "max_entries:\t128\r\n" ++
            "value_size:\t4\r\n" ++
            "key_size:\t 4\r\n" ++
            "map_type:\t1\r\n",
    );

    try std.testing.expectEqual(@as(u32, 1), info.map_type);
    try std.testing.expectEqual(@as(u32, 4), info.key_size);
    try std.testing.expectEqual(@as(u32, 4), info.value_size);
    try std.testing.expectEqual(@as(u32, 128), info.max_entries);
    try std.testing.expectEqual(@as(u32, 512), info.map_flags);
}

test "parseMapInfoFromFdinfo keeps malformed duplicates and missing fields explicit" {
    try std.testing.expectError(error.DuplicateField, parseMapInfoFromFdinfo(
        "map_type:\t1\n" ++
            "map_type:\t2\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t16\n" ++
            "map_flags:\t32\n",
    ));
    try std.testing.expectError(error.InvalidValue, parseMapInfoFromFdinfo(
        "map_type:\t1\n" ++
            "key_size:\tfour\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t16\n" ++
            "map_flags:\t32\n",
    ));
    try std.testing.expectError(error.MissingMapFlags, parseMapInfoFromFdinfo(
        "map_type:\t1\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t16\n",
    ));
}
