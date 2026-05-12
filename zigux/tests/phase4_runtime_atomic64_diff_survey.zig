const std = @import("std");
const phase4_build_source = @embedFile("phase4_build.zig");
const phase9_build_source = @embedFile("phase9_build.zig");

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

fn readRepoFile(allocator: std.mem.Allocator, repo_root_relative_path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        repo_root_relative_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn gitBlobShaHex(source: []const u8) ![40]u8 {
    var header_buf: [64]u8 = undefined;
    const header = try std.fmt.bufPrint(&header_buf, "blob {}\x00", .{source.len});

    var hasher = std.crypto.hash.Sha1.init(.{});
    hasher.update(header);
    hasher.update(source);

    var digest: [20]u8 = undefined;
    hasher.final(&digest);

    var out: [40]u8 = undefined;
    const alphabet = "0123456789abcdef";
    for (digest, 0..) |byte, index| {
        out[index * 2] = alphabet[byte >> 4];
        out[index * 2 + 1] = alphabet[byte & 0x0f];
    }
    return out;
}

fn expectBlobShaMatchesSource(blob_sha: []const u8, source: []const u8) !void {
    const computed = try gitBlobShaHex(source);
    try std.testing.expectEqualStrings(computed[0..], blob_sha);
}

fn expectMarker(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
}

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
    try expectBlobShaMatchesSource(manifest.phase4_build_blob_sha, phase4_build_source);
    try std.testing.expect(manifest.phase4_validator_atomic64_diff_present);
    try std.testing.expect(manifest.phase4_validator_runtime_atomic64_diff_present);
    const validate_phase4_source = try readRepoFile(
        std.testing.allocator,
        "scripts/zigux/validate-phase4.py",
    );
    defer std.testing.allocator.free(validate_phase4_source);
    try expectBlobShaMatchesSource(manifest.phase4_validator_blob_sha, validate_phase4_source);
    try std.testing.expectEqualStrings("Documentation/zigux/phase4-gate-evidence.md", manifest.phase4_gate_evidence_path);
    try std.testing.expect(manifest.phase9_build_present);
    try std.testing.expectEqualStrings("7f855cce2b91c156d5c0373b3b0fa096eab0aeda", manifest.phase9_build_blob_sha);
    try expectBlobShaMatchesSource(manifest.phase9_build_blob_sha, phase9_build_source);
    try std.testing.expect(manifest.phase4_validation_matrix_atomic64_diff_note_present);
    try std.testing.expect(manifest.phase4_validation_matrix_runtime_atomic64_note_present);
    const phase4_validation_matrix_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/phase4-validation-matrix.md",
    );
    defer std.testing.allocator.free(phase4_validation_matrix_source);
    try expectBlobShaMatchesSource(
        manifest.phase4_validation_matrix_blob_sha,
        phase4_validation_matrix_source,
    );
    const review_checklist_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/review-checklist.md",
    );
    defer std.testing.allocator.free(review_checklist_source);
    try expectBlobShaMatchesSource(manifest.phase4_review_checklist_blob_sha, review_checklist_source);
    try std.testing.expectEqualStrings(
        "threshold_pending_until_runtime_atomic64_scope_widens",
        manifest.threshold_posture,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "gate-evidence surfaces again") != null);
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.roadmap_gap_summary, "self-referential gate-evidence blob pin") != null,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "approved local benchmark commands") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "approved local-only acceptable limits") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/atomic64_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/runtime_atomic64_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/phase4_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "scripts/zigux/validate-phase4.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "Documentation/zigux/phase4-validation-matrix.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "Documentation/zigux/phase4-gate-evidence.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "benchmark command") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "acceptable limit") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "shared CI perf promotion") != null);
}

test "phase 4 atomic64 survey keeps the current roadmap gap summary reviewable" {
    const parsed = try std.json.parseFromSlice(
        Manifest,
        std.testing.allocator,
        @embedFile("phase4_runtime_atomic64_diff_manifest.json"),
        .{},
    );
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "gate-evidence surfaces again") != null);
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.roadmap_gap_summary, "self-referential gate-evidence blob pin") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.roadmap_gap_summary, "approved local benchmark commands") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.roadmap_gap_summary, "approved local-only acceptable limits") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.roadmap_gap_summary, "broader sample follow-ups remain intentionally open") != null,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "shared CI perf promotion") != null);
}

test "phase 4 atomic64 survey keeps reversible delivery and next-step evidence explicit" {
    const parsed = try std.json.parseFromSlice(
        Manifest,
        std.testing.allocator,
        @embedFile("phase4_runtime_atomic64_diff_manifest.json"),
        .{},
    );
    defer parsed.deinit();
    const manifest = parsed.value;

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

    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "benchmark command") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "acceptable limit") != null);
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.ready_next, "Documentation/zigux/phase4-validation-matrix.md") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.ready_next, "Documentation/zigux/phase4-gate-evidence.md") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.ready_next, "zigux/tests/phase4_perf_baseline_manifest.json") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.ready_next, "zigux/tests/phase4_perf_baseline_survey.zig") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.ready_next, "correctness-only replay routes") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.ready_next, "shared CI perf promotion") != null,
    );
}

test "phase 4 atomic64 survey keeps the gate-evidence wrapper blob pin aligned with the live wrapper" {
    const gate_evidence_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/phase4-gate-evidence.md",
    );
    defer std.testing.allocator.free(gate_evidence_source);

    const wrapper_source = try readRepoFile(
        std.testing.allocator,
        "zigux/tests/atomic64_diff.zig",
    );
    defer std.testing.allocator.free(wrapper_source);

    const wrapper_blob_sha = try gitBlobShaHex(wrapper_source);
    const marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE4_ATOMIC64_DIFF_BLOB_SHA={s}",
        .{wrapper_blob_sha},
    );
    defer std.testing.allocator.free(marker);

    try expectMarker(gate_evidence_source, marker);
}

// runtime replay blob 8965f1c3cbeaa4411cc5a82b8d1ea15aaf5a03a3
// runtime replay blob repeat 8965f1c3cbeaa4411cc5a82b8d1ea15aaf5a03a3
// phase4 build blob 86f88d03cd82e2e11ea6ed4a02175b77b472fdb4
// validator blob f502faede8b3c03b59314175b979412b0d88a005
// phase4 matrix blob 5ba1599569548585203e7d94fcec188b06eec210
// review checklist blob 1ec1d3f4f98c4ed1fa324af1c0e6d26489320fa4
// phase9 build blob 7f855cce2b91c156d5c0373b3b0fa096eab0aeda
