const std = @import("std");

pub const default_bpf_fs_path = "/sys/fs/bpf";

pub const PinPathError = error{
    NameTooLong,
    EmptyName,
    InvalidName,
    InvalidRootPath,
};

fn noSpaceToNameTooLong(err: anyerror) PinPathError {
    return switch (err) {
        error.NoSpaceLeft => error.NameTooLong,
        else => unreachable,
    };
}

pub fn pathnameConcat(buffer: []u8, path: []const u8, name: []const u8) PinPathError![]u8 {
    if (path.len != 0 and path[path.len - 1] == '/') {
        return std.fmt.bufPrint(buffer, "{s}{s}", .{ path, name }) catch |err| noSpaceToNameTooLong(err);
    }

    return std.fmt.bufPrint(buffer, "{s}/{s}", .{ path, name }) catch |err| noSpaceToNameTooLong(err);
}

pub fn sanitizePinPath(path: []u8) void {
    for (path) |*byte| {
        if (byte.* == '.') {
            byte.* = '_';
        }
    }
}

fn sanitizePinnedLeafName(path: []u8, leaf_name: []const u8) void {
    sanitizePinPath(path[path.len - leaf_name.len ..]);
}

pub fn validatePinName(name: []const u8) PinPathError!void {
    if (name.len == 0) {
        return error.EmptyName;
    }
    if (std.mem.indexOfScalar(u8, name, 0) != null or std.mem.indexOfScalar(u8, name, '/') != null) {
        return error.InvalidName;
    }
}

pub fn validatePinRootPath(root_path: []const u8) PinPathError!void {
    if (root_path.len == 0 or root_path[0] != '/') {
        return error.InvalidRootPath;
    }
    if (std.mem.indexOfScalar(u8, root_path, 0) != null) {
        return error.InvalidRootPath;
    }
    if (root_path.len > 1 and root_path[root_path.len - 1] == '/') {
        return error.InvalidRootPath;
    }
}

fn buildPinnedPath(buffer: []u8, root_path: ?[]const u8, leaf_name: []const u8) PinPathError![]u8 {
    return pathnameConcat(buffer, root_path orelse default_bpf_fs_path, leaf_name);
}

fn buildValidatedPinnedPath(buffer: []u8, root_path: ?[]const u8, leaf_name: []const u8) PinPathError![]u8 {
    const resolved_root = root_path orelse default_bpf_fs_path;
    try validatePinRootPath(resolved_root);
    try validatePinName(leaf_name);
    return pathnameConcat(buffer, resolved_root, leaf_name);
}

fn buildSanitizedPinnedPath(buffer: []u8, root_path: ?[]const u8, leaf_name: []const u8) PinPathError![]u8 {
    const full_path = try buildPinnedPath(buffer, root_path, leaf_name);
    sanitizePinnedLeafName(full_path, leaf_name);
    return full_path;
}

fn buildValidatedSanitizedPinnedPath(buffer: []u8, root_path: ?[]const u8, leaf_name: []const u8) PinPathError![]u8 {
    const full_path = try buildValidatedPinnedPath(buffer, root_path, leaf_name);
    sanitizePinnedLeafName(full_path, leaf_name);
    return full_path;
}

pub fn buildMapPinPath(buffer: []u8, root_path: ?[]const u8, map_name: []const u8) PinPathError![]u8 {
    return buildPinnedPath(buffer, root_path, map_name);
}

pub fn buildValidatedMapPinPath(buffer: []u8, root_path: ?[]const u8, map_name: []const u8) PinPathError![]u8 {
    return buildValidatedPinnedPath(buffer, root_path, map_name);
}

pub fn buildSanitizedMapPinPath(buffer: []u8, root_path: ?[]const u8, map_name: []const u8) PinPathError![]u8 {
    return buildSanitizedPinnedPath(buffer, root_path, map_name);
}

pub fn buildValidatedSanitizedMapPinPath(buffer: []u8, root_path: ?[]const u8, map_name: []const u8) PinPathError![]u8 {
    return buildValidatedSanitizedPinnedPath(buffer, root_path, map_name);
}

pub fn buildProgramPinPath(buffer: []u8, root_path: ?[]const u8, prog_name: []const u8) PinPathError![]u8 {
    return buildPinnedPath(buffer, root_path, prog_name);
}

pub fn buildValidatedProgramPinPath(buffer: []u8, root_path: ?[]const u8, prog_name: []const u8) PinPathError![]u8 {
    return buildValidatedPinnedPath(buffer, root_path, prog_name);
}

pub fn buildSanitizedProgramPinPath(buffer: []u8, root_path: ?[]const u8, prog_name: []const u8) PinPathError![]u8 {
    return buildSanitizedPinnedPath(buffer, root_path, prog_name);
}

pub fn buildValidatedSanitizedProgramPinPath(buffer: []u8, root_path: ?[]const u8, prog_name: []const u8) PinPathError![]u8 {
    return buildValidatedSanitizedPinnedPath(buffer, root_path, prog_name);
}

