const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 5 rbtree sample lane stays anchored to phase 7 owner surfaces instead of inventing a sample-root port" {
    const allocator = std.testing.allocator;

    const sample_root_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(sample_root_readme);
    const phase5_build = try readRepoFile(allocator, "zigux/tests/phase5_build.zig");
    defer allocator.free(phase5_build);
    const phase7_slice = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-slice.md");
    defer allocator.free(phase7_slice);
    const phase7_survey = try readRepoFile(allocator, "zigux/tests/phase7_rbtree_survey.zig");
    defer allocator.free(phase7_survey);

    try expectContains(sample_root_readme, "Current `master` still ships no standalone Phase 5 sample-root files here for:");
    try expectContains(sample_root_readme, "* `*rbtree*`");
    try expectContains(sample_root_readme, "Keep broader helper and formatting review surfaces in their existing helper, closure, or later-phase packets instead of treating this directory as proof that dedicated string, cmdline, argv, rbtree, kasprintf, strarray, printf, vsprintf, or broad format samples have landed here.");

    try expectNotContains(phase5_build, "../../samples/zigux/rbtree");
    try expectNotContains(phase5_build, "phase5-rbtree");

    try expectContains(phase7_slice, "`PHASE7_LANE_KEY=P7-L13`");
    try expectContains(phase7_slice, "`lib/rbtree.zig`");
    try expectContains(phase7_slice, "`zigux/tests/phase7_rbtree_survey.zig`");
    try expectContains(phase7_slice, "The current helper-local packet on `master` covers:");

    try expectContains(phase7_survey, "phase 7 rbtree survey keeps the returned json fixture, C harness, and direct helper packet truthful");
    try expectContains(phase7_survey, "\"lib/rbtree.zig\"");
    try expectContains(phase7_survey, "\"tools/lib/rbtree.zig\"");
}
