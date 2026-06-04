const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "Phase 15 decision index keeps future record linkage fields explicit" {
    const decision_index = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-index.md", 32 * 1024);
    defer std.testing.allocator.free(decision_index);

    const decision_template = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-record-template.md", 24 * 1024);
    defer std.testing.allocator.free(decision_template);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 48 * 1024);
    defer std.testing.allocator.free(review_process);

    try expectContains(decision_index, "every future Architecture Council decision record for a freeze-map anchor must be linked here with decision record ID, exact Linux anchor path, review outcome, evidence archive path, surveyed commit marker, and next bounded step");
    try expectContains(decision_index, "every linked record must also route back through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/phase15-parity-scorecard.md`");
    try expectContains(decision_index, "if a freeze-in-C anchor changes status bucket, update this note in the same bounded change as the linked decision record and the freeze-map governance packet");

    try expectContains(decision_index, "- decision record ID:");
    try expectContains(decision_index, "- exact Linux anchor path:");
    try expectContains(decision_index, "- review outcome:");
    try expectContains(decision_index, "- evidence archive path:");
    try expectContains(decision_index, "- surveyed commit marker:");
    try expectContains(decision_index, "- next bounded step:");

    try expectContains(decision_template, "This is a review packet template, not approval by itself.");
    try expectContains(decision_template, "`DECISION_RECORD_ID=<replace-with-stable-id>`");
    try expectContains(decision_template, "- decision record ID:");
    try expectContains(decision_template, "- exact Linux anchor path:");
    try expectContains(decision_template, "- closeout result:");
    try expectContains(decision_template, "- next bounded step:");

    try expectContains(review_process, "Any freeze-map anchor entering Architecture Council status review must keep all of the following explicit:");
    try expectContains(review_process, "decision record ID");
    try expectContains(review_process, "evidence archive path");
    try expectContains(review_process, "written rationale");
}

test "Phase 15 future records stay blocked until index, governance, and scorecard agree" {
    const decision_index = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-index.md", 32 * 1024);
    defer std.testing.allocator.free(decision_index);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 48 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const governance = try readRepoFile("Documentation/zigux/phase15-freeze-map-governance.md", 64 * 1024);
    defer std.testing.allocator.free(governance);

    const parity_scorecard = try readRepoFile("Documentation/zigux/phase15-parity-scorecard.md", 64 * 1024);
    defer std.testing.allocator.free(parity_scorecard);

    try expectContains(decision_index, "if no reviewable Architecture Council decision record exists yet, keep this note at an explicit zero-decision inventory instead of implying approval by omission");
    try expectContains(decision_index, "the freeze map, parity scorecard, and review-process packet therefore remain blocker-accounting and governance truthfulness evidence rather than approval evidence");

    try expectContains(freeze_map, "freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change");

    try expectContains(governance, "direct Zig bridge or port claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change");
    try expectContains(governance, "blocked_on_stay_in_c_evidence `phase15-deep-core-status-change-blocker`");

    try expectContains(parity_scorecard, "the scorecard remains an honest blocker-accounting packet, not a port-readiness claim");
    try expectContains(parity_scorecard, "Architecture Council approvals recorded for status change: `0`");
    try expectContains(parity_scorecard, "if a future lane wants a status change, it must update this scorecard together with `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/phase15-architecture-council-review-process.md`");
}

test "Phase 15 study-only anchors stay outside decision-index records until freeze map changes" {
    const decision_index = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-index.md", 32 * 1024);
    defer std.testing.allocator.free(decision_index);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 48 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const decision_template = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-record-template.md", 24 * 1024);
    defer std.testing.allocator.free(decision_template);

    try expectContains(freeze_map, "## Study / Boundary Only");
    try expectContains(freeze_map, "`kernel/workqueue.c`");
    try expectContains(freeze_map, "`kernel/trace/ring_buffer.c`");
    try expectContains(freeze_map, "study-only follow-up may gather narrower evidence, but it must not present `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as active delivery targets before an Architecture Council reviewable record changes their status bucket");

    try expectContains(decision_index, "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay outside this index until the freeze map changes");
    try expectContains(decision_index, "a status-review path for `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` while they remain study-only anchors");
    try expectContains(decision_template, "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.");

    try expectNotContains(decision_index, "kernel/workqueue.c` has an Architecture Council approval");
    try expectNotContains(decision_index, "kernel/trace/ring_buffer.c` has an Architecture Council approval");
}
