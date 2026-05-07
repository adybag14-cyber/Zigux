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
    shared_matrix_path: []const u8,
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
const gate_evidence_source = @embedFile("../../Documentation/zigux/phase4-gate-evidence.md");

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

    try std.testing.expectEqualStrings("P4-L07", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("zigux/tests/bitmap_diff.zig", manifest.roadmap_target_path);
    try std.testing.expect(manifest.roadmap_bitmap_diff_present);
    try std.testing.expectEqualStrings("zigux/tests/bitmap_diff.zig", manifest.live_gate_path);
    try std.testing.expectEqualStrings("zigux/tests/phase4_bitmap_live_helper_replay.zig", manifest.helper_replay_path);
    try std.testing.expectEqualStrings("Documentation/zigux/phase4-gate-evidence.md", manifest.gate_evidence_path);
    try std.testing.expectEqualStrings("threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks", manifest.threshold_posture);
    try std.testing.expect(manifest.phase4_build_present);
    try std.testing.expect(manifest.phase4_build_uses_bitmap_diff);
    try std.testing.expect(manifest.phase4_build_uses_bitmap_diff_survey);

    try std.testing.expectEqualStrings("825823b724a96c6d4fcca97071ddad8202686587", manifest.live_gate_blob_sha);
    try std.testing.expectEqualStrings("24418ad890696a59b95276fe8dec7eaeecf25172", manifest.helper_replay_blob_sha);
    try std.testing.expectEqualStrings("430276285cc2802b8daba429239dc1816e04defa", manifest.gate_evidence_blob_sha);
    try std.testing.expectEqualStrings("3164f1e56835ae0f0511d890f150dc374b45d1f4", manifest.phase4_build_blob_sha);

    try std.testing.expectEqualStrings(&gitBlobShaHex(bitmap_diff_source), manifest.live_gate_blob_sha);
    try std.testing.expectEqualStrings(&gitBlobShaHex(bitmap_live_helper_replay_source), manifest.helper_replay_blob_sha);
    try std.testing.expectEqualStrings(&gitBlobShaHex(gate_evidence_source), manifest.gate_evidence_blob_sha);
    try std.testing.expectEqualStrings(&gitBlobShaHex(phase4_build_source), manifest.phase4_build_blob_sha);

    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "zigux/tests/bitmap_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "shared Phase 4 gate-evidence note") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "phase4_build.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/bitmap_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_bitmap_live_helper_replay.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "Documentation/zigux/phase4-gate-evidence.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_bitmap_diff_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_bitmap_diff_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "measurable and reversible") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "scripts/zigux/validate-phase4.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "Documentation/zigux/phase4-validation-matrix.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "samples or perf-threshold approval") != null);
}

test "phase 4 bitmap survey keeps the shared build route explicit" {
    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, ".root_source_file = b.path(\"bitmap_diff.zig\")") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, ".root_source_file = b.path(\"phase4_bitmap_diff_survey.zig\")") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, ".name = \"phase4-bitmap-diff-tests\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, ".name = \"phase4-bitmap-diff-survey-tests\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, "\"phase4-bitmap-diff\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, "\"phase4-bitmap-diff-survey\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, "manifest-backed Phase 4 bitmap rollback survey") != null);
}

test "phase 4 bitmap survey keeps bitmap gate-evidence coverage explicit" {
    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_source, .{});
    defer parsed.deinit();

    _ = parsed.value;

    try expectContains(gate_evidence_source, "PHASE4_BITMAP_DIFF_BLOB_SHA=");
    try expectContains(gate_evidence_source, "PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=");
    try expectContains(gate_evidence_source, "zigux/tests/bitmap_diff.zig");
    try expectContains(gate_evidence_source, "zigux/tests/phase4_bitmap_live_helper_replay.zig");
    try expectContains(
        gate_evidence_source,
        "zig build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig",
    );
    try expectContains(gate_evidence_source, "make -C zigux phase4-bitmap-live-helper-replay");
    try expectContains(
        gate_evidence_source,
        "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
    );
    try expectContains(gate_evidence_source, "5216946504564592253");
    try expectContains(gate_evidence_source, "7942141539243507472");
    try expectContains(gate_evidence_source, "final_first_zero=109");
    try expectContains(gate_evidence_source, "final_weight=1005");
    try expectContains(gate_evidence_source, "final_nth_seven=123");
}

test "phase 4 bitmap survey keeps owner and rollback owner governance explicit" {
    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_source, .{});
    defer parsed.deinit();

    const manifest = parsed.value;

    try std.testing.expectEqualStrings("Shared Subsystems Pod", manifest.owner);
    try std.testing.expectEqualStrings("Shared Subsystems Pod", manifest.rollback_owner);
    try std.testing.expectEqualStrings("scripts/zigux/validate-phase4.py", manifest.shared_validator_path);
    try std.testing.expectEqualStrings("Documentation/zigux/phase4-validation-matrix.md", manifest.shared_matrix_path);
    try std.testing.expectEqualStrings("Documentation/zigux/phase4-gate-evidence.md", manifest.shared_gate_evidence_path);

    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "Shared Subsystems Pod owner plus rollback owner metadata") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "Shared Subsystems Pod owner plus rollback owner metadata") != null);
}
