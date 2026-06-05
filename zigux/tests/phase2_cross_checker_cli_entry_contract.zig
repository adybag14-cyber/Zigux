const std = @import("std");
const testing = std.testing;

const checker_path = "scripts/zigux/check-phase2-cross.py";

fn readCheckerSource(allocator: std.mem.Allocator) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, checker_path, allocator, .limited(1024 * 1024));
}

fn expectContains(source: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn expectNotContains(source: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, source, needle) == null);
}

fn expectBefore(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "phase2 cross checker keeps argparse entry points visible" {
    const source = try readCheckerSource(testing.allocator);
    defer testing.allocator.free(source);

    try expectContains(
        source,
        "description=\"Check that the rematerialized Phase 2 direct cross-route packet stays aligned.\"",
    );
    try expectContains(
        source,
        "parser.add_argument(\"--root\", type=Path, default=ROOT, help=\"Repository root to inspect\")",
    );
    try expectContains(
        source,
        "parser.add_argument(\"--self-test\", action=\"store_true\", help=\"Run built-in contract checks\")",
    );
    try expectContains(source, "args = parser.parse_args()");
    try expectBefore(source, "parser.add_argument(\"--root\"", "parser.add_argument(\"--self-test\"");
    try expectBefore(source, "args = parser.parse_args()", "if args.self_test:");
}

test "phase2 cross checker dispatches self test before repository inspection" {
    const source = try readCheckerSource(testing.allocator);
    defer testing.allocator.free(source);

    try expectContains(source, "if args.self_test:\n        return run_self_test()");
    try expectBefore(source, "if args.self_test:", "issues = collect_issues(args.root.resolve())");
    try expectBefore(source, "return run_self_test()", "issues = collect_issues(args.root.resolve())");
    try expectBefore(source, "issues = collect_issues(args.root.resolve())", "if issues:");
    try expectBefore(source, "if issues:", "return emit_issues(issues)");
}

test "phase2 cross checker success path stays count based" {
    const source = try readCheckerSource(testing.allocator);
    defer testing.allocator.free(source);

    try expectBefore(source, "if issues:", "fixture = read_json(resolve_path(args.root.resolve(), FIXTURE))");
    try expectBefore(
        source,
        "fixture = read_json(resolve_path(args.root.resolve(), FIXTURE))",
        "cross_targets = fixture.get(\"cross_targets\")",
    );
    try expectBefore(
        source,
        "cross_targets = fixture.get(\"cross_targets\")",
        "print(\"PHASE2_DIRECT_CROSS_ROUTE=pass\")",
    );
    try expectContains(source, "print(f\"PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT={len(cross_targets)}\")");
    try expectContains(
        source,
        "print(f\"PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT={len(load_archive_target_scope(args.root.resolve()))}\")",
    );
}

test "phase2 cross checker remains direct script executable" {
    const source = try readCheckerSource(testing.allocator);
    defer testing.allocator.free(source);

    try expectContains(source, "if __name__ == \"__main__\":\n    raise SystemExit(main())");
    try expectContains(source, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(source, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try expectContains(source, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT={checks_run}");
    try expectNotContains(source, "riscv64");
}
