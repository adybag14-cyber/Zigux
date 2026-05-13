const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectStringSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |entry| {
        if (std.mem.eql(u8, entry, needle)) return;
    }
    return error.TestExpectedEqual;
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

const PairCompileStatus = struct {
    status: []const u8,
    paths: []const []const u8,
};

const SharedBuildStatus = struct {
    status: []const u8,
    readback_on_utc: []const u8,
    build_file: []const u8,
    reviewable_sibling_paths: []const []const u8,
};

const CurrentVerification = struct {
    verified_on_utc: []const u8,
    cmdline_pair_compile: PairCompileStatus,
    shared_phase7_build: SharedBuildStatus,
};

const SurveySummary = struct {
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
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    current_verification: CurrentVerification,
    review_surfaces: []const []const u8,
    covered_helpers: []const []const u8,
    ownership_focus: []const []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

test "phase 7 cmdline survey keeps the roadmap-backed helper packet reviewable" {
    const allocator = std.testing.allocator;

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_cmdline_manifest.json");
    defer allocator.free(manifest_json);
    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P7-L05", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/cmdline.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("lib/cmdline.zig", manifest.roadmap_destinations[0]);

    try std.testing.expectEqualStrings("2026-05-13T18:54:07Z", manifest.current_verification.verified_on_utc);
    try std.testing.expectEqualStrings("confirmed", manifest.current_verification.cmdline_pair_compile.status);
    try std.testing.expectEqual(@as(usize, 2), manifest.current_verification.cmdline_pair_compile.paths.len);
    try expectStringSliceContains(manifest.current_verification.cmdline_pair_compile.paths, "lib/cmdline.zig");
    try expectStringSliceContains(manifest.current_verification.cmdline_pair_compile.paths, "zigux/tests/phase7_cmdline.zig");
    try std.testing.expectEqualStrings("present_on_master", manifest.current_verification.shared_phase7_build.status);
    try std.testing.expectEqualStrings("2026-05-13T18:54:07Z", manifest.current_verification.shared_phase7_build.readback_on_utc);
    try std.testing.expectEqualStrings("zigux/tests/phase7_build.zig", manifest.current_verification.shared_phase7_build.build_file);
    try std.testing.expectEqual(@as(usize, 6), manifest.current_verification.shared_phase7_build.reviewable_sibling_paths.len);
    try expectStringSliceContains(manifest.current_verification.shared_phase7_build.reviewable_sibling_paths, "lib/string_helpers.zig");
    try expectStringSliceContains(manifest.current_verification.shared_phase7_build.reviewable_sibling_paths, "zigux/tests/phase7_string_helpers.zig");
    try expectStringSliceContains(manifest.current_verification.shared_phase7_build.reviewable_sibling_paths, "lib/argv_split.zig");
    try expectStringSliceContains(manifest.current_verification.shared_phase7_build.reviewable_sibling_paths, "zigux/tests/phase7_argv_split.zig");
    try expectStringSliceContains(manifest.current_verification.shared_phase7_build.reviewable_sibling_paths, "lib/rbtree.zig");
    try expectStringSliceContains(manifest.current_verification.shared_phase7_build.reviewable_sibling_paths, "zigux/tests/phase7_rbtree.zig");

    try expectStringSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-cmdline-slice.md");
    try expectStringSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_cmdline.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_cmdline_survey.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_cmdline_manifest.json");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/tests/phase7_build.zig");
    try expectStringSliceContains(manifest.review_surfaces, "zigux/Makefile");

    try expectStringSliceContains(manifest.covered_helpers, "getOption");
    try expectStringSliceContains(manifest.covered_helpers, "getOptions");
    try expectStringSliceContains(manifest.covered_helpers, "memparse");
    try expectStringSliceContains(manifest.covered_helpers, "parseOptionStr");
    try expectStringSliceContains(manifest.covered_helpers, "nextArg");

    try expectStringSliceContains(manifest.ownership_focus, "nextArg caller-owned buffer slices");
    try expectStringSliceContains(manifest.ownership_focus, "nextArg empty-input borrowed-slice reuse");
    try expectStringSliceContains(manifest.ownership_focus, "nextArg leading-whitespace sentinel token");
    try expectStringSliceContains(manifest.ownership_focus, "validator-first shared Phase 7 replay route");
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_test_files);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_fixture_modules);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_helper_present);
    try std.testing.expectEqual(@as(usize, 7), manifest.gaps.len);

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-cmdline-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_LANE_KEY=P7-L05");
    try expectContains(slice_note, "lib/cmdline.c");
    try expectContains(slice_note, "lib/cmdline.zig");
    try expectContains(slice_note, "zigux/tests/phase7_cmdline.zig");
    try expectContains(slice_note, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(slice_note, "zigux/tests/phase7_cmdline_manifest.json");
    try expectContains(slice_note, "zig build phase7-cmdline-survey --build-file zigux/tests/phase7_build.zig --summary all");
    try expectContains(slice_note, "make -C zigux phase7-cmdline-survey");
    try expectContains(slice_note, "zig build test --build-file zigux/tests/phase7_build.zig");
    try expectContains(slice_note, "runtime-safe parsing helpers that:");
    try expectContains(slice_note, "- do not allocate");
    try expectContains(slice_note, "empty-input handling keeps `param` and `rest` borrowed from the caller slice");
    try expectContains(slice_note, "leading-whitespace handling keeps the Linux-style empty sentinel token");
    try expectContains(slice_note, "shared-route note: fresh 2026-05-13 current-master readback confirms `zigux/tests/phase7_build.zig` together with the sibling `string_helpers`, `argv_split`, and `rbtree` helper-local replays is directly readable on `master`");
    try expectContains(slice_note, "getOption() clears caller-provided output on malformed signed and unsigned input");
    try expectContains(
        slice_note,
        "serialized `next_arg()` edge cases covering quoted values, quoted bare tokens, empty quoted bare tokens, leading quoted tokens that contain `=` and still split at the first equals, empty quoted or whitespace-only values, unquoted punctuation-rich values, first-equals splitting, leading-equals sentinel handling, unterminated quoted values, mixed-whitespace rest trimming, and empty-rest termination",
    );

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);
    try expectContains(docs_root, "Documentation/zigux/phase7-cmdline-slice.md");
    try expectContains(docs_root, "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample");
    try expectContains(docs_root, "zigux/tests/phase7_cmdline.zig");
    try expectContains(docs_root, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(docs_root, "zigux/tests/phase7_build.zig");

    const review_checklist = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(review_checklist);
    try expectContains(review_checklist, "there is no standalone `samples/zigux/*cmdline*` reference sample");
    try expectContains(review_checklist, "Documentation/zigux/phase7-cmdline-slice.md");
    try expectContains(review_checklist, "lib/cmdline.zig");
    try expectContains(review_checklist, "zigux/tests/phase7_cmdline.zig");
    try expectContains(review_checklist, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(review_checklist, "zigux/tests/phase7_cmdline_manifest.json");
    try expectContains(review_checklist, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");

    const helper_lane_note = try readRepoFile(allocator, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(helper_lane_note);
    try expectContains(helper_lane_note, "cmdline packet, lane `P7-L05`:");
    try expectContains(helper_lane_note, "Documentation/zigux/phase7-cmdline-slice.md");
    try expectContains(helper_lane_note, "PHASE7_CMDLINE_LANE=P7-L05");
    try expectContains(
        helper_lane_note,
        "P7-L05 owns only cmdline helper-local parity, survey, manifest, fixture, or same-slice reminder drift.",
    );

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);
    try expectContains(samples_readme, "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample;");
    try expectContains(samples_readme, "Documentation/zigux/phase7-cmdline-slice.md");
    try expectContains(samples_readme, "lib/cmdline.zig");
    try expectContains(samples_readme, "zigux/tests/phase7_cmdline.zig");
    try expectContains(samples_readme, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(samples_readme, "zigux/tests/phase7_cmdline_manifest.json");
    try expectContains(samples_readme, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");

    const scripts_root = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_root);
    try expectContains(scripts_root, "scripts/zigux/check-phase7-build-wiring.py");
    try expectContains(scripts_root, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(scripts_root, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");
    try expectContains(scripts_root, "make -C zigux phase7-validate");
    try expectContains(scripts_root, "make -C zigux phase7");

    const validate_phase7 = try readRepoFile(allocator, "scripts/zigux/validate-phase7.py");
    defer allocator.free(validate_phase7);
    try expectContains(validate_phase7, "\"scripts/zigux/check-phase7-make-wrapper.py\"");
    try expectContains(validate_phase7, "\"scripts/zigux/check-phase7-build-wiring.py\"");
    try expectContains(validate_phase7, "\"zigux/tests/phase7_build.zig\"");

    const tests_root = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_root);
    try expectContains(tests_root, "`zigux/tests/phase7_build.zig`");
    try expectContains(tests_root, "`zigux/tests/phase7_cmdline.zig`");
    try expectContains(tests_root, "`zigux/tests/phase7_cmdline_survey.zig`");
    try expectContains(tests_root, "`zigux/tests/phase7_cmdline_manifest.json`");
    try expectContains(tests_root, "`zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`");

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "../../lib/string_helpers.zig");
    try expectContains(build_file, "\"phase7_string_helpers.zig\"");
    try expectContains(build_file, "\"phase7_cmdline.zig\"");
    try expectContains(build_file, "\"phase7_cmdline_survey.zig\"");
    try expectContains(build_file, "\"phase7-cmdline-tests\"");
    try expectContains(build_file, "\"phase7-cmdline-survey-tests\"");
    try expectContains(build_file, "run_cmdline_survey_tests.setCwd(b.path(\"../..\"));");
    try expectContains(build_file, "\"phase7-cmdline-survey\"");
    try expectContains(build_file, "cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step);");

    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);
    try expectContains(makefile, "phase7-validate:");
    try expectContains(makefile, "phase7-cmdline-survey:");
    try expectContains(makefile, "zig build phase7-cmdline-survey --build-file zigux/tests/phase7_build.zig --summary all");
    try expectContains(makefile, "phase7-test:");
    try expectContains(makefile, "phase7: phase7-validate phase7-test");

    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);
    try expectContains(workflow, "Validate Phase 7 runtime helper gates");
    try expectContains(workflow, "make -C zigux phase7-validate");
    try expectContains(workflow, "Run Phase 7 runtime helper tests");
    try expectContains(workflow, "make -C zigux phase7-test");

    const cmdline_tests = try readRepoFile(allocator, "zigux/tests/phase7_cmdline.zig");
    defer allocator.free(cmdline_tests);
    try expectContains(cmdline_tests, "const next_arg_vectors = @import(\"fixtures/phase7_cmdline_next_arg_vectors.zig\");");
    try expectContains(cmdline_tests, "phase 7 getOption and getOptions preserve Linux-style range parsing");
    try expectContains(cmdline_tests, "phase 7 getOption clears caller output on malformed signed and unsigned input");
    try expectContains(cmdline_tests, "phase 7 getOption keeps incomplete hex prefixes aligned with Linux simple_strtoull consumption");
    try expectContains(cmdline_tests, "const single_rest = cmdline.getOptions(\"1-1\", single.len, &single);");
    try expectContains(cmdline_tests, "const single_validate_rest = cmdline.getOptions(\"1-1\", 0, &single_validate);");
    try expectContains(cmdline_tests, "phase 7 parseOptionStr matches only exact bare options");
    try expectContains(cmdline_tests, "phase 7 nextArg matches serialized edge fixtures");
    try expectContains(cmdline_tests, "for (next_arg_vectors.next_arg_cases) |fixture| {");
    try expectContains(cmdline_tests, "cmdline.nextArg");

    const helper_impl = try readRepoFile(allocator, "lib/cmdline.zig");
    defer allocator.free(helper_impl);
    try expectContains(
        helper_impl,
        "test \"getOption keeps incomplete hex prefixes aligned with Linux simple_strtoull consumption\"",
    );
    try expectContains(
        helper_impl,
        "test \"nextArg keeps param, value, and rest borrowed from the caller buffer\"",
    );
    try expectContains(
        helper_impl,
        "test \"nextArg trims mixed trailing whitespace from rest and leaves whitespace-only tails empty\"",
    );
    try expectContains(
        helper_impl,
        "test \"nextArg returns an empty sentinel token before leading whitespace and trims the following rest\"",
    );

    const next_arg_fixture = try readRepoFile(
        allocator,
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
    );
    defer allocator.free(next_arg_fixture);
    try expectContains(next_arg_fixture, ".name = \"leading equals sign stays in the parameter token\",");
    try expectContains(next_arg_fixture, ".name = \"unterminated quoted value consumes the token tail\",");
    try expectContains(next_arg_fixture, ".name = \"trailing spaces after key=value trim to empty rest\",");
}
