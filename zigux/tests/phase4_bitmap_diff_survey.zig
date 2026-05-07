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
    try std.testing.expectEqualStrings("threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks", manifest.threshold_posture);
    try std.testing.expect(manifest.phase4_build_present);
    try std.testing.expect(manifest.phase4_build_uses_bitmap_diff);
    try std.testing.expect(manifest.phase4_build_uses_bitmap_diff_survey);

    try std.testing.expectEqualStrings("825823b724a96c6d4fcca97071ddad8202686587", manifest.live_gate_blob_sha);
    try std.testing.expectEqualStrings("24418ad890696a59b95276fe8dec7eaeecf25172", manifest.helper_replay_blob_sha);
    try std.testing.expectEqualStrings("3164f1e56835ae0f0511d890f150dc374b45d1f4", manifest.phase4_build_blob_sha);

    try std.testing.expectEqualStrings(&gitBlobShaHex(bitmap_diff_source), manifest.live_gate_blob_sha);
    try std.testing.expectEqualStrings(&gitBlobShaHex(bitmap_live_helper_replay_source), manifest.helper_replay_blob_sha);
    try std.testing.expectEqualStrings(&gitBlobShaHex(phase4_build_source), manifest.phase4_build_blob_sha);

    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "zigux/tests/bitmap_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "manifest-backed survey packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "phase4_build.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/bitmap_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_bitmap_live_helper_replay.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_bitmap_diff_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_bitmap_diff_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "measurable and reversible") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "zigux/tests/phase4_bitmap_diff_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "zigux/tests/phase4_bitmap_diff_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "shared Phase 4 validator") != null);
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
