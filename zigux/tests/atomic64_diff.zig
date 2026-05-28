const std = @import("std");
const sample = @import("runtime_atomic64_sample");
const atomic64_diff_source = @embedFile("atomic64_diff.zig");
const runtime_atomic64_diff = @import("runtime_atomic64_diff.zig");
const runtime_atomic64_diff_source = @embedFile("runtime_atomic64_diff.zig");
const phase4_runtime_atomic64_manifest_source = @embedFile("phase4_runtime_atomic64_diff_manifest.json");
const phase4_runtime_atomic64_diff_survey_source = @embedFile("phase4_runtime_atomic64_diff_survey.zig");
const phase4_perf_baseline_manifest_source = @embedFile("phase4_perf_baseline_manifest.json");
const phase4_build_source = @embedFile("phase4_build.zig");
const phase9_build_source = @embedFile("phase9_build.zig");

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
    phase4_validator_atomic64_diff_present: bool,
    phase4_validator_runtime_atomic64_diff_present: bool,
    phase4_gate_evidence_path: []const u8,
    phase9_build_present: bool,
    phase4_validation_matrix_atomic64_diff_note_present: bool,
    phase4_validation_matrix_runtime_atomic64_note_present: bool,
    threshold_posture: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
};

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

fn sourceLineCount(source: []const u8) usize {
    if (source.len == 0) return 0;

    var count: usize = std.mem.count(u8, source, "\n");
    if (source[source.len - 1] != '\n') count += 1;
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
    const runtime_line_count = sourceLineCount(runtime_atomic64_diff_source);

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
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"lane_key\": \"P4-L01\"");
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

test "atomic64 diff wrapper structurally parses the current manifest handoff" {
    const parsed = try std.json.parseFromSlice(
        Atomic64Manifest,
        std.testing.allocator,
        phase4_runtime_atomic64_manifest_source,
        .{},
    );
    defer parsed.deinit();
    const manifest = parsed.value;

    const runtime_blob_sha = try gitBlobShaHex(runtime_atomic64_diff_source);

    try std.testing.expectEqualStrings("P4-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("zigux/tests/atomic64_diff.zig", manifest.roadmap_target_path);
    try std.testing.expect(manifest.roadmap_atomic64_diff_present);
    try std.testing.expect(manifest.roadmap_atomic64_wrapper_targets_runtime_diff);
    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", manifest.live_gate_path);
    try std.testing.expectEqualStrings(runtime_blob_sha[0..], manifest.live_gate_blob_sha);
    try std.testing.expectEqual(sourceLineCount(runtime_atomic64_diff_source), manifest.live_gate_line_count);
    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", manifest.runtime_replay_path);
    try std.testing.expectEqualStrings(runtime_blob_sha[0..], manifest.runtime_replay_blob_sha);
    try std.testing.expectEqual(sourceLineCount(runtime_atomic64_diff_source), manifest.runtime_replay_line_count);
    try std.testing.expect(manifest.phase4_build_present);
    try std.testing.expect(manifest.phase4_build_uses_atomic64_wrapper);
    try std.testing.expect(manifest.phase4_validator_atomic64_diff_present);
    try std.testing.expect(manifest.phase4_validator_runtime_atomic64_diff_present);
    try std.testing.expectEqualStrings("Documentation/zigux/phase4-gate-evidence.md", manifest.phase4_gate_evidence_path);
    try std.testing.expect(manifest.phase9_build_present);
    try std.testing.expect(manifest.phase4_validation_matrix_atomic64_diff_note_present);
    try std.testing.expect(manifest.phase4_validation_matrix_runtime_atomic64_note_present);
    try std.testing.expectEqualStrings(
        "threshold_pending_until_runtime_atomic64_scope_widens",
        manifest.threshold_posture,
    );
    try std.testing.expectEqualStrings("ABI and Runtime Team", manifest.owner);
    try std.testing.expectEqualStrings("ABI and Runtime Team", manifest.rollback_owner);
}

test "atomic64 diff wrapper keeps the paired survey contract explicit" {
    try expectOrderedMarkersInSection(
        phase4_runtime_atomic64_diff_survey_source,
        "test \"phase 4 atomic64 survey keeps wrapper handoff, owner map, and current local-only perf evidence explicit\" {",
        "test \"phase 4 atomic64 survey keeps the gate-evidence wrapper and runtime blob pins aligned with the live gate\" {",
        &.{
            "test \"phase 4 atomic64 survey keeps wrapper handoff, owner map, and current local-only perf evidence explicit\" {",
            "test \"phase 4 atomic64 survey keeps the current roadmap gap summary reviewable\" {",
            "test \"phase 4 atomic64 survey keeps reversible delivery and next-step evidence explicit\" {",
        },
    );
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "test \"phase 4 atomic64 survey keeps the gate-evidence wrapper and runtime blob pins aligned with the live gate\" {",
    );
}

