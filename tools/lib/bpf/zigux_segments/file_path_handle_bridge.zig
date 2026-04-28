const std = @import("std");

pub const FdInfoMapInfo = struct {
    map_type: u32,
    key_size: u32,
    value_size: u32,
    max_entries: u32,
    map_flags: u32,
};

pub const ReuseProbeExpectation = struct {
    map_type: u32,
    key_size: u32,
    value_size: u32,
    max_entries: u32,
    map_flags: u32,
};

pub const bpf_map_type_devmap: u32 = 14;
pub const bpf_map_type_devmap_hash: u32 = 25;
pub const bpf_f_rdonly_prog: u32 = 1 << 7;

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

fn normalizedReuseFlags(info: FdInfoMapInfo) u32 {
    return switch (info.map_type) {
        bpf_map_type_devmap, bpf_map_type_devmap_hash => info.map_flags & ~bpf_f_rdonly_prog,
        else => info.map_flags,
    };
}

pub fn isReuseCompatibleWithinFdinfo(
    fdinfo_info: FdInfoMapInfo,
    expectation: ReuseProbeExpectation,
) bool {
    return fdinfo_info.map_type == expectation.map_type and
        fdinfo_info.key_size == expectation.key_size and
        fdinfo_info.value_size == expectation.value_size and
        fdinfo_info.max_entries == expectation.max_entries and
        normalizedReuseFlags(fdinfo_info) == expectation.map_flags;
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

test "isReuseCompatibleWithinFdinfo mirrors the devmap read-only-prog flag exception" {
    const devmap_fdinfo = FdInfoMapInfo{
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 4,
        .max_entries = 64,
        .map_flags = bpf_f_rdonly_prog | 0x20,
    };

    try std.testing.expect(isReuseCompatibleWithinFdinfo(devmap_fdinfo, .{
        .map_type = bpf_map_type_devmap,
        .key_size = 4,
        .value_size = 4,
        .max_entries = 64,
        .map_flags = 0x20,
    }));

    const devmap_hash_fdinfo = FdInfoMapInfo{
        .map_type = bpf_map_type_devmap_hash,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = bpf_f_rdonly_prog | 0x8,
    };

    try std.testing.expect(isReuseCompatibleWithinFdinfo(devmap_hash_fdinfo, .{
        .map_type = bpf_map_type_devmap_hash,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 32,
        .map_flags = 0x8,
    }));
}

test "isReuseCompatibleWithinFdinfo keeps non-devmap flag drift and shape mismatches explicit" {
    const base = FdInfoMapInfo{
        .map_type = 1,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 128,
        .map_flags = 0x20,
    };

    try std.testing.expect(isReuseCompatibleWithinFdinfo(base, .{
        .map_type = 1,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 128,
        .map_flags = 0x20,
    }));
    try std.testing.expect(!isReuseCompatibleWithinFdinfo(base, .{
        .map_type = 1,
        .key_size = 4,
        .value_size = 8,
        .max_entries = 128,
        .map_flags = 0x40,
    }));
    try std.testing.expect(!isReuseCompatibleWithinFdinfo(base, .{
        .map_type = 1,
        .key_size = 4,
        .value_size = 16,
        .max_entries = 128,
        .map_flags = 0x20,
    }));
}
