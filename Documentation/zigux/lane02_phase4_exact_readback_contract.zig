const std = @import("std");
const testing = std.testing;

const docs_readme = @embedFile("README.md");
const review_checklist = @embedFile("review-checklist.md");
const freeze_map = @embedFile("freeze-map.md");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "docs root keeps the phase4 exact-readback split explicit" {
    try expectContains(docs_readme, "## Phase 4 Exact-Readback Reminder");
    try expectContains(docs_readme, "scripts/zigux/validate-phase4.py");
    try expectContains(docs_readme, "zigux/tests/phase4_build.zig");
    try expectContains(docs_readme, "zigux/tests/bitmap_diff.zig");
    try expectContains(docs_readme, "zigux/tests/phase4_bitmap_live_helper_replay.zig");
    try expectContains(docs_readme, "still flap");
    try expectContains(docs_readme, "public raw fallback rereads return those three files");
    try expectContains(docs_readme, "authenticated blob-pin refresh remains pending");
}

test "review checklist preserves phase4 rollback and exact-readback prompts" {
    try expectContains(review_checklist, "if the change touches the shared Phase 4 rollback-ownership and lab-matrix packet");
    try expectContains(review_checklist, "Documentation/zigux/phase4-reversible-delivery-evidence.md");
    try expectContains(review_checklist, "scripts/zigux/check-phase4-repo-reality-warning.py");
    try expectContains(review_checklist, "scripts/zigux/check-phase4-reversible-delivery-pins.py");
    try expectContains(review_checklist, "Phase 4 Exact-Readback Reminder");
    try expectContains(review_checklist, "keep the directly readable local-only perf packet explicit");
    try expectContains(review_checklist, "keep the recovered broader note-and-checker companions explicit");
    try expectContains(review_checklist, "pending shared-CI perf-promotion posture explicit");
}

test "freeze map still blocks deep-core delivery claims while phase4 remains evidence-only" {
    try expectContains(freeze_map, "## Freeze In C Initially");
    try expectContains(freeze_map, "`kernel/sched/core.c`");
    try expectContains(freeze_map, "`mm/page_alloc.c`");
    try expectContains(freeze_map, "`kernel/rcu/tree.c`");
    try expectContains(freeze_map, "`net/core/skbuff.c`");
    try expectContains(freeze_map, "## Study / Boundary Only");
    try expectContains(freeze_map, "`kernel/workqueue.c`");
    try expectContains(freeze_map, "`kernel/trace/ring_buffer.c`");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "study-only follow-up may gather narrower evidence");
}
