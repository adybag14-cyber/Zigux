const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    roadmap_target_path: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
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
    phase4_gate_evidence_path: []const u8,
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

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn readRepoFile(allocator: std.mem.Allocator, repo_root_relative_path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        repo_root_relative_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectAtomic64MatrixMarkerCount(marker: []const u8, expected_count: usize) !void {
    const phase4_validation_matrix_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/phase4-validation-matrix.md",
    );
    defer std.testing.allocator.free(phase4_validation_matrix_source);
    const section_start = std.mem.indexOf(
        u8,
        phase4_validation_matrix_source,
        "### `zigux/tests/atomic64_diff.zig`",
    ) orelse return error.MissingAtomic64MatrixSection;
    const section_end = std.mem.indexOfPos(
        u8,
        phase4_validation_matrix_source,
        section_start,
        "### `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`",
    ) orelse return error.MissingAtomic64MatrixSectionBoundary;
    const section = phase4_validation_matrix_source[section_start..section_end];
    try std.testing.expectEqual(expected_count, countOccurrences(section, marker));
}

test "phase 4 atomic64 survey keeps wrapper handoff, owner map, and sibling blob pins explicit" {
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
    try std.testing.expectEqualStrings("ABI and Runtime Team", manifest.owner);
    try std.testing.expectEqualStrings("ABI and Runtime Team", manifest.rollback_owner);

    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", manifest.live_gate_path);
    try std.testing.expectEqualStrings("8965f1c3cbeaa4411cc5a82b8d1ea15aaf5a03a3", manifest.live_gate_blob_sha);
    try std.testing.expectEqual(@as(usize, 204), manifest.live_gate_line_count);

    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", manifest.runtime_replay_path);
    try std.testing.expectEqualStrings("8965f1c3cbeaa4411cc5a82b8d1ea15aaf5a03a3", manifest.runtime_replay_blob_sha);
    try std.testing.expectEqual(@as(usize, 204), manifest.runtime_replay_line_count);

    try std.testing.expect(manifest.phase4_build_present);
    try std.testing.expect(manifest.phase4_build_uses_atomic64_wrapper);
    try std.testing.expectEqualStrings("9944a72ef3d53ff098dd44ea9c8a905d7f212db3", manifest.phase4_build_blob_sha);

    try std.testing.expect(manifest.phase4_validator_atomic64_diff_present);
    try std.testing.expect(manifest.phase4_validator_runtime_atomic64_diff_present);
    try std.testing.expectEqualStrings("4b3798851901ab60ffbe8e7576bdba2988fd5346", manifest.phase4_validator_blob_sha);
    try std.testing.expectEqualStrings(
        "Documentation/zigux/phase4-gate-evidence.md",
        manifest.phase4_gate_evidence_path,
    );

    try std.testing.expect(manifest.phase9_build_present);
    try std.testing.expectEqualStrings("8f6ce92cfaff8eb1225686b5474ec91e7c76dd3f", manifest.phase9_build_blob_sha);

    try std.testing.expect(manifest.phase4_validation_matrix_atomic64_diff_note_present);
    try std.testing.expect(manifest.phase4_validation_matrix_runtime_atomic64_note_present);
    try std.testing.expectEqualStrings("ac4b1297b4ddc9c1947f308bda7335315d402a72", manifest.phase4_validation_matrix_blob_sha);
    try std.testing.expectEqualStrings("a64c4400f26216b266c5733fdf0b8bbd205a4b5b", manifest.phase4_review_checklist_blob_sha);
    try std.testing.expectEqualStrings(
        "threshold_pending_until_runtime_atomic64_scope_widens",
        manifest.threshold_posture,
    );

    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "zigux/tests/atomic64_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "zigux/tests/phase4_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "zigux/tests/runtime_atomic64_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "single bounded replay body") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "Phase 9") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "same current named owner, rollback owner, matrix, validator, and review-checklist surfaces again") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "zigux/tests/phase4_perf_baseline_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "zigux/tests/phase4_perf_baseline_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "still-unapproved benchmark-command and acceptable-limit posture measurable") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "next atomic64-only perf promotion") != null);

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
        std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "Documentation/zigux/phase4-gate-evidence.md") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "Documentation/zigux/review-checklist.md") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "Documentation/zigux/phase4-validation-matrix.md") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_perf_baseline_manifest.json") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_perf_baseline_survey.zig") != null,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "validator-first bootstrap replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "exact-readback note") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "shared reviewer checklist") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "named owner") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "rollback-owner matrix") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "local-only perf-baseline survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "measurable and reversible") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "same rollback packet pinned") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "benchmark command") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "acceptable limit") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "Documentation/zigux/phase4-validation-matrix.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "Documentation/zigux/phase4-gate-evidence.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "zigux/tests/phase4_perf_baseline_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "zigux/tests/phase4_perf_baseline_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "atomic64 handoff packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "correctness-only replay routes") != null);
}

test "phase 4 atomic64 survey keeps roadmap rollback ownership and replay routes explicit" {
    try expectAtomic64MatrixMarkerCount("- owner: `ABI and Runtime Team`", 1);
    try expectAtomic64MatrixMarkerCount("- rollback owner: `ABI and Runtime Team`", 1);
    try expectAtomic64MatrixMarkerCount(
        "`python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml`",
        1,
    );
    try expectAtomic64MatrixMarkerCount(
        "`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig`",
        1,
    );
    try expectAtomic64MatrixMarkerCount(
        "- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded exchange, cmpxchg, add_unless, bitwise, and selftest-family replay set",
        1,
    );
}
