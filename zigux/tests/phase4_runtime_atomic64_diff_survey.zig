const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    roadmap_target_path: []const u8,
    roadmap_atomic64_diff_present: bool,
    roadmap_atomic64_wrapper_targets_runtime_diff: bool,
    live_gate_path: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
    live_gate_blob_sha: []const u8,
    live_gate_line_count: usize,
    runtime_replay_path: []const u8,
    runtime_replay_blob_sha: []const u8,
    runtime_replay_line_count: usize,
    phase4_build_present: bool,
    phase4_build_uses_atomic64_wrapper: bool,
    phase4_build_blob_sha: []const u8,
    phase4_validator_atomic64_diff_present: bool,
    phase4_validator_runtime_atomic64_diff_present: bool,
    phase4_validator_blob_sha: []const u8,
    phase4_gate_evidence_path: []const u8,
    phase4_gate_evidence_blob_sha: []const u8,
    phase9_build_present: bool,
    phase9_build_blob_sha: []const u8,
    phase4_validation_matrix_atomic64_diff_note_present: bool,
    phase4_validation_matrix_runtime_atomic64_note_present: bool,
    phase4_validation_matrix_blob_sha: []const u8,
    phase4_review_checklist_blob_sha: []const u8,
    threshold_posture: []const u8,
    roadmap_gap_summary: []const u8,
    reversible_delivery_evidence: []const u8,
    ready_next: []const u8,
};

test "phase 4 atomic64 survey keeps wrapper handoff, owner map, and current local-only perf evidence explicit" {
    const parsed = try std.json.parseFromSlice(
        Manifest,
        std.testing.allocator,
        @embedFile("phase4_runtime_atomic64_diff_manifest.json"),
        .{},
    );
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P4-L02", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("zigux/tests/atomic64_diff.zig", manifest.roadmap_target_path);
    try std.testing.expect(manifest.roadmap_atomic64_diff_present);
    try std.testing.expect(manifest.roadmap_atomic64_wrapper_targets_runtime_diff);
    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", manifest.live_gate_path);
    try std.testing.expectEqualStrings("ABI and Runtime Team", manifest.owner);
    try std.testing.expectEqualStrings("ABI and Runtime Team", manifest.rollback_owner);
    try std.testing.expectEqualStrings("8965f1c3cbeaa4411cc5a82b8d1ea15aaf5a03a3", manifest.live_gate_blob_sha);
    try std.testing.expectEqual(@as(usize, 204), manifest.live_gate_line_count);
    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", manifest.runtime_replay_path);
    try std.testing.expectEqualStrings("8965f1c3cbeaa4411cc5a82b8d1ea15aaf5a03a3", manifest.runtime_replay_blob_sha);
    try std.testing.expectEqual(@as(usize, 204), manifest.runtime_replay_line_count);
    try std.testing.expect(manifest.phase4_build_present);
    try std.testing.expect(manifest.phase4_build_uses_atomic64_wrapper);
    try std.testing.expectEqualStrings("86f88d03cd82e2e11ea6ed4a02175b77b472fdb4", manifest.phase4_build_blob_sha);
    try std.testing.expect(manifest.phase4_validator_atomic64_diff_present);
    try std.testing.expect(manifest.phase4_validator_runtime_atomic64_diff_present);
    try std.testing.expectEqualStrings("b03d10e18821c2a239c39906f81943e73f7fb306", manifest.phase4_validator_blob_sha);
    try std.testing.expectEqualStrings("Documentation/zigux/phase4-gate-evidence.md", manifest.phase4_gate_evidence_path);
    try std.testing.expectEqualStrings("c2fb45991974e1768182955b63397ed6549bc8b0", manifest.phase4_gate_evidence_blob_sha);
    try std.testing.expect(manifest.phase9_build_present);
    try std.testing.expectEqualStrings("613dd2d8ad020c72a523c8fb8b2fe51ae65e6bba", manifest.phase9_build_blob_sha);
    try std.testing.expect(manifest.phase4_validation_matrix_atomic64_diff_note_present);
    try std.testing.expect(manifest.phase4_validation_matrix_runtime_atomic64_note_present);
    try std.testing.expectEqualStrings("89da8bf3722b8f0265279181929e9982ad0c59ef", manifest.phase4_validation_matrix_blob_sha);
    try std.testing.expectEqualStrings("8cc12bb18de948b312b47989a813dd3666fcebdd", manifest.phase4_review_checklist_blob_sha);
    try std.testing.expectEqualStrings(
        "threshold_pending_until_runtime_atomic64_scope_widens",
        manifest.threshold_posture,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "gate-evidence surfaces again") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "approved local benchmark commands") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "approved local-only acceptable limits") != null);
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/atomic64_diff.zig") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/runtime_atomic64_diff.zig") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_build.zig") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "scripts/zigux/validate-phase4.py") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "Documentation/zigux/phase4-validation-matrix.md") != null,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "shared CI perf promotion") != null);
}

// runtime replay blob 8965f1c3cbeaa4411cc5a82b8d1ea15aaf5a03a3
// runtime replay blob repeat 8965f1c3cbeaa4411cc5a82b8d1ea15aaf5a03a3
// phase4 build blob 86f88d03cd82e2e11ea6ed4a02175b77b472fdb4
// validator blob b03d10e18821c2a239c39906f81943e73f7fb306
// phase4 gate evidence blob c2fb45991974e1768182955b63397ed6549bc8b0
// phase4 matrix blob 89da8bf3722b8f0265279181929e9982ad0c59ef
// review checklist blob 8cc12bb18de948b312b47989a813dd3666fcebdd
// phase9 build blob 613dd2d8ad020c72a523c8fb8b2fe51ae65e6bba
