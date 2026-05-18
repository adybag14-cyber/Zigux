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

test "phase 7 string helpers survey keeps the helper-local packet truthful" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=starter_landed");
    try expectContains(slice_note, "expanded starter packet");
    try expectContains(slice_note, "`parseIntArray()` and `parse_int_array()`");
    try expectContains(slice_note, "bounded parse-int-array decoding for comma-separated lists, positive ranges, first-NUL and explicit-count limits, trailing-invalid-token stop behavior, and clean allocation-failure replay");
    try expectContains(slice_note, "`parseIntArray()` and `parse_int_array()` keep the returned storage caller-owned");
    try expectContains(slice_note, "The next bounded follow-through should realign the dedicated survey and sample-boundary replays so they treat `parse_int_array()` as landed");
    try expectNotContains(slice_note, "`parse_int_array()` can join the same helper-local packet");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "\"current_master_state\": \"expanded_starter_packet\"");
    try expectContains(manifest, "\"parseIntArray\"");
    try expectContains(manifest, "\"parse_int_array\"");
    try expectContains(manifest, "bounded parse-int-array helper pair");
    try expectContains(manifest, "bounded parse-int-array decoding with comma lists, positive ranges, first-NUL and count limits, trailing-invalid-token stop behavior, and caller-owned result storage");
    try expectContains(manifest, "parseIntArray() and parse_int_array() keep the returned storage caller-owned");
    try expectContains(manifest, "Sync `zigux/tests/phase7_string_helpers_survey.zig` and `zigux/tests/phase7_string_helpers_sample_boundary.zig` so the dedicated helper-local packet treats `parse_int_array()` as landed");
    try expectNotContains(manifest, "`parse_int_array()` belongs in the same helper-local packet");
    try expectNotContains(manifest, "missing_review_surfaces");
    try expectNotContains(manifest, "missing_on_master");

    const helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(helper);
    try expectContains(helper, "pub fn parseIntArray");
    try expectContains(helper, "pub fn parse_int_array");
    try expectContains(helper, "pub fn kasprintfStrarray");
    try expectContains(helper, "pub fn kstrdupQuotableCmdline");

    const helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(helper_tests);
    try expectContains(helper_tests, "parseIntArray parses bounded comma lists and positive ranges");
    try expectContains(helper_tests, "parseIntArray stops at invalid trailing tokens while respecting count and first NUL");
    try expectContains(helper_tests, "parseIntArray reports NoEntry when no integers are available");
    try expectContains(helper_tests, "runParseIntArrayWithFailingAllocator");
    try expectContains(helper_tests, "phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators");
    try expectContains(helper_tests, "phase 7 string helpers starter mirrors kfree_strarray teardown and stays idempotent");

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);
    try expectContains(samples_readme, "* `*string*`");
    try expectContains(samples_readme, "* `*cmdline*`");
    try expectContains(samples_readme, "* `*argv*`");
    try expectContains(samples_readme, "* `*rbtree*`");
}
