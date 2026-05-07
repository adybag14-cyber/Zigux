const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    roadmap_target_path: []const u8,
    roadmap_atomic64_diff_present: bool,
    roadmap_atomic64_wrapper_targets_runtime_diff: bool,
    live_gate_path: []const u8,
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

test "phase 4 atomic64 survey keeps wrapper handoff and remaining shared drift explicit" {
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
    try std.testing.expectEqualStrings("d3c082339d3357d7f4ed458313966705a7a9c409", manifest.live_gate_blob_sha);
    try std.testing.expectEqual(@as(usize, 204), manifest.live_gate_line_count);

    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", manifest.runtime_replay_path);
    try std.testing.expectEqualStrings("d3c082339d3357d7f4ed458313966705a7a9c409", manifest.runtime_replay_blob_sha);
    try std.testing.expectEqual(@as(usize, 204), manifest.runtime_replay_line_count);

    try std.testing.expect(manifest.phase4_build_present);
    try std.testing.expect(manifest.phase4_build_uses_atomic64_wrapper);
    try std.testing.expectEqualStrings("3164f1e56835ae0f0511d890f150dc374b45d1f4", manifest.phase4_build_blob_sha);

    try std.testing.expect(manifest.phase4_validator_atomic64_diff_present);
    try std.testing.expect(manifest.phase4_validator_runtime_atomic64_diff_present);
    try std.testing.expectEqualStrings("60dd5759e0c149f70802e4474b2e22513ceabcab", manifest.phase4_validator_blob_sha);

    try std.testing.expect(manifest.phase9_build_present);
    try std.testing.expectEqualStrings("ca1c72f01108e57b4fc118aeed6b5a33a5ce54ea", manifest.phase9_build_blob_sha);

    try std.testing.expect(manifest.phase4_validation_matrix_atomic64_diff_note_present);
    try std.testing.expect(manifest.phase4_validation_matrix_runtime_atomic64_note_present);
    try std.testing.expectEqualStrings("f14c9826dfb5b9271b0dd085edec23a36209a4ff", manifest.phase4_validation_matrix_blob_sha);
    try std.testing.expectEqualStrings("e1def97f99abd39d47b9b2fd35ea8c833b4d13c3", manifest.phase4_review_checklist_blob_sha);
    try std.testing.expectEqualStrings(
        "threshold_pending_until_runtime_atomic64_scope_widens",
        manifest.threshold_posture,
    );

    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "zigux/tests/atomic64_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "zigux/tests/phase4_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "zigux/tests/runtime_atomic64_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "single bounded replay body") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "Phase 9") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "Phase 4 reviewer packet") != null);

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
        std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "Documentation/zigux/review-checklist.md") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "Documentation/zigux/phase4-validation-matrix.md") != null,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "validator-first bootstrap replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "shared reviewer checklist") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "rollback-owner matrix") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "measurable and reversible") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "zigux/tests/atomic64_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "zigux/tests/runtime_atomic64_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "zigux/tests/phase4_build.zig") != null);
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.ready_next, "zigux/tests/phase4_runtime_atomic64_diff_survey.zig") != null,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "scripts/zigux/validate-phase4.py") != null);
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.ready_next, "Documentation/zigux/review-checklist.md") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.ready_next, "Documentation/zigux/phase4-validation-matrix.md") != null,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "wrapper-first rollback surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "reviewer checklist remain reviewable") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "Phase 9 handoff") != null);
}