test "atomic64 diff wrapper keeps the paired survey gate-evidence self-test markers exact" {
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "const phase4_gate_evidence_self_test_cases_line =",
    );
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "shared_validator_expected_self_test_case_count_drift,runtime_atomic64_survey_packet_presence_drift,",
    );
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "perf_baseline_shared_promotion_status_drift,test_fsmount_gap_packet_presence_drift,",
    );
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45",
    );
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45",
    );
    try expectMarker(
        phase4_runtime_atomic64_diff_survey_source,
        "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19",
    );
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

test "atomic64 diff wrapper keeps the Linux-style phase4 make routes explicit" {
    const makefile_source = try readRepoFile(std.testing.allocator, "zigux/Makefile");
    defer std.testing.allocator.free(makefile_source);
    try expectMarker(
        makefile_source,
        "PHONY += phase3-low-level-wrappers-test phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4",
    );
    try expectMarker(makefile_source, "phase4-runtime-atomic64-diff:");
    try expectMarker(
        makefile_source,
        "$(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
    );
    try expectMarker(makefile_source, "phase4-runtime-atomic64-diff-survey:");
    try expectMarker(
        makefile_source,
        "$(ZIG) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig",
    );
    try expectMarker(makefile_source, "phase4-perf-baseline-survey:");
    try expectMarker(
        makefile_source,
        "$(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    );
    try expectMarker(makefile_source, "phase4-test-fsmount-survey:");
    try expectMarker(
        makefile_source,
        "$(ZIG) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    );
    try expectMarker(makefile_source, "phase4-kprobe-example-survey:");
    try expectMarker(makefile_source, "$(ZIG) test zigux/tests/phase4_kprobe_example_survey.zig");
    try expectMarker(makefile_source, "phase4: phase4-validate phase4-test");
}

test "atomic64 diff wrapper keeps the shared phase4 validator packet explicit" {
    const validate_phase4_source = try readRepoFile(
        std.testing.allocator,
        "scripts/zigux/validate-phase4.py",
    );
    defer std.testing.allocator.free(validate_phase4_source);
    try expectMarker(validate_phase4_source, "\"zigux/tests/atomic64_diff.zig\"");
    try expectMarker(validate_phase4_source, "\"zigux/tests/runtime_atomic64_diff.zig\"");
    try expectMarker(validate_phase4_source, "\"zigux/tests/phase4_runtime_atomic64_diff_manifest.json\"");
    try expectMarker(validate_phase4_source, "\"zigux/tests/phase4_runtime_atomic64_diff_survey.zig\"");
    try expectMarker(
        validate_phase4_source,
        "phase 4 atomic64 survey keeps the current roadmap gap summary reviewable",
    );
    try expectMarker(
        validate_phase4_source,
        "phase 4 atomic64 survey keeps reversible delivery and next-step evidence explicit",
    );
    try expectMarker(validate_phase4_source, "run_phase4_runtime_atomic64_packet_check");
    try expectMarker(validate_phase4_source, "phase4_runtime_atomic64_packet");
}

test "atomic64 diff wrapper keeps the shared gate-evidence packet explicit" {
    const gate_evidence_source = try readRepoFile(
        std.testing.allocator,
        "Documentation/zigux/phase4-gate-evidence.md",
    );
    defer std.testing.allocator.free(gate_evidence_source);

    const atomic64_diff_blob_sha = try gitBlobShaHex(atomic64_diff_source);
    const atomic64_diff_blob_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE4_ATOMIC64_DIFF_BLOB_SHA={s}",
        .{atomic64_diff_blob_sha},
    );
    defer std.testing.allocator.free(atomic64_diff_blob_marker);

    const runtime_atomic64_diff_blob_sha = try gitBlobShaHex(runtime_atomic64_diff_source);
    const runtime_atomic64_diff_blob_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA={s}",
        .{runtime_atomic64_diff_blob_sha},
    );
    defer std.testing.allocator.free(runtime_atomic64_diff_blob_marker);

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

    try expectMarker(gate_evidence_source, atomic64_diff_blob_marker);
    try expectMarker(gate_evidence_source, runtime_atomic64_diff_blob_marker);
    try expectMarker(gate_evidence_source, validate_phase4_marker);
    try expectMarker(gate_evidence_source, gate_evidence_checker_marker);
    try expectMarker(gate_evidence_source, review_checklist_marker);
    try expectMarker(gate_evidence_source, "PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=19");
    try expectMarker(gate_evidence_source, "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45");
    try expectMarker(gate_evidence_source, "phase4_build_manifest_blob_pin_drift");
    try expectMarker(gate_evidence_source, "phase4_build_survey_blob_pin_drift");
    try expectMarker(gate_evidence_source, "phase9_build_manifest_blob_pin_drift");
    try expectMarker(gate_evidence_source, "phase9_build_survey_blob_pin_drift");
    try expectMarker(gate_evidence_source, "validator_blob_pin_drift");
    try expectMarker(gate_evidence_source, "gate_evidence_self_test_case_count_drift");
    try expectMarker(gate_evidence_source, "gate_evidence_self_test_cases_drift");
    try expectMarker(gate_evidence_source, "shared_validator_expected_self_test_case_count_drift");
    try expectMarker(gate_evidence_source, "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true");
    try expectMarker(gate_evidence_source, "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true");
    try expectMarker(gate_evidence_source, "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19");
    try expectMarker(gate_evidence_source, "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=45");
    try expectMarker(gate_evidence_source, "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true");
    try expectMarker(gate_evidence_source, "scripts/zigux/check-phase4-gate-evidence.py");
    try expectMarker(gate_evidence_source, "phase4-runtime-atomic64-diff-survey-tests");
    try expectMarker(gate_evidence_source, "make -C zigux phase4-runtime-atomic64-diff-survey");
    try expectMarker(gate_evidence_source, "two `inc_not_zero` checks");
    try expectMarker(gate_evidence_source, "three `dec_if_positive` checks");
    try expectAtomic64GateEvidenceMarkerCount("PHASE4_ATOMIC64_DIFF_BLOB_SHA=", 1);
    try expectAtomic64GateEvidenceMarkerCount("PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA=", 1);
    try expectAtomic64GateEvidenceMarkerCount("PHASE4_VALIDATOR_BLOB_SHA=", 1);
    try expectAtomic64GateEvidenceMarkerCount("PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=", 1);
    try expectAtomic64GateEvidenceMarkerCount("PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=", 1);
    try expectAtomic64GateEvidenceMarkerCount("PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=", 1);
    try expectAtomic64GateEvidenceMarkerCount("PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA=", 1);
    try expectAtomic64GateEvidenceMarkerCount("PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=", 1);
    try expectAtomic64GateEvidenceMarkerCount("PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=", 1);
    try expectAtomic64GateEvidenceMarkerCount("PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=", 1);
}

