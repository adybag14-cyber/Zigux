const std = @import("std");
const testing = std.testing;

const alignment_checker_path = "scripts/zigux/check-phase2-cross-selftest-alignment.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try testing.expect(earlier_index < later_index);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    try testing.expectEqual(expected, count);
}

test "alignment checker keeps required Phase 2 route tuple ordered" {
    const checker = try readRepoFile(testing.allocator, alignment_checker_path);
    defer testing.allocator.free(checker);

    const routes = [_][]const u8{
        "\"phase2-toolchain\"",
        "\"phase2-tools\"",
        "\"phase2-kconfig\"",
        "\"phase2-cross\"",
        "\"phase2-genksyms\"",
        "\"phase2-fixdep\"",
        "\"phase2-validate\"",
    };

    try expectContains(checker, "EXPECTED_REQUIRED_MAKE_ROUTES = (");
    for (routes) |route| {
        try expectContains(checker, route);
    }

    try expectOrdered(checker, "\"phase2-kconfig\"", "\"phase2-cross\"");
    try expectOrdered(checker, "\"phase2-cross\"", "\"phase2-genksyms\"");
    try expectOrdered(checker, "\"phase2-fixdep\"", "\"phase2-validate\"");
    try expectContains(checker, "invalid required_make_routes");
}

test "supported target set stays limited to current direct cross matrix" {
    const checker = try readRepoFile(testing.allocator, alignment_checker_path);
    defer testing.allocator.free(checker);

    try expectContains(checker, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try expectContains(checker, "unsupported archive_target_scope targets");
    try expectNotContains(checker, "\"riscv64-linux\"");
}

test "policy and fixture keep archive authority scoped to x86 only" {
    const policy = try readRepoFile(testing.allocator, policy_path);
    defer testing.allocator.free(policy);
    const fixture = try readRepoFile(testing.allocator, fixture_path);
    defer testing.allocator.free(fixture);

    try expectContains(policy, "\"archive_sha256\": {\n    \"x86_64-linux\"");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectContains(policy, "\"required_make_routes\": [");
    try expectContains(policy, "\"phase2-cross\"");
    try expectNotContains(policy, "\"aarch64-linux\":");
    try expectNotContains(policy, "\"riscv64-linux\"");

    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "riscv64-linux");
}

test "mode derivation and public alignment markers keep route and target counts visible" {
    const checker = try readRepoFile(testing.allocator, alignment_checker_path);
    defer testing.allocator.free(checker);
    const fixture = try readRepoFile(testing.allocator, fixture_path);
    defer testing.allocator.free(fixture);

    try expectContains(checker, "\"archive_required\" if target in seen_scope else \"route_contract_only\"");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT=pass");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_MARKER_COUNT");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT");

    try expectOrdered(fixture, "\"target\": \"x86_64-linux\"", "\"target\": \"aarch64-linux\"");
    try expectCount(fixture, "\"target\":", 2);
    try expectCount(fixture, "\"validation_mode\":", 2);
    try expectCount(fixture, "\"route\": \"make -C zigux phase2-cross\"", 3);
}
