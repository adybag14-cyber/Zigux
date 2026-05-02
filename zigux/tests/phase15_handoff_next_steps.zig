const std = @import("std");

const RepoEvidence = struct {
    freeze_map_governance_present: bool,
    review_process_present: bool,
    parity_scorecard_present: bool,
    indefinite_c_policy_present: bool,
    readiness_gate_present: bool,
    phase15_build_present: bool,
    phase15_make_target_present: bool,
    shared_ci_phase15_present: bool,
    docs_index_handoff_pointer_present: bool,
    docs_root_reviewability_guard_present: bool,
    phase15_replay_green_on_current_master: bool,
    docs_root_phase15_summary_aligned: bool,
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
    roadmap_phase_title: []const u8,
    roadmap_requirements: []const []const u8,
    bootstrap_ledger_anchor: []const u8,
    repo_evidence: RepoEvidence,
    open_handoff_gaps: []const Gap,
    pending_next_steps: []const []const u8,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

test "phase 15 handoff manifest records the parked governance contract" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_handoff_next_steps_manifest.json",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-Y01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("b5f64cf3306b706ea93cc9d3de769d545849b2d4", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Full-Parity Blockers and Long-Term Governance", manifest.roadmap_phase_title);
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_requirements.len);
    try std.testing.expectEqualStrings("freeze map", manifest.roadmap_requirements[0]);
    try std.testing.expectEqualStrings("Architecture Council review process", manifest.roadmap_requirements[1]);
    try std.testing.expectEqualStrings("parity scorecard", manifest.roadmap_requirements[2]);
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirements[3]);
    try std.testing.expect(std.mem.indexOf(u8, manifest.bootstrap_ledger_anchor, "freeze map") != null);

    try std.testing.expect(manifest.repo_evidence.freeze_map_governance_present);
    try std.testing.expect(manifest.repo_evidence.review_process_present);
    try std.testing.expect(manifest.repo_evidence.parity_scorecard_present);
    try std.testing.expect(manifest.repo_evidence.indefinite_c_policy_present);
    try std.testing.expect(manifest.repo_evidence.readiness_gate_present);
    try std.testing.expect(manifest.repo_evidence.phase15_build_present);
    try std.testing.expect(manifest.repo_evidence.phase15_make_target_present);
    try std.testing.expect(manifest.repo_evidence.shared_ci_phase15_present);
    try std.testing.expect(manifest.repo_evidence.docs_index_handoff_pointer_present);
    try std.testing.expect(manifest.repo_evidence.docs_root_reviewability_guard_present);
    try std.testing.expect(manifest.repo_evidence.phase15_replay_green_on_current_master);
    try std.testing.expect(manifest.repo_evidence.docs_root_phase15_summary_aligned);
    try std.testing.expect(!manifest.repo_evidence.deep_core_status_change_ready);

    try std.testing.expectEqual(@as(usize, 1), manifest.open_handoff_gaps.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.pending_next_steps.len);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[0], "shared Phase 15 replay drifts again") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[0], "named reopen trigger") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "zig build test --build-file zigux/tests/phase15_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "make -C zigux phase15") != null);

    const gap = manifest.open_handoff_gaps[0];
    try std.testing.expect(isAllowedStatus(gap.status));
    try std.testing.expectEqualStrings("phase15-deep-core-status-change-blocker", gap.id);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", gap.zigux_destination);
    try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "freeze-in-C posture") != null);
}

test "phase 15 handoff note keeps the open gaps and parked next steps explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const handoff_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-handoff-next-steps-survey.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(handoff_note);

    const docs_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(40 * 1024),
    );
    defer std.testing.allocator.free(docs_readme);

    const workflow = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(workflow);

    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "PHASE15_LANE_KEY=P15-Y01") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Roadmap Versus Ledger") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Current Handoff Surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Open Handoff Gaps") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Pending Next Steps") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Maintenance Handoff Contract") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "shared bootstrap workflow still runs `Run Phase 15 governance tests`") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "docs-root release evidence now matches the dedicated maintenance packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "phase15-docs-root-summary-alignment") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "phase15-deep-core-status-change-blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "make -C zigux phase15") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "zig build test --build-file zigux/tests/phase15_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "named reopen trigger") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "phase15-review-process-replay-drift") == null);

    try std.testing.expect(std.mem.indexOf(u8, docs_readme, "Documentation/zigux/phase15-handoff-next-steps-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_readme, "only remaining blocked work is the deep-core status-change evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_readme, "remaining broader replay drift on current `master`") == null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Run Phase 15 governance tests") != null);
}
