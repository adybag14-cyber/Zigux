const std = @import("std");

const fixture = @embedFile("fixtures/phase1_bench_expectations.json");

const ExpectedPair = struct {
    name: []const u8,
    value: u64,
};

const iteration_expectations = [_]ExpectedPair{
    .{ .name = "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS", .value = 20000 },
    .{ .name = "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS", .value = 20000 },
    .{ .name = "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS", .value = 20000 },
    .{ .name = "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS", .value = 20000 },
    .{ .name = "PHASE1_BENCH_STRING_ITERATIONS", .value = 40000 },
    .{ .name = "PHASE1_BENCH_HWEIGHT_ITERATIONS", .value = 100000 },
    .{ .name = "PHASE1_BENCH_LIST_SORT_ITERATIONS", .value = 1000 },
    .{ .name = "PHASE1_BENCH_RBTREE_ITERATIONS", .value = 4000 },
};

const checksum_expectations = [_]ExpectedPair{
    .{ .name = "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM", .value = 100000 },
    .{ .name = "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM", .value = 120000 },
    .{ .name = "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM", .value = 3780000 },
    .{ .name = "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM", .value = 4020000 },
    .{ .name = "PHASE1_BENCH_STRING_CHECKSUM", .value = 400000 },
    .{ .name = "PHASE1_BENCH_HWEIGHT_CHECKSUM", .value = 6800000 },
    .{ .name = "PHASE1_BENCH_LIST_SORT_CHECKSUM", .value = 10000 },
    .{ .name = "PHASE1_BENCH_RBTREE_CHECKSUM", .value = 24000 },
    .{ .name = "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM", .value = 24000 },
    .{ .name = "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM", .value = 8000 },
    .{ .name = "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM", .value = 24000 },
    .{ .name = "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM", .value = 4000 },
};

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, fixture, needle) != null);
}

fn expectPair(pair: ExpectedPair) !void {
    var expected: [128]u8 = undefined;
    const line = try std.fmt.bufPrint(&expected, "\"{s}\": {d}", .{ pair.name, pair.value });
    try expectContains(line);
}

test "phase1 bench expectation fixture keeps pass marker and closed rosters" {
    try expectContains("\"status\": \"pass\"");
    try expectContains("\"iterations\"");
    try expectContains("\"checksums\"");
    try expectContains("\"exact_checksums\"");

    for (iteration_expectations) |pair| {
        try expectContains(pair.name);
    }
    for (checksum_expectations) |pair| {
        try expectContains(pair.name);
    }
}

test "phase1 bench iteration constants stay aligned with the artifact packet" {
    for (iteration_expectations) |pair| {
        try expectPair(pair);
    }
}

test "phase1 bench exact checksum packet stays explicit" {
    for (checksum_expectations) |pair| {
        try expectPair(pair);
    }
}
