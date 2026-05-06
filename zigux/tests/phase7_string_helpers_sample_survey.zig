const std = @import("std");
const escape_vectors = @import("fixtures/phase7_string_helpers_escape_vectors.zig");
const string_helpers_sample = @import("../../samples/zigux/string_helpers_sample.zig");

const SurveySummary = struct {
    string_helpers_c_lines: usize,
    preexisting_phase7_test_files: usize,
    preexisting_phase7_fixture_modules: usize,
    preexisting_phase7_build_present: bool,
    preexisting_phase7_doc_present: bool,
    preexisting_phase7_helper_present: bool,
    preexisting_phase7_sample_present: bool,
};

const SampleReplayContract = struct {
    descriptor_name: []const u8,
    matched_index: i32,
    checked_focus: []const []const u8,
    lifecycle_states: []const []const u8,
    helper_call_markers: []const []const u8,
    test_assertions: []const []const u8,
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
    sample_replay_contract: SampleReplayContract,
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

fn expectOrderedContains(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const index = std.mem.indexOfPos(u8, haystack, cursor, needle);
        try std.testing.expect(index != null);
        cursor = (index orelse unreachable) + needle.len;
    }
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var total: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        total += 1;
        cursor = index + needle.len;
    }
    return total;
}

fn findUniqueUnescapeCase(name: []const u8) !escape_vectors.UnescapeCase {
    var found: ?escape_vectors.UnescapeCase = null;

    for (escape_vectors.unescape_cases) |case| {
        if (std.mem.eql(u8, case.name, name)) {
            try std.testing.expect(found == null);
            found = case;
        }
    }

    try std.testing.expect(found != null);
    return found.?;
}

fn findUniqueEscapeCase(name: []const u8) !escape_vectors.EscapeCase {
    var found: ?escape_vectors.EscapeCase = null;

    for (escape_vectors.escape_cases) |case| {
        if (std.mem.eql(u8, case.name, name)) {
            try std.testing.expect(found == null);
            found = case;
        }
    }

    try std.testing.expect(found != null);
    return found.?;
}

test "phase 7 string helper sample survey manifest records the bounded sample-backed review packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_string_helpers_sample_manifest.json",
        std.testing.allocator,
        .limited(20 * 1024),
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
    try std.testing.expectEqualStrings("P5-L18", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("f5c88e925f37281428bf9fa1fb11eacee60b567a", manifest.surveyed_commit);
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

    try std.testing.expectEqualStrings("string_helpers_sample", manifest.sample_replay_contract.descriptor_name);
    try std.testing.expectEqual(@as(i32, 1), manifest.sample_replay_contract.matched_index);
    try std.testing.expectEqual(@as(usize, 4), manifest.sample_replay_contract.checked_focus.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.sample_replay_contract.lifecycle_states.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.sample_replay_contract.helper_call_markers.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.sample_replay_contract.test_assertions.len);

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

    try expectContains(sample_source, ".name = \"string_helpers_sample\"");
    try expectContains(sample_source, ".anchor = \"lib/string_helpers.c\"");
    try expectContains(sample_source, ".matched_index = string_helpers.sysfsMatchString(&values, values.len, \"enabled\\n\"),");
    try expectContains(sample_source, "const values = [_]?[]const u8{ \"disabled\", \"enabled\", null, \"ignored\" };");
    try expectContains(sample_source, "string_helpers.STRING_UNITS_2 | string_helpers.STRING_UNITS_NO_SPACE | string_helpers.STRING_UNITS_NO_BYTES,");
    try expectContains(sample_source, "string_helpers.ESCAPE_NAP | string_helpers.ESCAPE_HEX | string_helpers.ESCAPE_APPEND,");

    try expectOrderedContains(sample_source, manifest.sample_replay_contract.lifecycle_states);
    try expectOrderedContains(sample_source, manifest.sample_replay_contract.checked_focus);

    for (manifest.sample_replay_contract.helper_call_markers) |marker| {
        try expectContains(sample_source, marker);
    }
    for (manifest.sample_replay_contract.test_assertions) |marker| {
        try expectContains(sample_source, marker);
    }

    try std.testing.expectEqual(@as(usize, 2), countOccurrences(sample_source, "test \"string helper sample"));

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
        "sample replay newline suffix",
        ".input = \"line\\\\n\"",
        ".expected = \"line\\n\"",
        "sample replay newline hex escape",
        ".input = \"\\n\"",
        ".expected = \"\\\\x0a\"",
    };
    for (expected_fixture_markers) |marker| {
        try expectContains(fixture_source, marker);
    }
    try std.testing.expectEqual(@as(usize, 2), countOccurrences(fixture_source, "sample replay newline "));

    const expected_build_markers = [_][]const u8{
        "const repo_root = b.path(\"../..\");",
        "../../samples/zigux/string_helpers_sample.zig",
        "phase7-string-helpers-sample-tests",
        "phase7-string-helpers-sample-survey-tests",
        "phase7_string_helpers_sample_survey.zig",
        "string_helpers_sample_survey_root_module.addImport(\"string_helpers\", string_helpers_module);",
        "run_string_helpers_sample_survey_tests.setCwd(repo_root);",
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
        "the bounded `samples/zigux/string_helpers_sample.zig` replay for descriptor ownership, lifecycle transitions, newline-tolerant matching, binary size rendering, compact no-space-no-bytes formatting, and deterministic plus append-selected newline hex escaping",
        "the manifest-backed `zigux/tests/phase7_string_helpers_sample_survey.zig` gate so the helper, shared fixtures, sample replay, and slice note stay aligned in one reviewable packet after the added compact-format and append-selected escape proofs",
    };
    for (expected_doc_markers) |marker| {
        try expectContains(slice_note, marker);
    }
}

test "phase 7 string helper sample survey replays the shared fixture-backed outputs directly" {
    const newline_suffix = try findUniqueUnescapeCase("sample replay newline suffix");
    const newline_hex_escape = try findUniqueEscapeCase("sample replay newline hex escape");
    const append_newline_hex_escape = try findUniqueEscapeCase("append dictionary entries with hex escaping");

    var sample = string_helpers_sample.StringHelpersSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqual(@as(i32, 1), replay.matched_index);
    try std.testing.expectEqual(@as(usize, 4), replay.checked_focus.len);
    try std.testing.expectEqualSlices(u8, "1.50Ki", replay.compact_size_text.bytes[0..replay.compact_size_text.len]);
    try std.testing.expectEqual(newline_suffix.expected_len, replay.unescaped_text.len);
    try std.testing.expectEqualSlices(u8, newline_suffix.expected, replay.unescaped_text.bytes[0..replay.unescaped_text.len]);
    try std.testing.expectEqual(newline_hex_escape.expected_len, replay.escaped_text.len);
    try std.testing.expectEqualSlices(u8, newline_hex_escape.expected, replay.escaped_text.bytes[0..replay.escaped_text.len]);
    try std.testing.expectEqual(append_newline_hex_escape.expected_len, replay.appended_escape_text.len);
    try std.testing.expectEqualSlices(u8, append_newline_hex_escape.expected, replay.appended_escape_text.bytes[0..replay.appended_escape_text.len]);

    try sample.exit();
    try std.testing.expectEqual(string_helpers_sample.SampleStage.exited, sample.stage());
}
