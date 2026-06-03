const std = @import("std");
const testing = std.testing;

const checker_source = @embedFile("check-zig-toolchain.py");
const suffix = ".tar.xz";

fn hasNeedle(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn duplicateSuffixStem(path_name: []const u8) ?[]const u8 {
    if (!std.mem.endsWith(u8, path_name, suffix)) return null;

    const without_suffix = path_name[0 .. path_name.len - suffix.len];
    if (without_suffix.len < " (1)".len) return null;
    if (without_suffix[without_suffix.len - 1] != ')') return null;

    const marker = std.mem.lastIndexOf(u8, without_suffix, " (") orelse return null;
    const copy = without_suffix[marker + 2 .. without_suffix.len - 1];
    if (copy.len == 0) return null;
    for (copy) |byte| {
        if (!std.ascii.isDigit(byte)) return null;
    }

    return without_suffix[0..marker];
}

fn archiveNameHasDuplicateSuffix(path_name: []const u8, expected_filename: []const u8) bool {
    if (!std.mem.endsWith(u8, expected_filename, suffix)) return false;
    const stem = duplicateSuffixStem(path_name) orelse return false;
    return std.mem.eql(u8, stem, expected_filename[0 .. expected_filename.len - suffix.len]);
}

fn archiveNameMatchesPolicy(path_name: []const u8, expected_filename: []const u8) bool {
    return std.mem.eql(u8, path_name, expected_filename) or
        archiveNameHasDuplicateSuffix(path_name, expected_filename);
}

test "toolchain checker keeps duplicate suffix helper wired into archive matching" {
    try testing.expect(hasNeedle(checker_source, "ARCHIVE_DUPLICATE_SUFFIX_RE"));
    try testing.expect(hasNeedle(checker_source, "def archive_name_has_duplicate_suffix("));
    try testing.expect(hasNeedle(checker_source, "def archive_name_matches_policy("));
    try testing.expect(hasNeedle(checker_source, "path_name == expected_filename or archive_name_has_duplicate_suffix"));
    try testing.expect(hasNeedle(checker_source, "if archive_name_has_duplicate_suffix(child.name, expected_filename):"));
}

test "browser duplicate suffixes stay valid repo-local archive candidates" {
    const expected = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz";

    try testing.expect(archiveNameMatchesPolicy(expected, expected));
    try testing.expect(archiveNameMatchesPolicy(
        "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz",
        expected,
    ));
    try testing.expect(archiveNameMatchesPolicy(
        "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (42).tar.xz",
        expected,
    ));
}

test "nearby malformed or unrelated archive names stay rejected" {
    const expected = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz";

    try testing.expect(!archiveNameMatchesPolicy(
        "zig-aarch64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz",
        expected,
    ));
    try testing.expect(!archiveNameMatchesPolicy(
        "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2(1).tar.xz",
        expected,
    ));
    try testing.expect(!archiveNameMatchesPolicy(
        "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (copy).tar.xz",
        expected,
    ));
    try testing.expect(!archiveNameMatchesPolicy(
        "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).zip",
        expected,
    ));
}
