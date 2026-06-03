const std = @import("std");

const docs_root = @embedFile("README.md");
const review_checklist = @embedFile("review-checklist.md");
const freeze_map = @embedFile("freeze-map.md");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var seen: usize = 0;
    var start: usize = 0;

    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        seen += 1;
        start = index + needle.len;
    }

    try std.testing.expectEqual(expected, seen);
}

test "docs root keeps the phase15 governance packet bounded" {
    try expectContains(docs_root, "Phase 15 notes");
    try expectContains(docs_root, "`Documentation/zigux/freeze-map.md`");
    try expectContains(docs_root, "`Documentation/zigux/phase15-freeze-map-governance.md`");
    try expectContains(docs_root, "`Documentation/zigux/phase15-architecture-council-review-process.md`");
    try expectContains(docs_root, "Architecture Council approval");
    try expectContains(docs_root, "freeze-map status change");
}

test "review checklist routes shared freeze summaries through the owning docs" {
    try expectContains(review_checklist, "does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?");
    try expectContains(review_checklist, "if the change asks for a freeze-map status change");
    try expectContains(review_checklist, "current status bucket plus requested decision bucket");
    try expectContains(review_checklist, "required approver set");
    try expectContains(review_checklist, "rollback owner");
    try expectContains(review_checklist, "evidence archive path");
    try expectContains(review_checklist, "`Documentation/zigux/freeze-map.md`");
    try expectContains(review_checklist, "`kernel/workqueue.c`");
    try expectContains(review_checklist, "`kernel/trace/ring_buffer.c`");
}

test "freeze map preserves deep-core and study-only anchor buckets" {
    try expectContains(freeze_map, "## Freeze In C Initially");
    try expectContains(freeze_map, "## Study / Boundary Only");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "wrapper-first or helper-first experiments may continue only for study-only anchors");
    try expectContains(freeze_map, "`Documentation/zigux/phase15-architecture-council-review-process.md`");
    try expectContains(freeze_map, "`Documentation/zigux/phase15-freeze-map-governance.md`");

    try expectCount(freeze_map, "- `kernel/sched/core.c`", 1);
    try expectCount(freeze_map, "- `mm/page_alloc.c`", 1);
    try expectCount(freeze_map, "- `kernel/rcu/tree.c`", 1);
    try expectCount(freeze_map, "- `net/core/skbuff.c`", 1);
    try expectCount(freeze_map, "- `kernel/workqueue.c`", 1);
    try expectCount(freeze_map, "- `kernel/trace/ring_buffer.c`", 1);
}