test "atomic64 diff wrapper keeps rollback ownership and threshold posture explicit" {
    try expectAtomic64MatrixMarkerCount("- owner: `ABI and Runtime Team`", 1);
    try expectAtomic64MatrixMarkerCount("- rollback owner: `ABI and Runtime Team`", 1);
    try expectAtomic64MatrixMarkerCount(
        "- fallback path: keep the current C anchor plus the existing Phase 9 runtime atomic64 starter surface as the source of truth if the Zig replay gate regresses",
        1,
    );
    try expectAtomic64MatrixMarkerCount(
        "- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded exchange, cmpxchg, add_unless, bitwise, and selftest-family replay set",
        1,
    );
    try expectAtomic64MatrixMarkerCount(
        "- survey packet: `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` keep the wrapper-to-runtime handoff, the shared build wiring, and the matrix wording reviewable beside the executable replay",
        1,
    );
}

test "atomic64 diff wrapper keeps the phase4 replay routes measurable" {
    try expectAtomic64MatrixMarkerCount(
        "`python3 scripts/zigux/validate-phase4.py` then `zig build test --build-file zigux/tests/phase4_build.zig` in `.github/workflows/zigux-bootstrap.yml`",
        1,
    );
    try expectAtomic64MatrixMarkerCount(
        "`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig`",
        1,
    );
    try expectAtomic64MatrixMarkerCount(
        "`zigux/tests/atomic64_diff.zig` bounded atomic64 exchange, cmpxchg, add_unless, bitwise, and selftest-family replay via the shared runtime-backed gate",
        1,
    );
}

