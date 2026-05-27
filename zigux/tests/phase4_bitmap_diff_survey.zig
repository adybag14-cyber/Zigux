const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    roadmap_target_path: []const u8,
    roadmap_bitmap_diff_present: bool,
    live_gate_path: []const u8,
    live_gate_blob_sha: []const u8,
    helper_replay_path: []const u8,
    helper_replay_blob_sha: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
    shared_validator_path: []const u8,
    shared_validator_blob_sha: []const u8,
    shared_matrix_path: []const u8,
    shared_matrix_blob_sha: []const u8,
    shared_gate_evidence_path: []const u8,
    gate_evidence_path: []const u8,
    gate_evidence_blob_sha: []const u8,
    phase4_build_present: bool,
    phase4_build_uses_bitmap_diff: bool,
    phase4_build_uses_bitmap_diff_survey: bool,
    phase4_build_blob_sha: []const u8,
    threshold_posture: []const u8,
    roadmap_gap_summary: []const u8,
    reversible_delivery_evidence: []const u8,
    ready_next: []const u8,
};

const manifest_source = @embedFile("phase4_bitmap_diff_manifest.json");
const bitmap_diff_source = @embedFile("bitmap_diff.zig");
const bitmap_live_helper_replay_source = @embedFile("phase4_bitmap_live_helper_replay.zig");
const phase4_build_source = @embedFile("phase4_build.zig");
const validator_source = @embedFile("../../scripts/zigux/validate-phase4.py");
const validation_matrix_source = @embedFile("../../Documentation/zigux/phase4-validation-matrix.md");

fn gitBlobShaHex(source: []const u8) [40]u8 {
    var hasher = std.crypto.hash.Sha1.init(.{});
    hasher.update("blob ");

    var len_buf: [32]u8 = undefined;
    const len_text = std.fmt.bufPrint(&len_buf, "{}", .{source.len}) catch unreachable;
    hasher.update(len_text);
    hasher.update(&[_]u8{0});
    hasher.update(source);

    var digest: [20]u8 = undefined;
    hasher.final(&digest);
    return std.fmt.bytesToHex(digest, .lower);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 4 bitmap survey keeps the roadmap rollback gate and helper replay measurable" {
    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_source, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P4-L10", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("zigux/tests/bitmap_diff.zig", manifest.roadmap_target_path);
    try std.testing.expect(manifest.roadmap_bitmap_diff_present);
    try std.testing.expectEqualStrings("zigux/tests/bitmap_diff.zig", manifest.live_gate_path);
    try std.testing.expectEqualStrings("7b802d3d710426c6369e73dbdeee568a8c045221", manifest.live_gate_blob_sha);
    try std.testing.expectEqualStrings("zigux/tests/phase4_bitmap_live_helper_replay.zig", manifest.helper_replay_path);
    try std.testing.expectEqualStrings("375f7f5ac9dfecee48500cf52a4edbcd7cd02e2f", manifest.helper_replay_blob_sha);
    try std.testing.expectEqualStrings("Shared Subsystems Pod", manifest.owner);
    try std.testing.expectEqualStrings("Shared Subsystems Pod", manifest.rollback_owner);
    try std.testing.expectEqualStrings("scripts/zigux/validate-phase4.py", manifest.shared_validator_path);
    try std.testing.expectEqualStrings("e0240439445ea311a49f0d832398806d1bd49cbc", manifest.shared_validator_blob_sha);
    try std.testing.expectEqualStrings("Documentation/zigux/phase4-validation-matrix.md", manifest.shared_matrix_path);
    try std.testing.expectEqualStrings("348984ebc5a7ac85433a11f87396117059eb34f1", manifest.shared_matrix_blob_sha);
    try std.testing.expectEqualStrings("Documentation/zigux/phase4-gate-evidence.md", manifest.shared_gate_evidence_path);
    try std.testing.expectEqualStrings("Documentation/zigux/phase4-gate-evidence.md", manifest.gate_evidence_path);
    try std.testing.expect(manifest.phase4_build_present);
    try std.testing.expect(manifest.phase4_build_uses_bitmap_diff);
    try std.testing.expect(manifest.phase4_build_uses_bitmap_diff_survey);
    try std.testing.expectEqualStrings(
        "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        manifest.threshold_posture,
    );

    try std.testing.expectEqualStrings(&gitBlobShaHex(bitmap_diff_source), manifest.live_gate_blob_sha);
    try std.testing.expectEqualStrings(
        &gitBlobShaHex(bitmap_live_helper_replay_source),
        manifest.helper_replay_blob_sha,
    );
    try std.testing.expectEqualStrings(&gitBlobShaHex(validator_source), manifest.shared_validator_blob_sha);
    try std.testing.expectEqualStrings(&gitBlobShaHex(validation_matrix_source), manifest.shared_matrix_blob_sha);
}

test "phase 4 bitmap survey keeps the shared build route explicit" {
    try expectContains(phase4_build_source, ".root_source_file = b.path(\"bitmap_diff.zig\")");
    try expectContains(phase4_build_source, ".root_source_file = b.path(\"phase4_bitmap_diff_survey.zig\")");
    try expectContains(
        phase4_build_source,
        ".root_source_file = b.path(\"phase4_bitmap_live_helper_replay.zig\")",
    );
    try expectContains(phase4_build_source, ".name = \"phase4-bitmap-diff-tests\"");
    try expectContains(phase4_build_source, ".name = \"phase4-bitmap-diff-survey-tests\"");
    try expectContains(phase4_build_source, ".name = \"phase4-bitmap-live-helper-replay-tests\"");
    try expectContains(phase4_build_source, "\"phase4-bitmap-diff\"");
    try expectContains(phase4_build_source, "\"phase4-bitmap-diff-survey\"");
    try expectContains(phase4_build_source, "\"phase4-bitmap-live-helper-replay\"");
}

test "phase 4 bitmap survey keeps the helper-backed rollback replay explicit" {
    try expectContains(
        bitmap_live_helper_replay_source,
        "test \"phase4 bitmap live helper replay keeps fill exact and zero rounded\" {",
    );
    try expectContains(
        bitmap_live_helper_replay_source,
        "try std.testing.expectEqual(@as(usize, 35), bitmap.firstZero());",
    );
    try expectContains(
        bitmap_live_helper_replay_source,
        "try std.testing.expectEqual(@as(usize, 115), bitmap.firstZero());",
    );
    try expectContains(
        bitmap_live_helper_replay_source,
        "test \"phase4 bitmap live helper replay keeps copy-tail rollback explicit\" {",
    );
}
