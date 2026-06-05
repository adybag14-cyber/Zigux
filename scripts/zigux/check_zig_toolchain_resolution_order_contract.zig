const std = @import("std");

const checker_path = "scripts/zigux/check-zig-toolchain.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";

fn readRepoFile(path: []const u8, max_bytes: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(max_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "repo-local pinned zig executable candidates precede PATH fallback" {
    const source = try readRepoFile(checker_path, 96 * 1024);
    defer std.testing.allocator.free(source);

    try expectContains(source, "def iter_zig_search_roots(root: Path = ROOT) -> list[Path]:");
    try expectContains(source, "add_search_root(root / \".zig-toolchain\")");
    try expectContains(source, "add_search_root(root / \"toolchains\")");
    try expectContains(source, "add_search_root(root / \".toolchains\")");
    try expectContains(source, "for parent in root.parents:");
    try expectContains(source, "add_search_root(parent / \".toolchains\")");
    try expectContains(source, "add_search_root(parent / \"toolchains\")");

    try expectContains(source, "def iter_repo_local_zig_candidates(");
    try expectContains(source, "pinned_dirname = f\"zig-x86_64-linux-{pinned_channel}\"");
    try expectContains(source, "add_candidate_roots(base / pinned_dirname)");
    try expectContains(source, "add_candidate_roots(child / pinned_dirname)");
    try expectContains(source, "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):");
    try expectContains(source, "return which(\"zig\")");
    try expectBefore(source, "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):", "return which(\"zig\")");

    try expectContains(source, "zig not found on PATH or in repo-local toolchain search roots");
    try expectContains(source, "ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}");
}

test "archive resolver searches policy filename before duplicate download suffixes" {
    const source = try readRepoFile(checker_path, 96 * 1024);
    defer std.testing.allocator.free(source);

    try expectContains(source, "def iter_archive_search_roots(root: Path = ROOT) -> list[Path]:");
    try expectContains(source, "add_search_root(root / \"third_party\")");
    try expectContains(source, "add_search_root(root / \"agent_files\")");
    try expectContains(source, "add_search_root(parent / \"agent_files\")");

    try expectContains(source, "def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:");
    try expectContains(source, "return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)");
    try expectContains(source, "path = base / expected_filename");
    try expectContains(source, "if archive_name_has_duplicate_suffix(child.name, expected_filename):");
    try expectBefore(source, "path = base / expected_filename", "if archive_name_has_duplicate_suffix(child.name, expected_filename):");

    try expectContains(source, "multiple repo-local pinned archive candidates matched");
    try expectContains(source, "pinned Zig archive not found in archive search roots");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}");
}

test "current policy keeps the pinned channel and required phase2 routes aligned" {
    const policy = try readRepoFile(policy_path, 16 * 1024);
    defer std.testing.allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_target_scope\": [");
    try expectContains(policy, "\"x86_64-linux\"");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-tools\"");
    try expectContains(policy, "\"phase2-kconfig\"");
    try expectContains(policy, "\"phase2-cross\"");
    try expectContains(policy, "\"phase2-genksyms\"");
    try expectContains(policy, "\"phase2-fixdep\"");
    try expectContains(policy, "\"phase2-validate\"");
}
