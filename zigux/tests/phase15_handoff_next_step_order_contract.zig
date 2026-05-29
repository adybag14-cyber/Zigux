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

test "phase 15 handoff next-step order starts from current governance evidence before wrapper recovery" {
    const handoff_note = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md", 64 * 1024);
    defer std.testing.allocator.free(handoff_note);

    try expectContains(handoff_note, "## Pending next-step order");
    try expectContains(handoff_note, "compare the live Phase 15 governance packet against the roadmap first and use the bootstrap ledger only as early-tranche context");
    try expectContains(handoff_note, "tighten the smallest shared reminder surface first if docs-root, checklist, scripts-root, or tests-root wording drifts away");
    try expectContains(handoff_note, "reread this handoff note together with any newly landed dedicated `phase15*` wrapper or shared-CI route recovery before treating that broader replay surface as current evidence here");
    try expectContains(handoff_note, "revisit freeze-map or parity-scorecard status only if an owning governance packet changes or a deep-core blocker disposition actually moves");
    try expectContains(handoff_note, "Keep this note parked until one broad Phase 15 reminder surface drifts away from the materialized governance packet above");
    try expectContains(handoff_note, "one of the broader dedicated `phase15*` wrapper routes or shared-CI routes returns on current `master`");
    try expectNotContains(handoff_note, "treat a dedicated Phase 15 review section as still-unlanded by default");
}

test "docs root and freeze map route the handoff through shared reminder surfaces without implying a status change" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 96 * 1024);
    defer std.testing.allocator.free(docs_root);
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 64 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(docs_root, "Phase 15 notes");
    try expectContains(docs_root, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    try expectContains(docs_root, "scripts/zigux/validate-phase15.py");
    try expectContains(docs_root, "keep the Phase 15 reminder bounded below any Architecture Council approval claim");
    try expectContains(docs_root, "dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, or shared-CI Phase 15 routes");

    try expectContains(freeze_map, "shared Phase 15 handoff and gap notes");
    try expectContains(freeze_map, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    try expectContains(freeze_map, "directly materialized validator, tests-root reminder, and shared build companion aligned as landed governance evidence");
    try expectContains(freeze_map, "still-missing dedicated `phase15*` wrapper routes and shared-CI companions");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`");
}

test "review checklist keeps study-only and Architecture Council ownership boundaries visible" {
    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 96 * 1024);
    defer std.testing.allocator.free(review_checklist);

    try expectContains(review_checklist, "is the status bucket explicit: port now, port after substrate, dual implementation required, study only, or freeze in C initially?");
    try expectContains(review_checklist, "does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?");
    try expectContains(review_checklist, "if a freeze-map anchor is entering Architecture Council status review or recording a stay-in-C closeout");
    try expectContains(review_checklist, "if a shared reminder surface summarizes the study-only freeze-map anchors");
    try expectContains(review_checklist, "kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context");
    try expectContains(review_checklist, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
}
