const std = @import("std");

pub const default_bpf_fs_path = "/sys/fs/bpf";

pub const PinPathError = error{
    NameTooLong,
};

fn noSpaceToNameTooLong(err: anyerror) PinPathError {
    return switch (err) {
        error.NoSpaceLeft => error.NameTooLong,
        else => unreachable,
    };
}

pub fn pathnameConcat(buffer: []u8, path: []const u8, name: []const u8) PinPathError![]u8 {
    return std.fmt.bufPrint(buffer, "{s}/{s}", .{ path, name }) catch |err| noSpaceToNameTooLong(err);
}

pub fn sanitizePinPath(path: []u8) void {
    for (path) |*byte| {
        if (byte.* == '.') {
            byte.* = '_';
        }
    }
}

pub fn buildMapPinPath(buffer: []u8, root_path: ?[]const u8, map_name: []const u8) PinPathError![]u8 {
    return pathnameConcat(buffer, root_path orelse default_bpf_fs_path, map_name);
}

pub fn buildSanitizedMapPinPath(buffer: []u8, root_path: ?[]const u8, map_name: []const u8) PinPathError![]u8 {
    const full_path = try buildMapPinPath(buffer, root_path, map_name);
    sanitizePinPath(full_path);
    return full_path;
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
        "/tmp/bpf_v1_2/cache_map",
        try buildSanitizedMapPinPath(&buffer, "/tmp/bpf.v1.2", "cache.map"),
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
}
