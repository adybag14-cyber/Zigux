const std = @import("std");

const RepoEvidence = struct {
    freeze_map_present: bool,
    review_process_present: bool,
    parity_scorecard_present: bool,
    indefinite_c_policy_present: bool,
    docs_index_handoff_pointer_present: bool,
    phase15_make_target_present: bool,
    shared_ci_phase15_present: bool,
    dedicated_handoff_guard_present: bool,
    shared_build_handoff_replay_present: bool,
    named_reopen_trigger_catalog_present: bool,
    deep_core_status_change_ready: bool,
    tests_root_validator_routes_explicit: bool,
};

const AdjacentLaneBoundary = struct {
    lane_family: []const u8,
    zigux_destination: []const u8,
    why_out_of_scope: []const u8,
};

const Trigger = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    roadmap_phase_title: []const u8,
    roadmap_requirements: []const []const u8,
    bootstrap_ledger_anchor: []const u8,
    repo_evidence: RepoEvidence,
    adjacent_lane_boundaries: []const AdjacentLaneBoundary,
    named_reopen_triggers: []const Trigger,
    pending_next_steps: []const []const u8,
};

test "phase 15 handoff manifest records the current parked packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_handoff_next_steps_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-13", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Full-Parity Blockers and Long-Term Governance", manifest.roadmap_phase_title);
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_requirements.len);
    try std.testing.expect(manifest.repo_evidence.freeze_map_present);
    try std.testing.expect(manifest.repo_evidence.review_process_present);
    try std.testing.expect(manifest.repo_evidence.parity_scorecard_present);
    try std.testing.expect(manifest.repo_evidence.indefinite_c_policy_present);
    try std.testing.expect(manifest.repo_evidence.docs_index_handoff_pointer_present);
    try std.testing.expect(manifest.repo_evidence.phase15_make_target_present);
    try std.testing.expect(manifest.repo_evidence.shared_ci_phase15_present);
    try std.testing.expect(manifest.repo_evidence.dedicated_handoff_guard_present);
    try std.testing.expect(manifest.repo_evidence.shared_build_handoff_replay_present);
    try std.testing.expect(manifest.repo_evidence.named_reopen_trigger_catalog_present);
    try std.testing.expect(!manifest.repo_evidence.deep_core_status_change_ready);
    try std.testing.expect(manifest.repo_evidence.tests_root_validator_routes_explicit);
    try std.testing.expectEqual(@as(usize, 5), manifest.adjacent_lane_boundaries.len);
    try std.testing.expect(std.mem.eql(u8, "shared-summaries", manifest.adjacent_lane_boundaries[0].lane_family));
    try std.testing.expect(std.mem.indexOf(u8, manifest.adjacent_lane_boundaries[0].why_out_of_scope, "Compact docs-root") != null);
    try std.testing.expect(std.mem.eql(u8, "review-process", manifest.adjacent_lane_boundaries[1].lane_family));
    try std.testing.expect(std.mem.indexOf(u8, manifest.adjacent_lane_boundaries[1].why_out_of_scope, "Review-field wording") != null);
    try std.testing.expect(std.mem.eql(u8, "parity-scorecard-survey", manifest.adjacent_lane_boundaries[2].lane_family));
    try std.testing.expect(std.mem.indexOf(u8, manifest.adjacent_lane_boundaries[2].why_out_of_scope, "Roadmap-versus-repo truthfulness") != null);
    try std.testing.expect(std.mem.eql(u8, "parity-scorecard", manifest.adjacent_lane_boundaries[3].lane_family));
    try std.testing.expect(std.mem.indexOf(u8, manifest.adjacent_lane_boundaries[3].why_out_of_scope, "aggregate-metric") != null);
    try std.testing.expect(std.mem.eql(u8, "readiness-gate", manifest.adjacent_lane_boundaries[4].lane_family));
    try std.testing.expect(std.mem.indexOf(u8, manifest.adjacent_laneBoundaries[4].why_out_of_scope, "Validator-first maintenance posture") != null);
    try std.testing.expectEqual(@as(usize, 3), manifest.named_reopen_triggers.len);
    try std.testing.expect(std.mem.indexOf(u8, manifest.named_reopen_triggers[0].why_now, "dedicated handoff note, manifest, or Zig guard") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.named_reopen_triggers[0].why_now, "shared validator still undercounts") == null);
    try std.testing.expectEqual(@as(usize, 3), manifest.pending_next_steps.len);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[0], "named reopen triggers") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "shared-summaries") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "Documentation/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "Documentation/zigux/review-checklist.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "Documentation/zigux/phase15-governance-lane-sequencing.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "Documentation/zigux/phase15-parity-scorecard-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "zigux/tests/phase15_handoff_next_steps_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "zigux/tests/phase15_readiness_gate_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "dedicated packet itself starts drifting") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "scripts/zigux/validate-phase15.py") == null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "zigux/tests/README.md") == null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "shared validator still undercounts") == null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[2], "shared build wiring") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[2], "parity-scorecard blocker edits") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[2], "readiness-validator ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[2], "freeze-map approval posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[2], "dedicated handoff packet can no longer describe") != null);
}

test "phase 15 handoff note keeps the parked trigger catalog explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const handoff_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-handoff-next-steps-survey.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(handoff_note);

    const workflow = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(workflow);

    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "PHASE15_LANE_KEY=P15-L08") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "PHASE15_PROVENANCE_MODE=dated_master_readback") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "PHASE15_SURVEYED_HEAD=current-master-readback-2026-05-13") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Roadmap Versus Ledger") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Current Handoff Surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Adjacent Lane Boundaries") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Named Reopen Triggers") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "evidence_packet_stale_or_contradictory") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "narrower_followup_answers_blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "ownership_or_validation_changed") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "shared-summaries") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "review-process") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "parity-scorecard-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "parity-scorecard") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "readiness-gate") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/phase15-freeze-map-governance.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/phase15-parity-scorecard-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/phase15-parity-scorecard.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/phase15-indefinite-c-policy.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/phase15-readiness-gate-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/phase15-governance-lane-sequencing.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "zigux/tests/phase15_parity_scorecard.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "should no longer point at `zigux/tests/phase15_parity_scorecard.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "zigux/tests/phase15_governance_lane_sequencing.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "zigux/tests/phase15_architecture_council_review_process.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "zigux/tests/phase15_indefinite_c_policy.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "zigux/tests/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "tests-root Phase 15 guards") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "make -C zigux phase15") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "the compact docs-root Phase 15 reminder in `Documentation/zigux/README.md` already keeps") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Those parked maintenance notes still belong to `shared-summaries`") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "any future docs-root reminder repair should stay there before this handoff lane reopens") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "phase15-docs-root-handoff-pointer-visible") == null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/phase15-parity-scorecard-survey.md`, `zigux/tests/phase15_handoff_next_steps_manifest.json`") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Run Phase 15 governance tests") != null);
}
