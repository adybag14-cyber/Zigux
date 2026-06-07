const std = @import("std");
const testing = std.testing;

const max_file_size = 1024 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase2 cross policy keeps single archive sha owner" {
    const allocator = testing.allocator;
    const policy = try readRepoFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);

    try expectContains(policy, "\"archive_sha256\": {");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectNotContains(policy, "\"aarch64-linux\": \"");
    try expectNotContains(policy, "\"riscv64-linux\": \"");
}

test "phase2 cross fixture keeps archive-required target aligned with policy sha scope" {
    const allocator = testing.allocator;
    const fixture = try readRepoFile(allocator, "zigux/tests/fixtures/phase2_cross_targets.json");
    defer allocator.free(fixture);

    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "\"target\": \"riscv64-linux\"");
}

test "phase2 cross alignment checker self-test keeps archive sha mutation surface" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-cross-selftest-alignment.py");
    defer allocator.free(checker);

    try expectContains(checker, "\"archive_sha256\": {\"x86_64-linux\": \"3\" * 64}");
    try expectContains(checker, "payload[\"archive_sha256\"] = {\"aarch64-linux\": \"3\" * 64}");
    try expectContains(checker, "payload[\"archive_sha256\"] = {\"riscv64-linux\": \"3\" * 64}");
    try expectContains(checker, "unsupported archive_target_scope targets");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=");
}
