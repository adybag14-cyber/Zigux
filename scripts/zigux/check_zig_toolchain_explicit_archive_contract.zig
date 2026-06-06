const std = @import("std");

const checker_path = "scripts/zigux/check-zig-toolchain.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectInOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_offset = std.mem.indexOf(u8, haystack[before_index..], after) orelse return error.MissingAfterMarker;
    try std.testing.expect(after_offset > 0);
}

fn expectNotInWindow(haystack: []const u8, start_marker: []const u8, end_marker: []const u8, needle: []const u8) !void {
    const start_index = std.mem.indexOf(u8, haystack, start_marker) orelse return error.MissingStartMarker;
    const end_offset = std.mem.indexOf(u8, haystack[start_index..], end_marker) orelse return error.MissingEndMarker;
    const window = haystack[start_index..][0..end_offset];
    try std.testing.expect(std.mem.indexOf(u8, window, needle) == null);
}

test "explicit archive cli surface remains tied to archive-only validation" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "parser.add_argument(\"--archive-only\", action=\"store_true\", help=\"Validate the pinned Zig archive artifact without probing a zig executable.\")");
    try expectContains(checker, "parser.add_argument(\"--archive\", help=\"Explicit Zig archive path for archive-integrity validation.\")");
    try expectContains(checker, "parser.add_argument(\"--archive-target\", help=\"Archive target key from scripts/zigux/zig-toolchain-policy.json.\")");
    try expectInOrder(checker, "if args.archive_only:", "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)");
    try expectInOrder(checker, "if args.archive_only:", "expected_sha, expected_filename = expected_archive_metadata(archive_target)");
}

test "explicit archive directories fail invalid with policy metadata" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    const invalid_block = "if args.archive is not None and archive_path is not None:";
    const missing_block = "if archive_path is None or not archive_path.is_file():";

    try expectInOrder(checker, invalid_block, "invalid_archive_note = describe_invalid_explicit_archive_path(archive_path)");
    try expectInOrder(checker, invalid_block, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")");
    try expectInOrder(checker, invalid_block, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path}\")");
    try expectInOrder(checker, invalid_block, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}\")");
    try expectInOrder(checker, invalid_block, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}\")");
    try expectInOrder(checker, invalid_block, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}\")");
    try expectInOrder(checker, invalid_block, "print(f\"ZIG_TOOLCHAIN_NOTE={invalid_archive_note}\")");
    try expectInOrder(checker, invalid_block, "return 1");
    try expectInOrder(checker, invalid_block, missing_block);
}

test "missing explicit archive reports the explicit path without repo search roots" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    const helper = "def describe_missing_archive(";
    const explicit_branch = "if explicit_archive is not None:";
    const repo_search_branch = "return \"pinned Zig archive not found in archive search roots\", format_search_roots(search_roots)";

    try expectInOrder(checker, helper, explicit_branch);
    try expectInOrder(checker, explicit_branch, "resolved = archive_path or Path(explicit_archive)");
    try expectInOrder(checker, explicit_branch, "return f\"explicit archive path does not exist: {resolved}\", None");
    try expectInOrder(checker, explicit_branch, repo_search_branch);
    try expectNotInWindow(checker, explicit_branch, repo_search_branch, "format_search_roots(search_roots)");
}

test "self-test pins explicit archive missing and directory diagnostics" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "missing_explicit_path = root / \"missing.tar.xz\"");
    try expectContains(checker, "f\"explicit archive path does not exist: {missing_explicit_path}\"");
    try expectContains(checker, "explicit_archive_dir = root / \"archive-dir\"");
    try expectContains(checker, "f\"explicit archive path is a directory, expected a regular file: {explicit_archive_dir}\"");
}

test "policy still exposes the pinned explicit archive metadata" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);

    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"archive_sha256\": {");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"archive_target_scope\": [");
    try expectContains(policy, "\"x86_64-linux\"");
}
