const std = @import("std");

const iteration_markers = [_][]const u8{
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS",
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS",
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS",
    "PHASE1_BENCH_STRING_ITERATIONS",
    "PHASE1_BENCH_HWEIGHT_ITERATIONS",
    "PHASE1_BENCH_LIST_SORT_ITERATIONS",
    "PHASE1_BENCH_RBTREE_ITERATIONS",
};

const checksum_markers = [_][]const u8{
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    "PHASE1_BENCH_STRING_CHECKSUM",
    "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try expectContains(haystack, needle);
    }
}

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

test "phase1 bench checker keeps the closed iteration and checksum contract" {
    const checker = try readFixture(std.testing.allocator, "scripts/zigux/check-phase1-bench.py");
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "EXPECTED_ITERATIONS");
    try expectContains(checker, "EXPECTED_CHECKSUMS");
    try expectContains(checker, "REQUIRED_EXACT_CHECKSUMS");
    try expectContainsAll(checker, iteration_markers[0..]);
    try expectContainsAll(checker, checksum_markers[0..]);

    try expectContains(checker, "exact_checksums");
    try expectContains(checker, "missing_find_bit_exact");
    try expectContains(checker, "missing_exact");
}

test "phase1 bench checker keeps outward pass and fail markers stable" {
    const checker = try readFixture(std.testing.allocator, "scripts/zigux/check-phase1-bench.py");
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "PHASE1_BENCH_CHECK_SELF_TEST=pass");
    try expectContains(checker, "PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT");
    try expectContains(checker, "PHASE1_BENCH_CHECK=pass");
    try expectContains(checker, "PHASE1_BENCH_EXPECTATIONS=");
    try expectContains(checker, "PHASE1_BENCH_SOURCE=");
    try expectContains(checker, "PHASE1_BENCH_ZIG=");

    try expectContains(checker, "PHASE1_BENCH_CHECK=fail");
    try expectContains(checker, "MISSING_EXPECTATION_ITERATIONS_START");
    try expectContains(checker, "MISSING_EXPECTATION_CHECKSUMS_START");
    try expectContains(checker, "MISSING_PHASE1_BENCH_SOURCE_MARKER_GROUP=");
    try expectContains(checker, "MISSING_PHASE1_BENCH_EXACT_CHECKSUMS_START");
}

test "phase1 bench checker still protects the live bench source and fixture packet" {
    const checker = try readFixture(std.testing.allocator, "scripts/zigux/check-phase1-bench.py");
    defer std.testing.allocator.free(checker);
    const bench_source = try readFixture(std.testing.allocator, "zigux/tests/phase1_bench.zig");
    defer std.testing.allocator.free(bench_source);
    const expectations = try readFixture(std.testing.allocator, "zigux/tests/fixtures/phase1_bench_expectations.json");
    defer std.testing.allocator.free(expectations);

    try expectContains(checker, "phase1_bench_expectations.json");
    try expectContains(checker, "phase1_bench.zig");
    try expectContains(checker, "build");
    try expectContains(checker, "bench");
    try expectContains(checker, "-Doptimize=ReleaseSafe");

    try expectContainsAll(bench_source, iteration_markers[0..]);
    try expectContainsAll(bench_source, checksum_markers[0..]);
    try expectContains(bench_source, "fn findBitBench() struct { checksum: u64 } {");
    try expectContains(bench_source, "fn rbtreeBench()");

    try expectContains(expectations, "\"status\": \"pass\"");
    try expectContainsAll(expectations, iteration_markers[0..]);
    try expectContainsAll(expectations, checksum_markers[0..]);
    try expectContains(expectations, "\"exact_checksums\"");
}
