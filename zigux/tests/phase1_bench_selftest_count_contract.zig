const std = @import("std");
const config = @import("config");

fn readChecker(allocator: std.mem.Allocator) ![]const u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, config.checker_path, allocator, .limited(512 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: []const u8 = haystack;
    while (std.mem.indexOf(u8, cursor, needle)) |index| {
        count += 1;
        cursor = cursor[index + needle.len ..];
    }
    return count;
}

fn summedCaseCountIncrements(source: []const u8) !usize {
    var total: usize = 0;
    var cursor: []const u8 = source;
    const prefix = "case_count += ";
    while (std.mem.indexOf(u8, cursor, prefix)) |index| {
        const value_start = index + prefix.len;
        const value_end = std.mem.indexOfScalarPos(u8, cursor, value_start, '\n') orelse cursor.len;
        const raw_value = std.mem.trim(u8, cursor[value_start..value_end], " \t\r");
        total += try std.fmt.parseInt(usize, raw_value, 10);
        cursor = cursor[value_end..];
    }
    return total;
}

test "phase1 bench checker self-test publishes the current success and case-count footer" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try requireContains(checker, "parser.add_argument(\"--self-test\", action=\"store_true\", help=\"Run checker self-test cases without invoking Zig.\")");
    try requireContains(checker, "if args.self_test:");
    try requireContains(checker, "run_self_test()");
    try requireContains(checker, "print(\"PHASE1_BENCH_CHECK_SELF_TEST=pass\")");
    try requireContains(checker, "print(f\"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}\")");
    try requireAbsent(checker, "PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT=19");
}

test "phase1 bench checker self-test count remains tied to all guarded regression cases" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try std.testing.expectEqual(@as(usize, 21), try summedCaseCountIncrements(checker));
    try std.testing.expect(countOccurrences(checker, "case_count += 1") >= 16);
    try requireContains(checker, "case_count += 3");
    try requireContains(checker, "kind == \"missing_bench_source_file\"");
    try requireContains(checker, "kind == \"bench_source_missing_markers\"");
    try requireContains(checker, "kind == \"bench_source_duplicate_rbtree_markers\"");
    try requireContains(checker, "kind == \"expectations_duplicate_keys\"");
    try requireContains(checker, "kind == \"expectations_missing_rbtree_iterations\"");
    try requireContains(checker, "kind == \"expectations_checksums_rbtree_exact_required\"");
    try requireContains(checker, "kind == \"missing_rbtree_iterations\"");
    try requireContains(checker, "kind == \"missing_rbtree_exact_checksums\"");
}

test "phase1 bench checker self-test still covers rooted fixture reads before runtime bench execution" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try requireContains(checker, "with tempfile.TemporaryDirectory(prefix=\"phase1-bench-root-\") as tmp:");
    try requireContains(checker, "assert_case(repo_root(str(root)) == root.resolve(), \"repo root override\")");
    try requireContains(checker, "kind, payload = load_runtime_bench_source(bench_source_path(root))");
    try requireContains(checker, "kind, payload = load_runtime_expectations(expectations_path(root))");
    try requireContains(checker, "case_count += 3");
    try requireContains(checker, "[zig, \"build\", \"bench\", \"--build-file\", \"zigux/tests/phase1_bench_build.zig\", \"-Doptimize=ReleaseSafe\"]");
}
