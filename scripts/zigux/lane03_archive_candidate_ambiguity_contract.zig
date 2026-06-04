const std = @import("std");

const checker_text = @embedFile("check-zig-toolchain.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "archive search roots include repo and attached-runtime trusted archive locations" {
    try expectContains(checker_text, "def iter_archive_search_roots(root: Path = ROOT) -> list[Path]:");
    try expectContains(checker_text, "add_search_root(root / \".zig-toolchain\")");
    try expectContains(checker_text, "add_search_root(root / \"toolchains\")");
    try expectContains(checker_text, "add_search_root(root / \".toolchains\")");
    try expectContains(checker_text, "add_search_root(root / \"third_party\")");
    try expectContains(checker_text, "add_search_root(root / \"agent_files\")");
    try expectContains(checker_text, "add_search_root(parent / \"agent_files\")");
}

test "duplicate archive names are accepted only through the policy filename stem" {
    try expectContains(checker_text, "ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile");
    try expectContains(checker_text, "def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:");
    try expectContains(checker_text, "if not expected_filename.endswith(\".tar.xz\"):");
    try expectContains(checker_text, "return match.group(\"stem\") == expected_filename[: -len(\".tar.xz\")]");
    try expectContains(checker_text, "def archive_name_matches_policy(path_name: str, expected_filename: str) -> bool:");
    try expectContains(checker_text, "return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)");
}

test "repo local archive discovery de-duplicates candidate paths before selection" {
    try expectContains(checker_text, "def iter_repo_local_archive_candidates(");
    try expectContains(checker_text, "seen: set[Path] = set()");
    try expectContains(checker_text, "if path not in seen:");
    try expectContains(checker_text, "seen.add(path)");
    try expectContains(checker_text, "for child in sorted(base.iterdir()):");
    try expectContains(checker_text, "if child in seen or not child.is_file():");
    try expectContains(checker_text, "if archive_name_has_duplicate_suffix(child.name, expected_filename):");
    try expectBefore(checker_text, "seen: set[Path] = set()", "def select_matching_policy_archive(");
}

test "multiple visible pinned archive candidates fail closed instead of selecting one" {
    try expectContains(checker_text, "def select_matching_policy_archive(");
    try expectContains(checker_text, "matching_candidates = [");
    try expectContains(checker_text, "if candidate_path.is_file()");
    try expectContains(checker_text, "if len(matching_candidates) > 1:");
    try expectContains(checker_text, "multiple repo-local pinned archive candidates matched in {policy_path}: ");
    try expectContains(checker_text, "candidate_summary = \", \".join(");
    try expectContains(checker_text, "return candidate_target, candidate_path");
    try expectContains(checker_text, "return None, None");
}
