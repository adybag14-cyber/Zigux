const std = @import("std");
const phase4_build_source = @embedFile("phase4_build.zig");
const phase9_build_source = @embedFile("phase9_build.zig");
const runtime_atomic64_diff_source = @embedFile("runtime_atomic64_diff.zig");
const phase4_runtime_atomic64_manifest_source = @embedFile("phase4_runtime_atomic64_diff_manifest.json");

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

const phase4_gate_evidence_self_test_cases_line =
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift," ++
    "missing_exact_readback_heading,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift," ++
    "phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift," ++
    "doc_readme_blob_pin_drift,script_readme_blob_pin_drift,tests_readme_blob_pin_drift," ++
    "gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift," ++
    "shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift," ++
    "shared_validator_expected_self_test_case_count_drift,runtime_atomic64_survey_packet_presence_drift," ++
    "bitmap_diff_survey_replay_marker_drift,kprobe_gap_packet_presence_drift,kprobe_owner_drift," ++
    "kprobe_validation_entrypoint_drift,kprobe_next_step_drift,perf_baseline_packet_presence_drift," ++
    "perf_baseline_note_split_marker_drift,perf_baseline_owner_drift," ++
    "perf_baseline_shared_promotion_status_drift,test_fsmount_gap_packet_presence_drift," ++
    "test_fsmount_threshold_posture_drift,test_fsmount_owner_drift,test_fsmount_validation_entrypoint_drift," ++
    "test_fsmount_linux_style_wrapper_drift,test_fsmount_next_step_drift,missing_note_file";

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

fn sourceLineCount(source: []const u8) usize {
    if (source.len == 0) return 0;

    var count: usize = std.mem.count(u8, source, "\n");
    if (source[source.len - 1] != '\n') count += 1;
    return count;
}

fn expectBlobShaMatchesSource(blob_sha: []const u8, source: []const u8) !void {
    const computed = try gitBlobShaHex(source);
    try std.testing.expectEqualStrings(computed[0..], blob_sha);
}

fn expectMarker(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
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
    try expectBlobShaMatchesSource(manifest.live_gate_blob_sha, runtime_atomic64_diff_source);
    try std.testing.expectEqual(sourceLineCount(runtime_atomic64_diff_source), manifest.live_gate_line_count);
    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", manifest.runtime_replay_path);
    try expectBlobShaMatchesSource(manifest.runtime_replay_blob_sha, runtime_atomic64_diff_source);
    try std.testing.expectEqual(sourceLineCount(runtime_atomic64_diff_source), manifest.runtime_replay_line_count);
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
    try std.testing.expectEqualStrings("3f9c864f8bfe679533b64d6b310154c0629b5cf8", manifest.phase9_build_blob_sha);
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
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "lib/atomic64_test.c") != null);
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

    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "lib/atomic64_test.c") != null);
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

test "phase 4 atomic64 survey keeps the gate-evidence phase4 build blob pin aligned with live sources" {
    const gate_evidence_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/phase4-gate-evidence.md",
    );
    defer std.testing.allocator.free(gate_evidence_source);

    const phase4_build_blob_sha = try gitBlobShaHex(phase4_build_source);
    const phase4_build_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE4_BUILD_BLOB_SHA={s}",
        .{phase4_build_blob_sha},
    );
    defer std.testing.allocator.free(phase4_build_marker);

    try expectMarker(gate_evidence_source, phase4_build_marker);
}

