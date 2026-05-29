const std = @import("std");

const shared_tests_build_source = @embedFile("build.zig");
const phase4_build_source = @embedFile("phase4_build.zig");
const atomic64_diff_source = @embedFile("atomic64_diff.zig");
const runtime_atomic64_manifest_source = @embedFile("phase4_runtime_atomic64_diff_manifest.json");

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

test "shared tests root keeps the Phase 4 atomic64 survey as the promoted route" {
    try expectMarker(shared_tests_build_source, "fn addPhase4RuntimeAtomic64DiffSurvey(");
    try expectMarker(shared_tests_build_source, "phase4_runtime_atomic64_diff_survey.zig");
    try expectMarker(shared_tests_build_source, "phase4-runtime-atomic64-diff-survey");
    try expectMarker(
        shared_tests_build_source,
        "Run the Phase 4 runtime atomic64 diff survey anchor from the shared tests root",
    );
    try expectMarker(
        shared_tests_build_source,
        "phase4_step.dependOn(&phase4_runtime_atomic64_diff_survey.step);",
    );
    try expectMarker(
        shared_tests_build_source,
        "smoke_step.dependOn(&phase4_runtime_atomic64_diff_survey.step);",
    );
    try expectMarker(
        shared_tests_build_source,
        "test_step.dependOn(&phase4_runtime_atomic64_diff_survey.step);",
    );
}

test "dedicated Phase 4 root keeps wrapper, runtime survey, and manifest routes together" {
    try expectMarker(phase4_build_source, ".root_source_file = b.path(\"atomic64_diff.zig\")");
    try expectMarker(phase4_build_source, ".root_source_file = b.path(\"phase4_runtime_atomic64_diff_survey.zig\")");
    try expectMarker(phase4_build_source, "phase4-runtime-atomic64-diff-tests");
    try expectMarker(phase4_build_source, "phase4-runtime-atomic64-diff-survey-tests");
    try expectMarker(phase4_build_source, "phase4-runtime-atomic64-diff");
    try expectMarker(phase4_build_source, "phase4-runtime-atomic64-diff-survey");
    try expectMarker(phase4_build_source, "Run the isolated Phase 4 runtime atomic64 diff replay");
    try expectMarker(phase4_build_source, "Run the manifest-backed Phase 4 runtime atomic64 handoff survey");
}

test "atomic64 wrapper continues to target the runtime replay and manifest packet" {
    try expectMarker(atomic64_diff_source, "const runtime_atomic64_diff = @import(\"runtime_atomic64_diff.zig\");");
    try expectMarker(atomic64_diff_source, "const runtime_atomic64_diff_source = @embedFile(\"runtime_atomic64_diff.zig\");");
    try expectMarker(atomic64_diff_source, "const phase4_runtime_atomic64_manifest_source = @embedFile(\"phase4_runtime_atomic64_diff_manifest.json\");");
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(atomic64_diff_source, "@import(\"runtime_atomic64_diff.zig\")"));
}

test "runtime atomic64 manifest names the same wrapper and runtime replay surfaces" {
    try expectMarker(runtime_atomic64_manifest_source, "\"roadmap_target_path\": \"zigux/tests/atomic64_diff.zig\"");
    try expectMarker(runtime_atomic64_manifest_source, "\"live_gate_path\": \"zigux/tests/runtime_atomic64_diff.zig\"");
    try expectMarker(runtime_atomic64_manifest_source, "\"runtime_replay_path\": \"zigux/tests/runtime_atomic64_diff.zig\"");
    try expectMarker(runtime_atomic64_manifest_source, "\"phase4_build_uses_atomic64_wrapper\": true");
    try expectMarker(runtime_atomic64_manifest_source, "\"phase4_validator_atomic64_diff_present\": true");
    try expectMarker(runtime_atomic64_manifest_source, "\"phase4_validator_runtime_atomic64_diff_present\": true");
    try expectMarker(runtime_atomic64_manifest_source, "\"rollback_owner\": \"ABI and Runtime Team\"");
}
