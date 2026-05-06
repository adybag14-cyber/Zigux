const std = @import("std");

pub const BridgeError = error{
    InvalidPid,
    InvalidFd,
    PathTooLong,
    MissingSeparator,
    EmptyFieldName,
    EmptyFieldValue,
    InvalidInteger,
};

pub const ParsedFdinfoLine = struct {
    field_name: []const u8,
    field_value: []const u8,
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
    has_map_extra: bool,
};

fn noSpaceToPathTooLong(err: anyerror) BridgeError {
    return switch (err) {
        error.NoSpaceLeft => error.PathTooLong,
        else => unreachable,
    };
}

fn parseAutoBaseU32(text: []const u8) BridgeError!u32 {
    const trimmed = std.mem.trim(u8, text, " \t\r\n");
    if (trimmed.len == 0) return error.InvalidInteger;

    if (trimmed[0] == '-') return error.InvalidInteger;

    if (trimmed.len > 2 and trimmed[0] == '0' and (trimmed[1] == 'x' or trimmed[1] == 'X')) {
        return std.fmt.parseUnsigned(u32, trimmed[2..], 16) catch error.InvalidInteger;
    }
    if (trimmed.len > 1 and trimmed[0] == '0') {
        return std.fmt.parseUnsigned(u32, trimmed[1..], 8) catch error.InvalidInteger;
    }

    return std.fmt.parseUnsigned(u32, trimmed, 10) catch error.InvalidInteger;
}

fn parseAutoBaseU64(text: []const u8) BridgeError!u64 {
    const trimmed = std.mem.trim(u8, text, " \t\r\n");
    if (trimmed.len == 0) return error.InvalidInteger;

    if (trimmed[0] == '-') return error.InvalidInteger;

    if (trimmed.len > 2 and trimmed[0] == '0' and (trimmed[1] == 'x' or trimmed[1] == 'X')) {
        return std.fmt.parseUnsigned(u64, trimmed[2..], 16) catch error.InvalidInteger;
    }
    if (trimmed.len > 1 and trimmed[0] == '0') {
        return std.fmt.parseUnsigned(u64, trimmed[1..], 8) catch error.InvalidInteger;
    }

    return std.fmt.parseUnsigned(u64, trimmed, 10) catch error.InvalidInteger;
}

pub fn buildProcFdinfoPath(buffer: []u8, pid: i32, fd: i32) BridgeError![]u8 {
    if (pid < 0) return error.InvalidPid;
    if (fd < 0) return error.InvalidFd;

    return std.fmt.bufPrint(buffer, "/proc/{d}/fdinfo/{d}", .{ pid, fd }) catch |err| noSpaceToPathTooLong(err);
}

pub fn parseFdinfoLine(line: []const u8) BridgeError!ParsedFdinfoLine {
    const trimmed = std.mem.trim(u8, line, " \t\r\n");
    const separator_index = std.mem.indexOfScalar(u8, trimmed, ':') orelse return error.MissingSeparator;

    const field_name = std.mem.trim(u8, trimmed[0..separator_index], " \t");
    const field_value = std.mem.trim(u8, trimmed[separator_index + 1 ..], " \t");

    if (field_name.len == 0) return error.EmptyFieldName;
    if (field_value.len == 0) return error.EmptyFieldValue;

    return .{
        .field_name = field_name,
        .field_value = field_value,
    };
}

pub fn applyFdinfoMapInfoLine(info: *FdinfoMapInfo, line: []const u8) BridgeError!bool {
    const trimmed = std.mem.trim(u8, line, " \t\r\n");
    if (trimmed.len == 0) return false;

    const parsed = try parseFdinfoLine(trimmed);

    if (std.mem.eql(u8, parsed.field_name, "map_type")) {
        info.map_type = try parseAutoBaseU32(parsed.field_value);
        return true;
    }
    if (std.mem.eql(u8, parsed.field_name, "key_size")) {
        info.key_size = try parseAutoBaseU32(parsed.field_value);
        return true;
    }
    if (std.mem.eql(u8, parsed.field_name, "value_size")) {
        info.value_size = try parseAutoBaseU32(parsed.field_value);
        return true;
    }
    if (std.mem.eql(u8, parsed.field_name, "max_entries")) {
        info.max_entries = try parseAutoBaseU32(parsed.field_value);
        return true;
    }
    if (std.mem.eql(u8, parsed.field_name, "map_flags")) {
        info.map_flags = try parseAutoBaseU32(parsed.field_value);
        return true;
    }
    if (std.mem.eql(u8, parsed.field_name, "map_extra")) {
        info.map_extra = try parseAutoBaseU64(parsed.field_value);
        return true;
    }

    return false;
}

pub fn parseFdinfoMapInfo(text: []const u8) BridgeError!FdinfoMapInfo {
    var info = FdinfoMapInfo{};
    var lines = std.mem.splitScalar(u8, text, '\n');

    while (lines.next()) |line| {
        _ = try applyFdinfoMapInfoLine(&info, line);
    }

    return info;
}

