const std = @import("std");

const Lane02Surface = struct {
    path: []const u8,
    max_bytes: usize,
};

const lane02_surfaces = [_]Lane02Surface{
    .{ .path = "Documentation/zigux/README.md", .max_bytes = 192 * 1024 },
    .{ .path = "Documentation/zigux/review-checklist.md", .max_bytes = 192 * 1024 },
    .{ .path = "Documentation/zigux/freeze-map.md", .max_bytes = 96 * 1024 },
};

fn loadFile(io: std.Io, surface: Lane02Surface) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, surface.path, std.testing.allocator, .limited(surface.max_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSharedStudyOnlyInventory(surface: []const u8) !void {
    try expectContains(surface, "kernel/workqueue.c");
    try expectContains(surface, "kernel/trace/ring_buffer.c");
}

test "lane 02 shared surfaces keep the study-only anchor inventory visible" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const docs_root = try loadFile(io_instance.io(), lane02_surfaces[0]);
    defer std.testing.allocator.free(docs_root);

    const review_checklist = try loadFile(io_instance.io(), lane02_surfaces[1]);
    defer std.testing.allocator.free(review_checklist);

    const freeze_map = try loadFile(io_instance.io(), lane02_surfaces[2]);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(docs_root, "Documentation/zigux/freeze-map.md");
    try expectContains(docs_root, "Documentation/zigux/review-checklist.md");
    try expectContains(docs_root, "Phase 15 notes");

    try expectSharedStudyOnlyInventory(review_checklist);
    try expectContains(review_checklist, "without implying an active deep-core port claim");

    try expectSharedStudyOnlyInventory(freeze_map);
    try expectContains(freeze_map, "## Study / Boundary Only");
}

test "phase 15 docs root keeps current governance packet visible" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const docs_root = try loadFile(io_instance.io(), lane02_surfaces[0]);
    defer std.testing.allocator.free(docs_root);

    const freeze_map = try loadFile(io_instance.io(), lane02_surfaces[2]);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(docs_root, "Documentation/zigux/phase15-freeze-map-governance.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(docs_root, "zigux/tests/phase15_build.zig");

    try expectContains(freeze_map, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-freeze-map-governance.md");
    try expectContains(freeze_map, "parity scorecard link or blocker record");
}

test "freeze-map status changes remain Architecture Council gated" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const docs_root = try loadFile(io_instance.io(), lane02_surfaces[0]);
    defer std.testing.allocator.free(docs_root);

    const review_checklist = try loadFile(io_instance.io(), lane02_surfaces[1]);
    defer std.testing.allocator.free(review_checklist);

    const freeze_map = try loadFile(io_instance.io(), lane02_surfaces[2]);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(docs_root, "without implying any Architecture Council approval for a freeze-map status change");

    try expectContains(review_checklist, "without an Architecture Council decision");
    try expectContains(review_checklist, "required approver set");
    try expectContains(review_checklist, "evidence archive path");

    try expectContains(freeze_map, "explicit Architecture Council decision with written rationale");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "there is no silent exception path around the stay-in-C policy");
}
