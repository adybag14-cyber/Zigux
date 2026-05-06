const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

const SurveySummary = struct {
    argv_split_c_lines: usize,
    preexisting_phase7_test_files: usize,
    preexisting_phase7_fixture_modules: usize,
    preexisting_phase7_build_present: bool,
    preexisting_phase7_doc_present: bool,
    preexisting_phase7_helper_present: bool,
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
        std.mem.eql(u8, status, "ready_next");
}

test "phase 7 argv_split survey manifest records the parked runtime leaf surface without an active follow-up" {
    const allocator = std.testing.allocator;

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_argv_split_manifest.json");
    defer allocator.free(manifest_json);

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-argv-split-slice.md");
    defer allocator.free(slice_note);

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_argv_split.zig");
    defer allocator.free(helper_tests);

    const fixture_module = try readRepoFile(allocator, "zigux/tests/fixtures/phase7_argv_split_vectors.zig");
    defer allocator.free(fixture_module);

    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-argv-split-packet.py");
    defer allocator.free(checker);

    const scripts_root = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_root);

    const tests_root = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_root);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P7-Y07", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("d198f036eb3ef64b2c5fb5ff3f52ed596e8adfa9", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("lib/argv_split.c", manifest.anchor);
    try std.testing.expect(std.mem.containsAtLeast(u8, slice_note, 1, "PHASE7_LANE_KEY=P7-Y07"));
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("lib/argv_split.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqual(@as(usize, 95), manifest.survey_summary.argv_split_c_lines);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_test_files);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_fixture_modules);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_helper_present);
    try std.testing.expectEqual(@as(usize, 7), manifest.gaps.len);

    try expectContains(slice_note, "first-NUL C-string bounds on both counting and splitting");
    try expectContains(slice_note, "strict non-goal behavior where quote characters stay inside the returned tokens");
    try expectContains(slice_note, "blank-input sentinel reuse and repeatable teardown through both `deinit()` and `argvFree()`");
    try expectContains(slice_note, "zigux/tests/fixtures/phase7_argv_split_vectors.zig");
    try expectContains(slice_note, "python3 scripts/zigux/check-phase7-argv-split-packet.py");

    try expectContains(build_file, "\"phase7_argv_split.zig\"");
    try expectContains(build_file, "\"phase7_argv_split_survey.zig\"");
    try expectContains(build_file, "\"phase7-argv-split-tests\"");
    try expectContains(build_file, "\"phase7-argv-split-survey-tests\"");
    try expectContains(build_file, "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));");

    try expectContains(helper_tests, "const phase7_vectors = @import(\"fixtures/phase7_argv_split_vectors.zig\");");
    try expectContains(helper_tests, "phase 7 argvSplit matches focused parity fixtures");
    try expectContains(helper_tests, "phase 7 blank argvSplit input reuses the empty exported argv view");
    try expectContains(helper_tests, "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space");
    try expectContains(helper_tests, "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable");
    try expectContains(helper_tests, "phase 7 argvSplit deinit clears exported storage and argv views");
    try expectContains(helper_tests, "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable");
    try expectContains(helper_tests, "split.cArgv()");

    try expectContains(fixture_module, ".name = \"whitespace before first NUL stays blank\",");
    try expectContains(fixture_module, ".name = \"leading NUL truncates to zero argv entries\",");
    try expectContains(fixture_module, ".name = \"first NUL stops counting and splitting\",");
    try expectContains(fixture_module, ".name = \"quote characters stay inside returned tokens\",");

    try expectContains(checker, "\"zigux/tests/phase7_argv_split.zig\"");
    try expectContains(checker, "\"zigux/tests/phase7_argv_split_survey.zig\"");
    try expectContains(checker, "\"zigux/tests/phase7_argv_split_manifest.json\"");
    try expectContains(checker, "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\"");

    try expectContains(scripts_root, "zigux/tests/phase7_argv_split_survey.zig");
    try expectContains(scripts_root, "zigux/tests/phase7_argv_split_manifest.json");
    try expectContains(scripts_root, "scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(scripts_root, "make -C zigux phase7-validate");
    try expectContains(scripts_root, "make -C zigux phase7");

    try expectContains(tests_root, "`scripts/zigux/check-phase7-argv-split-packet.py`");
    try expectContains(tests_root, "the dedicated `zigux/tests/phase7_argv_split_survey.zig` argvSplit survey gate");
    try expectContains(tests_root, "`make -C zigux phase7-validate`");
    try expectContains(tests_root, "`make -C zigux phase7`");

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_helper = false;
    var saw_survey_gate = false;
    var saw_packet_checker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase7-argv-split-helper")) {
            saw_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/argv_split.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-argv-split-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase7_argv_split_survey.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-argv-split-packet-checker")) {
            saw_packet_checker = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("scripts/zigux/check-phase7-argv-split-packet.py", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try std.testing.expectEqual(manifest.gaps.len, starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(saw_helper);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_packet_checker);
}
