const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "review checklist routes study-only summaries through freeze-map owners" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 96 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 192 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const study_only_accounting = try readRepoFile("Documentation/zigux/phase15-study-only-anchor-accounting.md", 96 * 1024);
    defer std.testing.allocator.free(study_only_accounting);

    try expectContains(freeze_map, "shared reminder surfaces that summarize freeze posture");
    try expectContains(freeze_map, "`Documentation/zigux/review-checklist.md`");
    try expectContains(freeze_map, "`Documentation/zigux/phase15-study-only-anchor-accounting.md`");
    try expectContains(freeze_map, "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`");

    try expectContains(review_checklist, "if a shared reminder surface summarizes the study-only freeze-map anchors");
    try expectContains(review_checklist, "`Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`");
    try expectContains(review_checklist, "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence");

    try expectContains(study_only_accounting, "# Phase 15 Study-Only Anchor Accounting");
    try expectContains(study_only_accounting, "### `kernel/workqueue.c`");
    try expectContains(study_only_accounting, "### `kernel/trace/ring_buffer.c`");
    try expectContains(study_only_accounting, "this note is an inventory and handoff surface, not an approval record");
    try expectContains(study_only_accounting, "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it");
}

test "sequencing note keeps shared reminders out of freeze-map ownership" {
    const lane_sequencing = try readRepoFile("Documentation/zigux/phase15-governance-lane-sequencing.md", 96 * 1024);
    defer std.testing.allocator.free(lane_sequencing);

    const shared_gap = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 96 * 1024);
    defer std.testing.allocator.free(shared_gap);

    try expectContains(lane_sequencing, "`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory");
    try expectContains(lane_sequencing, "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces");
    try expectContains(lane_sequencing, "they do not own freeze-map status decisions themselves");
    try expectContains(lane_sequencing, "The shared reminder surfaces must not say that:");
    try expectContains(lane_sequencing, "a deep-core status change has been approved");
    try expectContains(lane_sequencing, "a freeze-in-C anchor is ready for a direct Zigux bridge");

    try expectContains(shared_gap, "the checklist-specific study-only anchor summary boundary");
    try expectContains(shared_gap, "fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims");
    try expectContains(shared_gap, "do not treat present focused companions as Architecture Council approval or direct deep-core delivery evidence by themselves");
}

test "study-only contract stays below wrapper route recovery claims" {
    const lane_sequencing = try readRepoFile("Documentation/zigux/phase15-governance-lane-sequencing.md", 96 * 1024);
    defer std.testing.allocator.free(lane_sequencing);

    const shared_gap = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 96 * 1024);
    defer std.testing.allocator.free(shared_gap);

    try expectContains(lane_sequencing, "no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`");
    try expectContains(lane_sequencing, ".github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route name on current `master`");
    try expectContains(lane_sequencing, "Those route gaps do not erase the landed governance packet or the directly readable `zigux/tests/phase15_build.zig` shared build companion.");

    try expectContains(shared_gap, "Still-missing broader wrapper and shared-CI route companions on current master");
    try expectContains(shared_gap, "no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`");
    try expectContains(shared_gap, "do not treat the parked make-route vocabulary or shared-CI route vocabulary as shipped evidence until direct current-tree reads recover them");
}