test "atomic64 diff wrapper keeps its local-only perf-baseline governance explicit" {
    try expectMarker(
        phase4_perf_baseline_manifest_source,
        "\"decision_owner\": \"Validation and Perf Team\"",
    );
    try expectOrderedMarkersInSection(
        phase4_perf_baseline_manifest_source,
        "\"decision_owner\": \"Validation and Perf Team\"",
        "\"shared_ci_perf_promotion_status\": \"pending\"",
        &.{
            "\"coordination_owners\": [",
            "\"ABI and Runtime Team\"",
            "\"Shared Subsystems Pod\"",
        },
    );
    try expectMarker(
        phase4_perf_baseline_manifest_source,
        "\"shared_ci_perf_promotion_status\": \"pending\"",
    );
    try expectMarker(
        phase4_perf_baseline_manifest_source,
        "\"local_only_posture_note\": \"The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.\"",
    );
    try expectOrderedMarkersInSection(
        phase4_perf_baseline_manifest_source,
        "\"surface\": \"zigux/tests/atomic64_diff.zig\"",
        "\"surface\": \"zigux/tests/bitmap_diff.zig\"",
        &.{
            "\"gate_owner\": \"ABI and Runtime Team\"",
            "\"gate_rollback_owner\": \"ABI and Runtime Team\"",
            "\"threshold_posture\": \"threshold_pending_until_runtime_atomic64_scope_widens\"",
        },
    );
    try expectOrderedMarkersInSection(
        phase4_perf_baseline_manifest_source,
        "\"atomic64\": {",
        "\"bitmap\": {",
        &.{
            "\"benchmark_command\": \"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\"",
            "\"acceptable_limit_status\": \"approved_local_only\"",
            "\"acceptable_limit_metric\": \"median_elapsed_ns\"",
            "\"acceptable_limit_iterations\": 4",
            "\"acceptable_limit_sample_count\": 7",
            "\"acceptable_limit_max_elapsed_ns\": 8192",
            "\"iterations\": 1",
            "\"checksum\": 3626254113632800175",
            "\"final_counter\": 130322557735600377",
            "\"iterations\": 4",
            "\"checksum\": 9210681150676220922",
            "\"final_counter\": 130322557735600376",
        },
    );
}

test "atomic64 diff wrapper records the exact bounded arithmetic and threshold checks" {
    try expectOrderedMarkersInSection(
        runtime_atomic64_diff_source,
        "const arithmetic_cases = [_]ArithmeticCase{",
        "const cases = [_]DiffCase{",
        &.{
            ".name = \"v0 arithmetic path mirrors add/sub/add_return/sub_return/inc_return/dec_return sequencing\"",
            ".name = \"negative-one arithmetic path keeps decrement-style updates visible\"",
        },
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "test \"runtime atomic64 diff gate rejects an empty threshold replay batch\" {",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "try std.testing.expectError(error.EmptyThresholdReplayBatch, runThresholdReplay(0));",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "test \"runtime atomic64 diff gate keeps a deterministic threshold replay batch ready for future perf baselines\" {",
    );
    try expectMarker(runtime_atomic64_diff_source, "try std.testing.expectEqual(@as(usize, 1), single.iterations);");
    try expectMarker(runtime_atomic64_diff_source, "try std.testing.expectEqual(@as(usize, 4), repeated.iterations);");
    try expectMarker(runtime_atomic64_diff_source, "try std.testing.expectEqual(@as(i64, 130322557735600377), single.final_counter);");
    try expectMarker(runtime_atomic64_diff_source, "try std.testing.expectEqual(@as(i64, 130322557735600376), repeated.final_counter);");
    try expectMarker(runtime_atomic64_diff_source, "try std.testing.expectEqual(@as(u64, 3626254113632800175), single.checksum);");
    try expectMarker(runtime_atomic64_diff_source, "try std.testing.expectEqual(@as(u64, 9210681150676220922), repeated.checksum);");
    try expectMarker(runtime_atomic64_diff_source, "try std.testing.expectEqualDeep(repeated, try runThresholdReplay(4));");
    try expectMarker(runtime_atomic64_diff_source, "try std.testing.expect(repeated.checksum != single.checksum);");
}

