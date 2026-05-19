const std = @import("std");
const escape_vectors = @import("fixtures/phase7_string_helpers_escape_vectors.zig");
const string_helpers_sample = @import("string_helpers_sample");
const string_helpers = @import("string_helpers");

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
    draft_review_packet_paths: []const []const u8,
    survey_summary: SurveySummary,
    sample_replay_contract: SampleReplayContract,
    verification_checks: []const []const u8,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked");
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

fn focusName(focus: string_helpers_sample.SampleFocus) []const u8 {
    return switch (focus) {
        .newline_tolerant_matching => "newline_tolerant_matching",
        .bounded_size_rendering => "bounded_size_rendering",
        .deterministic_escape_subset => "deterministic_escape_subset",
        .bounded_destination_discipline => "bounded_destination_discipline",
        .bounded_buffer_mutation => "bounded_buffer_mutation",
        .case_conversion_preview => "case_conversion_preview",
        .non_allocating_runtime_safe => "non_allocating_runtime_safe",
    };
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

fn expectExactCount(haystack: []const u8, needle: []const u8, expected_count: usize) !void {
    try std.testing.expectEqual(expected_count, countOccurrences(haystack, needle));
}

test "phase 7 string helper sample survey manifest records the bounded sample-backed review packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_string_helpers_sample_manifest.json",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const sample_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/string_helpers_sample.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(sample_source);

    const sample_root_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(sample_root_readme);

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
    try std.testing.expectEqualStrings("P5-L14", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("d9ef77ab8ba69735614b7b04e42d3335f002c708", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("lib/string_helpers.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("lib/string_helpers.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqual(@as(usize, 3), manifest.draft_review_packet_paths.len);
    const expected_draft_review_packet_paths = [_][]const u8{
        "samples/zigux/string_helpers_sample.zig",
        "zigux/tests/phase7_string_helpers_sample_survey.zig",
        "zigux/tests/phase7_string_helpers_sample_manifest.json",
    };
    for (expected_draft_review_packet_paths, 0..) |expected, index| {
        try std.testing.expectEqualStrings(expected, manifest.draft_review_packet_paths[index]);
    }
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
    try std.testing.expectEqual(@as(usize, 7), manifest.sample_replay_contract.checked_focus.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.sample_replay_contract.lifecycle_states.len);
    try std.testing.expectEqual(@as(usize, 14), manifest.sample_replay_contract.helper_call_markers.len);
    try std.testing.expectEqual(@as(usize, 24), manifest.sample_replay_contract.test_assertions.len);
    try std.testing.expectEqual(@as(usize, 18), manifest.verification_checks.len);

    const expected_focuses = [_][]const u8{
        "newline_tolerant_matching",
        "bounded_size_rendering",
        "deterministic_escape_subset",
        "bounded_destination_discipline",
        "bounded_buffer_mutation",
        "case_conversion_preview",
        "non_allocating_runtime_safe",
    };
    for (expected_focuses, 0..) |expected, index| {
        try std.testing.expectEqualStrings(expected, manifest.sample_replay_contract.checked_focus[index]);
    }

    const expected_lifecycle_states = [_][]const u8{
        "cold",
        "initialized",
        "replay_complete",
        "exited",
    };
    for (expected_lifecycle_states, 0..) |expected, index| {
        try std.testing.expectEqualStrings(expected, manifest.sample_replay_contract.lifecycle_states[index]);
    }

    const expected_verification_checks = [_][]const u8{
        "descriptor stays `string_helpers_sample` and anchors to `lib/string_helpers.c`",
        "lifecycle starts at `cold`, `init()` moves to `initialized`, replay moves to `replay_complete`, and `exit()` finishes at `exited`",
        "`runAnchorReplay()` rejects calls before `init()` with `error.InvalidLifecycleTransition`",
        "`sysfsStreq(\"mode\", \"mode\\n\")` returns `true` for newline-tolerant matching",
        "`sysfsMatchString([disabled, enabled, null, ignored], \"enabled\\n\")` returns index `1`",
        "`matchString([disabled, enabled], \"ignored\")` returns `-EINVAL` when the bounded table misses",
        "`stringGetSize(1536, 1, STRING_UNITS_2)` renders `1.50 KiB` with reported length `8`",
        "`stringGetSize(1536, 1, STRING_UNITS_2 | STRING_UNITS_NO_SPACE | STRING_UNITS_NO_BYTES)` renders `1.50Ki` with reported length `6`",
        "in-place `strreplace(\"mode-ready\")` rewrites the replay buffer to `mode_ready`",
        "bounded `memcpyAndPad(\"xy\", count=2, pad='.')` fills the five-byte replay window as `xy...`",
        "bounded `stringUpper(\"miXeD\")` and `stringLower(\"HeLP\")` previews render `MIXED` and `help` through fixed destinations",
        "`stringUnescape(\"line\\\\n\")` produces `line` plus a trailing newline byte",
        "exact-fit `stringUnescape(\"\\\\n\", size=2)` returns length `1` and leaves a trailing NUL terminator",
        "`stringEscapeMem(\"\\n\", ESCAPE_HEX)` produces `\\\\x0a`",
        "bounded `stringEscapeMem(\"\\n\", dst[0..5], ESCAPE_HEX)` reports length `4` and leaves the untouched `?` sentinel in `\\\\x0a?`",
        "dictionary-limited `stringEscapeMem(\"A\\n\\tZ\", ESCAPE_SPACE, only=\"\\n\")` produces `A\\\\n\\tZ`",
        "append-selected `stringEscapeMem(\"A\\nZ\", ESCAPE_NAP | ESCAPE_HEX | ESCAPE_APPEND, only=\"\\n\")` produces `A\\\\x0aZ`",
        "the replay records exactly seven checked focus markers",
    };
    for (expected_verification_checks, 0..) |expected, index| {
        try std.testing.expectEqualStrings(expected, manifest.verification_checks[index]);
    }

    for (manifest.sample_replay_contract.helper_call_markers) |marker| {
        try expectExactCount(sample_source, marker, 1);
    }
    for (manifest.sample_replay_contract.test_assertions) |assertion| {
        try expectExactCount(sample_source, assertion, 1);
    }

    try expectExactCount(sample_source, ".name = \"string_helpers_sample\"", 1);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "_ = string_helpers.strreplace(replaced_text.bytes[0..11], '-', '_');") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "string_helpers.memcpyAndPad(padded_text.bytes[0..5], \"xy\", 2, '.');") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "bounded_escape_text.bytes[0..5],") != null);
    try expectExactCount(sample_root_readme, "Separate helper-backed sample packet", 1);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "pub fn strreplace") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "pub fn memcpyAndPad") != null);
    try expectExactCount(fixture_source, "sample replay newline hex escape", 1);
    try expectExactCount(fixture_source, "sample replay exact-fit newline", 1);
    try expectExactCount(build_source, "phase7-string-helpers-sample-tests", 1);
    try expectExactCount(build_source, "string_helpers_sample_survey_root_module.addImport(\"string_helpers_sample\", string_helpers_sample_module);", 1);
    try expectExactCount(slice_note, "`samples/zigux/string_helpers_sample.zig`", 2);
}

