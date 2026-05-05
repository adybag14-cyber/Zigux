const std = @import("std");
const runtime_atomic64_diff = @import("runtime_atomic64_diff.zig");
const runtime_atomic64_diff_source = @embedFile("runtime_atomic64_diff.zig");
const phase4_runtime_atomic64_manifest_source = @embedFile("phase4_runtime_atomic64_diff_manifest.json");
const phase4_build_source = @embedFile("phase4_build.zig");
const phase9_build_source = @embedFile("phase9_build.zig");

fn expectMarker(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
}

fn expectNoMarker(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, marker) == null);
}

test "atomic64 diff canonical wrapper keeps the shipped runtime gate wired in" {
    _ = runtime_atomic64_diff;
}

test "atomic64 diff wrapper records the current bounded runtime checks" {
    try expectMarker(
        runtime_atomic64_diff_source,
        "runtime atomic64 diff gate replays bounded atomic64_test.c exchange, cmpxchg, and add_unless expectations",
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
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"roadmap_target_path\": \"zigux/tests/atomic64_diff.zig\"");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"roadmap_atomic64_diff_present\": true");
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "\"live_gate_path\": \"zigux/tests/runtime_atomic64_diff.zig\"",
    );
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"phase4_build_present\": true");
    try expectMarker(phase4_runtime_atomic64_manifest_source, "\"phase9_build_present\": true");
    try expectMarker(
        phase4_runtime_atomic64_manifest_source,
        "\"threshold_posture\": \"threshold_pending_until_runtime_atomic64_scope_widens\"",
    );
}

test "atomic64 diff wrapper keeps the current phase4 and phase9 build routing explicit" {
    try expectMarker(phase4_build_source, ".root_source_file = b.path(\"atomic64_diff.zig\")");
    try expectMarker(phase4_build_source, "phase4-runtime-atomic64-diff-tests");
    try expectNoMarker(phase4_build_source, ".root_source_file = b.path(\"runtime_atomic64_diff.zig\")");
    try expectMarker(phase9_build_source, ".root_source_file = b.path(\"runtime_atomic64_diff.zig\")");
    try expectMarker(phase9_build_source, "phase9-runtime-atomic64-diff-tests");
}
