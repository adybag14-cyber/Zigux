const std = @import("std");

fn loadRoadmap(io: std.Io) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        io,
        "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "Lane 01 roadmap keeps zigux-alpha as planning and mapping scope" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const roadmap = try loadRoadmap(io_instance.io());
    defer std.testing.allocator.free(roadmap);

    try expectContains(roadmap, "## zigux-alpha Scope");
    try expectContains(roadmap, "`zigux-alpha/` is the staging area for:");
    try expectContains(roadmap, "- roadmap and phase sequencing");
    try expectContains(roadmap, "- source mapping");
    try expectContains(roadmap, "- validation strategy");
    try expectContains(roadmap, "- freeze map");
    try expectContains(roadmap, "- first commit ledger");
    try expectContains(roadmap, "- workstream ownership");
}

test "Lane 01 roadmap rejects zigux-alpha as final product home" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const roadmap = try loadRoadmap(io_instance.io());
    defer std.testing.allocator.free(roadmap);

    try expectContains(roadmap, "`zigux-alpha/` is not the final home for:");
    try expectContains(roadmap, "- subsystem ports");
    try expectContains(roadmap, "- runtime helpers");
    try expectContains(roadmap, "- drivers");
    try expectContains(roadmap, "- bindings");
    try expectContains(roadmap, "- UAPI shims");
}

test "Lane 01 roadmap preserves approved destination families" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const roadmap = try loadRoadmap(io_instance.io());
    defer std.testing.allocator.free(roadmap);

    try expectBefore(roadmap, "`zigux-alpha/` is the staging area for:", "`zigux-alpha/` is not the final home for:");
    try expectBefore(roadmap, "`zigux-alpha/` is not the final home for:", "Those should eventually land in:");

    try expectContains(roadmap, "Those should eventually land in:");
    try expectContains(roadmap, "- `tools/lib/*.zig`");
    try expectContains(roadmap, "- `scripts/zigux/`");
    try expectContains(roadmap, "- `zigux/`");
    try expectContains(roadmap, "- `Documentation/zigux/`");
    try expectContains(roadmap, "- `samples/zigux/`");
    try expectContains(roadmap, "- `lib/*.zig`");
    try expectContains(roadmap, "- `drivers/*/*.zig`");
    try expectContains(roadmap, "- `fs/*.zig`");
    try expectContains(roadmap, "- `security/*/*.zig`");
}
