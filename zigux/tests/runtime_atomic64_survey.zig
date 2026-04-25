const std = @import("std");

const SurveySummary = struct {
    atomic64_test_c_lines: usize,
    preexisting_runtime_test_files: usize,
    preexisting_samples_zigux_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_phase9_doc_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_runtime_substrate");
}

test "phase 9 runtime atomic64 survey records the pilot-module gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_atomic64_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P9-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.atomic64_test_c_lines >= 200);
    try std.testing.expectEqual(@as(usize, 0), manifest.survey_summary.preexisting_runtime_test_files);
    try std.testing.expect(!manifest.survey_summary.preexisting_samples_zigux_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase9_doc_present);
    try std.testing.expect(manifest.gaps.len >= 3);

    var runtime_test_destination_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.startsWith(u8, gap.zigux_destination, "zigux/tests/")) {
            runtime_test_destination_count += 1;
        } else {
            try std.testing.expect(std.mem.startsWith(u8, gap.zigux_destination, "samples/zigux/"));
        }

        if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_runtime_substrate")) {
            blocked_count += 1;
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try std.testing.expect(runtime_test_destination_count >= 2);
    try std.testing.expect(ready_next_count >= 2);
    try std.testing.expect(blocked_count >= 1);
}
