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

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "\"phase7_cmdline.zig\"");
    try expectContains(build_file, "\"phase7_cmdline_survey.zig\"");
    try expectContains(build_file, "\"phase7-cmdline-tests\"");
    try expectContains(build_file, "\"phase7-cmdline-survey-tests\"");

    const cmdline_tests = try readRepoFile(allocator, "zigux/tests/phase7_cmdline.zig");
    defer allocator.free(cmdline_tests);
    try expectContains(cmdline_tests, "phase 7 parseOptionStr matches only exact bare options");
    try expectContains(cmdline_tests, "phase 7 nextArg matches serialized edge fixtures");
    try expectContains(cmdline_tests, "cmdline.nextArg");
}
