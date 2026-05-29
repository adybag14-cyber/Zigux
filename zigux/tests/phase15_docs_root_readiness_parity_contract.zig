const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectDocsRootNamesPhase15ReadinessPacket(readme: []const u8) !void {
    try expectContains(readme, "Phase 15 notes");
    try expectContains(readme, "Documentation/zigux/freeze-map.md");
    try expectContains(readme, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectContains(readme, "Documentation/zigux/phase15-readiness-gate-survey.md");
    try expectContains(readme, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(readme, "Documentation/zigux/phase15-shared-summary-gap.md");
    try expectContains(readme, "scripts/zigux/check-phase15-docs-readme-alignment.py");
    try expectContains(readme, "scripts/zigux/check-phase15-architecture-council-packet.py");
    try expectContains(readme, "scripts/zigux/validate-phase15.py");
    try expectContains(readme, "Architecture Council");
    try expectContains(readme, "freeze-map status change");
    try expectContains(readme, "dedicated `phase15*` wrapper routes");
    try expectContains(readme, "shared-CI companions");
}

fn expectChecklistKeepsFreezeMapGate(checklist: []const u8) !void {
    try expectContains(checklist, "Zigux Review Checklist");
    try expectContains(checklist, "deep-core scope creep into scheduler, MM, RCU, or skbuff");
    try expectContains(checklist, "freeze-map anchor is entering Architecture Council status review");
    try expectContains(checklist, "required approver set");
    try expectContains(checklist, "rollback owner");
    try expectContains(checklist, "evidence archive path");
    try expectContains(checklist, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(checklist, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(checklist, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(checklist, "Documentation/zigux/freeze-map.md");
    try expectContains(checklist, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(checklist, "kernel/workqueue.c");
    try expectContains(checklist, "kernel/trace/ring_buffer.c");
}

fn expectFreezeMapAndParityAgree(freeze_map: []const u8, parity_scorecard: []const u8) !void {
    const freeze_in_c_targets = [_][]const u8{
        "kernel/sched/core.c",
        "mm/page_alloc.c",
        "kernel/rcu/tree.c",
        "net/core/skbuff.c",
    };
    for (freeze_in_c_targets) |target| {
        try expectContains(freeze_map, target);
        try expectContains(parity_scorecard, target);
    }

    try expectContains(freeze_map, "kernel/workqueue.c");
    try expectContains(freeze_map, "kernel/trace/ring_buffer.c");
    try expectContains(parity_scorecard, "study-only anchors tracked outside this scorecard: `2`");
    try expectContains(parity_scorecard, "Architecture Council approvals recorded for status change: `0`");
    try expectContains(parity_scorecard, "PHASE15_SCORECARD_ROLE=blocked_posture_accounting_not_port_readiness");
    try expectContains(parity_scorecard, "This scorecard does not claim");
    try expectContains(parity_scorecard, "Architecture Council approval for any direct Zigux deep-core port");
    try expectContains(parity_scorecard, "validator-first reminder route is directly readable on current `master` through `python3 scripts/zigux/validate-phase15.py`");
    try expectContains(parity_scorecard, "shared replay build route is directly readable on current `master` through `zigux/tests/phase15_build.zig` and `zig build test --build-file zigux/tests/phase15_build.zig`");
    try expectContains(parity_scorecard, "current `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15` targets");
}

fn expectReadinessAndValidatorKeepRouteGaps(readiness: []const u8, validator: []const u8) !void {
    try expectContains(readiness, "PHASE15_STATUS=readiness_gate_survey_landed");
    try expectContains(readiness, "PHASE15_SLICE=validator_first_readiness_packet");
    try expectContains(readiness, "the dedicated validator now exists as a directly readable maintenance gate");
    try expectContains(readiness, "the roadmap-versus-ledger gap matrix now keeps the remaining readiness requirements explicit");
    try expectContains(readiness, "make -C zigux phase15-validate` remains blocked route vocabulary");
    try expectContains(readiness, "make -C zigux phase15-test` remains blocked route vocabulary");
    try expectContains(readiness, "make -C zigux phase15` remains blocked route vocabulary");
    try expectContains(readiness, ".github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route");
    try expectContains(readiness, "no Architecture Council approval is currently recorded for a freeze-map status change");

    try expectContains(validator, "EXPECTED_BLOCKED_BROADER_ROUTES");
    try expectContains(validator, "missing_make_targets");
    try expectContains(validator, "phase15-validate");
    try expectContains(validator, "phase15-test");
    try expectContains(validator, "phase15");
    try expectContains(validator, "missing_workflow_phase15_route");
    try expectContains(validator, "phase15_build_zig_present");
    try expectContains(validator, "phase15_gap_matrix_present");
    try expectContains(validator, "phase15_replay_green_on_current_master");
}

test "docs root and review checklist keep the Phase 15 readiness packet reviewable" {
    const readme = try readRepoFile("Documentation/zigux/README.md", 96 * 1024);
    defer std.testing.allocator.free(readme);
    const checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 160 * 1024);
    defer std.testing.allocator.free(checklist);

    try expectDocsRootNamesPhase15ReadinessPacket(readme);
    try expectChecklistKeepsFreezeMapGate(checklist);
}

test "freeze map and parity scorecard keep blocked posture aligned" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 64 * 1024);
    defer std.testing.allocator.free(freeze_map);
    const parity_scorecard = try readRepoFile("Documentation/zigux/phase15-parity-scorecard.md", 48 * 1024);
    defer std.testing.allocator.free(parity_scorecard);

    try expectFreezeMapAndParityAgree(freeze_map, parity_scorecard);
}

test "readiness survey and validator keep broader Phase 15 routes as gaps" {
    const readiness = try readRepoFile("Documentation/zigux/phase15-readiness-gate-survey.md", 48 * 1024);
    defer std.testing.allocator.free(readiness);
    const validator = try readRepoFile("scripts/zigux/validate-phase15.py", 48 * 1024);
    defer std.testing.allocator.free(validator);

    try expectReadinessAndValidatorKeepRouteGaps(readiness, validator);
}