test "atomic64 diff wrapper records the exact bounded runtime case names" {
    try expectOrderedMarkersInSection(
        runtime_atomic64_diff_source,
        "const cases = [_]DiffCase{",
        "const compare_swap_cases = [_]CompareSwapCase{",
        &.{
            ".name = \"v0 to v1 keeps the original counter visible as the exchange return value\"",
            ".name = \"v1 to v2 keeps wide negative and positive 64-bit values distinct\"",
            ".name = \"high-bit starter from atomic64_test.c still round-trips through exchange\"",
        },
    );
    try expectOrderedMarkersInSection(
        runtime_atomic64_diff_source,
        "const compare_swap_cases = [_]CompareSwapCase{",
        "const add_unless_cases = [_]AddUnlessCase{",
        &.{
            ".name = \"cmpxchg success path stores the desired value when the expected value matches\"",
            ".name = \"cmpxchg mismatch keeps the original value visible\"",
        },
    );
    try expectOrderedMarkersInSection(
        runtime_atomic64_diff_source,
        "const add_unless_cases = [_]AddUnlessCase{",
        "const inc_not_zero_cases = [_]IncNotZeroCase{",
        &.{
            ".name = \"add_unless leaves the counter untouched when it already matches the blocked value\"",
            ".name = \"add_unless applies the addend when the current value differs from the blocked value\"",
        },
    );
    try expectOrderedMarkersInSection(
        runtime_atomic64_diff_source,
        "const inc_not_zero_cases = [_]IncNotZeroCase{",
        "const dec_if_positive_cases = [_]DecIfPositiveCase{",
        &.{
            ".name = \"inc_not_zero leaves a zero counter untouched\"",
            ".name = \"inc_not_zero increments a live counter without hiding the previous value\"",
        },
    );
    try expectOrderedMarkersInSection(
        runtime_atomic64_diff_source,
        "const dec_if_positive_cases = [_]DecIfPositiveCase{",
        "const bitwise_cases = [_]BitwiseCase{",
        &.{
            ".name = \"dec_if_positive decrements a positive counter and stores the result\"",
            ".name = \"dec_if_positive reports the negative-one result while leaving zero unchanged\"",
            ".name = \"dec_if_positive keeps a negative counter unchanged while still reporting the decremented result\"",
        },
    );
    try expectOrderedMarkersInSection(
        runtime_atomic64_diff_source,
        "const bitwise_cases = [_]BitwiseCase{",
        "for (bitwise_cases) |case| {",
        &.{
            ".name = \"and preserves only the masked bits from an all-ones starter\"",
            ".name = \"or lifts high and low flags into the running counter\"",
            ".name = \"xor toggles separated flag groups without losing the wide value shape\"",
        },
    );
    try expectOrderedMarkersInSection(
        runtime_atomic64_diff_source,
        "test \"runtime atomic64 diff gate keeps selftest family coverage explicit\" {",
        "try module.exit();",
        &.{
            "summary.operation_families[0]",
            "summary.operation_families[1]",
            "summary.operation_families[2]",
            "summary.operation_families[3]",
            "summary.operation_families[4]",
        },
    );
}

