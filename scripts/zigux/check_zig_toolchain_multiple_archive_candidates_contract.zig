const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");
const policy_source = @embedFile("zig-toolchain-policy.json");

const pinned_channel = "0.17.0-dev.758+748e7c5e3";
const pinned_target = "x86_64-linux";
const pinned_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const expected_archive = "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const historical_runtime_channel = "0.17.0-dev.87+9b177a7d2";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "multiple repo-local archive candidates remain a fail-closed diagnostic" {
    try expectContains(checker_source, "def select_matching_policy_archive(");
    try expectContains(checker_source, "matching_candidates = [");
    try expectContains(checker_source, "if len(matching_candidates) > 1:");
    try expectContains(checker_source, "candidate_summary = \", \".join(");
    try expectContains(checker_source, "f\"{candidate_target}:{candidate_path}\"");
    try expectContains(checker_source, "multiple repo-local pinned archive candidates matched in {policy_path}: ");
    try expectContains(checker_source, "raise ValueError(");
}

test "duplicate-suffix self-test covers one accepted archive and one conflict" {
    try expectContains(checker_source, "def archive_name_has_duplicate_suffix(");
    try expectContains(checker_source, "def archive_name_matches_policy(");
    try expectContains(checker_source, "duplicate_archive_path = workspace_archive_path.with_name(");
    try expectContains(checker_source, "f\"zig-x86_64-linux-{self_test_archive_channel} (1).tar.xz\"");
    try expectContains(checker_source, "workspace_archive_path.unlink()");
    try expectContains(checker_source, "expect_equal(resolve_policy_archive(root=root, policy_path=policy_path), (\"x86_64-linux\", duplicate_archive_path))");
    try expectContains(checker_source, "conflicting_archive_path = duplicate_archive_path.with_name(");
    try expectContains(checker_source, "f\"zig-x86_64-linux-{self_test_archive_channel} (2).tar.xz\"");
    try expectContains(checker_source, "expect_raises(");
    try expectContains(checker_source, "\"multiple repo-local pinned archive candidates matched\"");
}

test "archive-only CLI reports candidate collisions as invalid, not missing" {
    try expectContains(checker_source, "if args.archive_only:");
    try expectContains(checker_source, "archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)");
    try expectContains(checker_source, "except ValueError as exc:");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_PATH={args.archive or 'unresolved'}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={args.archive_target}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
    try expectContains(checker_source, "return 1");
}

test "contract stays tied to the current pinned archive policy tuple" {
    try expectContains(policy_source, "\"channel\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy_source, "\"minimum_version\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy_source, "\"" ++ pinned_target ++ "\": \"" ++ pinned_sha256 ++ "\"");
    try expectContains(policy_source, "\"archive_target_scope\"");
    try expectContains(policy_source, "\"" ++ pinned_target ++ "\"");

    try expectContains(checker_source, "policy_archive_filename(target: str, channel: str) -> str");
    try expectContains(checker_source, "return f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(checker_source, expected_archive);
    try expectNotContains(policy_source, historical_runtime_channel);
}
