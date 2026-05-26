const std = @import("std");

pub const default_proc_fdinfo_root = "/proc/self/fdinfo";

pub const FilePathHandleBridgeError = error{
    EmptyMapName,
    EmptyFdinfoLine,
    EmptyFdinfoLineKey,
    EmptyFdinfoLineValue,
    MissingFdinfoLineSeparator,
    InvalidProcRoot,
    NameTooLong,
    NegativeFd,
};

pub const FdinfoLine = struct {
    key: []const u8,
    value: []const u8,
};

pub const ReusedMapNameDisposition = enum {
    exact_name,
    terminated_prefix,
    truncated_fixed_width,
};

pub const ReusedMapNameSummary = struct {
    source_len: usize,
    retained_len: usize,
    terminator_index: ?usize,
    disposition: ReusedMapNameDisposition,
    name: []const u8,
};

fn noSpaceToNameTooLong(err: anyerror) FilePathHandleBridgeError {
    return switch (err) {
        error.NoSpaceLeft => error.NameTooLong,
        else => unreachable,
    };
}

pub fn validateProcFdinfoRoot(root: []const u8) FilePathHandleBridgeError!void {
    if (root.len == 0 or root[0] != '/') {
        return error.InvalidProcRoot;
    }
    if (std.mem.indexOfScalar(u8, root, 0) != null) {
        return error.InvalidProcRoot;
    }
    if (root.len > 1 and root[root.len - 1] == '/') {
        return error.InvalidProcRoot;
    }
}

pub fn buildProcFdinfoPath(
    buffer: []u8,
    proc_root: ?[]const u8,
    fd: i32,
) FilePathHandleBridgeError![]const u8 {
    const root = proc_root orelse default_proc_fdinfo_root;
    try validateProcFdinfoRoot(root);
    if (fd < 0) {
        return error.NegativeFd;
    }
    return std.fmt.bufPrint(buffer, "{s}/{d}", .{ root, fd }) catch |err| noSpaceToNameTooLong(err);
}

pub fn parseFdinfoLine(line: []const u8) FilePathHandleBridgeError!FdinfoLine {
    const trimmed_line = std.mem.trim(u8, line, " \t\r\n");
    if (trimmed_line.len == 0) {
        return error.EmptyFdinfoLine;
    }

    const separator_index = std.mem.indexOfScalar(u8, trimmed_line, ':') orelse {
        return error.MissingFdinfoLineSeparator;
    };

    const key = std.mem.trim(u8, trimmed_line[0..separator_index], " \t");
    if (key.len == 0) {
        return error.EmptyFdinfoLineKey;
    }

    const value = std.mem.trim(u8, trimmed_line[separator_index + 1 ..], " \t");
    if (value.len == 0) {
        return error.EmptyFdinfoLineValue;
    }

    return .{
        .key = key,
        .value = value,
    };
}

fn retainedNameSlice(observed_name: []const u8) FilePathHandleBridgeError!ReusedMapNameSummary {
    if (observed_name.len == 0) {
        return error.EmptyMapName;
    }

    const terminator_index = std.mem.indexOfScalar(u8, observed_name, 0);
    const retained_len = terminator_index orelse observed_name.len;
    const disposition: ReusedMapNameDisposition = if (terminator_index) |index|
        if (index + 1 == observed_name.len) .exact_name else .terminated_prefix
    else
        .truncated_fixed_width;

    return .{
        .source_len = observed_name.len,
        .retained_len = retained_len,
        .terminator_index = terminator_index,
        .disposition = disposition,
        .name = observed_name[0..retained_len],
    };
}

pub fn summarizeReusedMapName(observed_name: []const u8) FilePathHandleBridgeError!ReusedMapNameSummary {
    return retainedNameSlice(observed_name);
}

pub fn resolveReusedMapName(
    buffer: []u8,
    observed_name: []const u8,
) FilePathHandleBridgeError![]const u8 {
    const summary = try retainedNameSlice(observed_name);
    return std.fmt.bufPrint(buffer, "{s}", .{summary.name}) catch |err| noSpaceToNameTooLong(err);
}

fn bridgeErrorReturn(err: FilePathHandleBridgeError) i32 {
    return switch (err) {
        error.NameTooLong => -@as(i32, @intFromEnum(std.os.linux.E.NAMETOOLONG)),
        error.EmptyMapName,
        error.EmptyFdinfoLine,
        error.EmptyFdinfoLineKey,
        error.EmptyFdinfoLineValue,
        error.MissingFdinfoLineSeparator,
        error.InvalidProcRoot,
        error.NegativeFd,
        => -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
    };
}

fn bridgeLengthReturn(result: FilePathHandleBridgeError![]const u8) i32 {
    const value = result catch |err| return bridgeErrorReturn(err);
    return std.math.cast(i32, value.len) orelse -@as(i32, @intFromEnum(std.os.linux.E.OVERFLOW));
}

pub fn buildProcFdinfoPathReturn(
    buffer: []u8,
    proc_root: ?[]const u8,
    fd: i32,
) i32 {
    return bridgeLengthReturn(buildProcFdinfoPath(buffer, proc_root, fd));
}

pub fn resolveReusedMapNameReturn(buffer: []u8, observed_name: []const u8) i32 {
    return bridgeLengthReturn(resolveReusedMapName(buffer, observed_name));
}

