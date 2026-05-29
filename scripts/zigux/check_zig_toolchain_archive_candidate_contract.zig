const std = @import("std");

const source = @embedFile("check-zig-toolchain.py");

fn requireContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "repo-local archive search keeps trusted roots before parent fallbacks" {
    try requireContains("def iter_archive_search_roots(root: Path = ROOT) -> list[Path]:");
    try requireContains("add_search_root(root / \".zig-toolchain\")");
    try requireContains("add_search_root(root / \"toolchains\")");
    try requireContains("add_search_root(root / \".toolchains\")");
    try requireContains("add_search_root(root / \"third_party\")");
    try requireContains("add_search_root(root / \"agent_files\")");
    try requireContains("for parent in root.parents:");

    try requireOrdered(
        "add_search_root(root / \"third_party\")",
        "for parent in root.parents:",
    );
    try requireOrdered(
        "add_search_root(root / \"agent_files\")",
        "add_search_root(parent / \"agent_files\")",
    );
}

test "archive candidates include exact policy names and browser duplicate suffixes" {
    try requireContains("ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile");
    try requireContains("def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:");
    try requireContains("match.group(\"stem\") == expected_filename[: -len(\".tar.xz\")]");
    try requireContains("def archive_name_matches_policy(path_name: str, expected_filename: str) -> bool:");
    try requireContains("return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)");
    try requireContains("path = base / expected_filename");
    try requireContains("if archive_name_has_duplicate_suffix(child.name, expected_filename):");

    try requireOrdered(
        "path = base / expected_filename",
        "if archive_name_has_duplicate_suffix(child.name, expected_filename):",
    );
}

test "multiple matched archive candidates fail closed before selection" {
    try requireContains("def select_matching_policy_archive(");
    try requireContains("matching_candidates = [");
    try requireContains("if len(matching_candidates) > 1:");
    try requireContains("candidate_summary = \", \".join(");
    try requireContains("multiple repo-local pinned archive candidates matched in {policy_path}");
    try requireContains("return candidate_target, candidate_path");
    try requireContains("return None, None");

    try requireOrdered(
        "if len(matching_candidates) > 1:",
        "if matching_candidates:",
    );
}

test "archive CLI emits target, path, expected hash, and search-root diagnostics" {
    try requireContains("parser.add_argument(\"--check-archive\", action=\"store_true\", help=\"Check the pinned Zig archive instead of the zig executable.\")");
    try requireContains("parser.add_argument(\"--archive\", help=\"Explicit Zig archive path for --check-archive.\")");
    try requireContains("parser.add_argument(\"--archive-target\", help=\"Archive target key for --check-archive.\")");
    try requireContains("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing");
    try requireContains("ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid");
    try requireContains("ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}");
    try requireContains("ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}");
    try requireContains("ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}");
}
