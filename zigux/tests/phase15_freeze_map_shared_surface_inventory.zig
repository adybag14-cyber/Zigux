const std = @import("std");

const SharedSurface = struct {
    path: []const u8,
    role: []const u8,
    required_markers: []const []const u8,
};

const freeze_in_c_anchors = [_][]const u8{
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
};

const study_only_anchors = [_][]const u8{
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

const shared_surfaces = [_]SharedSurface{
    .{
        .path = "Documentation/zigux/README.md",
        .role = "docs_root_phase15_reminder",
        .required_markers = &.{
            "Phase 15 notes",
            "`Documentation/zigux/freeze-map.md`",
            "`Documentation/zigux/review-checklist.md`",
            "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
            "bounded below any Architecture Council approval claim",
            "any freeze-map status change",
        },
    },
    .{
        .path = "Documentation/zigux/review-checklist.md",
        .role = "review_checklist_shared_prompt",
        .required_markers = &.{
            "deep-core scope creep into scheduler, MM, RCU, or skbuff",
            "Documentation/zigux/freeze-map.md",
            "Documentation/zigux/phase15-study-only-anchor-accounting.md",
            "kernel/workqueue.c",
            "kernel/trace/ring_buffer.c",
            "study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
        },
    },
    .{
        .path = "Documentation/zigux/freeze-map.md",
        .role = "freeze_map_owner",
        .required_markers = &.{
            "## Freeze In C Initially",
            "## Study / Boundary Only",
            "## Governance For Freeze-Map Changes",
            "shared reminder surfaces that summarize freeze posture",
            "Documentation/zigux/README.md",
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/phase15-study-only-anchor-accounting.md",
            "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked",
        },
    },
};

fn loadFile(io: std.Io, path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAnchors(surface_text: []const u8, anchors: []const []const u8) !void {
    for (anchors) |anchor| {
        try expectContains(surface_text, anchor);
    }
}

test "phase 15 shared Lane 02 surfaces keep study-only anchors in the same inventory" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const docs_root = try loadFile(io_instance.io(), "Documentation/zigux/README.md", 256 * 1024);
    defer std.testing.allocator.free(docs_root);

    const review_checklist = try loadFile(io_instance.io(), "Documentation/zigux/review-checklist.md", 256 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const freeze_map = try loadFile(io_instance.io(), "Documentation/zigux/freeze-map.md", 128 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectAnchors(docs_root, &study_only_anchors);
    try expectAnchors(review_checklist, &study_only_anchors);
    try expectAnchors(freeze_map, &study_only_anchors);

    try expectContains(docs_root, "study-only");
    try expectContains(review_checklist, "study-only");
    try expectContains(freeze_map, "Study / Boundary Only");
}

test "phase 15 shared Lane 02 surfaces keep freeze-in-C anchors blocked unless governance changes" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const docs_root = try loadFile(io_instance.io(), "Documentation/zigux/README.md", 256 * 1024);
    defer std.testing.allocator.free(docs_root);

    const freeze_map = try loadFile(io_instance.io(), "Documentation/zigux/freeze-map.md", 128 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectAnchors(docs_root, &freeze_in_c_anchors);
    try expectAnchors(freeze_map, &freeze_in_c_anchors);

    try expectContains(docs_root, "bounded below any Architecture Council approval claim");
    try expectContains(docs_root, "any freeze-map status change");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "required approver set");
}

test "phase 15 shared Lane 02 surfaces preserve their owner roles" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    inline for (shared_surfaces) |surface| {
        const text = try loadFile(io_instance.io(), surface.path, 256 * 1024);
        defer std.testing.allocator.free(text);

        try std.testing.expect(surface.role.len > 0);
        for (surface.required_markers) |marker| {
            try expectContains(text, marker);
        }
    }
}
