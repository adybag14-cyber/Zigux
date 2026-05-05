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
    try std.testing.expectEqualStrings("P15-L11", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("0f06196", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Full-Parity Blockers and Long-Term Governance", manifest.roadmap_phase_title);
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_requirements.len);
    try std.testing.expect(manifest.repo_evidence.freeze_map_present);
    try std.testing.expect(manifest.repo_evidence.review_process_present);
    try std.testing.expect(manifest.repo_evidence.parity_scorecard_present);
    try std.testing.expect(manifest.repo_evidence.indefinite_c_policy_present);
    try std.testing.expect(!manifest.repo_evidence.docs_index_handoff_pointer_present);
    try std.testing.expect(manifest.repo_evidence.phase15_make_target_present);
    try std.testing.expect(manifest.repo_evidence.shared_ci_phase15_present);
    try std.testing.expect(manifest.repo_evidence.dedicated_handoff_guard_present);
    try std.testing.expect(!manifest.repo_evidence.shared_build_handoff_replay_present);
    try std.testing.expect(!manifest.repo_evidence.deep_core_status_change_ready);
    try std.testing.expectEqual(@as(usize, 3), manifest.open_handoff_gaps.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.pending_next_steps.len);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[0], "README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[1], "phase15_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.pending_next_steps[2], "deep-core blocker posture") != null);
}

test "phase 15 handoff note keeps the missing pointer and build hook explicit" {
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

    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "PHASE15_LANE_KEY=P15-L11") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "commit `0f06196` observed on May 5, 2026") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Roadmap Versus Ledger") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Current Handoff Surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "## Open Handoff Gaps") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "phase15-docs-root-handoff-pointer-gap") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "phase15-build-handoff-replay-gap") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "phase15-deep-core-status-change-blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "Documentation/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "zigux/tests/phase15_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff_note, "make -C zigux phase15") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Run Phase 15 governance tests") != null);
}
