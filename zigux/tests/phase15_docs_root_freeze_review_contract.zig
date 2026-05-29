const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "docs root, review checklist, and freeze map keep the Architecture Council status-change guard aligned" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 512 * 1024);
    defer std.testing.allocator.free(docs_root);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 512 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 256 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(docs_root, "Phase 15 notes");
    try expectContains(docs_root, "Documentation/zigux/freeze-map.md");
    try expectContains(docs_root, "Documentation/zigux/review-checklist.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(docs_root, "Architecture Council");

    try expectContains(review_checklist, "is the status bucket explicit");
    try expectContains(review_checklist, "does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?");
    try expectContains(review_checklist, "freeze-map anchor");
    try expectContains(review_checklist, "required approver set");
    try expectContains(review_checklist, "rollback owner");
    try expectContains(review_checklist, "validation gate summary");
    try expectContains(review_checklist, "evidence archive path");

    try expectContains(freeze_map, "This file records code that should not move into active Zigux delivery without an explicit Architecture Council decision.");
    try expectContains(freeze_map, "changes to either list require an explicit Architecture Council decision with written rationale");
    try expectContains(freeze_map, "any lane that touches a listed anchor must declare owner, phase, status bucket");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
}

test "freeze-map anchors stay explicit across the shared review surfaces" {
    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 512 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 256 * 1024);
    defer std.testing.allocator.free(freeze_map);

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

    for (freeze_in_c_anchors) |anchor| {
        try expectContains(freeze_map, anchor);
    }
    for (study_only_anchors) |anchor| {
        try expectContains(freeze_map, anchor);
        try expectContains(review_checklist, anchor);
    }

    try expectContains(review_checklist, "without implying an active deep-core port claim");
    try expectContains(freeze_map, "wrapper-first or helper-first experiments may continue only for study-only anchors");
    try expectContains(freeze_map, "there is no silent exception path around the stay-in-C policy");
}
