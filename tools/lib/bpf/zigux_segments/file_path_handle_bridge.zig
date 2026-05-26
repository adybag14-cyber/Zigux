const std = @import("std");

pub const default_proc_fdinfo_root = "/proc/self/fdinfo";

pub const FilePathHandleBridgeError = error{
    EmptyMapName,
    InvalidProcRoot,
    NameTooLong,
    NegativeFd,
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
        error.EmptyMapName, error.InvalidProcRoot, error.NegativeFd => -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
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
