const std = @import("std");

const checker_path = "scripts/zigux/check-lane05-archive-parts-packet.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "archive-parts checker keeps x86_64-linux trusted size fallback" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "EXPECTED_ARCHIVE_SIZES = {\"x86_64-linux\": 58_159_088}");
    try expectContains(checker, "optional_size = policy.get(\"archive_size_bytes\")");
    try expectContains(checker, "missing expected archive size for {target}");
    try expectContains(checker, "expected_size = EXPECTED_ARCHIVE_SIZES[target]");
}

test "current policy deliberately relies on checker fallback size" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);

    try expectContains(policy, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy, "\"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"");
    try std.testing.expect(std.mem.indexOf(u8, policy, "archive_size_bytes") == null);
}

test "checker reports the fallback size in bootstrap-readable status output" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "LANE05_ARCHIVE_PARTS_PACKET_EXPECTED_SIZE={validated['size']}");
    try expectContains(checker, "LANE05_ARCHIVE_PARTS_PACKET_STATUS={status}");
    try expectContains(checker, "status in {'verified', 'missing_allowed'}");
}
