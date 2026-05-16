const std = @import("std");
const atomic64_diff_source = @embedFile("atomic64_diff.zig");
const runtime_atomic64_diff = @import("runtime_atomic64_diff.zig");
const runtime_atomic64_diff_source = @embedFile("runtime_atomic64_diff.zig");
const phase4_runtime_atomic64_manifest_source = @embedFile("phase4_runtime_atomic64_diff_manifest.json");
const phase4_runtime_atomic64_diff_survey_source = @embedFile("phase4_runtime_atomic64_diff_survey.zig");
const phase4_perf_baseline_manifest_source = @embedFile("phase4_perf_baseline_manifest.json");
const phase4_build_source = @embedFile("phase4_build.zig");
const phase9_build_source = @embedFile("phase9_build.zig");

fn expectMarker(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
}

fn expectNoMarker(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, marker) == null);
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

fn expectManifestContainsGitBlobSha(
    manifest_source: []const u8,
    field_name: []const u8,
    source: []const u8,
) !void {
    const blob_sha = try gitBlobShaHex(source);
    const marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"{s}\": \"{s}\"",
        .{ field_name, blob_sha },
    );
    defer std.testing.allocator.free(marker);
    try expectMarker(manifest_source, marker);
}

fn readRepoFile(allocator: std.mem.Allocator, repo_root_relative_path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        repo_root_relative_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectRuntimeCaseGroupCardinality(
    group_header: []const u8,
    next_header: []const u8,
    expected_case_count: usize,
) !void {
    const section_start = std.mem.indexOf(u8, runtime_atomic64_diff_source, group_header) orelse
        return error.MissingRuntimeCaseGroupHeader;
    const section_end = std.mem.indexOfPos(u8, runtime_atomic64_diff_source, section_start, next_header) orelse
        return error.MissingRuntimeCaseGroupBoundary;
    const section = runtime_atomic64_diff_source[section_start..section_end];
    try std.testing.expectEqual(expected_case_count, countOccurrences(section, ".name = "));
}

fn expectOrderedMarkersInSection(
    haystack: []const u8,
    section_header: []const u8,
    section_footer: []const u8,
    expected_markers: []const []const u8,
) !void {
    const section_start = std.mem.indexOf(u8, haystack, section_header) orelse
        return error.MissingOrderedMarkerSectionHeader;
    const section_end = std.mem.indexOfPos(u8, haystack, section_start, section_footer) orelse
        return error.MissingOrderedMarkerSectionFooter;
    const section = haystack[section_start..section_end];

    var cursor: usize = 0;
    for (expected_markers) |marker| {
        const offset = std.mem.indexOfPos(u8, section, cursor, marker) orelse
            return error.MissingOrderedSectionMarker;
        cursor = offset + marker.len;
    }
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

fn expectAtomic64GateEvidenceMarkerCount(marker: []const u8, expected_count: usize) !void {
    const gate_evidence_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/phase4-gate-evidence.md",
    );
    defer std.testing.allocator.free(gate_evidence_source);
    try std.testing.expectEqual(expected_count, countOccurrences(gate_evidence_source, marker));
}

test "atomic64 diff canonical wrapper keeps the shipped runtime gate wired in" {
    _ = runtime_atomic64_diff;
}

test "atomic64 diff wrapper records the current bounded runtime checks" {
    try expectMarker(
        runtime_atomic64_diff_source,
        "runtime atomic64 diff gate replays bounded atomic64_test.c arithmetic, exchange, cmpxchg, add_unless, and bitwise expectations",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "v0 to v1 keeps the original counter visible as the exchange return value",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "v1 to v2 keeps wide negative and positive 64-bit values distinct",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "high-bit starter from atomic64_test.c still round-trips through exchange",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "cmpxchg success path stores the desired value when the expected value matches",
    );
    try expectMarker(runtime_atomic64_diff_source, "cmpxchg mismatch keeps the original value visible");
    try expectMarker(
        runtime_atomic64_diff_source,
        "add_unless leaves the counter untouched when it already matches the blocked value",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "add_unless applies the addend when the current value differs from the blocked value",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "runtime atomic64 diff gate keeps inc_not_zero and dec_if_positive guard paths explicit",
    );
    try expectMarker(runtime_atomic64_diff_source, "inc_not_zero leaves a zero counter untouched");
    try expectMarker(
        runtime_atomic64_diff_source,
        "inc_not_zero increments a live counter without hiding the previous value",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "dec_if_positive decrements a positive counter and stores the result",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "dec_if_positive reports the negative-one result while leaving zero unchanged",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "dec_if_positive keeps a negative counter unchanged while still reporting the decremented result",
    );
    try expectMarker(runtime_atomic64_diff_source, "runtime atomic64 diff gate keeps selftest family coverage explicit");
}

test "atomic64 diff wrapper keeps the bounded guard-path case cardinality explicit" {
    try expectRuntimeCaseGroupCardinality(
        "    const inc_not_zero_cases = [_]IncNotZeroCase{",
        "    const dec_if_positive_cases = [_]DecIfPositiveCase{",
        2,
    );
    try expectRuntimeCaseGroupCardinality(
        "    const dec_if_positive_cases = [_]DecIfPositiveCase{",
        "test \"runtime atomic64 diff gate keeps selftest family coverage explicit\" {",
        3,
    );
}

test "atomic64 diff wrapper keeps the runtime handoff blob pins exact" {
    try expectManifestContainsGitBlobSha(
        phase4_runtime_atomic64_manifest_source,
        "live_gate_blob_sha",
        runtime_atomic64_diff_source,
    );
    try expectManifestContainsGitBlobSha(
        phase4_runtime_atomic64_manifest_source,
        "runtime_replay_blob_sha",
        runtime_atomic64_diff_source,
    );
}

test "atomic64 diff wrapper keeps the runtime handoff line counts exact" {
    const runtime_line_count = countOccurrences(runtime_atomic64_diff_source, "\n");

    const live_gate_line_count_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"live_gate_line_count\": {}",
        .{runtime_line_count},
    );
    defer std.testing.allocator.free(live_gate_line_count_marker);
    try expectMarker(phase4_runtime_atomic64_manifest_source, live_gate_line_count_marker);

    const runtime_replay_line_count_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "\"runtime_replay_line_count\": {}",
        .{runtime_line_count},
    );
    defer std.testing.allocator.free(runtime_replay_line_count_marker);
    try expectMarker(phase4_runtime_atomic64_manifest_source, runtime_replay_line_count_marker);

    const live_gate_survey_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "try std.testing.expectEqual(@as(usize, {}), manifest.live_gate_line_count);",
        .{runtime_line_count},
    );
    defer std.testing.allocator.free(live_gate_survey_marker);
    try expectMarker(phase4_runtime_atomic64_diff_survey_source, live_gate_survey_marker);

    const runtime_replay_survey_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "try std.testing.expectEqual(@as(usize, {}), manifest.runtime_replay_line_count);",
        .{runtime_line_count},
    );
    defer std.testing.allocator.free(runtime_replay_survey_marker);
    try expectMarker(phase4_runtime_atomic64_diff_survey_source, runtime_replay_survey_marker);
}

