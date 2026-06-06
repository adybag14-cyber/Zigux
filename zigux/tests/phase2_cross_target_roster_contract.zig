const std = @import("std");
const testing = std.testing;

const direct_checker_path = "scripts/zigux/check-phase2-cross.py";
const alignment_checker_path = "scripts/zigux/check-phase2-cross-selftest-alignment.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectInOrder(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
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

test "direct cross checker keeps target-count and archive-scope summary markers" {
    const checker = try readRepoFile(testing.allocator, direct_checker_path);
    defer testing.allocator.free(checker);

    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(checker, "ALLOWED_VALIDATION_MODES = (\"archive_required\", \"route_contract_only\")");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=");
    try expectContains(checker, "(\"ARCHIVE_SCOPE_MISMATCH\", \",\".join(archive_target_scope))");
    try expectContains(checker, "(\"ARCHIVE_REQUIRED_TARGET_SET_MISMATCH\", \",\".join(sorted(archive_required_targets)))");
    try expectContains(checker, "(\"DUPLICATE_CROSS_TARGET\", target)");
    try expectContains(checker, "(\"INVALID_CROSS_TARGET_MODE\", target)");
}

test "alignment checker derives the supported two-target roster from policy scope" {
    const checker = try readRepoFile(testing.allocator, alignment_checker_path);
    defer testing.allocator.free(checker);

    try expectContains(checker, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try expectContains(checker, "target: (\"archive_required\" if target in seen_scope else \"route_contract_only\")");
    try expectContains(checker, "\"phase2-cross\",");
    try expectContains(checker, "unsupported archive_target_scope targets");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=");
    try expectContains(checker, "(\"INVALID_CROSS_TARGET_MATRIX\", json.dumps(actual_modes, sort_keys=True))");

    try expectInOrder(checker, "\"phase2-kconfig\",", "\"phase2-cross\",");
    try expectInOrder(checker, "\"phase2-cross\",", "\"phase2-genksyms\",");
}

test "cross-target fixture keeps the current x86 archive-backed and aarch64 route-only split" {
    const fixture = try readRepoFile(testing.allocator, fixture_path);
    defer testing.allocator.free(fixture);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"review_status\": \"route contract only\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "riscv64-linux");

    try expectInOrder(fixture, "\"target\": \"x86_64-linux\"", "\"target\": \"aarch64-linux\"");
    try expectCount(fixture, "\"target\":", 2);
    try expectCount(fixture, "\"validation_mode\":", 2);
    try expectCount(fixture, "\"route\": \"make -C zigux phase2-cross\"", 3);
}

test "toolchain policy keeps archive authority scoped to the x86 bootstrap target" {
    const policy = try readRepoFile(testing.allocator, policy_path);
    defer testing.allocator.free(policy);

    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"archive_sha256\": {\n    \"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"\n  }");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectContains(policy, "\"required_make_routes\": [");
    try expectContains(policy, "\"phase2-cross\"");
    try expectNotContains(policy, "\"aarch64-linux\":");
    try expectNotContains(policy, "\"riscv64-linux\":");

    try expectInOrder(policy, "\"phase2-kconfig\"", "\"phase2-cross\"");
    try expectInOrder(policy, "\"phase2-cross\"", "\"phase2-genksyms\"");
}
