const std = @import("std");

const checker_path = "scripts/zigux/check-zig-toolchain.py";

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

test "policy JSON duplicate tracking remains wired into load_policy" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "class DuplicateTrackingDict(dict[str, object]):");
    try expectContains(checker, "self.duplicate_keys: list[str] = []");
    try expectContains(checker, "object_pairs_hook=DuplicateTrackingDict");
    try expectInOrder(checker, "json.loads(", "object_pairs_hook=DuplicateTrackingDict");
    try expectInOrder(checker, "if isinstance(payload, DuplicateTrackingDict) and payload.duplicate_keys:", "duplicate toolchain policy keys");
}

test "archive and upgrade policy duplicate keys fail closed" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectInOrder(checker, "archive_sha256 = payload.get(\"archive_sha256\")", "duplicate archive_sha256 targets");
    try expectInOrder(checker, "upgrade_policy = payload.get(\"upgrade_policy\")", "duplicate upgrade_policy keys");
    try expectContains(checker, "if isinstance(archive_sha256, DuplicateTrackingDict) and archive_sha256.duplicate_keys:");
    try expectContains(checker, "if isinstance(upgrade_policy, DuplicateTrackingDict) and upgrade_policy.duplicate_keys:");
}

test "toolchain policy list duplicates remain rejected" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "duplicate {field_name} entry in {policy_path}: ");
    try expectContains(checker, "archive_target_scope = require_string_list(");
    try expectContains(checker, "required_make_routes = require_string_list(");
    try expectInOrder(checker, "def require_string_list(", "if normalized_entry in seen:");
    try expectInOrder(checker, "if normalized_entry in seen:", "raise ValueError(");
}

test "checker self-test keeps representative duplicate cases" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "\"phase\":\"Phase 2\",\"phase\":\"Phase 3\"");
    try expectContains(checker, "\"channel_minimum_lockstep\":true,\"channel_minimum_lockstep\":false");
    try expectContains(checker, "\"required_make_routes\":[\"phase2-toolchain\",\"phase2-toolchain\"]");
    try expectContains(checker, "\"duplicate toolchain policy keys\"");
    try expectContains(checker, "\"duplicate upgrade_policy keys\"");
    try expectContains(checker, "\"duplicate required_make_routes entry\"");
}
