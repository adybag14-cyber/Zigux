const std = @import("std");

const active_lane_key = "P7-L09";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectStringSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) {
            return;
        }
    }
    try std.testing.expect(false);
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

const ArgvSplitPairCompile = struct {
    status: []const u8,
    paths: []const []const u8,
};

const SharedPhase7Build = struct {
    status: []const u8,
    readback_on_utc: []const u8,
    build_file: []const u8,
    reviewable_sibling_paths: []const []const u8,
};

const CurrentVerification = struct {
    verified_on_utc: []const u8,
    argv_split_pair_compile: ArgvSplitPairCompile,
    shared_phase7_build: SharedPhase7Build,
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
    current_verification: CurrentVerification,
    ownership_focus: []const []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next");
}

fn isLowerHexCommitId(value: []const u8) bool {
    if (value.len != 40) {
        return false;
    }

    for (value) |byte| {
        if (!std.ascii.isDigit(byte) and (byte < 'a' or byte > 'f')) {
            return false;
        }
    }

    return true;
}

test "phase 7 argv_split survey manifest records the parked runtime leaf surface without an active follow-up" {
    const allocator = std.testing.allocator;

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_argv_split_manifest.json");
    defer allocator.free(manifest_json);

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-argv-split-slice.md");
    defer allocator.free(slice_note);

    const helper_lane_note = try readRepoFile(allocator, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(helper_lane_note);

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);

    const scripts_root = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_root);

    const tests_root = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_root);

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_argv_split.zig");
    defer allocator.free(helper_tests);

    const fixture_module = try readRepoFile(allocator, "zigux/tests/fixtures/phase7_argv_split_vectors.zig");
    defer allocator.free(fixture_module);

    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-argv-split-packet.py");
    defer allocator.free(checker);

    const validate_phase7 = try readRepoFile(allocator, "scripts/zigux/validate-phase7.py");
    defer allocator.free(validate_phase7);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings(active_lane_key, manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expect(isLowerHexCommitId(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("lib/argv_split.c", manifest.anchor);
    try std.testing.expect(std.mem.containsAtLeast(u8, slice_note, 1, "PHASE7_LANE_KEY=P7-L09"));
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("lib/argv_split.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.current_verification.verified_on_utc.len != 0);
    try std.testing.expectEqualStrings("confirmed", manifest.current_verification.argv_split_pair_compile.status);
    try std.testing.expectEqual(@as(usize, 2), manifest.current_verification.argv_split_pair_compile.paths.len);
    try expectStringSliceContains(manifest.current_verification.argv_split_pair_compile.paths, "lib/argv_split.zig");
    try expectStringSliceContains(manifest.current_verification.argv_split_pair_compile.paths, "zigux/tests/phase7_argv_split.zig");
    try std.testing.expectEqualStrings("present_on_master", manifest.current_verification.shared_phase7_build.status);
    try std.testing.expect(manifest.current_verification.shared_phase7_build.readback_on_utc.len != 0);
    try std.testing.expectEqualStrings("zigux/tests/phase7_build.zig", manifest.current_verification.shared_phase7_build.build_file);
    try expectStringSliceContains(manifest.current_verification.shared_phase7_build.reviewable_sibling_paths, "lib/string_helpers.zig");
    try expectStringSliceContains(manifest.current_verification.shared_phase7_build.reviewable_sibling_paths, "zigux/tests/phase7_string_helpers.zig");
    try expectStringSliceContains(manifest.current_verification.shared_phase7_build.reviewable_sibling_paths, "lib/rbtree.zig");
    try expectStringSliceContains(manifest.current_verification.shared_phase7_build.reviewable_sibling_paths, "zigux/tests/phase7_rbtree.zig");
    try std.testing.expectEqual(@as(usize, 95), manifest.survey_summary.argv_split_c_lines);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_test_files);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_fixture_modules);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_helper_present);
    try std.testing.expectEqual(@as(usize, 7), manifest.gaps.len);

    try expectStringSliceContains(
        manifest.ownership_focus,
        "copied token-buffer ownership and later source-mutation isolation",
    );
    try expectStringSliceContains(
        manifest.ownership_focus,
        "owned-storage reuse keeps token pointers inside caller-managed storage",
    );
    try expectContains(slice_note, "first-NUL C-string bounds on both counting and splitting");
    try expectContains(slice_note, "strict non-goal behavior where quote characters stay inside the returned tokens");
    try expectContains(slice_note, "keep copied-buffer ownership so later source mutation does not affect split results");
    try expectContains(slice_note, "blank-input sentinel reuse and repeatable teardown through both `deinit()` and `argvFree()`");
    try expectContains(slice_note, "non-blank cross-result teardown safety where `deinit()` or `argvFree()` on one live split keeps a sibling caller's storage, argv slices, and exported `cArgv()` view intact");
    try expectContains(slice_note, "zigux/tests/fixtures/phase7_argv_split_vectors.zig");
    try expectContains(slice_note, "python3 scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(slice_note, "shared `phase7_build.zig` route is also back to a directly readable shared reminder instead of the older missing-sibling blocker wording");

    try expectContains(helper_lane_note, "argv-split packet, lane `P7-L09`:");
    try expectContains(helper_lane_note, "Documentation/zigux/phase7-argv-split-slice.md");
    try expectContains(helper_lane_note, "PHASE7_ARGV_SPLIT_LANE=P7-L09");
    try expectContains(helper_lane_note, "`P7-L09` owns only argv-split helper-local parity, fixture, survey, manifest, or reminder drift.");

    try expectContains(docs_root, "Documentation/zigux/phase7-argv-split-slice.md");
    try expectContains(docs_root, "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample");
    try expectContains(docs_root, "lib/argv_split.zig");
    try expectContains(docs_root, "scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(docs_root, "zigux/tests/phase7_build.zig");

    try expectContains(scripts_root, "scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(scripts_root, "zigux/tests/phase7_argv_split.zig");
    try expectContains(scripts_root, "zigux/tests/phase7_argv_split_survey.zig");
    try expectContains(scripts_root, "zigux/tests/phase7_argv_split_manifest.json");
    try expectContains(scripts_root, "zigux/tests/fixtures/phase7_argv_split_vectors.zig");
    try expectContains(scripts_root, "make -C zigux phase7-validate");
    try expectContains(scripts_root, "make -C zigux phase7");

    try expectContains(tests_root, "`scripts/zigux/check-phase7-argv-split-packet.py`");
    try expectContains(tests_root, "`zigux/tests/phase7_argv_split_survey.zig`");
    try expectContains(tests_root, "`zigux/tests/phase7_argv_split_manifest.json`");
    try expectContains(tests_root, "`zigux/tests/fixtures/phase7_argv_split_vectors.zig`");
    try expectContains(tests_root, "`make -C zigux phase7-validate`");
    try expectContains(tests_root, "`make -C zigux phase7`");

    try expectContains(samples_readme, "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample;");
    try expectContains(samples_readme, "Documentation/zigux/phase7-argv-split-slice.md");
    try expectContains(samples_readme, "lib/argv_split.zig");
    try expectContains(samples_readme, "zigux/tests/phase7_argv_split.zig");
    try expectContains(samples_readme, "zigux/tests/phase7_argv_split_survey.zig");
    try expectContains(samples_readme, "zigux/tests/phase7_argv_split_manifest.json");
    try expectContains(samples_readme, "scripts/zigux/check-phase7-argv-split-packet.py");
    try expectContains(samples_readme, "zigux/tests/phase7_build.zig");

    try expectContains(build_file, "\"phase7_argv_split.zig\"");
    try expectContains(build_file, "\"phase7_argv_split_survey.zig\"");
    try expectContains(build_file, "\"phase7-argv-split-tests\"");
    try expectContains(build_file, "\"phase7-argv-split-survey-tests\"");
    try expectContains(build_file, "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));");

    try expectContains(helper_tests, "const phase7_vectors = @import(\"fixtures/phase7_argv_split_vectors.zig\");");
    try expectContains(helper_tests, "phase 7 argvSplit matches focused parity fixtures");
    try expectContains(helper_tests, "phase 7 argvSplit token buffer does not alias the source text");
    try expectContains(helper_tests, "phase 7 argvSplit keeps every shared token pointer inside the owned storage copy");
    try expectContains(helper_tests, "phase 7 argvSplit zeroes copied whitespace separators across the tokenized buffer");
    try expectContains(helper_tests, "phase 7 argvSplit zeroes carriage-return, vertical-tab, and form-feed separators too");
    try expectContains(helper_tests, "phase 7 blank argvSplit input reuses the empty exported argv view");
    try expectContains(helper_tests, "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space");
    try expectContains(helper_tests, "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable");
    try expectContains(helper_tests, "phase 7 argvSplit deinit clears exported storage and argv views");
    try expectContains(helper_tests, "phase 7 argvSplit deinit stays safe when called after teardown already cleared the result");
    try expectContains(helper_tests, "phase 7 argvSplit deinit on one non-blank result keeps sibling caller-owned views intact");
    try expectContains(helper_tests, "phase 7 argvFree on one non-blank result keeps sibling caller-owned views intact");
    try expectContains(helper_tests, "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable");
    try expectContains(helper_tests, "split.cArgv()");

    try expectContains(fixture_module, ".name = \"whitespace before first NUL stays blank\",\n");
    try expectContains(fixture_module, ".name = \"leading NUL truncates to zero argv entries\",\n");
    try expectContains(fixture_module, ".name = \"first NUL stops counting and splitting\",\n");
    try expectContains(fixture_module, ".name = \"quote characters stay inside returned tokens\",\n");

    try expectContains(checker, "\"zigux/tests/phase7_argv_split.zig\"");
    try expectContains(checker, "\"zigux/tests/phase7_argv_split_survey.zig\"");
    try expectContains(checker, "\"zigux/tests/phase7_argv_split_manifest.json\"");
    try expectContains(checker, "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\"");

    try expectContains(validate_phase7, "\"scripts/zigux/check-phase7-argv-split-packet.py\",");
    try expectContains(validate_phase7, "\"zigux/tests/phase7_argv_split.zig\",");
    try expectContains(validate_phase7, "\"zigux/tests/phase7_argv_split_survey.zig\",");
    try expectContains(validate_phase7, "\"zigux/tests/phase7_argv_split_manifest.json\",");
    try expectContains(validate_phase7, "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\",");

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
