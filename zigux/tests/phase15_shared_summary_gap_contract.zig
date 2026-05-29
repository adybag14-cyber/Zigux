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

test "phase 15 shared-summary gap keeps docs root and checklist aligned with current governance packet" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 128 * 1024);
    defer std.testing.allocator.free(docs_root);
    const checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 128 * 1024);
    defer std.testing.allocator.free(checklist);

    try expectContains(docs_root, "Phase 15 notes");
    try expectContains(docs_root, "Documentation/zigux/phase15-freeze-map-governance.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-readiness-gate-survey.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-governance-lane-sequencing.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-shared-summary-gap.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    try expectContains(docs_root, "scripts/zigux/check-phase15-docs-readme-alignment.py");
    try expectContains(docs_root, "scripts/zigux/check-phase15-architecture-council-packet.py");
    try expectContains(docs_root, "scripts/zigux/validate-phase15.py");
    try expectContains(docs_root, "no Architecture Council approval claim");
    try expectContains(docs_root, "no active-delivery implication for `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`");
    try expectContains(docs_root, "make -C zigux phase15-validate");
    try expectContains(docs_root, "make -C zigux phase15-test");
    try expectContains(docs_root, "make -C zigux phase15");

    try expectContains(checklist, "is the status bucket explicit: port now, port after substrate, dual implementation required, study only, or freeze in C initially?");
    try expectContains(checklist, "if a shared reminder surface summarizes the study-only freeze-map anchors");
    try expectContains(checklist, "Documentation/zigux/freeze-map.md");
    try expectContains(checklist, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(checklist, "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence");
    try expectNotContains(checklist, "Phase 15 wrapper routes are shipped on current `master`");
}

test "phase 15 freeze map and study-only accounting keep shared-summary route gaps out of approval language" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 96 * 1024);
    defer std.testing.allocator.free(freeze_map);
    const accounting = try readRepoFile("Documentation/zigux/phase15-study-only-anchor-accounting.md", 32 * 1024);
    defer std.testing.allocator.free(accounting);

    try expectContains(freeze_map, "## Study / Boundary Only");
    try expectContains(freeze_map, "- `kernel/workqueue.c`");
    try expectContains(freeze_map, "- `kernel/trace/ring_buffer.c`");
    try expectContains(freeze_map, "shared reminder surfaces that summarize freeze posture");
    try expectContains(freeze_map, "Documentation/zigux/README.md");
    try expectContains(freeze_map, "Documentation/zigux/review-checklist.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(freeze_map, "shared Phase 15 handoff and gap notes");
    try expectContains(freeze_map, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-shared-summary-gap.md");
    try expectContains(freeze_map, "only the still-missing dedicated `phase15*` wrapper routes and shared-CI companions as repo-reality gaps on current `master`");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");

    try expectContains(accounting, "PHASE15_STATUS=study_only_accounting_slice_landed");
    try expectContains(accounting, "kernel/workqueue.c");
    try expectContains(accounting, "kernel/trace/ring_buffer.c");
    try expectContains(accounting, "tracked outside the freeze-in-C scorecard and outside blocked status-change rows");
    try expectContains(accounting, "not an approval record");
    try expectContains(accounting, "an Architecture Council approval for any study-only anchor to leave its current posture");
    try expectNotContains(accounting, "direct Zigux bridge for `kernel/workqueue.c` landed");
    try expectNotContains(accounting, "direct Zigux bridge for `kernel/trace/ring_buffer.c` landed");
}

test "phase 15 shared-summary gap distinguishes materialized governance evidence from missing route bodies" {
    const shared_gap = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 64 * 1024);
    defer std.testing.allocator.free(shared_gap);

    try expectContains(shared_gap, "PHASE15_STATUS=shared_summary_gap_recorded");
    try expectContains(shared_gap, "PHASE15_LANE_KEY=P15-L02");
    try expectContains(shared_gap, "PHASE15_PROVENANCE_MODE=dated_master_readback");
    try expectContains(shared_gap, "## Materialized Phase 15 governance assets");
    try expectContains(shared_gap, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(shared_gap, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(shared_gap, "Documentation/zigux/phase15-architecture-council-decision-index.md");
    try expectContains(shared_gap, "Documentation/zigux/phase15-parity-scorecard-survey.md");
    try expectContains(shared_gap, "Documentation/zigux/phase15-readiness-gate-survey.md");
    try expectContains(shared_gap, "Documentation/zigux/phase15-governance-lane-sequencing.md");
    try expectContains(shared_gap, "Documentation/zigux/phase15-deep-core-blocker-survey.md");
    try expectContains(shared_gap, "zigux/tests/phase15_build.zig");
    try expectContains(shared_gap, "scripts/zigux/validate-phase15.py");
    try expectContains(shared_gap, "## Still-missing broader wrapper and shared-CI route companions on current master");
    try expectContains(shared_gap, "no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`");
    try expectContains(shared_gap, "do not treat the parked make-route vocabulary or shared-CI route vocabulary as shipped evidence until direct current-tree reads recover them");
    try expectContains(shared_gap, "do not treat present focused companions as Architecture Council approval or direct deep-core delivery evidence by themselves");
    try expectContains(shared_gap, "an Architecture Council approval workflow implementation");
    try expectContains(shared_gap, "a direct deep-core Zig bridge or port-readiness decision");
    try expectNotContains(shared_gap, "all dedicated Phase 15 wrapper routes are shipped evidence");
}
