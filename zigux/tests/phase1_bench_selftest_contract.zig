const std = @import("std");

const checker_paths = [_][]const u8{
    "scripts/zigux/check-phase1-bench.py",
    "../../scripts/zigux/check-phase1-bench.py",
};

fn readChecker(allocator: std.mem.Allocator) ![]const u8 {
    var last_error: anyerror = error.FileNotFound;
    for (checker_paths) |path| {
        return std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            path,
            allocator,
            .limited(512 * 1024),
        ) catch |err| {
            last_error = err;
            continue;
        };
    }
    return last_error;
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, std.mem.count(u8, haystack, needle));
}

test "phase1 bench checker exposes self-test command and pass markers" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "def run_self_test() -> None:");
    try requireContains(source, "parser.add_argument(\"--self-test\", action=\"store_true\", help=\"Run checker self-test cases without invoking Zig.\")");
    try requireContains(source, "if args.self_test:");
    try requireContains(source, "run_self_test()");
    try requireContains(source, "PHASE1_BENCH_CHECK_SELF_TEST=pass");
    try requireContains(source, "PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}");
    try requireCount(source, "PHASE1_BENCH_CHECK_SELF_TEST=pass", 1);
    try requireCount(source, "PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}", 1);
}

test "phase1 bench checker self-test pins path root and fixture loading cases" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "missing_bench_source_file");
    try requireContains(source, "loaded bench source pass");
    try requireContains(source, "repo root override");
    try requireContains(source, "bench source root override");
    try requireContains(source, "expectations root override");
    try requireContains(source, "duplicate top-level key");
    try requireContains(source, "expectations_duplicate_keys");
    try requireContains(source, "duplicate top-level payload");
}

test "phase1 bench checker self-test covers source marker drift cases" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "omit_find_bit_label");
    try requireContains(source, "bench_source_missing_markers");
    try requireContains(source, "missing find_bit marker");
    try requireContains(source, "find_edge_checksum_print");
    try requireContains(source, "omit_rbtree_label");
    try requireContains(source, "missing rbtree marker");
    try requireContains(source, "rbtree_cached_print");
    try requireContains(source, "bench_source_duplicate_rbtree_markers");
    try requireContains(source, "duplicate rbtree marker");
    try requireContains(source, "duplicate rbtree marker payload");
}

test "phase1 bench checker self-test keeps rbtree exact-output labels visible" {
    const source = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "missing rbtree expectation iteration");
    try requireContains(source, "expectations_missing_rbtree_iterations");
    try requireContains(source, "PHASE1_BENCH_RBTREE_ITERATIONS");
    try requireContains(source, "missing rbtree expectation exact checksum");
    try requireContains(source, "expectations_checksums_rbtree_exact_required");
    try requireContains(source, "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM");
    try requireContains(source, "missing rbtree output iteration");
    try requireContains(source, "missing_rbtree_iterations");
    try requireContains(source, "missing rbtree output exact checksum");
    try requireContains(source, "missing_rbtree_exact_checksums");
}
