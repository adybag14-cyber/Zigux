const std = @import("std");

const fixture_bytes = @embedFile("fixtures/phase1_bench_expectations.json");
const bench_source = @embedFile("phase1_bench.zig");

const Iterations = struct {
    PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS: u64,
    PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS: u64,
    PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS: u64,
    PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS: u64,
    PHASE1_BENCH_STRING_ITERATIONS: u64,
    PHASE1_BENCH_HWEIGHT_ITERATIONS: u64,
    PHASE1_BENCH_LIST_SORT_ITERATIONS: u64,
    PHASE1_BENCH_RBTREE_ITERATIONS: u64,
};

const ExactChecksums = struct {
    PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM: u64,
    PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM: u64,
    PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM: u64,
    PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM: u64,
    PHASE1_BENCH_STRING_CHECKSUM: u64,
    PHASE1_BENCH_HWEIGHT_CHECKSUM: u64,
    PHASE1_BENCH_LIST_SORT_CHECKSUM: u64,
    PHASE1_BENCH_RBTREE_CHECKSUM: u64,
    PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM: u64,
    PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM: u64,
    PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM: u64,
    PHASE1_BENCH_RBTREE_CACHED_CHECKSUM: u64,
};

const BenchExpectations = struct {
    status: []const u8,
    iterations: Iterations,
    checksums: []const []const u8,
    exact_checksums: ExactChecksums,
};

const iteration_roster = [_][]const u8{
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS",
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS",
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS",
    "PHASE1_BENCH_STRING_ITERATIONS",
    "PHASE1_BENCH_HWEIGHT_ITERATIONS",
    "PHASE1_BENCH_LIST_SORT_ITERATIONS",
    "PHASE1_BENCH_RBTREE_ITERATIONS",
};

const checksum_roster = [_][]const u8{
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

fn loadExpectations() !std.json.Parsed(BenchExpectations) {
    return std.json.parseFromSlice(BenchExpectations, std.testing.allocator, fixture_bytes, .{});
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase1 bench expectations fixture pins current artifact packet" {
    var parsed = try loadExpectations();
    defer parsed.deinit();
    const fixture = parsed.value;

    try std.testing.expectEqualStrings("pass", fixture.status);
    try std.testing.expectEqual(@as(u64, 20000), fixture.iterations.PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS);
    try std.testing.expectEqual(@as(u64, 20000), fixture.iterations.PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS);
    try std.testing.expectEqual(@as(u64, 20000), fixture.iterations.PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS);
    try std.testing.expectEqual(@as(u64, 20000), fixture.iterations.PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS);
    try std.testing.expectEqual(@as(u64, 40000), fixture.iterations.PHASE1_BENCH_STRING_ITERATIONS);
    try std.testing.expectEqual(@as(u64, 100000), fixture.iterations.PHASE1_BENCH_HWEIGHT_ITERATIONS);
    try std.testing.expectEqual(@as(u64, 1000), fixture.iterations.PHASE1_BENCH_LIST_SORT_ITERATIONS);
    try std.testing.expectEqual(@as(u64, 4000), fixture.iterations.PHASE1_BENCH_RBTREE_ITERATIONS);

    try std.testing.expectEqual(@as(usize, checksum_roster.len), fixture.checksums.len);
    for (checksum_roster, fixture.checksums) |expected, actual| {
        try std.testing.expectEqualStrings(expected, actual);
    }

    try std.testing.expectEqual(@as(u64, 100000), fixture.exact_checksums.PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM);
    try std.testing.expectEqual(@as(u64, 120000), fixture.exact_checksums.PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM);
    try std.testing.expectEqual(@as(u64, 3780000), fixture.exact_checksums.PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM);
    try std.testing.expectEqual(@as(u64, 4020000), fixture.exact_checksums.PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM);
    try std.testing.expectEqual(@as(u64, 400000), fixture.exact_checksums.PHASE1_BENCH_STRING_CHECKSUM);
    try std.testing.expectEqual(@as(u64, 6800000), fixture.exact_checksums.PHASE1_BENCH_HWEIGHT_CHECKSUM);
    try std.testing.expectEqual(@as(u64, 10000), fixture.exact_checksums.PHASE1_BENCH_LIST_SORT_CHECKSUM);
    try std.testing.expectEqual(@as(u64, 24000), fixture.exact_checksums.PHASE1_BENCH_RBTREE_CHECKSUM);
    try std.testing.expectEqual(@as(u64, 24000), fixture.exact_checksums.PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM);
    try std.testing.expectEqual(@as(u64, 8000), fixture.exact_checksums.PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM);
    try std.testing.expectEqual(@as(u64, 24000), fixture.exact_checksums.PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM);
    try std.testing.expectEqual(@as(u64, 4000), fixture.exact_checksums.PHASE1_BENCH_RBTREE_CACHED_CHECKSUM);
}

test "phase1 bench source still emits every fixture marker" {
    try expectContains(bench_source, "PHASE1_BENCH=pass");

    for (iteration_roster) |marker| {
        try expectContains(fixture_bytes, marker);
        try expectContains(bench_source, marker);
    }

    for (checksum_roster) |marker| {
        try expectContains(fixture_bytes, marker);
        try expectContains(bench_source, marker);
    }
}