test "atomic64 diff wrapper keeps the manifest build, validator, and matrix blob pins exact" {
    const validate_phase4_source = try readRepoFile(
        std.testing.allocator,
        "scripts/zigux/validate-phase4.py",
    );
    defer std.testing.allocator.free(validate_phase4_source);

    const phase4_validation_matrix_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/phase4-validation-matrix.md",
    );
    defer std.testing.allocator.free(phase4_validation_matrix_source);

    try expectManifestContainsGitBlobSha(
        phase4_runtime_atomic64_manifest_source,
        "phase4_build_blob_sha",
        phase4_build_source,
    );
    try expectManifestContainsGitBlobSha(
        phase4_runtime_atomic64_manifest_source,
        "phase4_validator_blob_sha",
        validate_phase4_source,
    );
    try expectManifestContainsGitBlobSha(
        phase4_runtime_atomic64_manifest_source,
        "phase9_build_blob_sha",
        phase9_build_source,
    );
    try expectManifestContainsGitBlobSha(
        phase4_runtime_atomic64_manifest_source,
        "phase4_validation_matrix_blob_sha",
        phase4_validation_matrix_source,
    );
}

test "atomic64 diff wrapper keeps the current manifest handoff explicit" {
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"lane_key\": \"P4-L04\"");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"roadmap_target_path\": \"zigux/tests/atomic64_diff.zig\"");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"owner\": \"ABI and Runtime Team\"");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"rollback_owner\": \"ABI and Runtime Team\"");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"roadmap_atomic64_diff_present\": true");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"roadmap_atomic64_wrapper_targets_runtime_diff\": true");
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "\"live_gate_path\": \"zigux/tests/runtime_atomic64_diff.zig\"",
    );
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"runtime_replay_path\": \"zigux/tests/runtime_atomic64_diff.zig\"");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"phase4_build_present\": true");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"phase4_build_uses_atomic64_wrapper\": true");
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "\"phase4_validator_atomic64_diff_present\": true",
    );
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "\"phase4_validator_runtime_atomic64_diff_present\": true",
    );
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "\"phase4_gate_evidence_path\": \"Documentation/zigux/phase4-gate-evidence.md\"",
    );
    try expectNoMarker(phase4_runtime_atomic64_manifest_source, "\"phase4_gate_evidence_blob_sha\": ");
    const review_checklist_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/review-checklist.md",
    );
    defer std.testing.allocator.free(review_checklist_source);
    try expectManifestContainsGitBlobSha(
        phase4_runtime_atomic64_manifest_source,
        "phase4_review_checklist_blob_sha",
        review_checklist_source,
    );
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "\"phase4_validation_matrix_atomic64_diff_note_present\": true",
    );
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "\"phase4_validation_matrix_runtime_atomic64_note_present\": true",
    );
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "\"threshold_posture\": \"threshold_pending_until_runtime_atomic64_scope_widens\"",
    );
    try expectMarker(phase4_runtime_atomic64_manifest_source, "single bounded replay body");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "Phase 9 runtime packet");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "shared reviewer checklist");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "rollback-owner matrix");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "shared runtime replay body");
}

