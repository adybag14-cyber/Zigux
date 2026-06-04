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

test "Phase 15 shared docs keep the no-silent-approval boundary explicit" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 96 * 1024);
    defer std.testing.allocator.free(docs_root);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 48 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 96 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 32 * 1024);
    defer std.testing.allocator.free(review_process);

    const decision_template = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-record-template.md", 16 * 1024);
    defer std.testing.allocator.free(decision_template);

    try expectContains(docs_root, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectContains(docs_root, "below any Architecture Council approval claim");
    try expectContains(docs_root, "below any freeze-map status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`");
    try expectContains(docs_root, "below any claim that dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, or shared-CI Phase 15 routes are already shipped on current `master`");

    try expectContains(freeze_map, "changes to either list require an explicit Architecture Council decision with written rationale");
    try expectContains(freeze_map, "there is no silent exception path around the stay-in-C policy");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change");

    try expectContains(review_checklist, "does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?");
    try expectContains(review_checklist, "if a freeze-map anchor is entering Architecture Council status review or recording a stay-in-C closeout");
    try expectContains(review_checklist, "required approver set, rollback owner, and evidence archive path");

    try expectContains(review_process, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectContains(review_process, "This note does not define an exception path outside those reviewable outcomes.");
    try expectContains(review_process, "There is no silent exception path around the indefinite-C policy.");
    try expectContains(review_process, "On current `master`, no freeze-map anchor has an Architecture Council approval for a status change.");

    try expectContains(decision_template, "This is a review packet template, not approval by itself.");
    try expectContains(decision_template, "REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>");
    try expectContains(decision_template, "If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.");
}

test "Phase 15 study-only anchors remain boundary context, not approval evidence" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 96 * 1024);
    defer std.testing.allocator.free(docs_root);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 48 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 96 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const review_process = try readRepoFile("Documentation/zigux/phase15-architecture-council-review-process.md", 32 * 1024);
    defer std.testing.allocator.free(review_process);

    const decision_template = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-record-template.md", 16 * 1024);
    defer std.testing.allocator.free(decision_template);

    try expectContains(freeze_map, "## Study / Boundary Only");
    try expectContains(freeze_map, "`kernel/workqueue.c`");
    try expectContains(freeze_map, "`kernel/trace/ring_buffer.c`");
    try expectContains(freeze_map, "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`");
    try expectContains(freeze_map, "study-only follow-up may gather narrower evidence, but it must not present `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as active delivery targets before an Architecture Council reviewable record changes their status bucket");

    try expectContains(review_checklist, "route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`");
    try expectContains(review_checklist, "so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence");

    try expectContains(review_process, "Study-only freeze-map anchors stay outside this Architecture Council status-review packet until the freeze map itself changes.");
    try expectContains(review_process, "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain boundary-study context routed through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`");
    try expectContains(review_process, "not candidates for a freeze-in-C status review through this note");

    try expectContains(decision_template, "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.");

    try expectContains(docs_root, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectNotContains(docs_root, "kernel/workqueue.c` has an Architecture Council approval");
    try expectNotContains(docs_root, "kernel/trace/ring_buffer.c` has an Architecture Council approval");
}

test "Phase 15 Makefile wrappers remain absent until the governance packet changes" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 96 * 1024);
    defer std.testing.allocator.free(docs_root);

    const governance_note = try readRepoFile("Documentation/zigux/phase15-freeze-map-governance.md", 48 * 1024);
    defer std.testing.allocator.free(governance_note);

    const makefile = try readRepoFile("zigux/Makefile", 96 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectContains(docs_root, "`zigux/tests/phase15_build.zig` stays the directly readable shared build companion");
    try expectContains(docs_root, "`make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` remain blocked route vocabulary rather than shipped replay paths on current `master`");

    try expectContains(governance_note, "direct contents readback resolves `zigux/tests/phase15_build.zig`, so the shared Phase 15 build companion stays adjacent direct-readback evidence");
    try expectContains(governance_note, "`zigux/Makefile` still carries no `phase15-validate`, `phase15-test`, or `phase15`");
    try expectContains(governance_note, "repo_reality_gap_confirmed `phase15-shared-wrapper-route-readback`");

    try expectContains(makefile, "phase14-validate");
    try expectNotContains(makefile, "\nphase15-validate:");
    try expectNotContains(makefile, "\nphase15-test:");
    try expectNotContains(makefile, "\nphase15:");
    try expectNotContains(makefile, ".PHONY: phase15-validate");
    try expectNotContains(makefile, ".PHONY: phase15-test");
}
