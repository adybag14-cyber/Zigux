const std = @import("std");

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

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNeedleCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, std.mem.count(u8, haystack, needle));
}

fn expectAnchorsPresent(haystack: []const u8, anchors: []const []const u8) !void {
    for (anchors) |anchor| {
        try expectContains(haystack, anchor);
    }
}

test "freeze map keeps the exact deep-core anchor inventory split" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 96 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(freeze_map, "## Freeze In C Initially");
    try expectContains(freeze_map, "## Study / Boundary Only");

    for (freeze_in_c_anchors) |anchor| {
        const listed = try std.fmt.allocPrint(std.testing.allocator, "- `{s}`", .{anchor});
        defer std.testing.allocator.free(listed);
        try expectNeedleCount(freeze_map, listed, 1);
    }

    for (study_only_anchors) |anchor| {
        const listed = try std.fmt.allocPrint(std.testing.allocator, "- `{s}`", .{anchor});
        defer std.testing.allocator.free(listed);
        try expectNeedleCount(freeze_map, listed, 1);
    }

    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review");
}

test "shared docs surfaces route the study-only anchors back to accounting" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 512 * 1024);
    defer std.testing.allocator.free(docs_root);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 192 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 96 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectAnchorsPresent(docs_root, &freeze_in_c_anchors);
    try expectAnchorsPresent(docs_root, &study_only_anchors);
    try expectContains(docs_root, "Documentation/zigux/freeze-map.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-study-only-anchor-accounting.md");

    try expectAnchorsPresent(review_checklist, &study_only_anchors);
    try expectContains(review_checklist, "summarizes the study-only freeze-map anchors");
    try expectContains(review_checklist, "Documentation/zigux/freeze-map.md");
    try expectContains(review_checklist, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(review_checklist, "rather than runtime-substrate or bridge-readiness evidence");

    try expectContains(freeze_map, "shared reminder surfaces that summarize freeze posture");
    try expectContains(freeze_map, "must keep the same study-only anchor inventory");
    try expectContains(freeze_map, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
}

test "study-only accounting remains a two-anchor inventory, not approval evidence" {
    const accounting_note = try readRepoFile("Documentation/zigux/phase15-study-only-anchor-accounting.md", 48 * 1024);
    defer std.testing.allocator.free(accounting_note);

    try expectContains(accounting_note, "PHASE15_STATUS=study_only_accounting_slice_landed");
    try expectContains(accounting_note, "two roadmap-backed study-only anchors");
    try expectContains(accounting_note, "two deep-core areas");
    try expectAnchorsPresent(accounting_note, &study_only_anchors);

    for (study_only_anchors) |anchor| {
        const heading = try std.fmt.allocPrint(std.testing.allocator, "### `{s}`", .{anchor});
        defer std.testing.allocator.free(heading);
        try expectNeedleCount(accounting_note, heading, 1);
    }

    try expectContains(accounting_note, "this note is an inventory and handoff surface, not an approval record");
    try expectContains(accounting_note, "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it");
    try expectContains(accounting_note, "a direct Zigux bridge for `kernel/workqueue.c`");
    try expectContains(accounting_note, "a direct Zigux bridge for `kernel/trace/ring_buffer.c`");
    try expectContains(accounting_note, "an Architecture Council approval for any study-only anchor to leave its current posture");
}