test "atomic64 diff wrapper keeps the paired survey contract explicit" {
    try expectOrderedMarkersInSection(
        phase4_runtime_atomic64_diff_survey_source,
        "test \"phase 4 atomic64 survey keeps wrapper handoff, owner map, and current local-only perf evidence explicit\" {",
        "test \"phase 4 atomic64 survey keeps the gate-evidence wrapper blob pin aligned with the live wrapper\" {",
        &.{
            "test \"phase 4 atomic64 survey keeps wrapper handoff, owner map, and current local-only perf evidence explicit\" {",
            "test \"phase 4 atomic64 survey keeps the current roadmap gap summary reviewable\" {",
            "test \"phase 4 atomic64 survey keeps reversible delivery and next-step evidence explicit\" {",
        },
    );
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "test \"phase 4 atomic64 survey keeps the gate-evidence wrapper blob pin aligned with the live wrapper\" {",
    );
}

test "atomic64 diff wrapper keeps the paired survey gate-evidence self-test markers exact" {
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "const phase4_gate_evidence_self_test_cases_line =",
    );
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "shared_validator_reruns_gate_evidence_check_drift,shared_validator_reruns_gate_evidence_self_test_drift,",
    );
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "shared_validator_expected_target_count_drift,shared_validator_expected_self_test_case_count_drift,",
    );
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34",
    );
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34",
    );
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19",
    );
}

test "atomic64 diff wrapper keeps the gate-evidence runtime survey blob pins exact" {
    const gate_evidence_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/phase4-gate-evidence.md",
    );
    defer std.testing.allocator.free(gate_evidence_source);

    const manifest_blob_sha = try gitBlobShaHex(phase4_runtime_atomic64_manifest_source);
    const manifest_blob_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA={s}",
        .{manifest_blob_sha},
    );
    defer std.testing.allocator.free(manifest_blob_marker);
    try expectMarker(gate_evidence_source, manifest_blob_marker);

    const survey_blob_sha = try gitBlobShaHex(phase4_runtime_atomic64_diff_survey_source);
    const survey_blob_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA={s}",
        .{survey_blob_sha},
    );
    defer std.testing.allocator.free(survey_blob_marker);
    try expectMarker(gate_evidence_source, survey_blob_marker);

    const review_checklist_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/review-checklist.md",
    );
    defer std.testing.allocator.free(review_checklist_source);
    const review_checklist_blob_sha = try gitBlobShaHex(review_checklist_source);
    const review_checklist_blob_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA={s}",
        .{review_checklist_blob_sha},
    );
    defer std.testing.allocator.free(review_checklist_blob_marker);
    try expectMarker(gate_evidence_source, review_checklist_blob_marker);
    try expectMarker(gate_evidence_source, "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true");
}

test "atomic64 diff wrapper keeps the current roadmap gap summary reviewable" {
    try expectOrderedMarkersInSection(
        phase4_runtime_atomic64_manifest_source,
        "\"roadmap_gap_summary\": \"",
        "\",\n  \"reversible_delivery_evidence\": \"",
        &.{
            "gate-evidence surfaces again",
            "approved local benchmark commands",
            "approved local-only acceptable limits",
            "broader sample follow-ups remain intentionally open",
            "shared CI perf promotion",
        },
    );
}

