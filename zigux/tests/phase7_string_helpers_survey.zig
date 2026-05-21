const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    if (needle.len == 0) return 0;

    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn expectContainsCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, countOccurrences(haystack, needle));
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 string helpers survey keeps the expanded starter packet truthful" {
    const allocator = std.testing.allocator;

    try std.testing.expectError(
        error.FileNotFound,
        std.Io.Dir.cwd().access(std.testing.io, "lib/string_helpers_parse_int_array.zig", .{}),
    );

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(slice_note);
    try expectContains(slice_note, "PHASE7_STATUS=starter_landed");
    try expectContains(slice_note, "the shared no-sample boundary stays reviewable only while `samples/zigux/README.md` keeps the explicit `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*kasprintf*`, and `*strarray*` exclusions aligned with the helper-local boundary test");

    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-string-helpers-packet.py");
    defer allocator.free(checker);
    try expectContains(checker, "the explicit `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*kasprintf*`, and `*strarray*` exclusions aligned");

    const manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(manifest);
    try expectContains(manifest, "the shared no-sample boundary stays reviewable only while `samples/zigux/README.md` keeps the explicit `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*kasprintf*`, and `*strarray*` exclusions aligned with the helper-local boundary test");
}
