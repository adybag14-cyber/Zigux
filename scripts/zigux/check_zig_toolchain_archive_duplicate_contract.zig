const std = @import("std");

const checker = @embedFile("check-zig-toolchain.py");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker, needle) != null);
}

fn expectOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, checker, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, checker, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn countOccurrences(needle: []const u8) usize {
    var count: usize = 0;
    var cursor: []const u8 = checker;
    while (std.mem.indexOf(u8, cursor, needle)) |index| {
        count += 1;
        cursor = cursor[index + needle.len ..];
    }
    return count;
}

test "archive duplicate suffix matcher stays scoped to pinned tarball names" {
    try expectContains("ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile");
    try expectContains("(?P<copy>\\d+)");
    try expectContains("(?P<suffix>\\.tar\\.xz)");
    try expectContains("def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:");
    try expectContains("if not expected_filename.endswith(\".tar.xz\"):");
    try expectContains("return match.group(\"stem\") == expected_filename[: -len(\".tar.xz\")]");
    try expectContains("return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)");

    try expectOrdered("def archive_name_has_duplicate_suffix", "def archive_name_matches_policy");
    try std.testing.expectEqual(@as(usize, 2), countOccurrences("archive_name_has_duplicate_suffix("));
}

test "repo-local pinned archive selection fails closed on ambiguity" {
    try expectContains("def select_matching_policy_archive(");
    try expectContains("matching_candidates = [");
    try expectContains("if len(matching_candidates) > 1:");
    try expectContains("candidate_summary = \", \".join(");
    try expectContains("raise ValueError(");
    try expectContains("multiple repo-local pinned archive candidates matched");
    try expectContains("f\"{candidate_target}:{candidate_path}\"");
    try expectContains("if matching_candidates:");
    try expectContains("return None, None");

    try expectOrdered("if len(matching_candidates) > 1:", "if matching_candidates:");
    try expectOrdered("multiple repo-local pinned archive candidates matched", "return None, None");
}

test "self-test keeps unique duplicate archive allowed and conflicting duplicate rejected" {
    try expectContains("duplicate_archive_path = workspace_archive_path.with_name(");
    try expectContains("zig-x86_64-linux-{self_test_archive_channel} (1).tar.xz");
    try expectContains("expect_equal(resolve_policy_archive(root=root, policy_path=policy_path), (\"x86_64-linux\", duplicate_archive_path))");
    try expectContains("validate_policy_archive(duplicate_archive_path, \"x86_64-linux\", policy_path=policy_path)");
    try expectContains("conflicting_archive_path = duplicate_archive_path.with_name(");
    try expectContains("zig-x86_64-linux-{self_test_archive_channel} (2).tar.xz");
    try expectContains("expect_raises(");
    try expectContains("lambda: resolve_policy_archive(root=root, policy_path=policy_path),");
    try expectContains("\"multiple repo-local pinned archive candidates matched\"");

    try expectOrdered("duplicate_archive_path = workspace_archive_path.with_name(", "conflicting_archive_path = duplicate_archive_path.with_name(");
    try expectOrdered("conflicting_archive_path = duplicate_archive_path.with_name(", "\"multiple repo-local pinned archive candidates matched\"");
}
