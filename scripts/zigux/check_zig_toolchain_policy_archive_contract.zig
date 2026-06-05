const std = @import("std");

const source_path = "scripts/zigux/check-zig-toolchain.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

test "toolchain policy schema stays fail-closed and duplicate-aware" {
    const allocator = std.testing.allocator;
    const source = try readFile(allocator, source_path);
    defer allocator.free(source);
    const policy = try readFile(allocator, policy_path);
    defer allocator.free(policy);

    try expectContains(source, "POLICY_KEYS = {\"phase\", \"channel\", \"minimum_version\", \"archive_sha256\", \"upgrade_policy\"}");
    try expectContains(source, "UPGRADE_POLICY_KEYS = {\"channel_minimum_lockstep\", \"archive_target_scope\", \"required_make_routes\"}");
    try expectContains(source, "class DuplicateTrackingDict(dict[str, object]):");
    try expectContains(source, "object_pairs_hook=DuplicateTrackingDict");
    try expectContains(source, "duplicate toolchain policy keys");
    try expectContains(source, "duplicate archive_sha256 targets");
    try expectContains(source, "duplicate upgrade_policy keys");
    try expectContains(source, "duplicate {field_name} entry");
    try expectContains(source, "unexpected toolchain policy keys");
    try expectContains(source, "unexpected upgrade_policy keys");
    try expectContains(source, "minimum_version must match channel when channel_minimum_lockstep is true");
    try expectContains(source, "archive_target_scope references missing archive_sha256 entries");
    try expectContains(source, "archive_sha256 contains targets outside archive_target_scope");

    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"required_make_routes\"");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-validate\"");
}

test "archive lookup keeps canonical and duplicate-suffix policy boundaries" {
    const allocator = std.testing.allocator;
    const source = try readFile(allocator, source_path);
    defer allocator.free(source);

    try expectContains(source, "ARCHIVE_DUPLICATE_SUFFIX_RE");
    try expectContains(source, "def policy_archive_filename(target: str, channel: str) -> str:");
    try expectContains(source, "return f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(source, "def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:");
    try expectContains(source, "return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)");
    try expectContains(source, "add_search_root(root / \"third_party\")");
    try expectContains(source, "add_search_root(root / \"agent_files\")");
    try expectContains(source, "add_search_root(parent / \"agent_files\")");
    try expectContains(source, "multiple repo-local pinned archive candidates matched");
    try expectContains(source, "archive target {target!r} is outside archive_target_scope");
    try expectContains(source, "archive target {archive_target!r} is not pinned");
    try expectContains(source, "expected archive filename {expected_filename} for {archive_target}, got {path.name}");
    try expectContains(source, "expected sha256 {expected_sha} for {archive_target}, got {actual_sha}");

    try expectBefore(source, "def iter_archive_search_roots", "def iter_repo_local_archive_candidates");
    try expectBefore(source, "def resolve_policy_archive", "def validate_policy_archive");
}

test "CLI status envelope reports invalid missing and mismatch states explicitly" {
    const allocator = std.testing.allocator;
    const source = try readFile(allocator, source_path);
    defer allocator.free(source);

    try expectContains(source, "parser.add_argument(\"--policy-only\"");
    try expectContains(source, "parser.add_argument(\"--archive-only\"");
    try expectContains(source, "parser.add_argument(\"--archive\"");
    try expectContains(source, "parser.add_argument(\"--archive-target\"");
    try expectContains(source, "ZIG_TOOLCHAIN_POLICY_STATUS=invalid");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME=");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256=");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256=");
    try expectContains(source, "ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS=");
    try expectContains(source, "ZIG_TOOLCHAIN_NOTE=");
    try expectContains(source, "return 0 if args.allow_missing else 1");

    try expectBefore(source, "if args.policy_only:", "if args.archive_only:");
}
