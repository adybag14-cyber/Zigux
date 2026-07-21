const std = @import("std");

pub const stage_python = "zig run scripts/zigux/stage_pinned_zig_archive.zig";
pub const stage_zig = "zig run scripts/zigux/stage_pinned_zig_archive.zig";
pub const archive_sha_verify = "verify_pinned_archive_sha256";
pub const bootstrap_zig_helper = "ensure_bootstrap_zig";
pub const archive_check_python = "zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only";
pub const archive_check_zig = "zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only";
pub const zig_probe_python = "zig run scripts/zigux/check_zig_toolchain.zig -- --zig";
pub const zig_probe_zig = "zig run scripts/zigux/check_zig_toolchain.zig -- --zig";

pub fn containsRoute(haystack: []const u8, python_route: []const u8, zig_route: []const u8) bool {
    return std.mem.indexOf(u8, haystack, python_route) != null or
        std.mem.indexOf(u8, haystack, zig_route) != null;
}

pub fn requireRoute(haystack: []const u8, python_route: []const u8, zig_route: []const u8) !void {
    if (!containsRoute(haystack, python_route, zig_route)) return error.MissingRoute;
}

pub fn routeIndex(haystack: []const u8, python_route: []const u8, zig_route: []const u8) ?usize {
    const python_index = std.mem.indexOf(u8, haystack, python_route);
    const zig_index = std.mem.indexOf(u8, haystack, zig_route);
    if (python_index) |py| {
        if (zig_index) |zi| return @min(py, zi);
        return py;
    }
    return zig_index;
}

pub fn requireRouteOrder(
    haystack: []const u8,
    earlier_python: []const u8,
    earlier_zig: []const u8,
    later_python: []const u8,
    later_zig: []const u8,
) !void {
    const earlier_index = routeIndex(haystack, earlier_python, earlier_zig) orelse return error.MissingEarlierRoute;
    const later_index = routeIndex(haystack, later_python, later_zig) orelse return error.MissingLaterRoute;
    try std.testing.expect(earlier_index < later_index);
}