test "atomic64 diff wrapper keeps post-exit guard-path rejection coverage explicit" {
    try expectOrderedMarkersInSection(
        runtime_atomic64_diff_source,
        "try module.exit();",
        "test \"runtime atomic64 diff gate rejects an empty threshold replay batch\" {",
        &.{
            "try std.testing.expectError(error.InvalidLifecycleTransition, module.addCounter(7));",
            "try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));",
            "try std.testing.expectError(error.InvalidLifecycleTransition, module.andCounter(7));",
            "try std.testing.expectError(error.InvalidLifecycleTransition, module.orCounter(7));",
            "try std.testing.expectError(error.InvalidLifecycleTransition, module.compareSwapCounter(17, 19));",
            "try std.testing.expectError(error.InvalidLifecycleTransition, module.addUnlessCounter(1, 17));",
            "try std.testing.expectError(error.InvalidLifecycleTransition, module.incNotZeroCounter());",
            "try std.testing.expectError(error.InvalidLifecycleTransition, module.decIfPositiveCounter());",
        },
    );
}

test "atomic64 diff wrapper pins the current bounded runtime case groups" {
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
        "const inc_not_zero_cases = [_]IncNotZeroCase{",
        2,
    );
    try expectRuntimeCaseGroupCardinality(
        "const inc_not_zero_cases = [_]IncNotZeroCase{",
        "const dec_if_positive_cases = [_]DecIfPositiveCase{",
        2,
    );
    try expectRuntimeCaseGroupCardinality(
        "const dec_if_positive_cases = [_]DecIfPositiveCase{",
        "const bitwise_cases = [_]BitwiseCase{",
        3,
    );
    try expectRuntimeCaseGroupCardinality(
        "const bitwise_cases = [_]BitwiseCase{",
        "for (bitwise_cases) |case| {",
        3,
    );
}

test "atomic64 diff wrapper records the threshold replay lifecycle markers" {
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
}

test "atomic64 diff wrapper executes the bounded threshold replay through the shipped runtime gate" {
    try std.testing.expectError(error.EmptyThresholdReplayBatch, runtime_atomic64_diff.runThresholdReplay(0));

    const single = try runtime_atomic64_diff.runThresholdReplay(1);
    const repeated = try runtime_atomic64_diff.runThresholdReplay(4);

    try std.testing.expectEqual(@as(usize, 1), single.iterations);
    try std.testing.expectEqual(@as(usize, 4), repeated.iterations);
    try std.testing.expectEqual(sample.ModuleStage.exited, single.final_stage);
    try std.testing.expectEqual(sample.ModuleStage.exited, repeated.final_stage);
    try std.testing.expectEqual(@as(usize, 1), single.final_selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), repeated.final_selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), single.final_exit_runs);
    try std.testing.expectEqual(@as(usize, 1), repeated.final_exit_runs);
    try std.testing.expectEqual(@as(i64, 130322557735600377), single.final_counter);
    try std.testing.expectEqual(@as(i64, 130322557735600376), repeated.final_counter);
    try std.testing.expectEqual(@as(u64, 3626254113632800175), single.checksum);
    try std.testing.expectEqual(@as(u64, 9210681150676220922), repeated.checksum);
    try std.testing.expectEqualDeep(repeated, try runtime_atomic64_diff.runThresholdReplay(4));
    try std.testing.expect(repeated.checksum != single.checksum);
}