test "phase8 file-path bridge keeps proc fdinfo path outputs stable" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/proc/self/fdinfo/17",
        try buildProcFdinfoPath(&buffer, null, 17),
    );
    try std.testing.expectEqualStrings(
        "/proc/4242/fdinfo/9",
        try buildProcFdinfoPath(&buffer, "/proc/4242/fdinfo", 9),
    );
}

test "phase8 file-path bridge keeps proc fdinfo validation failures explicit" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectError(error.InvalidProcRoot, buildProcFdinfoPath(&buffer, "proc/fdinfo", 7));
    try std.testing.expectError(error.InvalidProcRoot, buildProcFdinfoPath(&buffer, "/proc/fdinfo/", 7));
    try std.testing.expectError(error.NegativeFd, buildProcFdinfoPath(&buffer, null, -1));
}

test "phase8 file-path bridge keeps proc fdinfo errno-shaped return helpers explicit" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqual(
        @as(i32, "/proc/self/fdinfo/33".len),
        buildProcFdinfoPathReturn(&buffer, null, 33),
    );
    try std.testing.expectEqualStrings(
        "/proc/self/fdinfo/33",
        buffer[0.."/proc/self/fdinfo/33".len],
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        buildProcFdinfoPathReturn(&buffer, "proc/fdinfo", 33),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        buildProcFdinfoPathReturn(&buffer, null, -3),
    );

    var tiny: [12]u8 = undefined;
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NAMETOOLONG)),
        buildProcFdinfoPathReturn(&tiny, null, 12345),
    );
}

test "phase8 file-path bridge keeps fdinfo line splitting outputs stable" {
    const simple = try parseFdinfoLine("map_flags:\t0x20\n");
    try std.testing.expectEqualStrings("map_flags", simple.key);
    try std.testing.expectEqualStrings("0x20", simple.value);

    const padded = try parseFdinfoLine("  max_entries :  1024  \r\n");
    try std.testing.expectEqualStrings("max_entries", padded.key);
    try std.testing.expectEqualStrings("1024", padded.value);

    const extra_colon = try parseFdinfoLine("map_name:\tstats:rx\n");
    try std.testing.expectEqualStrings("map_name", extra_colon.key);
    try std.testing.expectEqualStrings("stats:rx", extra_colon.value);
}

test "phase8 file-path bridge keeps fdinfo line parser failures explicit" {
    try std.testing.expectError(error.EmptyFdinfoLine, parseFdinfoLine(""));
    try std.testing.expectError(error.EmptyFdinfoLine, parseFdinfoLine(" \t\r\n "));
    try std.testing.expectError(error.MissingFdinfoLineSeparator, parseFdinfoLine("map_flags 0x20"));
    try std.testing.expectError(error.EmptyFdinfoLineKey, parseFdinfoLine(" : 0x20"));
    try std.testing.expectError(error.EmptyFdinfoLineValue, parseFdinfoLine("map_flags:\t "));
}

test "phase8 file-path bridge keeps reused-map name retention summaries stable" {
    const exact = try summarizeReusedMapName("stats_map\x00");
    try std.testing.expectEqual(ReusedMapNameDisposition.exact_name, exact.disposition);
    try std.testing.expectEqual(@as(usize, 9), exact.retained_len);
    try std.testing.expectEqual(@as(?usize, 9), exact.terminator_index);
    try std.testing.expectEqualStrings("stats_map", exact.name);

    const prefix = try summarizeReusedMapName("stats\x00shadow");
    try std.testing.expectEqual(ReusedMapNameDisposition.terminated_prefix, prefix.disposition);
    try std.testing.expectEqual(@as(usize, 5), prefix.retained_len);
    try std.testing.expectEqual(@as(?usize, 5), prefix.terminator_index);
    try std.testing.expectEqualStrings("stats", prefix.name);

    const truncated = try summarizeReusedMapName("truncated_name");
    try std.testing.expectEqual(ReusedMapNameDisposition.truncated_fixed_width, truncated.disposition);
    try std.testing.expectEqual(@as(?usize, null), truncated.terminator_index);
    try std.testing.expectEqualStrings("truncated_name", truncated.name);
}

test "phase8 file-path bridge keeps reused-map name copy outputs stable" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "stats_map",
        try resolveReusedMapName(&buffer, "stats_map\x00"),
    );
    try std.testing.expectEqualStrings(
        "stats",
        try resolveReusedMapName(&buffer, "stats\x00shadow"),
    );
    try std.testing.expectEqualStrings(
        "truncated_name",
        try resolveReusedMapName(&buffer, "truncated_name"),
    );
}

test "phase8 file-path bridge keeps reused-map name errors and errno returns explicit" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectError(error.EmptyMapName, summarizeReusedMapName(""));
    try std.testing.expectError(error.EmptyMapName, resolveReusedMapName(&buffer, ""));

    try std.testing.expectEqual(
        @as(i32, "stats_map".len),
        resolveReusedMapNameReturn(&buffer, "stats_map\x00"),
    );
    try std.testing.expectEqualStrings("stats_map", buffer[0.."stats_map".len]);
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        resolveReusedMapNameReturn(&buffer, ""),
    );

    var tiny: [8]u8 = undefined;
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NAMETOOLONG)),
        resolveReusedMapNameReturn(&tiny, "very_long_fixed_width_name"),
    );
}
