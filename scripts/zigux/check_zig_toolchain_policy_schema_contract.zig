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

test "policy loader keeps duplicate-key and unexpected-key checks fail closed" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "class DuplicateTrackingDict(dict[str, object]):");
    try expectContains(checker, "self.duplicate_keys: list[str] = []");
    try expectContains(checker, "object_pairs_hook=DuplicateTrackingDict");
    try expectContains(checker, "POLICY_KEYS = {\"phase\", \"channel\", \"minimum_version\", \"archive_sha256\", \"upgrade_policy\"}");
    try expectContains(checker, "UPGRADE_POLICY_KEYS = {\"channel_minimum_lockstep\", \"archive_target_scope\", \"required_make_routes\"}");
    try expectContains(checker, "duplicate toolchain policy keys in {policy_path}: ");
    try expectContains(checker, "unexpected toolchain policy keys in {policy_path}: ");
    try expectContains(checker, "duplicate upgrade_policy keys in {policy_path}: ");
    try expectContains(checker, "unexpected upgrade_policy keys in {policy_path}: ");
}

test "archive target scope is bidirectionally checked against archive sha entries" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectInOrder(checker, "archive_target_scope = require_string_list(", "\"archive_target_scope\"");
    try expectInOrder(checker, "missing_archive_targets = [target for target in archive_target_scope", "archive_target_scope references missing archive_sha256 entries");
    try expectInOrder(checker, "extra_archive_targets = [target for target in normalized_archives", "archive_sha256 contains targets outside archive_target_scope");
    try expectInOrder(checker, "for target in archive_targets:", "expected_filename = policy_archive_filename(str(target), channel)");
    try expectContains(checker, "archive target {target!r} is outside archive_target_scope in {policy_path}: ");
}

test "required make routes remain non-empty unique policy schema entries" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectInOrder(checker, "required_make_routes = require_string_list(", "upgrade_policy.get(\"required_make_routes\")");
    try expectInOrder(checker, "required_make_routes = require_string_list(", "\"required_make_routes\"");
    try expectContains(checker, "duplicate {field_name} entry in {policy_path}: {normalized_entry}");
    try expectContains(checker, "invalid required_make_routes");
    try expectContains(checker, "duplicate required_make_routes entry");
    try expectContains(checker, "\"required_make_routes\": [\"phase2-toolchain\", \"phase2-validate\"]");
}

test "live policy pins phase two channel and target scope exactly" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectInOrder(policy, "\"archive_target_scope\": [", "\"x86_64-linux\"");
    try expectInOrder(policy, "\"required_make_routes\": [", "\"phase2-toolchain\"");
    try expectInOrder(policy, "\"phase2-toolchain\"", "\"phase2-validate\"");
}
