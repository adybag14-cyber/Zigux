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

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    review_surfaces: []const []const u8,
    covered_helpers: []const []const u8,
    ownership_focus: []const []const u8,
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
    try expectContains(slice_note, "getOption() clears caller-provided output on malformed signed and unsigned input");
    try expectContains(
        slice_note,
        "serialized `next_arg()` edge cases covering quoted values, quoted bare tokens, empty quoted bare tokens, leading quoted tokens that contain `=` and still split at the first equals, empty quoted or whitespace-only values, unquoted punctuation-rich values, first-equals splitting, leading-equals sentinel handling, unterminated quoted values, mixed-whitespace rest trimming, and empty-rest termination",
    );

    const helper_lane_note = try readRepoFile(allocator, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(helper_lane_note);
    try expectContains(helper_lane_note, "cmdline packet, lane `P7-L05`:");
    try expectContains(helper_lane_note, "Documentation/zigux/phase7-cmdline-slice.md");
    try expectContains(helper_lane_note, "PHASE7_CMDLINE_LANE=P7-L05");
    try expectContains(
        helper_lane_note,
        "P7-L05 owns only cmdline helper-local parity, survey, manifest, fixture, or same-slice reminder drift.",
    );

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "\"phase7_cmdline.zig\"");
    try expectContains(build_file, "\"phase7_cmdline_survey.zig\"");
    try expectContains(build_file, "\"phase7-cmdline-tests\"");
    try expectContains(build_file, "\"phase7-cmdline-survey-tests\"");
    try expectContains(build_file, "run_cmdline_survey_tests.setCwd(b.path(\"../..\"));");
    try expectContains(build_file, "\"phase7-cmdline-survey\"");
    try expectContains(build_file, "cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step);");

    const cmdline_tests = try readRepoFile(allocator, "zigux/tests/phase7_cmdline.zig");
    defer allocator.free(cmdline_tests);
    try expectContains(cmdline_tests, "const next_arg_vectors = @import(\"fixtures/phase7_cmdline_next_arg_vectors.zig\");");
    try expectContains(cmdline_tests, "phase 7 getOption and getOptions preserve Linux-style range parsing");
    try expectContains(cmdline_tests, "phase 7 getOption clears caller output on malformed signed and unsigned input");
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
