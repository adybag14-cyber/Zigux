const std = @import("std");

const checker_path = "scripts/zigux/check-phase2-cross.py";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "direct cross checker reports required file misses before route success" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "except FileNotFoundError as exc:");
    try expectContains(checker, "raise SystemExit(f\"required file missing: {path}\") from exc");
    try expectContains(checker, "TOOLCHAIN_POLICY = ROOT / \"scripts\" / \"zigux\" / \"zig-toolchain-policy.json\"");
    try expectContains(checker, "MAKEFILE = ROOT / \"zigux\" / \"Makefile\"");
    try expectContains(checker, "FIXTURE = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase2_cross_targets.json\"");
    try expectContains(checker, "issues = collect_issues(args.root.resolve())");
    try expectContains(checker, "if issues:");
    try expectContains(checker, "return emit_issues(issues)");
    try expectContains(checker, "print(\"PHASE2_DIRECT_CROSS_ROUTE=pass\")");
}

test "self-test keeps missing primary file coverage explicit" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(checker, "for primary_path in (TOOLCHAIN_POLICY, MAKEFILE, FIXTURE):");
    try expectContains(checker, "resolve_path(root, primary_path).unlink()");
    try expectContains(checker, "assert \"required file missing\" in str(exc)");
    try expectContains(checker, "raise AssertionError(f\"missing primary file did not abort: {primary_path}\")");
    try expectContains(checker, "print(\"PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass\")");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT={checks_run}");
}

test "direct cross fixture remains two-target missing-input boundary" {
    const allocator = std.testing.allocator;
    const fixture = try readFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "riscv64-linux");
}
