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

test "phase 7 string helpers survey keeps the expanded starter packet truthful" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=starter_landed");
    try expectContains(slice_note, "expanded starter packet");
    try expectContains(slice_note, "stringEscapeMem()");
    try expectContains(slice_note, "string_escape_str_any_np()");
    try expectContains(slice_note, "The next bounded follow-through should keep the expanded starter packet truthful");
    try expectNotContains(slice_note, "same-packet truthfulness repairs");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"current_master_state\": \"expanded_starter_packet\"");
    try expectContains(manifest, "\"stringEscapeMem\"");
    try expectContains(manifest, "\"string_escape_mem_any_np\"");
    try expectContains(manifest, "\"stringEscapeStr\"");
    try expectContains(manifest, "\"string_escape_str_any_np\"");
    try expectContains(manifest, "expanded starter packet");
    try expectNotContains(manifest, "missing_review_surfaces");
    try expectNotContains(manifest, "missing_on_master");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub const ESCAPE_SPACE");
    try expectContains(helper, "pub const ESCAPE_APPEND");
    try expectContains(helper, "pub fn stringEscapeMem");
    try expectContains(helper, "pub fn string_escape_mem");
    try expectContains(helper, "pub fn stringEscapeMemAnyNp");
    try expectContains(helper, "pub fn string_escape_mem_any_np");
    try expectContains(helper, "pub fn stringEscapeStr");
    try expectContains(helper, "pub fn string_escape_str");
    try expectContains(helper, "pub fn stringEscapeStrAnyNp");
    try expectContains(helper, "pub fn string_escape_str_any_np");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes");
    try expectContains(helper_tests, "string_helpers.stringEscapeMem(");
    try expectContains(helper_tests, "string_helpers.string_escape_mem_any_np");
    try expectContains(helper_tests, "string_helpers.stringEscapeStr(");
    try expectContains(helper_tests, "string_helpers.string_escape_str_any_np");

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "\"phase7_string_helpers.zig\"");
    try expectContains(build_file, "phase7-string-helpers-tests");
}
