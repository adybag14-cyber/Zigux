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
    try expectContains(slice_note, "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig");
    try expectContains(slice_note, "zig build test --build-file zigux/tests/phase7_build.zig");
    try expectContains(slice_note, "runtime-safe parsing helpers that:");
    try expectContains(slice_note, "- do not allocate");
    try expectContains(slice_note, "serialized `next_arg()` edge cases covering quoted values, quoted bare tokens, empty quoted or whitespace-only values, unquoted punctuation-rich values, first-equals splitting, leading-equals sentinel handling, unterminated quoted values, mixed-whitespace rest trimming, and empty-rest termination");
    try expectContains(slice_note, "the dedicated survey gate, the committed `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig` fixture module, and the shared `validate-phase7.py`, `check-phase7-make-wrapper.py`, `phase7_build.zig`, and `make -C zigux phase7-validate` plus `make -C zigux phase7` routes keep the roadmap anchor, serialized `next_arg()` replay, focused helper replay, and Linux-style validator-first packet aligned around the same parked cmdline slice");

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
}
