const std = @import("std");

const allocator = std.testing.allocator;

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase2 cross checker groups fail output by issue code" {
    const checker = try readRepoFile("scripts/zigux/check-phase2-cross.py");
    defer allocator.free(checker);

    try expectContains(checker, "def emit_issues(issues: list[tuple[str, str]]) -> int:");
    try expectContains(checker, "grouped: dict[str, list[str]] = {}");
    try expectContains(checker, "grouped.setdefault(code, []).append(value)");
    try expectContains(checker, "print(\"PHASE2_DIRECT_CROSS_ROUTE=fail\")");
    try expectContains(checker, "print(f\"{code}_START\")");
    try expectContains(checker, "print(f\"{code}_END\")");
    try expectContains(checker, "return 1");
}

test "phase2 cross checker self-test keeps issue vocabulary visible" {
    const checker = try readRepoFile("scripts/zigux/check-phase2-cross.py");
    defer allocator.free(checker);

    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(checker, "(\"ARCHIVE_SCOPE_MISMATCH\", \"x86_64-linux\")");
    try expectContains(checker, "(\"ARCHIVE_REQUIRED_TARGET_SET_MISMATCH\", \"\")");
    try expectContains(checker, "(\"DUPLICATE_CROSS_TARGET\", \"x86_64-linux\")");
    try expectContains(checker, "(\"INVALID_CROSS_TARGET_ROUTE\", \"aarch64-linux\")");
    try expectContains(checker, "(\"INVALID_CROSS_TARGET_ENTRY\", \"aarch64-linux:review_status\")");
    try expectContains(checker, "(\"INVALID_CROSS_TARGET_MODE\", \"aarch64-linux\")");
    try expectContains(checker, "duplicate archive_target_scope entry");
    try expectContains(checker, "required file missing");
}

test "phase2 cross checker pass output remains count based" {
    const checker = try readRepoFile("scripts/zigux/check-phase2-cross.py");
    defer allocator.free(checker);

    try expectContains(checker, "print(\"PHASE2_DIRECT_CROSS_ROUTE=pass\")");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT={len(cross_targets)}");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT={len(load_archive_target_scope(args.root.resolve()))}");
    try expectContains(checker, "parser.add_argument(\"--root\", type=Path, default=ROOT, help=\"Repository root to inspect\")");
    try expectContains(checker, "parser.add_argument(\"--self-test\", action=\"store_true\", help=\"Run built-in contract checks\")");
}

test "phase2 cross fixture and policy keep current issue-group boundary" {
    const fixture = try readRepoFile("zigux/tests/fixtures/phase2_cross_targets.json");
    defer allocator.free(fixture);
    const policy = try readRepoFile("scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "riscv64-linux");

    try expectContains(policy, "\"archive_sha256\": {\n    \"x86_64-linux\":");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectContains(policy, "\"phase2-cross\"");
    try expectNotContains(policy, "\"aarch64-linux\":");
    try expectNotContains(policy, "\"riscv64-linux\":");
}
