const std = @import("std");

const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";
const direct_checker_path = "scripts/zigux/check-phase2-cross.py";
const alignment_checker_path = "scripts/zigux/check-phase2-cross-selftest-alignment.py";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(512 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn policyDigest(policy: []const u8, target: []const u8) ![]const u8 {
    const target_index = std.mem.indexOf(u8, policy, target) orelse return error.MissingTarget;
    const after_target = policy[target_index + target.len ..];
    const colon_index = std.mem.indexOf(u8, after_target, ":") orelse return error.MissingDigestColon;
    const after_colon = after_target[colon_index + 1 ..];
    const first_quote = std.mem.indexOf(u8, after_colon, "\"") orelse return error.MissingDigestOpenQuote;
    const digest_start = first_quote + 1;
    const second_quote = std.mem.indexOf(u8, after_colon[digest_start..], "\"") orelse return error.MissingDigestCloseQuote;
    return after_colon[digest_start .. digest_start + second_quote];
}

fn requireHexDigest(digest: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 64), digest.len);
    for (digest) |byte| {
        try std.testing.expect(std.ascii.isHex(byte));
    }
}

test "policy keeps one archive-backed target with a concrete digest" {
    const allocator = std.testing.allocator;
    const policy = try readFile(allocator, policy_path);
    defer allocator.free(policy);
    const fixture = try readFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try requireContains(policy, "\"archive_sha256\"");
    try requireContains(policy, "\"x86_64-linux\"");
    try requireNotContains(policy, "\"aarch64-linux\": \"");

    const digest = try policyDigest(policy, "\"x86_64-linux\"");
    try requireHexDigest(digest);

    try requireContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try requireContains(fixture, "\"target\": \"x86_64-linux\"");
    try requireContains(fixture, "\"validation_mode\": \"archive_required\"");
    try requireContains(fixture, "\"target\": \"aarch64-linux\"");
    try requireContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try requireNotContains(fixture, "riscv64-linux");
}

test "direct cross checker self-test carries the digest boundary" {
    const allocator = std.testing.allocator;
    const direct_checker = try readFile(allocator, direct_checker_path);
    defer allocator.free(direct_checker);

    try requireContains(direct_checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try requireContains(direct_checker, "\"archive_sha256\": {\"x86_64-linux\": \"3\" * 64}");
    try requireContains(direct_checker, "\"archive_target_scope\": [\"x86_64-linux\"]");
    try requireContains(direct_checker, "\"validation_mode\": \"archive_required\"");
    try requireContains(direct_checker, "\"validation_mode\": \"route_contract_only\"");
    try requireContains(direct_checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT");
}

test "alignment checker rejects stale archive-target assumptions" {
    const allocator = std.testing.allocator;
    const alignment_checker = try readFile(allocator, alignment_checker_path);
    defer allocator.free(alignment_checker);

    try requireContains(alignment_checker, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try requireContains(alignment_checker, "\"archive_sha256\": {\"x86_64-linux\": \"3\" * 64}");
    try requireContains(alignment_checker, "\"archive_sha256\": {\"riscv64-linux\": \"3\" * 64}");
    try requireContains(alignment_checker, "unsupported archive_target_scope targets");
    try requireContains(alignment_checker, "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT");
    try requireContains(alignment_checker, "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT");
}
