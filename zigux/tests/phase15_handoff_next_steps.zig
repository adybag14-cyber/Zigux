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
    try std.testing.expectEqualStrings("cd03346960b3eee07e3f30d1461b089b30212de5", manifest.surveyed_commit);
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
    try std.testing.expectEqual(@as(usize, 3), manifest.named_reopen_triggers.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.pending_next_steps.len);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[0], "named reopen triggers") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "phase15-parity-scorecard.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[2], "shared README summaries") != null);
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
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "commit `cd03346960b3eee07e3f30d1461b089b30212de5` observed on May 10, 2026") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Roadmap Versus Ledger") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Current Handoff Surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Named Reopen Triggers") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "evidence_packet_stale_or_contradictory") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "narrower_followup_answers_blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "ownership_or_validation_changed") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/phase15-parity-scorecard.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/phase15-readiness-gate-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "make -C zigux phase15") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Run Phase 15 governance tests") != null);
}
