const std = @import("std");
const runtime_atomic64_diff = @import("runtime_atomic64_diff.zig");
const runtime_atomic64_diff_source = @embedFile("runtime_atomic64_diff.zig");
const phase4_runtime_atomic64_manifest_source = @embedFile("phase4_runtime_atomic64_diff_manifest.json");
const phase4_build_source = @embedFile("phase4_build.zig");
const phase9_build_source = @embedFile("phase9_build.zig");
const validate_phase4_source = @embedFile("../../scripts/zigux/validate-phase4.py");
const phase4_validation_matrix_source = @embedFile("../../Documentation/zigux/phase4-validation-matrix.md");

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

fn atomic64MatrixSection() ![]const u8 {
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
    return phase4_validation_matrix_source[section_start..section_end];
}

fn expectAtomic64MatrixMarkerCount(marker: []const u8, expected_count: usize) !void {
    const section = try atomic64MatrixSection();
    try std.testing.expectEqual(expected_count, countOccurrences(section, marker));
}

test "atomic64 diff canonical wrapper keeps the shipped runtime gate wired in" {
    _ = runtime_atomic64_diff;
}

test "atomic64 diff wrapper records the current bounded runtime checks" {
    try expectMarker(
        runtime_atomic64_diff_source,
        "runtime atomic64 diff gate replays bounded atomic64_test.c exchange, cmpxchg, add_unless, and bitwise expectations",
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
    try expectMarker(runtime_atomic64_diff_source, "runtime atomic64 diff gate keeps selftest family coverage explicit");
}

test "atomic64 diff wrapper keeps the current manifest handoff explicit" {
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"lane_key\": \"P4-L04\"");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"roadmap_target_path\": \"zigux/tests/atomic64_diff.zig\"");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"roadmap_atomic64_diff_present\": true");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"roadmap_atomic64_wrapper_targets_runtime_diff\": true");
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "\"live_gate_path\": \"zigux/tests/runtime_atomic64_diff.zig\"",
    );
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
        "\"phase4_validator_blob_sha\": \"3391f01bbc676c8f4da25833bff07dd38b2542aa\"",
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
        "\"phase4_validation_matrix_blob_sha\": \"9f01421b7ca24c16808195ceef449d9bd5d06970\"",
    );
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "\"threshold_posture\": \"threshold_pending_until_runtime_atomic64_scope_widens\"",
    );
    try expectMarker(phase4_runtime_atomic64_manifest_source, "single bounded replay body");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "Phase 9 runtime packet");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "Phase 4 reviewer packet");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "current wrapper-first rollback surface");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "shared runtime replay body");
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

test "atomic64 diff wrapper keeps the shared phase4 validator packet explicit" {
    try expectMarker(validate_phase4_source, "\"zigux/tests/atomic64_diff.zig\"");
    try expectMarker(validate_phase4_source, "\"zigux/tests/runtime_atomic64_diff.zig\"");
    try expectMarker(validate_phase4_source, "\"zigux/tests/phase4_runtime_atomic64_diff_manifest.json\"");
    try expectMarker(validate_phase4_source, "\"zigux/tests/phase4_runtime_atomic64_diff_survey.zig\"");
    try expectMarker(validate_phase4_source, "PHASE4_RUNTIME_ATOMIC64_PACKET_CHECK");
    try expectMarker(validate_phase4_source, "phase4_runtime_atomic64_packet");
}

test "atomic64 diff wrapper keeps rollback ownership and threshold posture explicit" {
    try expectAtomic64MatrixMarkerCount("- owner: `ABI and Runtime Team`", 1);
    try expectAtomic64MatrixMarkerCount("- rollback owner: `ABI and Runtime Team`", 1);
    try expectAtomic64MatrixMarkerCount(
        "- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded exchange, cmpxchg, add_unless, and selftest-family replay set",
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
}

test "atomic64 diff wrapper pins the current bounded runtime case groups" {
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
        "for (bitwise_cases) |case| {",
        3,
    );
}
