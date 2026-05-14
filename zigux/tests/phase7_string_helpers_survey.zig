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

test "phase 7 string helpers survey keeps the restored starter packet truthful" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=starter_landed");
    try expectContains(slice_note, "current `master` now carries both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`");
    try expectContains(slice_note, "keep the Phase 7 string-helpers lane limited to the restored starter packet");
    try expectContains(slice_note, "The restored starter packet on current `master` covers:");
    try expectContains(slice_note, "stringUnescape()");
    try expectContains(slice_note, "The next bounded follow-through should keep the expanded starter packet truthful");
    try expectNotContains(slice_note, "current `master` is missing both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`");
    try expectNotContains(slice_note, "same-packet truthfulness repairs");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"current_master_state\": \"restored_starter_packet\"");
    try expectContains(manifest, "\"lib/string_helpers.zig\"");
    try expectContains(manifest, "\"zigux/tests/phase7_string_helpers.zig\"");
    try expectContains(manifest, "\"zigux/tests/phase7_string_helpers_sample_boundary.zig\"");
    try expectContains(manifest, "\"memcpyAndPad\"");
    try expectContains(manifest, "\"memcpy_and_pad\"");
    try expectContains(manifest, "\"stringUnescape\"");
    try expectContains(manifest, "\"stringUnescapeAnyInplace\"");
    try expectContains(manifest, "The helper pair `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig` is back on current master as a restored starter packet.");
    try expectNotContains(manifest, "missing_review_surfaces");
    try expectNotContains(manifest, "missing_on_master");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub const UNESCAPE_SPACE");
    try expectContains(helper, "pub fn stringUnescape");
    try expectContains(helper, "pub fn string_unescape");
    try expectContains(helper, "pub fn stringUnescapeInplace");
    try expectContains(helper, "pub fn stringUnescapeAny");
    try expectContains(helper, "pub fn stringUnescapeAnyInplace");
    try expectContains(helper, "pub fn memcpyAndPad");
    try expectContains(helper, "pub fn memcpy_and_pad");
    try expectContains(helper, "pub fn strreplace");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "phase 7 string helpers starter covers whitespace trimming and prefix skipping");
    try expectContains(helper_tests, "phase 7 string helpers starter keeps sysfs matching newline aware");
    try expectContains(helper_tests, "phase 7 string helpers starter matches tables through the first null entry");
    try expectContains(helper_tests, "phase 7 string helpers starter unescapes supported escape families and preserves unsupported escapes");
    try expectContains(helper_tests, "phase 7 string helpers starter pads bounded copies without reading past the provided source slice");
    try expectContains(helper_tests, "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix");

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    try expectContains(build_file, "\"phase7_string_helpers.zig\"");
    try expectContains(build_file, "phase7-string-helpers-tests");
}
