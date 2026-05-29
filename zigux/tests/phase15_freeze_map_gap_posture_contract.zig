const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 15 freeze-map gap posture keeps current gaps separate from landed evidence" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 40 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(freeze_map, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-shared-summary-gap.md");
    try expectContains(freeze_map, "landed governance evidence");
    try expectContains(freeze_map, "still-missing dedicated `phase15*` wrapper routes");
    try expectContains(freeze_map, "shared-CI companions");
    try expectContains(freeze_map, "future Architecture Council status-change record");
    try expectContains(freeze_map, "repo-reality gaps on current `master`");
    try expectContains(freeze_map, "kernel/workqueue.c");
    try expectContains(freeze_map, "kernel/trace/ring_buffer.c");
}

test "shared Lane 02 reminders route study-only anchors back to freeze-map owners" {
    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 96 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const docs_root = try readRepoFile("Documentation/zigux/README.md", 96 * 1024);
    defer std.testing.allocator.free(docs_root);

    const shared_surfaces = [_][]const u8{ review_checklist, docs_root };
    for (shared_surfaces) |surface| {
        try expectContains(surface, "Documentation/zigux/freeze-map.md");
        try expectContains(surface, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
        try expectContains(surface, "kernel/workqueue.c");
        try expectContains(surface, "kernel/trace/ring_buffer.c");
        try expectContains(surface, "study-only");
    }
}

test "Phase 15 handoff and shared-summary notes keep missing route vocabulary gap-scoped" {
    const handoff_note = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md", 64 * 1024);
    defer std.testing.allocator.free(handoff_note);

    const shared_summary = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 64 * 1024);
    defer std.testing.allocator.free(shared_summary);

    try expectContains(handoff_note, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(handoff_note, "Documentation/zigux/phase15-shared-summary-gap.md");
    try expectContains(handoff_note, "phase15");
    try expectContains(handoff_note, "gap");

    try expectContains(shared_summary, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(shared_summary, "phase15");
    try expectContains(shared_summary, "gap");
    try expectContains(shared_summary, "does not claim");
    try expectContains(shared_summary, "Architecture Council");
}
