const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 cmdline survey keeps the roadmap-backed helper packet reviewable" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-cmdline-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "lib/cmdline.c");
    try expectContains(slice_note, "lib/cmdline.zig");
    try expectContains(slice_note, "zigux/tests/phase7_cmdline.zig");
    try expectContains(slice_note, "zigux/tests/phase7_cmdline_survey.zig");
    try expectContains(slice_note, "zig build test --build-file zigux/tests/phase7_build.zig");
    try expectContains(slice_note, "runtime-safe parsing helpers that:");
    try expectContains(slice_note, "- do not allocate");
    try expectContains(
        slice_note,
        "serialized `next_arg()` edge cases covering quoted values, quoted bare tokens, empty quoted or whitespace-only values, unquoted punctuation-rich values, first-equals splitting, leading-equals sentinel handling, unterminated quoted values, mixed-whitespace rest trimming, and empty-rest termination",
    );
    try expectContains(
        slice_note,
        "the dedicated survey gate keeps the roadmap anchor, focused helper replay, and shared `phase7_build.zig` compile-check path aligned around the same parked cmdline packet",
    );
    try expectContains(slice_note, "zigux/tests/phase7_cmdline_manifest.json");

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "\"phase7_cmdline.zig\"");
    try expectContains(build_file, "\"phase7_cmdline_survey.zig\"");
    try expectContains(build_file, "\"phase7-cmdline-tests\"");
    try expectContains(build_file, "\"phase7-cmdline-survey-tests\"");
    try expectContains(build_file, "run_cmdline_survey_tests.setCwd(b.path(\"../..\"));");

    const cmdline_tests = try readRepoFile(allocator, "zigux/tests/phase7_cmdline.zig");
    defer allocator.free(cmdline_tests);
    try expectContains(cmdline_tests, "const next_arg_vectors = @import(\"fixtures/phase7_cmdline_next_arg_vectors.zig\");");
    try expectContains(cmdline_tests, "phase 7 getOption and getOptions preserve Linux-style range parsing");
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
        "test \"nextArg trims mixed trailing whitespace from rest and leaves whitespace-only tails empty\"",
    );

    const next_arg_fixture = try readRepoFile(
        allocator,
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
    );
    defer allocator.free(next_arg_fixture);
    try expectContains(next_arg_fixture, ".name = \"mixed trailing whitespace is trimmed from rest\",");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_cmdline_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"lane_key\": \"P7-Y06\"");
    try expectContains(manifest, "\"anchor\": \"lib/cmdline.c\"");
    try expectContains(manifest, "\"zigux/tests/phase7_cmdline_survey.zig\"");
    try expectContains(manifest, "\"zigux/tests/phase7_cmdline_manifest.json\"");
    try expectContains(manifest, "\"nextArg caller-owned buffer slices\"");
    try expectContains(manifest, "\"nextArg empty-input borrowed-slice reuse\"");
    try expectContains(manifest, "\"nextArg leading-whitespace sentinel token\"");
    try expectContains(manifest, "\"validator-first shared Phase 7 replay route\"");

    const shared_validator = try readRepoFile(allocator, "scripts/zigux/validate-phase7.py");
    defer allocator.free(shared_validator);
    try expectContains(shared_validator, "\"zigux/tests/phase7_cmdline_survey.zig\"");
    try expectContains(shared_validator, "\"zigux/tests/phase7_cmdline_manifest.json\"");
    try expectContains(shared_validator, "\"zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig\"");
}
