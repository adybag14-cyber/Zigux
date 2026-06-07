const std = @import("std");
const testing = std.testing;

const checker_path = "scripts/zigux/check-phase2-cross.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, testing.allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "direct cross checker keeps malformed json and policy shape aborts" {
    const checker = try readRepoFile(checker_path);
    defer testing.allocator.free(checker);

    try expectContains(checker, "except json.JSONDecodeError as exc:");
    try expectContains(checker, "invalid json in required file");
    try expectContains(checker, "invalid json shape in required file");
    try expectContains(checker, "invalid upgrade_policy in required file");
    try expectContains(checker, "invalid archive_target_scope in required file");
    try expectContains(checker, "duplicate archive_target_scope entry in required file");
}

test "direct cross checker keeps fixture shape issue vocabulary" {
    const checker = try readRepoFile(checker_path);
    defer testing.allocator.free(checker);

    try expectContains(checker, "INVALID_FIXTURE_SHAPE");
    try expectContains(checker, "INVALID_FIXTURE_FIELD");
    try expectContains(checker, "ARCHIVE_SCOPE_MISMATCH");
    try expectContains(checker, "INVALID_CROSS_TARGET_ENTRY");
    try expectContains(checker, "DUPLICATE_CROSS_TARGET");
    try expectContains(checker, "INVALID_CROSS_TARGET_ROUTE");
    try expectContains(checker, "INVALID_CROSS_TARGET_MODE");
    try expectContains(checker, "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH");
}

test "policy and fixture keep two target json boundary" {
    const policy = try readRepoFile(policy_path);
    defer testing.allocator.free(policy);
    const fixture = try readRepoFile(fixture_path);
    defer testing.allocator.free(fixture);

    try expectContains(policy, "\"archive_sha256\"");
    try expectContains(policy, "\"x86_64-linux\"");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"phase2-cross\"");
    try expectNotContains(policy, "\"aarch64-linux\"");
    try expectNotContains(policy, "\"riscv64-linux\"");

    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectNotContains(fixture, "\"riscv64-linux\"");
}

test "checker success output remains count based after shape checks" {
    const checker = try readRepoFile(checker_path);
    defer testing.allocator.free(checker);

    const shape_guard_index = std.mem.indexOf(u8, checker, "load_archive_target_scope").?;
    const pass_marker_index = std.mem.indexOf(u8, checker, "PHASE2_DIRECT_CROSS_ROUTE=pass").?;
    try testing.expect(shape_guard_index < pass_marker_index);
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT");
}