test "pathnameConcat keeps the bounded libbpf path-join behavior" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/example_map",
        try pathnameConcat(&buffer, "/sys/fs/bpf", "example_map"),
    );
    try std.testing.expectEqualStrings(
        "relative/root/map",
        try pathnameConcat(&buffer, "relative/root", "map"),
    );
}

test "pathnameConcat preserves stable outputs when the root already ends in slash" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/root_map",
        try pathnameConcat(&buffer, "/", "root_map"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf/cache_map",
        try pathnameConcat(&buffer, "/tmp/bpf/", "cache_map"),
    );
}

test "buildMapPinPath defaults to bpffs when the caller leaves the root unset" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/stats_map",
        try buildMapPinPath(&buffer, null, "stats_map"),
    );
    try std.testing.expectEqualStrings(
        "/custom/root/stats_map",
        try buildMapPinPath(&buffer, "/custom/root", "stats_map"),
    );
}

test "buildSanitizedMapPinPath mirrors libbpf dot sanitization for pin names" {
    var buffer: [96]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/metrics_v1",
        try buildSanitizedMapPinPath(&buffer, null, "metrics.v1"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1.2/cache_map",
        try buildSanitizedMapPinPath(&buffer, "/tmp/bpf.v1.2", "cache.map"),
    );
    try std.testing.expectEqualStrings(
        "/cache_map",
        try buildSanitizedMapPinPath(&buffer, "/", "cache.map"),
    );
}

test "buildValidatedMapPinPath keeps unsanitized validated pin paths explicit" {
    var buffer: [96]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1/metrics.v1",
        try buildValidatedMapPinPath(&buffer, "/tmp/bpf.v1", "metrics.v1"),
    );
    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/stats.map",
        try buildValidatedMapPinPath(&buffer, null, "stats.map"),
    );
    try std.testing.expectError(
        error.InvalidName,
        buildValidatedMapPinPath(&buffer, null, "stats/map"),
    );
    try std.testing.expectError(
        error.InvalidRootPath,
        buildValidatedMapPinPath(&buffer, "/tmp/bpf\x00tmp", "stats.map"),
    );
}

test "program pin-path helpers mirror the bounded libbpf program pin contract" {
    var buffer: [96]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/xdp_dispatch",
        try buildProgramPinPath(&buffer, null, "xdp_dispatch"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1/xdp_dispatch",
        try buildValidatedProgramPinPath(&buffer, "/tmp/bpf.v1", "xdp_dispatch"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1/xdp_dispatch_v1",
        try buildSanitizedProgramPinPath(&buffer, "/tmp/bpf.v1", "xdp_dispatch.v1"),
    );
    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/xdp_dispatch_v1",
        try buildValidatedSanitizedProgramPinPath(&buffer, null, "xdp_dispatch.v1"),
    );
    try std.testing.expectError(
        error.InvalidName,
        buildValidatedProgramPinPath(&buffer, null, "xdp/dispatch"),
    );
    try std.testing.expectError(
        error.InvalidRootPath,
        buildValidatedSanitizedProgramPinPath(&buffer, "tmp/bpf", "xdp_dispatch.v1"),
    );
}

test "validated pin-path helpers keep pin-name and root-path shape checks explicit" {
    var buffer: [96]u8 = undefined;

    try validatePinName("stats_map");
    try std.testing.expectError(error.EmptyName, validatePinName(""));
    try std.testing.expectError(error.InvalidName, validatePinName("stats/map"));
    try std.testing.expectError(error.InvalidName, validatePinName("stats\x00map"));

    try validatePinRootPath("/sys/fs/bpf");
    try std.testing.expectError(error.InvalidRootPath, validatePinRootPath("relative/root"));
    try std.testing.expectError(error.InvalidRootPath, validatePinRootPath("/sys/fs/bpf/"));
    try std.testing.expectError(error.InvalidRootPath, validatePinRootPath("/sys/fs/bpf\x00tmp"));

    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/metrics_v1",
        try buildValidatedSanitizedMapPinPath(&buffer, null, "metrics.v1"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1/metrics_v1",
        try buildValidatedSanitizedMapPinPath(&buffer, "/tmp/bpf.v1", "metrics.v1"),
    );
    try std.testing.expectError(
        error.InvalidName,
        buildValidatedSanitizedMapPinPath(&buffer, null, "metrics/v1"),
    );
    try std.testing.expectError(
        error.InvalidRootPath,
        buildValidatedSanitizedMapPinPath(&buffer, "tmp/bpf", "metrics.v1"),
    );
    try std.testing.expectError(
        error.InvalidRootPath,
        buildValidatedSanitizedMapPinPath(&buffer, "/tmp/bpf\x00tmp", "metrics.v1"),
    );
}

test "pin-path helpers keep length failures explicit" {
    var buffer: [16]u8 = undefined;

    try std.testing.expectError(
        error.NameTooLong,
        pathnameConcat(&buffer, "/sys/fs/bpf", "very_long_map_name"),
    );
    try std.testing.expectError(
        error.NameTooLong,
        buildMapPinPath(&buffer, "/custom/root", "very_long_map_name"),
    );
    try std.testing.expectError(
        error.NameTooLong,
        buildProgramPinPath(&buffer, "/custom/root", "very_long_program_name"),
    );
}
