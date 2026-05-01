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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
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

    const sample_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/string_helpers_sample.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(sample_source);

    const helper_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/string_helpers.zig",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(helper_source);

    const fixture_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(fixture_source);

    const build_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_source);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-string-helpers-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

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
    try std.testing.expectEqual(@as(usize, 7), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var saw_helper = false;
    var saw_fixture_layer = false;
    var saw_sample_replay = false;
    var saw_sample_survey_gate = false;
    var saw_slice_note = false;

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

        if (std.mem.eql(u8, gap.id, "phase7-string-helpers-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase7-string-helpers-slice.md", gap.zigux_destination);
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
    try std.testing.expect(saw_slice_note);

    const expected_focuses = [_][]const u8{
        "newline_tolerant_matching",
        "bounded_size_rendering",
        "deterministic_escape_subset",
        "non_allocating_runtime_safe",
    };
    for (expected_focuses) |focus| {
        try expectContains(sample_source, focus);
    }

    const expected_sample_markers = [_][]const u8{
        "pub const SampleDescriptor",
        "pub fn init(self: *Self) !void",
        "pub fn runAnchorReplay(self: *Self) !ReplaySummary",
        "pub fn exit(self: *Self) !void",
        "string_helpers.sysfsStreq",
        "string_helpers.sysfsMatchString",
        "string_helpers.stringGetSize",
        "string_helpers.stringUnescape",
        "string_helpers.stringEscapeMem",
        ".stage_before_replay = .initialized",
        ".stage_after_replay = self.stage()",
    };
    for (expected_sample_markers) |marker| {
        try expectContains(sample_source, marker);
    }

    const expected_helper_markers = [_][]const u8{
        "pub fn sysfsStreq",
        "pub fn sysfsMatchString",
        "pub fn stringGetSize",
        "pub fn stringUnescape",
        "pub fn stringEscapeMem",
        "test \"stringEscapeMem covers the bounded Linux escape classes\"",
        "test \"stringEscapeMem honors only and append selection rules\"",
    };
    for (expected_helper_markers) |marker| {
        try expectContains(helper_source, marker);
    }

    const expected_fixture_markers = [_][]const u8{
        "pub const UnescapeCase",
        "pub const EscapeCase",
        "pub const unescape_cases",
        "pub const escape_cases",
        "space escapes",
        "dictionary-limited space escaping",
        "append dictionary entries with hex escaping",
    };
    for (expected_fixture_markers) |marker| {
        try expectContains(fixture_source, marker);
    }

    const expected_build_markers = [_][]const u8{
        "../../samples/zigux/string_helpers_sample.zig",
        "phase7-string-helpers-sample-tests",
        "phase7-string-helpers-sample-survey-tests",
        "phase7_string_helpers_sample_survey.zig",
        "test_step.dependOn(&run_string_helpers_sample_tests.step);",
        "test_step.dependOn(&run_string_helpers_sample_survey_tests.step);",
    };
    for (expected_build_markers) |marker| {
        try expectContains(build_source, marker);
    }

    const expected_doc_markers = [_][]const u8{
        "shared deterministic escape fixtures, bounded sample replay, and manifest-backed survey evidence landed",
        "`samples/zigux/string_helpers_sample.zig`",
        "`zigux/tests/phase7_string_helpers_sample_manifest.json`",
        "`zigux/tests/phase7_string_helpers_sample_survey.zig`",
        "the bounded `samples/zigux/string_helpers_sample.zig` replay for descriptor ownership, lifecycle transitions, newline-tolerant matching, binary size rendering, and deterministic hex escaping",
        "the manifest-backed `zigux/tests/phase7_string_helpers_sample_survey.zig` gate so the helper, shared fixtures, sample replay, and slice note stay aligned",
    };
    for (expected_doc_markers) |marker| {
        try expectContains(slice_note, marker);
    }
}
