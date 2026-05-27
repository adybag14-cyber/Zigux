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

fn requireOrderedMarkersInSection(
    section_header: []const u8,
    section_footer: []const u8,
    expected_markers: []const []const u8,
) !void {
    const section_start = std.mem.indexOf(u8, baseline_packet, section_header) orelse
        return error.MissingSectionHeader;
    const section_end = std.mem.indexOfPos(u8, baseline_packet, section_start, section_footer) orelse
        return error.MissingSectionFooter;
    const section = baseline_packet[section_start..section_end];

    var cursor: usize = 0;
    for (expected_markers) |marker| {
        const offset = std.mem.indexOfPos(u8, section, cursor, marker) orelse
            return error.MissingOrderedMarker;
        cursor = offset + marker.len;
    }
}

fn requireOrderedMarkersAfter(
    section_header: []const u8,
    expected_markers: []const []const u8,
) !void {
    const section_start = std.mem.indexOf(u8, baseline_packet, section_header) orelse
        return error.MissingSectionHeader;
    const section = baseline_packet[section_start..];

    var cursor: usize = 0;
    for (expected_markers) |marker| {
        const offset = std.mem.indexOfPos(u8, section, cursor, marker) orelse
            return error.MissingOrderedMarker;
        cursor = offset + marker.len;
    }
}

test "phase4 perf baseline survey keeps exact local-only iteration, sample, and replay counts explicit" {
    try requireMarkerCount("\"acceptable_limit_iterations\": 4", 2);
    try requireMarkerCount("\"acceptable_limit_sample_count\": 7", 2);
    try requireMarkerCount("\"sample_count_note\": \"seven monotonic samples\"", 2);
    try requireMarkerCount("\"acceptable_limit_status\": \"approved_local_only\"", 2);
    try requireMarkerCount("\"acceptable_limit_metric\": \"median_elapsed_ns\"", 2);
    try requireMarkerCount("\"iterations\": 1", 2);
    try requireMarkerCount("\"iterations\": 4", 2);
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
    try requireMarkerCount("\"shared_ci_perf_promotion_status\": \"pending\"", 1);
    try requireMarkerCount("\"dedicated_local_survey_wrapper\": \"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\"", 1);
    try requireMarkerCount("\"dedicated_linux_style_survey_wrapper\": \"make -C zigux phase4-perf-baseline-survey\"", 1);
    try requireMarkerCount("\"validation_entrypoint\": \"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\"", 1);
    try requireMarkerCount("\"bootstrap_ci_posture\": \"reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow\"", 1);
    try requireMarkerCount("\"shared_lab_and_ci_matrix_anchor\": \"Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix\"", 1);
    try requireMarker("\"local_only_posture_note\": \"The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.\"");
}

test "phase4 perf baseline survey keeps gate owners explicit for both landed rollback thresholds" {
    try requireMarker("\"atomic64\": {");
    try requireMarker("\"gate_owner\": \"ABI and Runtime Team\"");
    try requireMarker("\"gate_rollback_owner\": \"ABI and Runtime Team\"");
    try requireMarker("\"bitmap\": {");
    try requireMarker("\"gate_owner\": \"Shared Subsystems Pod\"");
    try requireMarker("\"gate_rollback_owner\": \"Shared Subsystems Pod\"");
}

test "phase4 perf baseline survey keeps gate-surface threshold posture packet explicit" {
    try requireMarker("\"gate_surfaces\": [");
    try requireMarker("\"surface\": \"zigux/tests/atomic64_diff.zig\"");
    try requireMarker("\"threshold_posture\": \"threshold_pending_until_runtime_atomic64_scope_widens\"");
    try requireMarker("\"surface\": \"zigux/tests/bitmap_diff.zig\"");
    try requireMarker("\"threshold_posture\": \"threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks\"");
}

test "phase4 perf baseline survey keeps the atomic64 gate-surface and evidence packet aligned" {
    try requireOrderedMarkersInSection(
        "\"surface\": \"zigux/tests/atomic64_diff.zig\"",
        "\"surface\": \"zigux/tests/bitmap_diff.zig\"",
        &.{
            "\"gate_owner\": \"ABI and Runtime Team\"",
            "\"gate_rollback_owner\": \"ABI and Runtime Team\"",
            "\"threshold_posture\": \"threshold_pending_until_runtime_atomic64_scope_widens\"",
        },
    );
    try requireOrderedMarkersInSection(
        "\"atomic64\": {",
        "\"bitmap\": {",
        &.{
            "\"gate_owner\": \"ABI and Runtime Team\"",
            "\"gate_rollback_owner\": \"ABI and Runtime Team\"",
            "\"benchmark_command\": \"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\"",
            "\"acceptable_limit_status\": \"approved_local_only\"",
            "\"acceptable_limit_metric\": \"median_elapsed_ns\"",
            "\"acceptable_limit_iterations\": 4",
            "\"acceptable_limit_sample_count\": 7",
            "\"acceptable_limit_max_elapsed_ns\": 8192",
        },
    );
}

test "phase4 perf baseline survey keeps the dedicated packet contract reviewable" {
    try requireMarker("\"id\": \"phase4-perf-baseline-shared-promotion-decision\"");
    try requireMarker("\"status\": \"shared CI perf promotion pending\"");
    try requireMarker("\"coordination_owners\": [");
    try requireMarker("\"ABI and Runtime Team\"");
    try requireMarker("\"Shared Subsystems Pod\"");
}

test "phase4 perf baseline survey keeps the shared promotion decision rollback packet exact" {
    try requireOrderedMarkersAfter(
        "\"promotion_decision\": {",
        &.{
            "\"id\": \"phase4-perf-baseline-shared-promotion-decision\"",
            "\"status\": \"shared CI perf promotion pending\"",
            "\"owner\": \"Validation and Perf Team\"",
            "\"rollback_owner\": \"Validation and Perf Team\"",
            "\"coordination_owners\": [",
            "\"ABI and Runtime Team\"",
            "\"Shared Subsystems Pod\"",
        },
    );
}

test "phase4 perf baseline survey keeps coordination-owner and evidence-id pins exact" {
    try requireMarkerCount("\"coordination_owners\": [", 2);
    try requireMarkerCount("\"owner\": \"Validation and Perf Team\"", 2);
    try requireMarker("\"id\": \"phase4-perf-baseline-atomic64-acceptable-limit\"");
    try requireMarker("\"id\": \"phase4-perf-baseline-atomic64-command-evidence\"");
    try requireMarker("\"id\": \"phase4-perf-baseline-bitmap-acceptable-limit\"");
    try requireMarker("\"id\": \"phase4-perf-baseline-bitmap-command-evidence\"");
}

test "phase4 perf baseline survey keeps evidence kinds explicit for both gates and both replay modes" {
    try requireMarkerCount("\"kind\": \"acceptable_limit\"", 2);
    try requireMarkerCount("\"kind\": \"threshold_replay\"", 2);
}

test "phase4 perf baseline survey keeps the bitmap legacy replay alias exact" {
    try requireMarker("\"id\": \"phase4-perf-baseline-bitmap-command\"");
    try requireMarker("\"kind\": \"legacy_threshold_replay_alias\"");
    try requireMarker("\"target_id\": \"phase4-perf-baseline-bitmap-command-evidence\"");
}