test "atomic64 diff wrapper keeps reversible delivery and next-step evidence explicit" {
    try expectOrderedMarkersInSection(
        phase4_runtime_atomic64_manifest_source,
        "\"reversible_delivery_evidence\": \"",
        "\",\n  \"ready_next\": \"",
        &.{
            "zigux/tests/atomic64_diff.zig",
            "zigux/tests/runtime_atomic64_diff.zig",
            "zigux/tests/phase4_build.zig",
            "scripts/zigux/validate-phase4.py",
            "Documentation/zigux/phase4-gate-evidence.md",
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/phase4-validation-matrix.md",
            "zigux/tests/phase4_perf_baseline_manifest.json",
            "zigux/tests/phase4_perf_baseline_survey.zig",
        },
    );
    try expectOrderedMarkersInSection(
        phase4_runtime_atomic64_manifest_source,
        "\"ready_next\": \"",
        "\",\n  \"owner\": \"",
        &.{
            "benchmark command",
            "acceptable limit",
            "Documentation/zigux/phase4-validation-matrix.md",
            "Documentation/zigux/phase4-gate-evidence.md",
            "zigux/tests/phase4_perf_baseline_manifest.json",
            "zigux/tests/phase4_perf_baseline_survey.zig",
            "correctness-only replay routes",
        },
    );
}

test "atomic64 diff wrapper keeps the current phase4 and phase9 build routing explicit" {
    try expectMarker(phase4_build_source, ".root_source_file = b.path(\"atomic64_diff.zig\")");
    try expectMarker(
        phase4_build_source,
        ".root_source_file = b.path(\"phase4_runtime_atomic64_diff_survey.zig\")",
    );
    try expectMarker(phase4_build_source, ".name = \"phase4-runtime-atomic64-diff-tests\"");
    try expectMarker(phase4_build_source, ".name = \"phase4-runtime-atomic64-diff-survey-tests\"");
    try expectMarker(phase4_build_source, "\"phase4-runtime-atomic64-diff\"");
    try expectMarker(phase4_build_source, "\"phase4-runtime-atomic64-diff-survey\"");
    try expectNoMarker(phase4_build_source, ".root_source_file = b.path(\"runtime_atomic64_diff.zig\")");
    try expectMarker(phase9_build_source, ".root_source_file = b.path(\"runtime_atomic64_diff.zig\")");
    try expectMarker(phase9_build_source, ".name = \"phase9-runtime-atomic64-diff-tests\"");
    try expectNoMarker(phase9_build_source, ".root_source_file = b.path(\"atomic64_diff.zig\")");
    try expectNoMarker(
        phase9_build_source,
        ".root_source_file = b.path(\"phase4_runtime_atomic64_diff_survey.zig\")",
    );
}

test "atomic64 diff wrapper keeps the current bounded runtime inventory explicit" {
    try expectRuntimeCaseGroupCardinality(
        "const arithmetic_cases = [_]ArithmeticCase{",
        "const cases = [_]DiffCase{",
        2,
    );
    try expectRuntimeCaseGroupCardinality(
        "const cases = [_]DiffCase{",
        "const compare_swap_cases = [_]CompareSwapCase{",
        3,
    );
    try expectRuntimeCaseGroupCardinality(
        "const compare_swap_cases = [_]CompareSwapCase{",
        "const add_unless_cases = [_]AddUnlessCase{",
        2,
    );
    try expectRuntimeCaseGroupCardinality(
        "const add_unless_cases = [_]AddUnlessCase{",
        "const bitwise_cases = [_]BitwiseCase{",
        2,
    );
    try expectRuntimeCaseGroupCardinality(
        "const bitwise_cases = [_]BitwiseCase{",
        "test \"runtime atomic64 diff gate keeps inc_not_zero and dec_if_positive guard paths explicit\" {",
        3,
    );
    try expectMarker(runtime_atomic64_diff_source, "if (iterations == 0) return error.EmptyThresholdReplayBatch;");
    try expectMarker(
        runtime_atomic64_diff_source,
        "try std.testing.expectError(error.EmptyThresholdReplayBatch, runThresholdReplay(0));",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "try std.testing.expectEqual(@as(i64, 130322557735600377), single.final_counter);",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "try std.testing.expectEqual(@as(i64, 130322557735600376), repeated.final_counter);",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "try std.testing.expectEqual(@as(u64, 3626254113632800175), single.checksum);",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "try std.testing.expectEqual(@as(u64, 9210681150676220922), repeated.checksum);",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "try std.testing.expectEqual(sample.ModuleStage.exited, single.final_stage);",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "try std.testing.expectEqual(sample.ModuleStage.exited, repeated.final_stage);",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "try std.testing.expectEqual(@as(usize, 1), single.final_selftest_runs);",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "try std.testing.expectEqual(@as(usize, 1), repeated.final_selftest_runs);",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "try std.testing.expectEqual(@as(usize, 1), single.final_exit_runs);",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "try std.testing.expectEqual(@as(usize, 1), repeated.final_exit_runs);",
    );
    try expectAtomic64MatrixMarkerCount("`lib/atomic64_test.c`", 1);
    try expectAtomic64MatrixMarkerCount(
        "`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig`",
        1,
    );
    try expectAtomic64MatrixMarkerCount("`threshold_pending_until_runtime_atomic64_scope_widens`", 1);
    try expectAtomic64GateEvidenceMarkerCount("two arithmetic checks", 1);
    try expectAtomic64GateEvidenceMarkerCount("three exchange checks", 1);
    try expectAtomic64GateEvidenceMarkerCount("two `cmpxchg` checks", 1);
    try expectAtomic64GateEvidenceMarkerCount("two `add_unless` checks", 1);
    try expectAtomic64GateEvidenceMarkerCount(
        "two `inc_not_zero` checks and three `dec_if_positive` checks",
        1,
    );
    try expectAtomic64GateEvidenceMarkerCount("three bitwise checks", 1);
    try expectAtomic64GateEvidenceMarkerCount("runThresholdReplay(0)", 1);
    try expectAtomic64GateEvidenceMarkerCount("final_selftest_runs=1", 1);
    try expectAtomic64GateEvidenceMarkerCount("final_exit_runs=1", 1);
}

