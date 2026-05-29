const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "stay-in-C exception path stays explicit across docs root, checklist, freeze map, and policy" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 128 * 1024);
    defer std.testing.allocator.free(docs_root);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 160 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 32 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const indefinite_c_policy = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 32 * 1024);
    defer std.testing.allocator.free(indefinite_c_policy);

    try expectContains(docs_root, "Documentation/zigux/freeze-map.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(docs_root, "any claim that dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, or shared-CI Phase 15 routes are already shipped on current `master`");

    try expectContains(review_checklist, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(review_checklist, "required approver set");
    try expectContains(review_checklist, "rollback owner");
    try expectContains(review_checklist, "evidence archive path");
    try expectContains(review_checklist, "trigger-specific evidence refresh");

    try expectContains(freeze_map, "there is no silent exception path around the stay-in-C policy");
    try expectContains(freeze_map, "only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review");
    try expectContains(freeze_map, "automatic return-to-blocked trigger");
    try expectContains(freeze_map, "trigger-specific evidence refresh");
    try expectContains(freeze_map, "the existing C implementation remains the product source of truth for every freeze-in-C anchor");

    try expectContains(indefinite_c_policy, "There is no silent exception path around the indefinite-C policy.");
    try expectContains(indefinite_c_policy, "The only allowed exception is a documented Architecture Council reopen request");
    try expectContains(indefinite_c_policy, "If the exception note cannot explain why dated master readback is insufficient");
    try expectContains(indefinite_c_policy, "the C implementation remains the product source of truth");
}

test "exception boundary preserves blocked posture instead of approval or route-recovery claims" {
    const shared_summary_gap = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 48 * 1024);
    defer std.testing.allocator.free(shared_summary_gap);

    const parity_scorecard = try readRepoFile("Documentation/zigux/phase15-parity-scorecard.md", 48 * 1024);
    defer std.testing.allocator.free(parity_scorecard);

    const indefinite_c_policy = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 32 * 1024);
    defer std.testing.allocator.free(indefinite_c_policy);

    try expectContains(shared_summary_gap, "This note does not claim:");
    try expectContains(shared_summary_gap, "an Architecture Council approval workflow implementation");
    try expectContains(shared_summary_gap, "a freeze-map status change for any deep-core anchor");
    try expectContains(shared_summary_gap, "do not treat the parked make-route vocabulary or shared-CI route vocabulary as shipped evidence");

    try expectContains(parity_scorecard, "Architecture Council approvals recorded for status change: `0`");
    try expectContains(parity_scorecard, "the scorecard remains an honest blocker-accounting packet, not a port-readiness claim");
    try expectContains(parity_scorecard, "current `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15` targets");

    try expectContains(indefinite_c_policy, "blocked_on_stay_in_c_evidence `phase15-deep-core-status-change-blocker`");
    try expectContains(indefinite_c_policy, "The repo must not use an indefinite-C record to justify:");
    try expectContains(indefinite_c_policy, "a new deep-core Zig bridge or rewrite for a freeze-in-C anchor");
    try expectContains(indefinite_c_policy, "silent reopening of status review without fresh named evidence");
}

test "reopen trigger catalog stays narrow and evidence-backed" {
    const indefinite_c_policy = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 32 * 1024);
    defer std.testing.allocator.free(indefinite_c_policy);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 32 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(indefinite_c_policy, "## Reopen Trigger Catalog");
    try expectContains(indefinite_c_policy, "`narrower_followup_answers_blocker`");
    try expectContains(indefinite_c_policy, "`evidence_packet_stale_or_contradictory`");
    try expectContains(indefinite_c_policy, "`ownership_or_validation_changed`");
    try expectContains(indefinite_c_policy, "fresh linked evidence");
    try expectContains(indefinite_c_policy, "an Architecture Council review request");

    try expectContains(freeze_map, "fresh linked evidence");
    try expectContains(freeze_map, "stale summaries, contradictory evidence, or route drift return the anchor to blocked posture");
    try expectContains(freeze_map, "record the blocker");
}
