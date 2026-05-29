const std = @import("std");

const checker_path = "scripts/zigux/check-zig-toolchain.py";

fn readChecker(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        checker_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(
        std.mem.indexOf(u8, haystack, needle) != null,
    );
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "archive search roots include repo-local and workspace fallback surfaces" {
    const allocator = std.testing.allocator;
    const checker = try readChecker(allocator);
    defer allocator.free(checker);

    try expectContains(checker, "def policy_archive_filename(target: str, channel: str) -> str:");
    try expectContains(checker, "return f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(checker, "def iter_archive_search_roots(root: Path = ROOT) -> list[Path]:");
    try expectContains(checker, "add_search_root(root / \".zig-toolchain\")");
    try expectContains(checker, "add_search_root(root / \"toolchains\")");
    try expectContains(checker, "add_search_root(root / \".toolchains\")");
    try expectContains(checker, "add_search_root(root / \"third_party\")");
    try expectContains(checker, "add_search_root(root / \"agent_files\")");
    try expectContains(checker, "add_search_root(parent / \"agent_files\")");
    try expectOrdered(
        checker,
        "def iter_archive_search_roots(root: Path = ROOT) -> list[Path]:",
        "def format_search_roots(search_roots: list[Path]) -> str:",
    );
}

test "repo-local archive candidates honor policy targets and duplicate download suffixes" {
    const allocator = std.testing.allocator;
    const checker = try readChecker(allocator);
    defer allocator.free(checker);

    try expectContains(checker, "ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile");
    try expectContains(checker, "def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:");
    try expectContains(checker, "return match.group(\"stem\") == expected_filename[: -len(\".tar.xz\")]");
    try expectContains(checker, "def archive_name_matches_policy(path_name: str, expected_filename: str) -> bool:");
    try expectContains(checker, "return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)");
    try expectContains(checker, "def iter_repo_local_archive_candidates(");
    try expectContains(checker, "archive_targets = payload[\"upgrade_policy\"][\"archive_target_scope\"]");
    try expectContains(checker, "expected_filename = policy_archive_filename(str(target), channel)");
    try expectContains(checker, "seen: set[Path] = set()");
    try expectContains(checker, "if archive_name_has_duplicate_suffix(child.name, expected_filename):");
    try expectContains(checker, "def select_matching_policy_archive(");
    try expectContains(checker, "if len(matching_candidates) > 1:");
    try expectContains(checker, "multiple repo-local pinned archive candidates matched");
    try expectOrdered(
        checker,
        "candidates = iter_repo_local_archive_candidates(root=root, policy_path=policy_path)",
        "candidate_target, candidate_path = select_matching_policy_archive(",
    );
}

test "archive-only mode reports missing archive roots before allowing missing" {
    const allocator = std.testing.allocator;
    const checker = try readChecker(allocator);
    defer allocator.free(checker);

    try expectContains(checker, "parser.add_argument(\"--archive-only\", action=\"store_true\"");
    try expectContains(checker, "parser.add_argument(\"--archive\", help=\"Explicit Zig archive path for archive-integrity validation.\")");
    try expectContains(checker, "parser.add_argument(\"--archive-target\", help=\"Archive target key from scripts/zigux/zig-toolchain-policy.json.\")");
    try expectContains(checker, "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)");
    try expectContains(checker, "expected_sha, expected_filename = expected_archive_metadata(archive_target)");
    try expectContains(checker, "message, search_roots_summary = describe_missing_archive(");
    try expectContains(checker, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path or args.archive or 'unresolved'}\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}\")");
    try expectContains(checker, "return 0 if args.allow_missing else 1");
    try expectOrdered(
        checker,
        "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)",
        "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")",
    );
}