const Atomic64Manifest = struct {
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
    owner: []const u8,
    rollback_owner: []const u8,
};

fn expectBlobShaShape(value: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 40), value.len);
    for (value) |byte| {
        const is_digit = byte >= '0' and byte <= '9';
        const is_lower_hex = byte >= 'a' and byte <= 'f';
        try std.testing.expect(is_digit or is_lower_hex);
    }
}

test "atomic64 diff wrapper keeps the manifest-backed runtime packet structurally parseable" {
    const parsed = try std.json.parseFromSlice(
        Atomic64Manifest,
        std.testing.allocator,
        phase4_runtime_atomic64_manifest_source,
        .{},
    );
    defer parsed.deinit();

    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P4-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("zigux/tests/atomic64_diff.zig", manifest.roadmap_target_path);
    try std.testing.expect(manifest.roadmap_atomic64_diff_present);
    try std.testing.expect(manifest.roadmap_atomic64_wrapper_targets_runtime_diff);
    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", manifest.live_gate_path);
    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", manifest.runtime_replay_path);
    try std.testing.expectEqualStrings("ABI and Runtime Team", manifest.owner);
    try std.testing.expectEqualStrings("ABI and Runtime Team", manifest.rollback_owner);
    try std.testing.expect(manifest.phase4_build_present);
    try std.testing.expect(manifest.phase4_build_uses_atomic64_wrapper);
    try std.testing.expect(manifest.phase4_validator_atomic64_diff_present);
    try std.testing.expect(manifest.phase4_validator_runtime_atomic64_diff_present);
    try std.testing.expect(manifest.phase9_build_present);
    try std.testing.expect(manifest.phase4_validation_matrix_atomic64_diff_note_present);
    try std.testing.expect(manifest.phase4_validation_matrix_runtime_atomic64_note_present);
    try std.testing.expectEqualStrings(
        "Documentation/zigux/phase4-gate-evidence.md",
        manifest.phase4_gate_evidence_path,
    );
    try std.testing.expectEqualStrings(
        "threshold_pending_until_runtime_atomic64_scope_widens",
        manifest.threshold_posture,
    );
    try std.testing.expect(manifest.live_gate_line_count > 0);
    try std.testing.expectEqual(manifest.live_gate_line_count, manifest.runtime_replay_line_count);
    try expectBlobShaShape(manifest.live_gate_blob_sha);
    try expectBlobShaShape(manifest.runtime_replay_blob_sha);
    try expectBlobShaShape(manifest.phase4_build_blob_sha);
    try expectBlobShaShape(manifest.phase4_validator_blob_sha);
    try expectBlobShaShape(manifest.phase9_build_blob_sha);
    try expectBlobShaShape(manifest.phase4_validation_matrix_blob_sha);
    try expectBlobShaShape(manifest.phase4_review_checklist_blob_sha);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "lib/atomic64_test.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_gap_summary, "approved local benchmark commands") != null);
    try std.testing.expect(
        std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "zigux/tests/runtime_atomic64_diff.zig") != null,
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest.reversible_delivery_evidence, "rollback-owner matrix") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "approved local benchmark commands") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.ready_next, "correctness-only replay routes") != null);
}
