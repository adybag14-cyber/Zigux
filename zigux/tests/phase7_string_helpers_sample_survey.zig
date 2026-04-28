const std = @import("std");

const SurveySummary = struct {
    string_helpers_c_lines: usize,
    preexisting_phase7_test_files: usize,
    preexisting_phase7_fixture_modules: usize,
    preexisting_phase7_build_present: bool,
    preexisting_phase7_doc_present: bool,
    preexisting_phase7_helper_present: bool,
    preexisting_phase7_sample_present: bool,
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
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked");
}

test "phase 7 string helper sample survey manifest records the bounded sample-backed review packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_string_helpers_sample_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P5-L17", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("49760085b479c32864eb6ab5dc9a03b36b2f1ea7", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("lib/string_helpers.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("lib/string_helpers.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("samples/zigux/string_helpers_sample.zig", manifest.roadmap_destinations[1]);
    try std.testing.expectEqual(@as(usize, 1047), manifest.survey_summary.string_helpers_c_lines);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_test_files);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_fixture_modules);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_helper_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_sample_present);
    try std.testing.expect(manifest.gaps.len >= 7);

    var starter_landed_count: usize = 0;
    var saw_helper = false;
    var saw_fixture_layer = false;
    var saw_sample_replay = false;
    var saw_sample_survey_gate = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase7-string-helpers-helper")) {
            saw_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/string_helpers.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-string-helpers-shared-fixtures")) {
            saw_fixture_layer = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-string-helpers-sample-replay")) {
            saw_sample_replay = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/string_helpers_sample.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-string-helpers-sample-survey-gate")) {
            saw_sample_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase7_string_helpers_sample_survey.zig", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try std.testing.expectEqual(@as(usize, 7), starter_landed_count);
    try std.testing.expect(saw_helper);
    try std.testing.expect(saw_fixture_layer);
    try std.testing.expect(saw_sample_replay);
    try std.testing.expect(saw_sample_survey_gate);
}
