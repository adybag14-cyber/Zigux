const std = @import("std");

const release_evidence = [_]struct {
    name: []const u8,
    path: []const u8,
}{
    .{ .name = "validator_first_replay", .path = "scripts/zigux/validate-phase15.py" },
    .{ .name = "readiness_packet_checker", .path = "scripts/zigux/check-phase15-readiness-gate-packet.py" },
    .{ .name = "shared_build_companion", .path = "zigux/tests/phase15_build.zig" },
    .{ .name = "readiness_gap_matrix", .path = "zigux/tests/phase15_readiness_gap_matrix.json" },
};

const blocked_make_routes = [_][]const u8{
    "phase15-validate",
    "phase15-test",
    "phase15",
};

const readiness_survey_markers =
    \\PHASE15_STATUS=readiness_gate_survey_landed
    \\PHASE15_LANE_KEY=P15-L04
    \\PHASE15_SLICE=validator_first_readiness_packet
    \\PHASE15_PROVENANCE_MODE=dated_master_readback
    \\current-master-readback-2026-05-27
    \\## Release Evidence Quartet
    \\release_evidence_count=4
    \\`scripts/zigux/validate-phase15.py` is the validator-first replay for the current maintenance gate
    \\`scripts/zigux/check-phase15-readiness-gate-packet.py` keeps the readiness note, manifest, gap matrix, blocked-route posture, and repo evidence aligned
    \\`zigux/tests/phase15_build.zig` is directly readable shared-build companion evidence, not proof that the missing wrappers exist
    \\`zigux/tests/phase15_readiness_gap_matrix.json` keeps the roadmap-versus-ledger blockers explicit as data rather than relying on prose-only handoff notes
    \\`make -C zigux phase15-validate` remains blocked route vocabulary rather than a directly readable shipped replay path
    \\`make -C zigux phase15-test` remains blocked route vocabulary rather than a directly readable shipped replay path
    \\`make -C zigux phase15` remains blocked route vocabulary rather than a directly readable shipped replay path
    \\`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route
    \\no Architecture Council approval is currently recorded for a freeze-map status change
;

const readiness_manifest_markers =
    \\"phase15_readiness_packet_checker_present": true
    \\"phase15_validator_script_present": true
    \\"phase15_build_zig_present": true
    \\"phase15_gap_matrix_present": true
    \\"phase15_validate_target_present": false
    \\"phase15_test_target_present": false
    \\"phase15_aggregate_target_present": false
    \\"shared_ci_phase15_present": false
    \\"phase15_replay_green_on_current_master": false
;

const gap_matrix_markers =
    \\"roadmap_required_feature_count": 4
    \\"ledger_anchor_count": 1
    \\"remaining_readiness_gap_count": 3
    \\"blocked_make_route_count": 3
    \\"blocked_workflow_route_count": 1
    \\"release_evidence_count": 4
    \\"gap": "missing_make_routes"
    \\"gap": "missing_workflow_route"
    \\"gap": "no_architecture_council_status_change_approval"
    \\"status": "blocked"
    \\"path": "zigux/Makefile"
    \\"path": ".github/workflows/zigux-bootstrap.yml"
    \\"Documentation/zigux/freeze-map.md"
    \\"Documentation/zigux/phase15-architecture-council-review-process.md"
;

const phase15_build_markers =
    \\"phase15-freeze-map-governance"
    \\"phase15-architecture-council-review-process"
    \\"phase15-architecture-council-decision-index"
    \\"phase15-governance-lane-sequencing"
    \\"phase15-parity-scorecard"
    \\"phase15-indefinite-c-policy"
    \\"phase15-handoff-next-steps"
    \\"phase15-indefinite-c-lane-owner-alignment"
    \\"phase15-readiness-gate"
    \\"phase15_readiness_gate.zig"
;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase 15 release-evidence quartet stays exactly scoped" {
    try std.testing.expectEqual(@as(usize, 4), release_evidence.len);
    try std.testing.expectEqualStrings("validator_first_replay", release_evidence[0].name);
    try std.testing.expectEqualStrings("scripts/zigux/validate-phase15.py", release_evidence[0].path);
    try std.testing.expectEqualStrings("readiness_packet_checker", release_evidence[1].name);
    try std.testing.expectEqualStrings("scripts/zigux/check-phase15-readiness-gate-packet.py", release_evidence[1].path);
    try std.testing.expectEqualStrings("shared_build_companion", release_evidence[2].name);
    try std.testing.expectEqualStrings("zigux/tests/phase15_build.zig", release_evidence[2].path);
    try std.testing.expectEqualStrings("readiness_gap_matrix", release_evidence[3].name);
    try std.testing.expectEqualStrings("zigux/tests/phase15_readiness_gap_matrix.json", release_evidence[3].path);

    try expectContains(readiness_survey_markers, "## Release Evidence Quartet");
    try expectContains(readiness_survey_markers, "release_evidence_count=4");
    try expectContains(readiness_survey_markers, "not proof that the missing wrappers exist");
    try expectContains(gap_matrix_markers, "\"release_evidence_count\": 4");
    try expectContains(readiness_manifest_markers, "\"phase15_validator_script_present\": true");
    try expectContains(readiness_manifest_markers, "\"phase15_readiness_packet_checker_present\": true");
    try expectContains(readiness_manifest_markers, "\"phase15_build_zig_present\": true");
    try expectContains(readiness_manifest_markers, "\"phase15_gap_matrix_present\": true");
}

test "phase 15 broader readiness remains blocked on wrappers and workflow route" {
    try std.testing.expectEqual(@as(usize, 3), blocked_make_routes.len);
    try std.testing.expectEqualStrings("phase15-validate", blocked_make_routes[0]);
    try std.testing.expectEqualStrings("phase15-test", blocked_make_routes[1]);
    try std.testing.expectEqualStrings("phase15", blocked_make_routes[2]);

    try expectContains(readiness_survey_markers, "`make -C zigux phase15-validate` remains blocked route vocabulary");
    try expectContains(readiness_survey_markers, "`make -C zigux phase15-test` remains blocked route vocabulary");
    try expectContains(readiness_survey_markers, "`make -C zigux phase15` remains blocked route vocabulary");
    try expectContains(readiness_survey_markers, "still carries no dedicated Phase 15 validate, test, or aggregate route");
    try expectContains(readiness_survey_markers, "no Architecture Council approval is currently recorded for a freeze-map status change");

    try expectContains(gap_matrix_markers, "\"blocked_make_route_count\": 3");
    try expectContains(gap_matrix_markers, "\"blocked_workflow_route_count\": 1");
    try expectContains(gap_matrix_markers, "\"gap\": \"missing_make_routes\"");
    try expectContains(gap_matrix_markers, "\"gap\": \"missing_workflow_route\"");
    try expectContains(gap_matrix_markers, "\"gap\": \"no_architecture_council_status_change_approval\"");
    try expectContains(readiness_manifest_markers, "\"phase15_validate_target_present\": false");
    try expectContains(readiness_manifest_markers, "\"phase15_test_target_present\": false");
    try expectContains(readiness_manifest_markers, "\"phase15_aggregate_target_present\": false");
    try expectContains(readiness_manifest_markers, "\"shared_ci_phase15_present\": false");
    try expectContains(readiness_manifest_markers, "\"phase15_replay_green_on_current_master\": false");
}

test "shared Phase 15 build companion is evidence without wrapper promotion" {
    const expected_steps = [_][]const u8{
        "phase15-freeze-map-governance",
        "phase15-architecture-council-review-process",
        "phase15-architecture-council-decision-index",
        "phase15-governance-lane-sequencing",
        "phase15-parity-scorecard",
        "phase15-indefinite-c-policy",
        "phase15-handoff-next-steps",
        "phase15-indefinite-c-lane-owner-alignment",
        "phase15-readiness-gate",
    };

    for (expected_steps) |step| {
        try expectContains(phase15_build_markers, step);
    }

    try expectContains(phase15_build_markers, "phase15_readiness_gate.zig");
    try expectNotContains(phase15_build_markers, "make -C zigux phase15-validate");
    try expectNotContains(phase15_build_markers, "make -C zigux phase15-test");
    try expectNotContains(phase15_build_markers, "make -C zigux phase15");
}
