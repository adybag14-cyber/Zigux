const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 15 shared reminder surfaces route study-only anchor summaries back to the owning accounting note" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 512 * 1024);
    defer std.testing.allocator.free(docs_root);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 128 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 64 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const accounting_note = try readRepoFile("Documentation/zigux/phase15-study-only-anchor-accounting.md", 32 * 1024);
    defer std.testing.allocator.free(accounting_note);

    try expectContains(docs_root, "Documentation/zigux/freeze-map.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(docs_root, "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain study-only anchors");
    try expectContains(docs_root, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectContains(docs_root, "shared reminder surfaces explicit here too");

    try expectContains(review_checklist, "if a shared reminder surface summarizes the study-only freeze-map anchors");
    try expectContains(review_checklist, "Documentation/zigux/freeze-map.md");
    try expectContains(review_checklist, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(review_checklist, "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context");

    try expectContains(freeze_map, "shared reminder surfaces that summarize freeze posture");
    try expectContains(freeze_map, "Documentation/zigux/README.md");
    try expectContains(freeze_map, "Documentation/zigux/review-checklist.md");
    try expectContains(freeze_map, "must keep the same study-only anchor inventory");
    try expectContains(freeze_map, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(freeze_map, "study-only anchor maintenance must stay aligned");

    try expectContains(accounting_note, "PHASE15_STATUS=study_only_accounting_slice_landed");
    try expectContains(accounting_note, "kernel/workqueue.c");
    try expectContains(accounting_note, "kernel/trace/ring_buffer.c");
    try expectContains(accounting_note, "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it");
    try expectContains(accounting_note, "if the governance-lane sequencing note, handoff-next-steps survey, shared-summary gap note, or landed tests-root reminder changes");
    try expectContains(accounting_note, "an Architecture Council approval for any study-only anchor to leave its current posture");
}

test "phase 15 study-only anchors stay accounting context rather than delivery evidence" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 512 * 1024);
    defer std.testing.allocator.free(docs_root);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 64 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const accounting_note = try readRepoFile("Documentation/zigux/phase15-study-only-anchor-accounting.md", 32 * 1024);
    defer std.testing.allocator.free(accounting_note);

    try expectContains(docs_root, "keep the Phase 15 reminder bounded below any Architecture Council approval claim");
    try expectContains(docs_root, "below any freeze-map status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`");
    try expectContains(docs_root, "do not own freeze-map decisions or broader route recovery by themselves");

    try expectContains(freeze_map, "study-only follow-up may gather narrower evidence");
    try expectContains(freeze_map, "must not present `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as active delivery targets");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review");

    try expectContains(accounting_note, "this note is an inventory and handoff surface, not an approval record");
    try expectContains(accounting_note, "a direct Zigux bridge for `kernel/workqueue.c`");
    try expectContains(accounting_note, "a direct Zigux bridge for `kernel/trace/ring_buffer.c`");
    try expectContains(accounting_note, "a new implementation roadmap beyond current governance accounting");
}

test "phase 15 handoff and shared-summary notes keep study-only anchors below route recovery" {
    const handoff_note = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md", 96 * 1024);
    defer std.testing.allocator.free(handoff_note);

    const shared_summary = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 64 * 1024);
    defer std.testing.allocator.free(shared_summary);

    const accounting_note = try readRepoFile("Documentation/zigux/phase15-study-only-anchor-accounting.md", 32 * 1024);
    defer std.testing.allocator.free(accounting_note);

    try expectContains(handoff_note, "keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`");
    try expectContains(handoff_note, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(handoff_note, "treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps");
    try expectContains(handoff_note, "do not treat any direct Zig deep-core bridge as a next-phase commitment");
    try expectContains(handoff_note, "no Architecture Council approval is currently recorded for a freeze-map status change");

    try expectContains(shared_summary, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(shared_summary, "do not treat present focused companions as Architecture Council approval or direct deep-core delivery evidence by themselves");
    try expectContains(shared_summary, "a freeze-map status change for any deep-core anchor");
    try expectContains(shared_summary, "broader wrapper-route wording around");
    try expectContains(shared_summary, "shared-CI route vocabulary as shipped evidence");

    try expectContains(accounting_note, "governance-lane sequencing note, handoff-next-steps survey, shared-summary gap note");
    try expectContains(accounting_note, "the current governance packet is still blocker-accounting and handoff truthfulness, not port-readiness");
}
