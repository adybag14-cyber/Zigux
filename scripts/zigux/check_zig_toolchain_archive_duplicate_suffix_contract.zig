const std = @import("std");
const testing = std.testing;

const checker = @embedFile("check-zig-toolchain.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

test "archive duplicate suffix helper accepts only policy-shaped browser copies" {
    try expectContains(checker, "ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile");
    try expectContains(checker, "(?P<copy>\\d+)");
    try expectContains(checker, "(?P<suffix>\\.tar\\.xz)");
    try expectContains(checker, "def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:");
    try expectContains(checker, "if not expected_filename.endswith(\".tar.xz\"):");
    try expectContains(checker, "return match.group(\"stem\") == expected_filename[: -len(\".tar.xz\")]");
    try expectContains(checker, "def archive_name_matches_policy(path_name: str, expected_filename: str) -> bool:");
    try expectContains(checker, "return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)");
}

test "repo-local archive resolver fails closed on multiple matching candidates" {
    try expectOrdered(checker, "def iter_repo_local_archive_candidates", "def select_matching_policy_archive");
    try expectContains(checker, "matching_candidates = [");
    try expectContains(checker, "if len(matching_candidates) > 1:");
    try expectContains(checker, "candidate_summary = \", \".join(");
    try expectContains(checker, "multiple repo-local pinned archive candidates matched in {policy_path}");
    try expectOrdered(checker, "if len(matching_candidates) > 1:", "if matching_candidates:");
    try expectOrdered(checker, "select_matching_policy_archive(", "if candidate_path is not None:");
}

test "archive search roots keep local trusted locations before parent fallbacks" {
    try expectContains(checker, "def iter_archive_search_roots(root: Path = ROOT) -> list[Path]:");
    try expectOrdered(checker, "add_search_root(root / \".zig-toolchain\")", "add_search_root(root / \"toolchains\")");
    try expectOrdered(checker, "add_search_root(root / \"toolchains\")", "add_search_root(root / \".toolchains\")");
    try expectOrdered(checker, "add_search_root(root / \".toolchains\")", "add_search_root(root / \"third_party\")");
    try expectOrdered(checker, "add_search_root(root / \"third_party\")", "add_search_root(root / \"agent_files\")");
    try expectOrdered(checker, "add_search_root(root / \"agent_files\")", "for parent in root.parents:");
    try expectContains(checker, "add_search_root(parent / \"agent_files\")");
}

test "checker self-test covers browser-copy suffix and conflict paths" {
    try expectContains(checker, "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3 (1).tar.xz");
    try expectContains(checker, " (2).tar.xz");
    try expectContains(checker, "duplicate_archive_path = workspace_archive_path.with_name(");
    try expectContains(checker, "conflicting_archive_path = duplicate_archive_path.with_name(");
    try expectContains(checker, "expect_equal(resolve_policy_archive(root=root, policy_path=policy_path), (\"x86_64-linux\", duplicate_archive_path))");
    try expectContains(checker, "expect_raises(");
    try expectContains(checker, "\"multiple repo-local pinned archive candidates matched\"");
    try expectContains(checker, "validate_policy_archive(duplicate_archive_path, \"x86_64-linux\", policy_path=policy_path)");
    try testing.expect(countOccurrences(checker, "archive_name_has_duplicate_suffix(") >= 3);
}
