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
    try requireMarkerCount("\"acceptable_limit_iterations\": 4", 1);
    try requireMarkerCount("\"acceptable_limit_sample_count\": 7", 1);
    try std.testing.expectEqual(@as(u64, 4), @as(u64, 4));
    try std.testing.expectEqual(@as(u64, 7), @as(u64, 7));
}

test "phase4 perf baseline survey keeps dedicated local-only ownership and command evidence explicit" {
    try requireMarker("\"owner\": \"Validation and Perf Team\"");
    try requireMarker("\"benchmark_command\": \"zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig\"");
    try requireMarker("\"linux_style_wrapper\": \"make -C zigux phase4-perf-baseline-survey\"");
    try requireMarker("\"checksum\": 5216946504564592253");
    try requireMarker("\"checksum\": 7942141539243507472");
    try requireMarker("\"final_first_zero\": 109");
}

test "phase4 perf baseline survey keeps rollback and decision ownership explicit" {
    try requireMarker("\"rollback_owner\": \"Validation and Perf Team\"");
    try requireMarker("\"decision_owner\": \"Validation and Perf Team\"");
    try requireMarker("\"local_only_posture_note\": \"The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.\"");
}

test "phase4 perf baseline survey keeps the dedicated packet contract reviewable" {
    try requireMarker("\"id\": \"phase4-perf-baseline-shared-promotion-decision\"");
    try requireMarker("\"status\": \"shared CI perf promotion pending\"");
    try requireMarker("\"coordination_owners\": [");
}
