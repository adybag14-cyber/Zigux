const std = @import("std");

fn readRoadmap() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
        std.testing.allocator,
        .limited(1024 * 1024),
    ) catch std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "../../zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "bootstrap status note preserves planning-baseline truth" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    const note_heading = "## Bootstrap Status Note";
    const note_start = std.mem.indexOf(u8, roadmap, note_heading) orelse return error.MissingBootstrapStatusNote;
    const positioning_start = std.mem.indexOf(u8, roadmap, "Positioning:") orelse return error.MissingPositioningSection;
    try std.testing.expect(note_start < positioning_start);

    const note = roadmap[note_start..positioning_start];

    try expectContains(note, "planning baseline for Zigux bootstrap sequencing and phase intent");
    try expectContains(note, "bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`");
    try expectContains(note, "confirm the live repo tree");
    try expectContains(note, "`Documentation/zigux/README.md`");
    try expectContains(note, "active lane notes");
    try expectContains(note, "before treating every later phase packet below as already materialized on `master`");
}

test "bootstrap status note stays between purpose and positioning" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    try expectOrder(
        roadmap,
        "This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.",
        "## Bootstrap Status Note",
    );
    try expectOrder(roadmap, "## Bootstrap Status Note", "Positioning:");
    try expectOrder(roadmap, "Positioning:", "## Inputs Reviewed");
}

test "bootstrap status note does not replace the folder charter" {
    const roadmap = try readRoadmap();
    defer std.testing.allocator.free(roadmap);

    try expectOrder(roadmap, "## Bootstrap Status Note", "## zigux-alpha Scope");
    try expectContains(roadmap, "`zigux-alpha/` is the staging area for:");
    try expectContains(roadmap, "`zigux-alpha/` is not the final home for:");
    try expectContains(roadmap, "Those should eventually land in:");
}