pub fn summarizeFdinfoMapInfo(info: FdinfoMapInfo) FdinfoMapInfoSummary {
    var parsed_field_count: usize = 0;

    inline for (.{ info.map_type, info.key_size, info.value_size, info.max_entries, info.map_flags }) |field| {
        if (field != null) parsed_field_count += 1;
    }
    if (info.map_extra != null) parsed_field_count += 1;

    return .{
        .parsed_field_count = parsed_field_count,
        .has_complete_legacy_fields = info.map_type != null and
            info.key_size != null and
            info.value_size != null and
            info.max_entries != null and
            info.map_flags != null,
        .has_map_extra = info.map_extra != null,
    };
}

test "buildProcFdinfoPath keeps the bounded procfs pathname contract explicit" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/proc/4321/fdinfo/17",
        try buildProcFdinfoPath(&buffer, 4321, 17),
    );
    try std.testing.expectError(error.InvalidPid, buildProcFdinfoPath(&buffer, -1, 17));
    try std.testing.expectError(error.InvalidFd, buildProcFdinfoPath(&buffer, 4321, -1));
}

test "buildProcFdinfoPath keeps overflow failures explicit" {
    var buffer: [12]u8 = undefined;

    try std.testing.expectError(
        error.PathTooLong,
        buildProcFdinfoPath(&buffer, 4321, 17),
    );
}

test "parseFdinfoLine trims libbpf style field names and values" {
    const parsed = try parseFdinfoLine(" key_size:\t64 \r");

    try std.testing.expectEqualStrings("key_size", parsed.field_name);
    try std.testing.expectEqualStrings("64", parsed.field_value);
}

test "parseFdinfoMapInfo keeps the legacy map info fields compact and ignores unrelated lines" {
    const parsed = try parseFdinfoMapInfo(
        \\pos: 0
        \\flags: 02000002
        \\mnt_id: 27
        \\map_type: 5
        \\key_size: 8
        \\value_size: 16
        \\max_entries: 1024
        \\map_flags: 0x20
    );

    try std.testing.expectEqual(@as(?u32, 5), parsed.map_type);
    try std.testing.expectEqual(@as(?u32, 8), parsed.key_size);
    try std.testing.expectEqual(@as(?u32, 16), parsed.value_size);
    try std.testing.expectEqual(@as(?u32, 1024), parsed.max_entries);
    try std.testing.expectEqual(@as(?u32, 0x20), parsed.map_flags);
    try std.testing.expectEqual(@as(?u64, null), parsed.map_extra);
}

test "applyFdinfoMapInfoLine keeps repeated fields last-write-wins and octal or decimal parsing explicit" {
    var info = FdinfoMapInfo{};

    try std.testing.expect(try applyFdinfoMapInfoLine(&info, "map_flags:\t010"));
    try std.testing.expect(try applyFdinfoMapInfoLine(&info, "map_flags:\t12"));
    try std.testing.expect(try applyFdinfoMapInfoLine(&info, "key_size:\t4"));
    try std.testing.expectEqual(@as(?u32, 12), info.map_flags);
    try std.testing.expectEqual(@as(?u32, 4), info.key_size);
}

test "fdinfo map info parsing keeps malformed lines and values explicit" {
    var info = FdinfoMapInfo{};

    try std.testing.expect(!try applyFdinfoMapInfoLine(&info, ""));
    try std.testing.expect(!try applyFdinfoMapInfoLine(&info, "ignored:\t17"));
    try std.testing.expectError(error.MissingSeparator, parseFdinfoLine("map_type"));
    try std.testing.expectError(error.EmptyFieldValue, parseFdinfoLine("map_type:\t"));
    try std.testing.expectError(error.InvalidInteger, applyFdinfoMapInfoLine(&info, "map_type:\tnope"));
    try std.testing.expectError(error.InvalidInteger, applyFdinfoMapInfoLine(&info, "map_flags:\t-1"));
    try std.testing.expectError(error.InvalidInteger, applyFdinfoMapInfoLine(&info, "map_extra:\tnope"));
}

test "parseFdinfoMapInfo keeps map_extra numeric parsing explicit" {
    const parsed = try parseFdinfoMapInfo(
        \\map_type: 14
        \\map_flags: 010
        \\map_extra: 0X2A
    );

    try std.testing.expectEqual(@as(?u32, 14), parsed.map_type);
    try std.testing.expectEqual(@as(?u32, 8), parsed.map_flags);
    try std.testing.expectEqual(@as(?u64, 42), parsed.map_extra);
}

test "summarizeFdinfoMapInfo keeps bounded completion state reviewable" {
    const partial = summarizeFdinfoMapInfo(.{
        .map_type = 5,
        .key_size = 8,
    });
    try std.testing.expectEqual(@as(usize, 2), partial.parsed_field_count);
    try std.testing.expect(!partial.has_complete_legacy_fields);
    try std.testing.expect(!partial.has_map_extra);

    const complete = summarizeFdinfoMapInfo(.{
        .map_type = 5,
        .key_size = 8,
        .value_size = 16,
        .max_entries = 1024,
        .map_flags = 0x20,
        .map_extra = 42,
    });
    try std.testing.expectEqual(@as(usize, 6), complete.parsed_field_count);
    try std.testing.expect(complete.has_complete_legacy_fields);
    try std.testing.expect(complete.has_map_extra);
}
