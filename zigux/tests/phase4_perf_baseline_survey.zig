const std = @import("std");

const baseline_packet = @embedFile("phase4_perf_baseline_manifest.json");

fn requireMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, baseline_packet, marker) != null);
}

fn requireMarkerCount(marker: []const u8, expected: usize) !void {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, baseline_packet, start, marker)) |idx| {
        count += 1;
        start = idx + marker.len;
    }
    try std.testing.expectEqual(expected, count);
}

test "phase4 perf baseline survey keeps exact local-only iteration and sample counts explicit" {
    try requireMarkerCount("\"acceptable_limit_iterations\": 4", 2);
    try requireMarkerCount("\"acceptable_limit_sample_count\": 7", 2);
    try requireMarkerCount("\"sample_count_note\": \"seven monotonic samples\"", 2);
    try requireMarkerCount("\"acceptable_limit_status\": \"approved_local_only\"", 2);
    try requireMarkerCount("\"acceptable_limit_metric\": \"median_elapsed_ns\"", 2);
    try std.testing.expectEqual(@as(u64, 4), @as(u64, 4));
    try std.testing.expectEqual(@as(u64, 7), @as(u64, 7));
}

test "phase4 perf baseline survey keeps atomic64 and bitmap command evidence explicit" {
    try requireMarker("\"owner\": \"Validation and Perf Team\"");
    try requireMarker("\"benchmark_command\": \"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\"");
    try requireMarker("\"benchmark_command\": \"zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig\"");
    try requireMarker("\"linux_style_wrapper\": \"make -C zigux phase4-perf-baseline-survey\"");
    try requireMarker("\"acceptable_limit_max_elapsed_ns\": 8192");
    try requireMarker("\"acceptable_limit_max_elapsed_ns\": 12288");
    try requireMarker("\"checksum\": 3626254113632800175");
    try requireMarker("\"checksum\": 9210681150676220922");
    try requireMarker("\"final_counter\": 130322557735600377");
    try requireMarker("\"final_counter\": 130322557735600376");
    try requireMarker("\"checksum\": 5216946504564592253");
    try requireMarker("\"checksum\": 7942141539243507472");
    try requireMarkerCount("\"final_first_zero\": 109", 2);
}

test "phase4 perf baseline survey keeps rollback, decision, and wrapper ownership explicit" {
    try requireMarker("\"lane_key\": \"P4-L20\"");
    try requireMarker("\"phase\": \"Phase 4\"");
    try requireMarker("\"rollback_owner\": \"Validation and Perf Team\"");
    try requireMarker("\"decision_owner\": \"Validation and Perf Team\"");
    try requireMarker("\"dedicated_local_survey_wrapper\": \"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\"");
    try requireMarker("\"dedicated_linux_style_survey_wrapper\": \"make -C zigux phase4-perf-baseline-survey\"");
    try requireMarker("\"validation_entrypoint\": \"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\"");
    try requireMarker("\"bootstrap_ci_posture\": \"reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow\"");
    try requireMarker("\"shared_ci_perf_promotion_status\": \"pending\"");
    try requireMarker("\"local_only_posture_note\": \"The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.\"");
}

test "phase4 perf baseline survey keeps the dedicated packet contract reviewable" {
    try requireMarker("\"id\": \"phase4-perf-baseline-shared-promotion-decision\"");
    try requireMarker("\"status\": \"shared CI perf promotion pending\"");
    try requireMarker("\"coordination_owners\": [");
    try requireMarker("\"ABI and Runtime Team\"");
    try requireMarker("\"Shared Subsystems Pod\"");
}
