const std = @import("std");
const testing = std.testing;

const max_file_size = 512 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "policy keeps archive sha key scoped to archive-backed target" {
    const allocator = testing.allocator;
    const policy = try readRepoFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);

    try expectContains(policy,
        \\"archive_sha256": {
        \\
    );
    try expectContains(policy,
        \\"x86_64-linux": "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6"
        \\
    );
    try expectContains(policy,
        \\"archive_target_scope": [
        \\      "x86_64-linux"
        \\    ]
    );
    try testing.expectEqual(@as(usize, 2), countOccurrences(policy, "\"x86_64-linux\""));
    try testing.expectEqual(@as(usize, 0), countOccurrences(policy, "\"aarch64-linux\""));
    try testing.expectEqual(@as(usize, 0), countOccurrences(policy, "\"riscv64-linux\""));
    try expectBefore(policy, "\"archive_sha256\"", "\"upgrade_policy\"");
    try expectBefore(policy, "\"archive_target_scope\"", "\"required_make_routes\"");
}

test "fixture validation modes match the policy archive sha boundary" {
    const allocator = testing.allocator;
    const fixture = try readRepoFile(allocator, "zigux/tests/fixtures/phase2_cross_targets.json");
    defer allocator.free(fixture);

    try expectContains(fixture,
        \\"archive_target_scope": [
        \\    "x86_64-linux"
        \\  ]
    );
    try expectContains(fixture,
        \\"target": "x86_64-linux",
        \\      "review_status": "pinned bootstrap archive",
        \\      "validation_mode": "archive_required"
    );
    try expectContains(fixture,
        \\"target": "aarch64-linux",
        \\      "review_status": "route contract only",
        \\      "validation_mode": "route_contract_only"
    );
    try testing.expectEqual(@as(usize, 2), countOccurrences(fixture, "\"target\""));
    try testing.expectEqual(@as(usize, 1), countOccurrences(fixture, "\"validation_mode\": \"archive_required\""));
    try testing.expectEqual(@as(usize, 1), countOccurrences(fixture, "\"validation_mode\": \"route_contract_only\""));
    try expectNotContains(fixture, "archive_sha256");
    try expectNotContains(fixture, "riscv64-linux");
}

test "cross checkers continue deriving archive scope from policy and fixture" {
    const allocator = testing.allocator;
    const direct_checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-cross.py");
    defer allocator.free(direct_checker);
    const alignment_checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-cross-selftest-alignment.py");
    defer allocator.free(alignment_checker);

    try expectContains(direct_checker, "TOOLCHAIN_POLICY = ROOT / \"scripts\" / \"zigux\" / \"zig-toolchain-policy.json\"");
    try expectContains(direct_checker, "FIXTURE = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase2_cross_targets.json\"");
    try expectContains(direct_checker, "archive_target_scope = upgrade_policy.get(\"archive_target_scope\")");
    try expectContains(direct_checker, "if fixture_scope != archive_target_scope:");
    try expectContains(direct_checker, "if archive_required_targets != set(archive_target_scope):");
    try expectContains(direct_checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT");
    try expectContains(direct_checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");

    try expectContains(alignment_checker, "TOOLCHAIN_POLICY = ROOT / \"scripts\" / \"zigux\" / \"zig-toolchain-policy.json\"");
    try expectContains(alignment_checker, "CROSS_TARGETS = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase2_cross_targets.json\"");
    try expectContains(alignment_checker, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try expectContains(alignment_checker, "unsupported_targets = [target for target in normalized_scope if target not in SUPPORTED_CROSS_TARGETS]");
    try expectContains(alignment_checker, "\"archive_sha256\": {\"x86_64-linux\": \"3\" * 64}");
    try expectContains(alignment_checker, "\"PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=\"");
}
