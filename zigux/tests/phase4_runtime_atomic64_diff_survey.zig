const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    roadmap_target_path: []const u8,
    roadmap_atomic64_diff_present: bool,
    live_gate_path: []const u8,
    live_gate_blob_sha: []const u8,
    live_gate_line_count: usize,
    phase4_build_present: bool,
    phase4_build_blob_sha: []const u8,
    phase4_validator_runtime_atomic64_diff_present: bool,
    phase4_validator_blob_sha: []const u8,
    phase9_build_present: bool,
    phase9_build_blob_sha: []const u8,
    phase4_validation_matrix_runtime_atomic64_note_present: bool,
    phase4_validation_matrix_blob_sha: []const u8,
    threshold_posture: []const u8,
    roadmap_gap_summary: []const u8,
    ready_next: []const u8,
};

test "phase 4 runtime atomic64 roadmap-gap survey keeps the shipped wrapper and runtime split explicit" {
    const parsed = try std.json.parseFromSlice(
        Manifest,
        std.testing.allocator,
        @embedFile("phase4_runtime_atomic64_diff_manifest.json"),
        .{},
    );
    defer parsed.deinit();

    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P4-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("zigux/tests/atomic64_diff.zig", manifest.roadmap_target_path);
    try std.testing.expect(manifest.roadmap_atomic64_diff_present);
    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", manifest.live_gate_path);
    try std.testing.expectEqualStrings("d65abeb53eb0248e1f0978a54cc48a7f561b148e", manifest.live_gate_blob_sha);
    try std.testing.expectEqual(@as(usize, 155), manifest.live_gate_line_count);

    try std.testing.expect(manifest.phase4_build_present);
    try std.testing.expectEqualStrings("b1ff06326c59dfe6190663a378b6cb60d64f457f", manifest.phase4_build_blob_sha);
    try std.testing.expect(manifest.phase4_validator_runtime_atomic64_diff_present);
    try std.testing.expectEqualStrings("4ac6d7657e43bb1ec9f9950c2ad5eb72573d568f", manifest.phase4_validator_blob_sha);
    try std.testing.expect(manifest.phase9_build_present);
    try std.testing.expectEqualStrings("8ecef19acf5953dce1bd9c59a9662e23c0da1f60", manifest.phase9_build_blob_sha);
    try std.testing.expect(manifest.phase4_validation_matrix_runtime_atomic64_note_present);
    try std.testing.expectEqualStrings("e2f0331f7e27d5d3a5d918b73c442eb8bda3e9bd", manifest.phase4_validation_matrix_blob_sha);
    try std.testing.expectEqualStrings(
        "threshold_pending_until_runtime_atomic64_scope_widens",
        manifest.threshold_posture,
    );

    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "zigux/tests/atomic64_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "Phase 4 build entrypoint") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "zigux/tests/runtime_atomic64_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "Phase 9 build") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "shared validator") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "Phase 4 notes") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "single bounded replay body") != null);
}
