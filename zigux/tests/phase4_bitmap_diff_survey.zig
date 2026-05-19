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

    try std.testing.expectEqualStrings("P4-L10", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);

    try std.testing.expectEqualStrings("zigux/tests/bitmap_diff.zig", manifest.roadmap_target_path);

    try std.testing.expect(manifest.roadmap_bitmap_diff_present);

    try std.testing.expectEqualStrings("zigux/tests/bitmap_diff.zig", manifest.live_gate_path);

    try std.testing.expectEqualStrings("zigux/tests/phase4_bitmap_live_helper_replay.zig", manifest.helper_replay_path);
    try std.testing.expectEqualStrings("Documentation/zigux/phase4-gate-evidence.md", manifest.gate_evidence_path);

    try std.testing.expectEqualStrings(
        "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        manifest.threshold_posture,
    );

    try std.testing.expect(manifest.phase4_build_present);

    try std.testing.expect(manifest.phase4_build_uses_bitmap_diff);

    try std.testing.expect(manifest.phase4_build_uses_bitmap_diff_survey);
    try std.testing.expectEqualStrings("683160d3a86552a2a1be34b445fd6e0fb38dc122", manifest.live_gate_blob_sha);

    try std.testing.expectEqualStrings("4a4c07e5f7b90fc96f06c86a17d3d30aa0d5b694", manifest.helper_replay_blob_sha);

    try std.testing.expectEqualStrings("4255a28c318c180b2772caf2211e16a91a0c8032", manifest.gate_evidence_blob_sha);

    try std.testing.expectEqualStrings("86f88d03cd82e2e11ea6ed4a02175b77b472fdb4", manifest.phase4_build_blob_sha);
    try std.testing.expectEqualStrings(&gitBlobShaHex(bitmap_diff_source), manifest.live_gate_blob_sha);

    try std.testing.expectEqualStrings(&gitBlobShaHex(bitmap_live_helper_replay_source), manifest.helper_replay_blob_sha);

    try std.testing.expectEqualStrings(&gitBlobShaHex(gate_evidence_source), manifest.gate_evidence_blob_sha);

    try std.testing.expectEqualStrings(&gitBlobShaHex(phase4_build_source), manifest.phase4_build_blob_sha);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "zigux/tests/bitmap_diff.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "exact synthetic bitmap_fill prefixes at 35 and 115 bits") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "lib/test_bitmap.c") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "64 and 128") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "Shared Subsystems Pod") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "same-lane roadmap-visible maintenance work") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/bitmap_diff.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_bitmap_live_helper_replay.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "Documentation/zigux/phase4-gate-evidence.md") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_bitmap_diff_manifest.json") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_bitmap_diff_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_build.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "measurable and reversible") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "park this lane unless") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "35-bit and 115-bit synthetic fill prefixes") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "rounded 64-bit and 128-bit zero boundaries") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "blob pins") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "shared build route drift again") != null);
}

test "phase 4 bitmap survey keeps the shared build route explicit" {
    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, ".root_source_file = b.path(\"bitmap_diff.zig\")") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, ".root_source_file = b.path(\"phase4_bitmap_diff_survey.zig\")") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, ".root_source_file = b.path(\"phase4_bitmap_live_helper_replay.zig\")") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, ".name = \"phase4-bitmap-diff-tests\"") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, ".name = \"phase4-bitmap-diff-survey-tests\"") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, ".name = \"phase4-bitmap-live-helper-replay-tests\"") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, "\"phase4-bitmap-diff\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, "\"phase4-bitmap-diff-survey\"") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, "\"phase4-bitmap-live-helper-replay\"") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, "manifest-backed Phase 4 bitmap rollback survey") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, "test_step.dependOn(&run_bitmap_live_helper_replay_tests.step);") != null);
}

