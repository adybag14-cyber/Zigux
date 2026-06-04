const std = @import("std");

const frozen_anchors = [_][]const u8{
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
};

const study_only_anchors = [_][]const u8{
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAllAnchors(surface: []const u8, anchors: []const []const u8) !void {
    for (anchors) |anchor| {
        try expectContains(surface, anchor);
    }
}

test "documentation root keeps the product scope and freeze-map routing visible" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 256 * 1024);
    defer std.testing.allocator.free(docs_root);

    try expectContains(docs_root, "product documentation root for Zigux");
    try expectContains(docs_root, "product charter");
    try expectContains(docs_root, "review rules");
    try expectContains(docs_root, "freeze map");
    try expectContains(docs_root, "keep product commitments here, not in ad hoc issue threads");
    try expectContains(docs_root, "keep deep-core freeze decisions explicit");
    try expectContains(docs_root, "require validation and rollback language for every new active port target");
    try expectContains(docs_root, "align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`");
    try expectContains(docs_root, "Documentation/zigux/review-checklist.md");
    try expectContains(docs_root, "Documentation/zigux/freeze-map.md");
}

test "review checklist preserves status-bucket and deep-core safety prompts" {
    const checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 256 * 1024);
    defer std.testing.allocator.free(checklist);

    try expectContains(checklist, "is the target phase named explicitly?");
    try expectContains(checklist, "is the status bucket explicit");
    try expectContains(checklist, "port now");
    try expectContains(checklist, "port after substrate");
    try expectContains(checklist, "dual implementation required");
    try expectContains(checklist, "study only");
    try expectContains(checklist, "freeze in C initially");
    try expectContains(checklist, "does the change avoid mirror-tree sprawl?");
    try expectContains(checklist, "does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?");
    try expectContains(checklist, "parity tests or fixture checks");
    try expectContains(checklist, "rollback owner");
    try expectContains(checklist, "fallback path");
}

test "freeze map keeps frozen and study-only anchor inventories distinct" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 128 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(freeze_map, "## Freeze In C Initially");
    try expectContains(freeze_map, "## Study / Boundary Only");
    try expectAllAnchors(freeze_map, &frozen_anchors);
    try expectAllAnchors(freeze_map, &study_only_anchors);
    try expectContains(freeze_map, "Architecture Council decision");
    try expectContains(freeze_map, "written rationale");
    try expectContains(freeze_map, "owner, phase, status bucket, validation gate summary, and rollback owner");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "wrapper-first or helper-first experiments may continue only for study-only anchors");
    try expectContains(freeze_map, "they still must keep scheduler, MM, RCU, skbuff, and other deep-core ownership explicit");
}

test "shared documentation surfaces preserve study-only anchor routing" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 256 * 1024);
    defer std.testing.allocator.free(docs_root);
    const checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 256 * 1024);
    defer std.testing.allocator.free(checklist);
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 128 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectAllAnchors(checklist, &study_only_anchors);
    try expectAllAnchors(freeze_map, &study_only_anchors);
    try expectContains(docs_root, "Documentation/zigux/freeze-map.md");
    try expectContains(docs_root, "study-only");
    try expectContains(freeze_map, "## Study / Boundary Only");
    try expectContains(checklist, "study-only");
}
