const std = @import("std");

const RepoEvidence = struct {
    freeze_map_present: bool,
    review_checklist_present: bool,
    review_process_present: bool,
    parity_scorecard_present: bool,
    indefinite_c_policy_present: bool,
    docs_index_handoff_pointer_present: bool,
    readiness_note_present: bool,
    tests_root_phase15_surface_present: bool,
    phase15_validate_target_present: bool,
    phase15_make_test_target_present: bool,
    scripts_alignment_guard_present: bool,
    phase15_make_target_present: bool,
    shared_ci_phase15_present: bool,
    dedicated_handoff_guard_present: bool,
    shared_build_handoff_replay_present: bool,
    indefinite_c_blocker_evidence_replay_present: bool,
    indefinite_c_lane_owner_alignment_replay_present: bool,
    governance_lane_sequencing_replay_present: bool,
    lane_key_matches_phase15_lane_map: bool,
    paired_parity_scorecard_blocker_posture_matches: bool,
    paired_parity_scorecard_lane_key_explicit: bool,
    paired_readiness_lane_key_explicit: bool,
    deep_core_status_change_ready: bool,
};

const Gap = struct {
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
    cross_packet_truthfulness_mode: []const u8,
    paired_lane_identity_alignment: []const u8,
    paired_parity_scorecard_exact_head_matches: bool,
    paired_parity_scorecard_provenance_marker: []const u8,
    paired_parity_scorecard_lane_key: []const u8,
    paired_readiness_lane_key: []const u8,
    paired_parity_scorecard_exact_head_fallback_reason: []const u8,
    roadmap_phase_title: []const u8,
    roadmap_requirements: []const []const u8,
    bootstrap_ledger_anchor: []const u8,
    repo_evidence: RepoEvidence,
    open_handoff_gaps: []const Gap,
    reopen_triggers: []const []const u8,
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
    try std.testing.expectEqualStrings("current-master-readback-2026-05-09", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("dated_master_readback_same_marker_alignment", manifest.cross_packet_truthfulness_mode);
    try std.testing.expectEqualStrings("scorecard_and_readiness_lane_keys_explicit", manifest.paired_lane_identity_alignment);
    try std.testing.expect(!manifest.paired_parity_scorecard_exact_head_matches);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-09", manifest.paired_parity_scorecard_provenance_marker);
    try std.testing.expectEqualStrings("P15-L12", manifest.paired_parity_scorecard_lane_key);
    try std.testing.expectEqualStrings("P15-L01", manifest.paired_readiness_lane_key);
    try std.testing.expect(std.mem.indexOf(u8, manifest.paired_parity_scorecard_exact_head_fallback_reason, manifest.paired_parity_scorecard_provenance_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.paired_parity_scorecard_exact_head_fallback_reason, manifest.surveyed_commit) != null);
    try std.testing.expectEqualStrings("This handoff packet was refreshed against current-master-readback-2026-05-09 and the paired parity scorecard now records the same dated master readback marker current-master-readback-2026-05-09, so the parked governance packet keeps same-marker dated-readback truthfulness explicit without implying exact-head parity.", manifest.paired_parity_scorecard_exact_head_fallback_reason);
    try std.testing.expectEqualStrings("Full-Parity Blockers and Long-Term Governance", manifest.roadmap_phase_title);
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_requirements.len);
    try std.testing.expect(manifest.repo_evidence.freeze_map_present);
    try std.testing.expect(manifest.repo_evidence.review_checklist_present);
    try std.testing.expect(manifest.repo_evidence.review_process_present);
    try std.testing.expect(manifest.repo_evidence.parity_scorecard_present);
    try std.testing.expect(manifest.repo_evidence.indefinite_c_policy_present);
    try std.testing.expect(manifest.repo_evidence.docs_index_handoff_pointer_present);
    try std.testing.expect(manifest.repo_evidence.readiness_note_present);
    try std.testing.expect(manifest.repo_evidence.tests_root_phase15_surface_present);
    try std.testing.expect(manifest.repo_evidence.phase15_validate_target_present);
    try std.testing.expect(manifest.repo_evidence.phase15_make_test_target_present);
    try std.testing.expect(manifest.repo_evidence.scripts_alignment_guard_present);
    try std.testing.expect(manifest.repo_evidence.phase15_make_target_present);
    try std.testing.expect(manifest.repo_evidence.shared_ci_phase15_present);
    try std.testing.expect(manifest.repo_evidence.dedicated_handoff_guard_present);
    try std.testing.expect(manifest.repo_evidence.shared_build_handoff_replay_present);
    try std.testing.expect(manifest.repo_evidence.indefinite_c_blocker_evidence_replay_present);
    try std.testing.expect(manifest.repo_evidence.indefinite_c_lane_owner_alignment_replay_present);
    try std.testing.expect(manifest.repo_evidence.governance_lane_sequencing_replay_present);
    try std.testing.expect(manifest.repo_evidence.lane_key_matches_phase15_lane_map);
    try std.testing.expect(manifest.repo_evidence.paired_parity_scorecard_blocker_posture_matches);
    try std.testing.expect(manifest.repo_evidence.paired_parity_scorecard_lane_key_explicit);
    try std.testing.expect(manifest.repo_evidence.paired_readiness_lane_key_explicit);
    try std.testing.expect(!manifest.repo_evidence.deep_core_status_change_ready);
    try std.testing.expectEqual(@as(usize, 1), manifest.open_handoff_gaps.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.reopen_triggers.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.pending_next_steps.len);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reopen_triggers[0], "evidence_packet_stale_or_contradictory") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reopen_triggers[1], "narrower_followup_answers_blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reopen_triggers[2], "ownership_or_validation_changed") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[0], "evidence_packet_stale_or_contradictory") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "narrower_followup_answers_blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "ownership_or_validation_changed") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], manifest.paired_parity_scorecard_lane_key) != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], manifest.paired_readiness_lane_key) != null);
    try std.testing.expectEqualStrings("phase15-deep-core-status-change-blocker", manifest.open_handoff_gaps[0].id);
}