test "phase 7 string helper sample survey replays the shared fixture-backed outputs directly" {
    const newline_suffix = try findUniqueUnescapeCase("sample replay newline suffix");
    const exact_fit_newline = try findUniqueUnescapeCase("sample replay exact-fit newline");
    const newline_hex_escape = try findUniqueEscapeCase("sample replay newline hex escape");
    const selected_newline_escape = try findUniqueEscapeCase("dictionary-limited space escaping");
    const append_newline_hex_escape = try findUniqueEscapeCase("append dictionary entries with hex escaping");
    const values = [_]?[]const u8{ "disabled", "enabled", null, "ignored" };
    const expected_focuses = [_][]const u8{
        "newline_tolerant_matching",
        "bounded_size_rendering",
        "deterministic_escape_subset",
        "bounded_destination_discipline",
        "bounded_buffer_mutation",
        "case_conversion_preview",
        "non_allocating_runtime_safe",
    };

    try std.testing.expectEqualStrings("line\\n", newline_suffix.input);
    try std.testing.expectEqual(string_helpers.UNESCAPE_SPACE, newline_suffix.flags);
    try std.testing.expectEqualSlices(u8, "\\n", exact_fit_newline.input);
    try std.testing.expectEqual(string_helpers.UNESCAPE_SPACE, exact_fit_newline.flags);
    try std.testing.expectEqualSlices(u8, "\n", newline_hex_escape.input);
    try std.testing.expectEqual(string_helpers.ESCAPE_HEX, newline_hex_escape.flags);
    try std.testing.expect(newline_hex_escape.only == null);
    try std.testing.expectEqualSlices(u8, "A\n\tZ", selected_newline_escape.input);
    try std.testing.expectEqual(string_helpers.ESCAPE_SPACE, selected_newline_escape.flags);
    try std.testing.expect(selected_newline_escape.only != null);
    try std.testing.expectEqualSlices(u8, "\n", selected_newline_escape.only.?);
    try std.testing.expectEqualSlices(u8, "A\nZ", append_newline_hex_escape.input);
    try std.testing.expectEqual(string_helpers.ESCAPE_NAP | string_helpers.ESCAPE_HEX | string_helpers.ESCAPE_APPEND, append_newline_hex_escape.flags);
    try std.testing.expect(append_newline_hex_escape.only != null);
    try std.testing.expectEqualSlices(u8, "\n", append_newline_hex_escape.only.?);

    var sample = string_helpers_sample.StringHelpersSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqual(string_helpers_sample.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(string_helpers_sample.SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expect(replay.comparable_match);
    try std.testing.expectEqual(@as(i32, 1), replay.matched_index);
    try std.testing.expectEqual(string_helpers.EINVAL, string_helpers.matchString(&values, 2, "ignored"));
    try std.testing.expectEqual(@as(usize, expected_focuses.len), replay.checked_focus.len);
    for (replay.checked_focus, expected_focuses, 0..) |focus, expected, index| {
        _ = index;
        try std.testing.expectEqualStrings(expected, focusName(focus));
    }
    try std.testing.expectEqual(@as(usize, 8), replay.size_text.len);
    try std.testing.expectEqualSlices(u8, "1.50 KiB", replay.size_text.bytes[0..replay.size_text.len]);
    try std.testing.expectEqualSlices(u8, "1.50Ki", replay.compact_size_text.bytes[0..replay.compact_size_text.len]);
    try std.testing.expectEqualSlices(u8, "mode_ready", replay.replaced_text.bytes[0..replay.replaced_text.len]);
    try std.testing.expectEqual(@as(usize, 5), replay.padded_text.len);
    try std.testing.expectEqualSlices(u8, "xy...", replay.padded_text.bytes[0..replay.padded_text.len]);
    try std.testing.expectEqualSlices(u8, "MIXED", replay.upper_text.bytes[0..replay.upper_text.len]);
    try std.testing.expectEqualSlices(u8, "help", replay.lower_text.bytes[0..replay.lower_text.len]);
    try std.testing.expectEqual(newline_suffix.expected_len, replay.unescaped_text.len);
    try std.testing.expectEqualSlices(u8, newline_suffix.expected, replay.unescaped_text.bytes[0..replay.unescaped_text.len]);
    try std.testing.expectEqual(exact_fit_newline.expected_len, replay.exact_unescape_text.len);
    try std.testing.expectEqualSlices(u8, exact_fit_newline.expected, replay.exact_unescape_text.bytes[0..replay.exact_unescape_text.len]);
    try std.testing.expectEqual(@as(u8, 0), replay.exact_unescape_text.bytes[replay.exact_unescape_text.len]);
    try std.testing.expectEqual(newline_hex_escape.expected_len, replay.escaped_text.len);
    try std.testing.expectEqualSlices(u8, newline_hex_escape.expected, replay.escaped_text.bytes[0..replay.escaped_text.len]);
    try std.testing.expectEqual(@as(usize, 4), replay.bounded_escape_text.len);
    try std.testing.expectEqualSlices(u8, "\\x0a?", replay.bounded_escape_text.bytes[0..5]);
    try std.testing.expectEqual(selected_newline_escape.expected_len, replay.selected_escape_text.len);
    try std.testing.expectEqualSlices(u8, selected_newline_escape.expected, replay.selected_escape_text.bytes[0..replay.selected_escape_text.len]);
    try std.testing.expectEqual(append_newline_hex_escape.expected_len, replay.appended_escape_text.len);
    try std.testing.expectEqualSlices(u8, append_newline_hex_escape.expected, replay.appended_escape_text.bytes[0..replay.appended_escape_text.len]);

    try sample.exit();
    try std.testing.expectEqual(string_helpers_sample.SampleStage.exited, sample.stage());
}
