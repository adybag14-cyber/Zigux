const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, relative_path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "direct cross checker exposes a staged-root CLI contract" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-cross.py");
    defer allocator.free(checker);

    try expectContains(checker, "parser.add_argument(\"--root\", type=Path, default=ROOT");
    try expectContains(checker, "issues = collect_issues(args.root.resolve())");
    try expectContains(checker, "fixture = read_json(resolve_path(args.root.resolve(), FIXTURE))");
    try expectContains(
        checker,
        "len(load_archive_target_scope(args.root.resolve()))",
    );
    try expectBefore(checker, "parser.add_argument(\"--root\"", "issues = collect_issues(args.root.resolve())");
}

test "direct cross checker rebases every required file through resolve_path" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-cross.py");
    defer allocator.free(checker);

    try expectContains(checker, "def resolve_path(root: Path, path: Path) -> Path:");
    try expectContains(checker, "return root / path.relative_to(ROOT)");
    try expectContains(checker, "return root / path");
    try expectContains(checker, "read_json(resolve_path(root, TOOLCHAIN_POLICY))");
    try expectContains(checker, "read_text(resolve_path(root, MAKEFILE))");
    try expectContains(checker, "read_json(resolve_path(root, FIXTURE))");
    try expectContains(checker, "load_archive_target_scope(root)");
}

test "direct cross self-test packet is also rooted under the supplied tree" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-cross.py");
    defer allocator.free(checker);

    try expectContains(checker, "def build_self_test_root(root: Path) -> None:");
    try expectContains(checker, "write_text(resolve_path(root, TOOLCHAIN_POLICY),");
    try expectContains(checker, "write_text(resolve_path(root, MAKEFILE),");
    try expectContains(checker, "write_text(\n        resolve_path(root, FIXTURE),");
    try expectContains(checker, "build_self_test_root(root)");
    try expectContains(checker, "assert collect_issues(root) == []");
    try expectContains(checker, "assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT");
}

test "live cross fixture remains a two-target staged-root boundary" {
    const allocator = std.testing.allocator;
    const fixture = try readRepoFile(allocator, "zigux/tests/fixtures/phase2_cross_targets.json");
    defer allocator.free(fixture);

    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try std.testing.expect(std.mem.indexOf(u8, fixture, "\"target\": \"riscv64-linux\"") == null);
}