test "phase 4 atomic64 survey keeps the gate-evidence runtime, manifest, survey, validator, and review-checklist blob pins aligned with live sources" {
    const gate_evidence_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/phase4-gate-evidence.md",
    );
    defer std.testing.allocator.free(gate_evidence_source);

    const runtime_atomic64_diff_blob_sha = try gitBlobShaHex(runtime_atomic64_diff_source);
    const runtime_atomic64_diff_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA={s}",
        .{runtime_atomic64_diff_blob_sha},
    );
    defer std.testing.allocator.free(runtime_atomic64_diff_marker);

    const runtime_atomic64_manifest_blob_sha = try gitBlobShaHex(phase4_runtime_atomic64_manifest_source);
    const runtime_atomic64_manifest_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA={s}",
        .{runtime_atomic64_manifest_blob_sha},
    );
    defer std.testing.allocator.free(runtime_atomic64_manifest_marker);

    const runtime_atomic64_survey_source = try readRepoFile(
        std.testing.allocator,
        "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    );
    defer std.testing.allocator.free(runtime_atomic64_survey_source);
    const runtime_atomic64_survey_blob_sha = try gitBlobShaHex(runtime_atomic64_survey_source);
    const runtime_atomic64_survey_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA={s}",
        .{runtime_atomic64_survey_blob_sha},
    );
    defer std.testing.allocator.free(runtime_atomic64_survey_marker);

    const validate_phase4_source = try readRepoFile(
        std.testing.allocator,
        "scripts/zigux/validate-phase4.py",
    );
    defer std.testing.allocator.free(validate_phase4_source);
    const validate_phase4_blob_sha = try gitBlobShaHex(validate_phase4_source);
    const validate_phase4_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE4_VALIDATOR_BLOB_SHA={s}",
        .{validate_phase4_blob_sha},
    );
    defer std.testing.allocator.free(validate_phase4_marker);

    const gate_evidence_checker_source = try readRepoFile(
        std.testing.allocator,
        "scripts/zigux/check-phase4-gate-evidence.py",
    );
    defer std.testing.allocator.free(gate_evidence_checker_source);
    const gate_evidence_checker_blob_sha = try gitBlobShaHex(gate_evidence_checker_source);
    const gate_evidence_checker_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA={s}",
        .{gate_evidence_checker_blob_sha},
    );
    defer std.testing.allocator.free(gate_evidence_checker_marker);

    const review_checklist_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/review-checklist.md",
    );
    defer std.testing.allocator.free(review_checklist_source);
    const review_checklist_blob_sha = try gitBlobShaHex(review_checklist_source);
    const review_checklist_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA={s}",
        .{review_checklist_blob_sha},
    );
    defer std.testing.allocator.free(review_checklist_marker);

    try expectMarker(gate_evidence_source, runtime_atomic64_diff_marker);
    try expectMarker(gate_evidence_source, runtime_atomic64_manifest_marker);
    try expectMarker(gate_evidence_source, runtime_atomic64_survey_marker);
    try expectMarker(gate_evidence_source, validate_phase4_marker);
    try expectMarker(gate_evidence_source, gate_evidence_checker_marker);
    try expectMarker(gate_evidence_source, review_checklist_marker);
    try expectMarker(gate_evidence_source, "PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=16");
    try expectMarker(gate_evidence_source, "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=33");
    try expectMarker(gate_evidence_source, "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=16");
    try expectMarker(gate_evidence_source, "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=33");
    try expectMarker(gate_evidence_source, "validator_blob_pin_drift");
    try expectMarker(gate_evidence_source, "gate_evidence_self_test_case_count_drift");
    try expectMarker(gate_evidence_source, "gate_evidence_self_test_cases_drift");
    try expectMarker(gate_evidence_source, "shared_validator_expected_self_test_case_count_drift");
}

test "phase 4 atomic64 survey keeps the gate-evidence exact-count markers aligned with live note" {
    const gate_evidence_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/phase4-gate-evidence.md",
    );
    defer std.testing.allocator.free(gate_evidence_source);

    try expectMarker(gate_evidence_source, "PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=");
    try expectMarker(gate_evidence_source, "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=");
    try expectMarker(gate_evidence_source, "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=");
    try expectMarker(gate_evidence_source, "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=");
    try expectMarker(gate_evidence_source, "PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=16");
    try expectMarker(gate_evidence_source, "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=33");
    try expectMarker(gate_evidence_source, "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=16");
    try expectMarker(gate_evidence_source, "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=33");
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(gate_evidence_source, "PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA="));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(gate_evidence_source, "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA="));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(gate_evidence_source, "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA="));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(gate_evidence_source, "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA="));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(gate_evidence_source, "PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT="));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(gate_evidence_source, "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(gate_evidence_source, "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT="));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(gate_evidence_source, "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="));
}

test "phase 4 atomic64 survey keeps the full gate-evidence self-test catalog line aligned with live note" {
    const gate_evidence_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/phase4-gate-evidence.md",
    );
    defer std.testing.allocator.free(gate_evidence_source);

    try expectMarker(gate_evidence_source, phase4_gate_evidence_self_test_cases_line);
    try std.testing.expectEqual(
        @as(usize, 1),
        countOccurrences(gate_evidence_source, phase4_gate_evidence_self_test_cases_line),
    );
}