test "phase 4 bitmap survey keeps the broader gate-evidence handoff explicit" {
    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_source, .{});

    defer parsed.deinit();

    _ = parsed.value;

    try expectContains(gate_evidence_source, "PHASE4_BITMAP_DIFF_BLOB_SHA=683160d3a86552a2a1be34b445fd6e0fb38dc122");

    try expectContains(gate_evidence_source, "PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA=4a4c07e5f7b90fc96f06c86a17d3d30aa0d5b694");

    try expectContains(gate_evidence_source, "PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19");

    try expectContains(gate_evidence_source, "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=42");

    try expectContains(gate_evidence_source, "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19");

    try expectContains(gate_evidence_source, "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=42");

    try expectContains(gate_evidence_source, "Documentation/zigux/phase4-reversible-delivery-evidence.md");

    try expectContains(gate_evidence_source, "scripts/zigux/check-phase4-gate-evidence.py");

    try expectContains(gate_evidence_source, "scripts/zigux/check-phase4-perf-baseline-packet.py");

    try expectContains(gate_evidence_source, "scripts/zigux/check-phase4-workflow-route-counts.py");

    try expectContains(gate_evidence_source, "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig");

    try expectContains(gate_evidence_source, "make -C zigux phase4-perf-baseline-survey");

    try expectContains(
        gate_evidence_source,
        "PHASE4_KPROBE_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
    );

    try expectContains(gate_evidence_source, "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m");

    try expectContains(gate_evidence_source, "make -C zigux phase4-kprobe-example-survey");
}

test "phase 4 bitmap survey keeps current exact-fill divergence explicit" {
    try expectContains(bitmap_diff_source, "test_fill_set bitmap_fill keeps the exact 35-bit prefix");
    try expectContains(bitmap_diff_source, "test_fill_set bitmap_fill keeps the exact 115-bit prefix");

    try expectContains(bitmap_diff_source, "try expectNthCase(&starter_bits, 123, starter_bits[0..7]);");

    try expectContains(bitmap_live_helper_replay_source, "phase4 bitmap live helper replay keeps fill exact and zero rounded");

    try expectContains(bitmap_live_helper_replay_source, "try std.testing.expectEqual(@as(usize, 35), bitmap.firstZero());");
    try expectContains(bitmap_live_helper_replay_source, "try std.testing.expectEqual(@as(usize, 115), bitmap.firstZero());");
}

test "phase 4 bitmap survey keeps zero-length and copy-alignment rollback checks explicit" {
    try expectContains(bitmap_diff_source, "test_zero_nbits zero-length range and prefix edits leave seeded bits unchanged");

    try expectContains(bitmap_diff_source, "test_zero_nbits zero-length copy leaves destination unchanged");
    try expectContains(bitmap_diff_source, "test_copy exact 23-bit replay from a cleared destination");

    try expectContains(bitmap_diff_source, "test_copy exact 23-bit replay clears the stale tail in the destination word");

    try expectContains(
        bitmap_diff_source,
        "test_copy exact 23-bit replay clears the first-word tail without dropping later filled words",
    );

    try expectContains(bitmap_diff_source, "test_copy exact word-aligned replay from a cleared destination");

    try expectContains(
        bitmap_diff_source,
        "test_copy exact word-aligned replay clears the first-word tail and leaves later filled words untouched",
    );

    try expectContains(bitmap_diff_source, "test_copy partial-word 109-bit replay keeps copied source tail bits through bit 126");

    try expectContains(
        bitmap_diff_source,
        "test_copy partial-word 109-bit replay clears the padded tail before the filled tail resumes",
    );

    try expectContains(
        bitmap_diff_source,
        "test_copy aligned 97-bit replay keeps the full second word before the filled tail resumes",
    );

    try expectContains(bitmap_diff_source, "test \"bitmap diff gate rejects out-of-bounds bitmap operations\" {");

    try expectContains(
        bitmap_diff_source,
        "try std.testing.expectError(error.BitRangeOutOfBounds, bitmap.findNthSet(BitmapHarness.bitmap_nbits + 1, 0));",
    );
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

    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "same-lane roadmap-visible maintenance work") != null);

    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "35-bit and 115-bit synthetic fill prefixes") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "rounded 64-bit and 128-bit zero boundaries") != null);
}
