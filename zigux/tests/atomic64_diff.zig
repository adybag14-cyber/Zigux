const std = @import("std");

const runtime_atomic64_diff = @import("runtime_atomic64_diff.zig");

const atomic64_diff_source = @embedFile("atomic64_diff.zig");
const runtime_atomic64_diff_source = @embedFile("runtime_atomic64_diff.zig");
const phase4_runtime_atomic64_manifest_source = @embedFile("phase4_runtime_atomic64_diff_manifest.json");
const phase4_build_source = @embedFile("phase4_build.zig");
const phase4_makefile_source = @embedFile("../Makefile");
const phase9_build_source = @embedFile("phase9_build.zig");
const validate_phase4_source = @embedFile("../../scripts/zigux/validate-phase4.py");

comptime {
    _ = runtime_atomic64_diff;
}

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
    loop_header: []const u8,
    expected_case_count: usize,
) !void {
    const section_start = std.mem.indexOf(u8, runtime_atomic64_diff_source, group_header) orelse
        return error.MissingRuntimeCaseGroupHeader;
    const section_end = std.mem.indexOfPos(u8, runtime_atomic64_diff_source, section_start, loop_header) orelse
        return error.MissingRuntimeCaseGroupLoop;
    const section = runtime_atomic64_diff_source[section_start..section_end];
    try std.testing.expectEqual(expected_case_count, countOccurrences(section, ".name = "));
}

test "atomic64 diff wrapper keeps the current bounded runtime replay body reachable" {
    try expectMarker(
        runtime_atomic64_diff_source,
        "runtime atomic64 diff gate replays bounded atomic64_test.c exchange, cmpxchg, and add_unless expectations",
    );
    try expectMarker(
        runtime_atomic64_diff_source,
        "runtime atomic64 diff gate keeps selftest family coverage explicit",
    );
}

test "atomic64 diff wrapper stays a thin roadmap-facing entrypoint" {
    try expectMarker(
        atomic64_diff_source,
        "const runtime_atomic64_diff = @import(\"runtime_atomic64_diff.zig\");",
    );
    try expectMarker(
        atomic64_diff_source,
        "const runtime_atomic64_diff_source = @embedFile(\"runtime_atomic64_diff.zig\");",
    );
    try expectNoMarker(
        atomic64_diff_source,
        "const sample = @import(\"runtime_atomic64_sample\");",
    );
    try expectNoMarker(atomic64_diff_source, "const summary = try module.runSelftest();");
}

test "atomic64 diff wrapper keeps the current roadmap-gap manifest explicit" {
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"zigux/tests/atomic64_diff.zig\"");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"roadmap_atomic64_diff_present\": false");
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "\"live_gate_path\": \"zigux/tests/runtime_atomic64_diff.zig\"",
    );
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"phase4_build_present\": true");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"phase9_build_present\": true");
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "\"phase4_validator_runtime_atomic64_diff_present\": true",
    );
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "threshold_pending_until_runtime_atomic64_scope_widens",
    );
}

test "atomic64 diff wrapper records the current phase4 and phase9 build routing" {
    try expectMarker(phase4_build_source, ".root_source_file = b.path(\"runtime_atomic64_diff.zig\")");
    try expectMarker(phase4_build_source, "phase4-runtime-atomic64-diff-tests");
    try expectNoMarker(phase4_build_source, ".root_source_file = b.path(\"atomic64_diff.zig\")");
    try expectMarker(phase9_build_source, ".root_source_file = b.path(\"runtime_atomic64_diff.zig\")");
    try expectMarker(phase9_build_source, "phase9-runtime-atomic64-diff-tests");
}

test "atomic64 diff wrapper records the published phase4 make and validator packet" {
    try expectMarker(phase4_makefile_source, "PHONY += phase4-validate phase4-test phase4");
    try expectMarker(phase4_makefile_source, "phase4-validate:");
    try expectMarker(phase4_makefile_source, "scripts/zigux/validate-phase4.py");
    try expectMarker(phase4_makefile_source, "phase4-test:");
    try expectMarker(phase4_makefile_source, "zigux/tests/phase4_build.zig");
    try expectNoMarker(phase4_makefile_source, "phase4-runtime-atomic64-diff:");
    try expectMarker(validate_phase4_source, "\"zigux/tests/runtime_atomic64_diff.zig\"");
    try expectMarker(validate_phase4_source, "threshold_pending_until_runtime_atomic64_scope_widens");
    try expectMarker(validate_phase4_source, "\"zigux/tests/phase4_build.zig\"");
    try expectNoMarker(validate_phase4_source, "\"zigux/tests/atomic64_diff.zig\"");
}

test "atomic64 diff wrapper records the exact bounded runtime atomic64 checks that currently ship" {
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
    try expectMarker(runtime_atomic64_diff_source, "checked_returning_paths");
    try expectMarker(runtime_atomic64_diff_source, "checked_guard_paths");
    try expectMarker(runtime_atomic64_diff_source, "error.InvalidLifecycleTransition, module.swapCounter(7)");
}

test "atomic64 diff wrapper pins the currently shipped bounded runtime case-group counts" {
    try expectRuntimeCaseGroupCardinality(
        "const cases = [_]DiffCase{",
        "for (cases) |case| {",
        3,
    );
    try expectRuntimeCaseGroupCardinality(
        "const compare_swap_cases = [_]CompareSwapCase{",
        "for (compare_swap_cases) |case| {",
        2,
    );
    try expectRuntimeCaseGroupCardinality(
        "const add_unless_cases = [_]AddUnlessCase{",
        "for (add_unless_cases) |case| {",
        2,
    );
}
