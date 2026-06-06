const std = @import("std");
const testing = std.testing;

const checker_source = @embedFile("check-zig-toolchain.py");

fn requireContains(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

fn requireOrder(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, checker_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, checker_source, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "archive search roots include local toolchains before trusted payload folders" {
    try requireContains("def iter_archive_search_roots(root: Path = ROOT) -> list[Path]:");
    try requireContains("add_search_root(root / \".zig-toolchain\")");
    try requireContains("add_search_root(root / \"toolchains\")");
    try requireContains("add_search_root(root / \".toolchains\")");
    try requireContains("add_search_root(root / \"third_party\")");
    try requireContains("add_search_root(root / \"agent_files\")");
    try requireContains("add_search_root(parent / \".toolchains\")");
    try requireContains("add_search_root(parent / \"toolchains\")");
    try requireContains("add_search_root(parent / \"agent_files\")");

    try requireOrder("add_search_root(root / \".zig-toolchain\")", "add_search_root(root / \"toolchains\")");
    try requireOrder("add_search_root(root / \"toolchains\")", "add_search_root(root / \".toolchains\")");
    try requireOrder("add_search_root(root / \".toolchains\")", "add_search_root(root / \"third_party\")");
    try requireOrder("add_search_root(root / \"third_party\")", "add_search_root(root / \"agent_files\")");
}

test "policy archive candidates use the pinned channel filename and duplicate suffixes" {
    try requireContains("def policy_archive_filename(target: str, channel: str) -> str:");
    try requireContains("return f\"zig-{target}-{channel}.tar.xz\"");
    try requireContains("def iter_repo_local_archive_candidates(");
    try requireContains("channel = str(payload[\"channel\"])");
    try requireContains("archive_targets = payload[\"upgrade_policy\"][\"archive_target_scope\"]");
    try requireContains("expected_filename = policy_archive_filename(str(target), channel)");
    try requireContains("path = base / expected_filename");
    try requireContains("archive_name_has_duplicate_suffix(child.name, expected_filename)");
    try requireContains("candidates.append((str(target), child))");

    try requireOrder("channel = str(payload[\"channel\"])", "expected_filename = policy_archive_filename(str(target), channel)");
    try requireOrder("path = base / expected_filename", "archive_name_has_duplicate_suffix(child.name, expected_filename)");
}

test "archive duplicate suffix acceptance is limited to policy tarballs" {
    try requireContains("ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(");
    try requireContains("def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:");
    try requireContains("if not expected_filename.endswith(\".tar.xz\"):");
    try requireContains("match = ARCHIVE_DUPLICATE_SUFFIX_RE.fullmatch(path_name)");
    try requireContains("return match.group(\"stem\") == expected_filename[: -len(\".tar.xz\")]");
    try requireContains("def archive_name_matches_policy(path_name: str, expected_filename: str) -> bool:");
    try requireContains("return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)");

    try requireOrder("if not expected_filename.endswith(\".tar.xz\"):", "match = ARCHIVE_DUPLICATE_SUFFIX_RE.fullmatch(path_name)");
    try requireOrder("def archive_name_matches_policy(path_name: str, expected_filename: str) -> bool:", "return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)");
}

test "missing and duplicate archive diagnostics expose the action path" {
    try requireContains("def describe_missing_archive(");
    try requireContains("explicit archive path does not exist: {resolved}");
    try requireContains("pinned Zig archive not found in archive search roots");
    try requireContains("format_search_roots(search_roots)");
    try requireContains("def select_matching_policy_archive(");
    try requireContains("if len(matching_candidates) > 1:");
    try requireContains("multiple repo-local pinned archive candidates matched in {policy_path}");
    try requireContains("candidate_summary = \", \".join(");

    try requireOrder("def describe_missing_archive(", "pinned Zig archive not found in archive search roots");
    try requireOrder("def select_matching_policy_archive(", "if len(matching_candidates) > 1:");
    try requireOrder("if len(matching_candidates) > 1:", "multiple repo-local pinned archive candidates matched in {policy_path}");
}
