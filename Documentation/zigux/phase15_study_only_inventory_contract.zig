const std = @import("std");

const docs_root = @embedFile("README.md");
const review_checklist = @embedFile("review-checklist.md");
const freeze_map = @embedFile("freeze-map.md");
const study_only_accounting = @embedFile("phase15-study-only-anchor-accounting.md");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "study-only accounting keeps dated two-anchor inventory explicit" {
    try expectContains(study_only_accounting, "PHASE15_STATUS=study_only_accounting_slice_landed");
    try expectContains(study_only_accounting, "PHASE15_SLICE=study-only-anchor-accounting");
    try expectContains(study_only_accounting, "current-master-readback-2026-05-25");
    try expectContains(study_only_accounting, "study-only anchors tracked outside this scorecard: 2");
    try expectContains(study_only_accounting, "### `kernel/workqueue.c`");
    try expectContains(study_only_accounting, "### `kernel/trace/ring_buffer.c`");
    try expectContains(study_only_accounting, "posture: `study_only`");
}

test "shared Lane 02 surfaces route study-only summaries back to owner docs" {
    try expectContains(docs_root, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(docs_root, "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain study-only anchors");
    try expectContains(review_checklist, "does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`");
    try expectContains(freeze_map, "shared reminder surfaces that summarize freeze posture");
    try expectContains(freeze_map, "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`");
}

test "accounting boundary stays below approval or direct bridge claims" {
    try expectContains(study_only_accounting, "a direct Zigux bridge for `kernel/workqueue.c`");
    try expectContains(study_only_accounting, "a direct Zigux bridge for `kernel/trace/ring_buffer.c`");
    try expectContains(study_only_accounting, "an Architecture Council approval for any study-only anchor to leave its current posture");
    try expectContains(study_only_accounting, "this note is an inventory and handoff surface, not an approval record");
    try expectContains(study_only_accounting, "no Architecture Council approval is currently recorded for a deep-core status change");
    try expectAbsent(study_only_accounting, "PHASE15_STATUS=approved");
}