test "atomic64 diff wrapper keeps the local perf-baseline manifest aligned with threshold replay evidence" {
    const perf_manifest_source = try readRepoFile(
        std.testing.allocator,
        "zigux/tests/phase4_perf_baseline_manifest.json",
    );
    defer std.testing.allocator.free(perf_manifest_source);

    try expectMarker(perf_manifest_source, "\"lane_key\": \"P4-L20\"");
    try expectMarker(perf_manifest_source, "\"surface\": \"zigux/tests/atomic64_diff.zig\"");
    try expectMarker(
        perf_manifest_source,
        "\"gate_owner\": \"ABI and Runtime Team\"",
    );
    try expectMarker(
        perf_manifest_source,
        "\"gate_rollback_owner\": \"ABI and Runtime Team\"",
    );
    try expectMarker(
        perf_manifest_source,
        "\"threshold_posture\": \"threshold_pending_until_runtime_atomic64_scope_widens\"",
    );

    const atomic64_section_start = std.mem.indexOf(
        u8,
        perf_manifest_source,
        "\"atomic64\": {",
    ) orelse return error.MissingAtomic64PerfBaselineSection;
    const atomic64_section_end = std.mem.indexOfPos(
        u8,
        perf_manifest_source,
        atomic64_section_start,
        "\"bitmap\": {",
    ) orelse return error.MissingBitmapPerfBaselineSection;
    const atomic64_section = perf_manifest_source[atomic64_section_start..atomic64_section_end];

    try expectMarker(
        atomic64_section,
        "\"benchmark_command\": \"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\"",
    );
    try expectMarker(atomic64_section, "\"acceptable_limit_status\": \"approved_local_only\"");
    try expectMarker(atomic64_section, "\"acceptable_limit_metric\": \"median_elapsed_ns\"");
    try expectMarker(atomic64_section, "\"acceptable_limit_iterations\": 4");
    try expectMarker(atomic64_section, "\"acceptable_limit_sample_count\": 7");
    try expectMarker(atomic64_section, "\"acceptable_limit_max_elapsed_ns\": 8192");
    try expectMarker(atomic64_section, "\"checksum\": 3626254113632800175");
    try expectMarker(atomic64_section, "\"final_counter\": 130322557735600377");
    try expectMarker(atomic64_section, "\"checksum\": 9210681150676220922");
    try expectMarker(atomic64_section, "\"final_counter\": 130322557735600376");
    try expectMarker(perf_manifest_source, "\"id\": \"phase4-perf-baseline-atomic64-command\"");
    try expectMarker(perf_manifest_source, "\"id\": \"phase4-perf-baseline-atomic64-acceptable-limit\"");
}

test "atomic64 diff wrapper keeps the local perf-baseline survey aligned with threshold replay evidence" {
    const perf_survey_source = try readRepoFile(
        std.testing.allocator,
        "zigux/tests/phase4_perf_baseline_survey.zig",
    );
    defer std.testing.allocator.free(perf_survey_source);

    try expectMarker(
        perf_survey_source,
        "test \"phase4 perf baseline survey manifest keeps the current benchmark-command posture explicit\" {",
    );
    try expectMarker(perf_survey_source, "phase4-perf-baseline-atomic64-command-evidence");
    try expectMarker(perf_survey_source, "phase4-perf-baseline-atomic64-command");
    try expectMarker(perf_survey_source, "phase4-perf-baseline-atomic64-acceptable-limit");
    try expectMarker(
        perf_survey_source,
        "\"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\"",
    );
    try expectMarker(perf_survey_source, "\"approved_local_only\"");
    try expectMarker(perf_survey_source, "\"median_elapsed_ns\"");
    try expectMarker(perf_survey_source, "@as(u64, 8192)");
    try expectMarker(perf_survey_source, "@as(u64, 3626254113632800175)");
    try expectMarker(perf_survey_source, "@as(i64, 130322557735600377)");
    try expectMarker(perf_survey_source, "@as(u64, 9210681150676220922)");
    try expectMarker(perf_survey_source, "@as(i64, 130322557735600376)");
    try expectMarker(perf_survey_source, "seven monotonic samples");
    try expectMarker(perf_survey_source, "shared CI perf promotion");
}

test "atomic64 diff wrapper keeps its own source inventory explicit" {
    try std.testing.expectEqual(@as(usize, 27), countOccurrences(atomic64_diff_source, "\ntest \""));
    try expectMarker(
        atomic64_diff_source,
        "test \"atomic64 diff canonical wrapper keeps the shipped runtime gate wired in\" {",
    );
    try expectMarker(
        atomic64_diff_source,
        "test \"atomic64 diff wrapper keeps the shared gate-evidence packet explicit\" {",
    );
    try expectMarker(
        atomic64_diff_source,
        "test \"atomic64 diff wrapper pins the current bounded runtime case groups\" {",
    );
    try expectMarker(
        atomic64_diff_source,
        "test \"atomic64 diff wrapper executes the bounded threshold replay through the shipped runtime gate\" {",
    );
    try expectMarker(
        atomic64_diff_source,
        "test \"atomic64 diff wrapper keeps the local perf-baseline survey aligned with threshold replay evidence\" {",
    );
    try expectMarker(
        atomic64_diff_source,
        "try std.testing.expectEqual(@as(usize, 27), countOccurrences(atomic64_diff_source, \"\\ntest \\\"\"));",
    );
}