test "phase 15 handoff note keeps the repaired validator-first surface and remaining blocker explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const handoff_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-handoff-next-steps-survey.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(handoff_note);

    const docs_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(docs_root);

    const readiness_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-readiness-gate-survey.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(readiness_note);

    const governance_lane_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-governance-lane-sequencing.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(governance_lane_note);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(96 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    const scripts_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        std.testing.allocator,
        .limited(96 * 1024),
    );
    defer std.testing.allocator.free(scripts_readme);

    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(96 * 1024),
    );
    defer std.testing.allocator.free(tests_readme);

    const phase15_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_build.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(phase15_build);

    const workflow = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(workflow);

    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "PHASE15_LANE_KEY=P15-L08") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "reviewed handoff provenance refreshed against dated `master` readback marker `current-master-readback-2026-05-09` on 2026-05-09 so this dedicated handoff packet now records current master reread timing without implying exact-head parity across later maintenance commits") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "paired parity scorecard provenance marker is now `current-master-readback-2026-05-09`") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "paired current scorecard owner lane is `P15-L12` and paired current readiness owner lane is `P15-L01`") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "the paired current `Documentation/zigux/phase15-parity-scorecard.md` packet now records the same dated `master` readback marker `current-master-readback-2026-05-09`") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "keeps same-marker dated-readback alignment explicit instead of overstating exact-head parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "machine-check `dated_master_readback_same_marker_alignment` as the active cross-packet truthfulness mode and `scorecard_and_readiness_lane_keys_explicit` as the active paired-lane ownership mode") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Current Handoff Surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "review checklist") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "the scripts root") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "the tests root") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "scripts/zigux/check-phase15-scripts-readme-alignment.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "scripts/zigux/check-phase15-review-process-handoff.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "make -C zigux phase15-validate") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "make -C zigux phase15-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "shared `zigux/tests/phase15_build.zig` replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/phase15-readiness-gate-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "deep-core-only blocker posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "phase15-deep-core-status-change-blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "lane identity is refreshed to `P15-L08`") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "remaining blocked work is only the deep-core status-change evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "keeps both neighboring lane identities plus matched dated-readback timing explicit beside that scorecard packet without implying exact-head parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "parked next-bound queue now mirrors the named scorecard reopen-trigger catalog") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "evidence_packet_stale_or_contradictory") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "narrower_followup_answers_blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "ownership_or_validation_changed") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "current parity-scorecard lane `P15-L12`") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "current readiness lane `P15-L01`") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "make -C zigux phase15") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "zigux/tests/phase15_indefinite_c_blocker_evidence.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "zigux/tests/phase15_governance_lane_sequencing.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "blocker vocabulary, lane-owner vocabulary, and anti-overlap posture explicit beside this parked next-step packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "Documentation/zigux/phase15-handoff-next-steps-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "phase15-deep-core-status-change-blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_lane_note, "### 5. Handoff lane: `P15-L08` parked next-step record only") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_lane_note, "Use the handoff lane `P15-L08` when the work is about the dedicated next-step packet, its manifest, or the statement that the current governance bundle should remain parked until a named reopen trigger fires or the blocker posture changes.") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_lane_note, "Documentation/zigux/phase15-handoff-next-steps-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_lane_note, "zigux/tests/phase15_handoff_next_steps.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_lane_note, "zigux/tests/phase15_handoff_next_steps_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_lane_note, "keep packet-local truthfulness or evidence changes inside the owning lane above") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_lane_note, "keep every Phase 15 governance run parked unless a named reopen trigger fires or the deep-core blocker posture changes") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "if the change touches the shared Phase 15 governance packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, scripts_readme, "Phase 15 flow") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "keep the parked Phase 15 governance packet explicit in the tests root too") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase15_build, "phase15_handoff_next_steps.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase15_build, "phase15-handoff-next-steps-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase15_build, "run_phase15_handoff_next_steps_tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Validate Phase 15 governance packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Run Phase 15 governance tests") != null);
}
