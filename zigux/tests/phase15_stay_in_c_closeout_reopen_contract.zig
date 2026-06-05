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

test "stay-in-C closeout keeps blocker, return trigger, and evidence refresh fields explicit" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 32 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 48 * 1024);
    defer std.testing.allocator.free(review_process);

    const decision_template = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-record-template.md", 24 * 1024);
    defer std.testing.allocator.free(decision_template);

    const policy_note = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 32 * 1024);
    defer std.testing.allocator.free(policy_note);

    try expectContains(freeze_map, "closing a freeze-in-C review without a status change must retain the blocker");
    try expectContains(freeze_map, "record the closeout as `retired_from_active_discussion`");
    try expectContains(freeze_map, "automatic return-to-blocked trigger explicit");
    try expectContains(freeze_map, "reopen triggers");
    try expectContains(freeze_map, "trigger-specific evidence refresh");
    try expectContains(freeze_map, "evidence archive path");

    try expectContains(review_process, "## Stay-in-C closeout rule");
    try expectContains(review_process, "the retained `freeze_in_c` decision");
    try expectContains(review_process, "the current blocker");
    try expectContains(review_process, "the required approver set");
    try expectContains(review_process, "governance lane sequencing link or explicit scope note");
    try expectContains(review_process, "`retired_from_active_discussion` state");
    try expectContains(review_process, "the automatic return-to-blocked trigger");
    try expectContains(review_process, "the reopen triggers");
    try expectContains(review_process, "the trigger-specific evidence refresh");
    try expectContains(review_process, "the evidence archive path that will be refreshed before any later reopen request");

    try expectContains(decision_template, "## Stay-In-C Closeout");
    try expectContains(decision_template, "- the retained `freeze_in_c` decision:");
    try expectContains(decision_template, "- the current blocker:");
    try expectContains(decision_template, "- automatic return-to-blocked trigger:");
    try expectContains(decision_template, "- the trigger-specific evidence refresh:");

    try expectContains(policy_note, "After an explicit stay-in-C outcome is recorded");
    try expectContains(policy_note, "policy, review-process, or scorecard maintenance that keeps the blocker posture truthful");
    try expectContains(policy_note, "the C implementation remains the product source of truth");
}

test "reopen requests require exact trigger, refreshed evidence, and narrower safe scope" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 32 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 48 * 1024);
    defer std.testing.allocator.free(review_process);

    const decision_template = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-record-template.md", 24 * 1024);
    defer std.testing.allocator.free(decision_template);

    const policy_note = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 32 * 1024);
    defer std.testing.allocator.free(policy_note);

    try expectContains(freeze_map, "there is no silent exception path around the stay-in-C policy");
    try expectContains(freeze_map, "only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review");
    try expectContains(freeze_map, "any reopen request for code that remains in C indefinitely must keep the automatic return-to-blocked trigger and trigger-specific evidence refresh explicit");

    try expectContains(review_process, "## Reopen evidence rule");
    try expectContains(review_process, "the exact reopen trigger being exercised");
    try expectContains(review_process, "refreshed evidence by path");
    try expectContains(review_process, "the blocker disposition being challenged");
    try expectContains(review_process, "the narrower seam or policy change that makes the new review safe to consider");
    try expectContains(review_process, "the request returns to blocked review posture immediately");

    try expectContains(decision_template, "## Reopen Evidence");
    try expectContains(decision_template, "- the exact reopen trigger being exercised:");
    try expectContains(decision_template, "- refreshed evidence by path:");
    try expectContains(decision_template, "- the blocker disposition being challenged:");
    try expectContains(decision_template, "- the narrower seam or policy change that makes the new review safe to consider:");

    try expectContains(policy_note, "## Reopen Trigger Catalog");
    try expectContains(policy_note, "narrower_followup_answers_blocker");
    try expectContains(policy_note, "evidence_packet_stale_or_contradictory");
    try expectContains(policy_note, "ownership_or_validation_changed");
    try expectContains(policy_note, "the named reopen trigger now being exercised");
    try expectContains(policy_note, "the trigger-specific evidence refresh that reopens the packet");
}

test "decision index keeps stay-in-C closeouts at zero until a linked record lands" {
    const decision_index = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-index.md", 24 * 1024);
    defer std.testing.allocator.free(decision_index);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 48 * 1024);
    defer std.testing.allocator.free(review_process);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 32 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(decision_index, "approved status-bucket changes recorded on current `master`: none");
    try expectContains(decision_index, "stay-in-C closeout decision records recorded on current `master`: none");
    try expectContains(decision_index, "no freeze-map anchor has an Architecture Council approval for a status change on current `master`");
    try expectContains(decision_index, "keep this note at an explicit zero-decision inventory instead of implying approval by omission");
    try expectContains(decision_index, "a stay-in-C closeout record that is not linked by path");
    try expectContains(decision_index, "every future Architecture Council decision record for a freeze-map anchor must be linked here");

    try expectContains(review_process, "Documentation/zigux/phase15-architecture-council-decision-index.md");
    try expectContains(review_process, "no freeze-map anchor has an approved status change or stay-in-C closeout record on current `master`");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry");

    try expectNotContains(decision_index, "approved status-bucket changes recorded on current `master`: one");
    try expectNotContains(decision_index, "stay-in-C closeout decision records recorded on current `master`: one");
}
