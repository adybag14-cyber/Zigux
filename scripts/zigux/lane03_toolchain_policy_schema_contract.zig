const std = @import("std");
const testing = std.testing;

const checker_source = @embedFile("check-zig-toolchain.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "toolchain policy schema parser keeps duplicate-aware strict key gates" {
    try expectContains(checker_source, "class DuplicateTrackingDict(dict[str, object]):");
    try expectContains(checker_source, "self.duplicate_keys: list[str] = []");
    try expectContains(checker_source, "object_pairs_hook=DuplicateTrackingDict");
    try expectContains(checker_source, "POLICY_KEYS = {\"phase\", \"channel\", \"minimum_version\", \"archive_sha256\", \"upgrade_policy\"}");
    try expectContains(checker_source, "UPGRADE_POLICY_KEYS = {\"channel_minimum_lockstep\", \"archive_target_scope\", \"required_make_routes\"}");
    try expectContains(checker_source, "unexpected_policy_keys = sorted(set(payload) - POLICY_KEYS)");
    try expectContains(checker_source, "unexpected_upgrade_keys = sorted(set(upgrade_policy) - UPGRADE_POLICY_KEYS)");
}

test "toolchain policy parser fail-closes malformed archive and route fields" {
    try expectContains(checker_source, "invalid archive_sha256 in {policy_path}");
    try expectContains(checker_source, "duplicate archive_sha256 targets in {policy_path}");
    try expectContains(checker_source, "invalid archive_sha256[{normalized_target}] in {policy_path}");
    try expectContains(checker_source, "archive_target_scope references missing archive_sha256 entries in {policy_path}");
    try expectContains(checker_source, "archive_sha256 contains targets outside archive_target_scope in {policy_path}");
    try expectContains(checker_source, "duplicate {field_name} entry in {policy_path}: {normalized_entry}");
    try expectContains(checker_source, "invalid required_make_routes");
}

test "toolchain policy parser keeps pinned channel lockstep explicit" {
    try expectContains(checker_source, "parse_zig_version(channel)");
    try expectContains(checker_source, "parse_zig_version(minimum_version)");
    try expectContains(checker_source, "invalid channel_minimum_lockstep in {policy_path}");
    try expectContains(checker_source, "minimum_version must match channel when channel_minimum_lockstep is true in {policy_path}");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_PIN_POLICY=exact");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_PINNED_CHANNEL={payload['channel']}");
}

test "toolchain policy self-test preserves negative schema fixtures" {
    try expectContains(checker_source, "duplicate toolchain policy keys");
    try expectContains(checker_source, "unexpected toolchain policy keys");
    try expectContains(checker_source, "duplicate upgrade_policy keys");
    try expectContains(checker_source, "unexpected upgrade_policy keys");
    try expectContains(checker_source, "duplicate required_make_routes entry");
    try expectContains(checker_source, "invalid toolchain policy JSON");
    try expectContains(checker_source, "expect_raises(lambda: parse_zig_version(\"master\"))");
}

test "policy-only command reports invalid schema with actionable status" {
    try expectContains(checker_source, "if args.policy_only:");
    try expectContains(checker_source, "emit_policy_summary()");
    try expectContains(checker_source, "except ValueError as exc:");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_POLICY_STATUS=invalid");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_POLICY_PATH={TOOLCHAIN_POLICY}");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_NOTE={exc}");
}
