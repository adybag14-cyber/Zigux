const std = @import("std");

const expectations_json = @embedFile("fixtures/phase1_bench_expectations.json");

const expected_iterations = [_]Expectation{
    .{ .name = "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS", .value = 20000 },
    .{ .name = "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS", .value = 20000 },
    .{ .name = "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS", .value = 20000 },
    .{ .name = "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS", .value = 20000 },
    .{ .name = "PHASE1_BENCH_STRING_ITERATIONS", .value = 40000 },
    .{ .name = "PHASE1_BENCH_HWEIGHT_ITERATIONS", .value = 100000 },
    .{ .name = "PHASE1_BENCH_LIST_SORT_ITERATIONS", .value = 1000 },
    .{ .name = "PHASE1_BENCH_RBTREE_ITERATIONS", .value = 4000 },
};

const expected_exact_checksums = [_]Expectation{
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

const Expectation = struct {
    name: []const u8,
    value: u64,
};

test "phase1 bench expectations keep the pass status" {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(expectations_json, "\"status\": \"pass\""));
}

test "phase1 bench expectations pin iteration budgets" {
    try expectNamedValuesInOrder("\"iterations\"", &expected_iterations);
}

test "phase1 bench expectations pin exact checksum values" {
    try expectNamedValuesInOrder("\"exact_checksums\"", &expected_exact_checksums);
}

test "phase1 bench expectations keep checksum roster aligned with exact checksum roster" {
    const checksums_start = requiredIndex(expectations_json, "\"checksums\": [");
    const exact_start = requiredIndex(expectations_json, "\"exact_checksums\": {");
    try std.testing.expect(checksums_start < exact_start);

    for (expected_exact_checksums) |expected| {
        try std.testing.expectEqual(@as(usize, 2), countOccurrences(expectations_json, expected.name));
    }
}

fn expectNamedValuesInOrder(section_name: []const u8, expectations: []const Expectation) !void {
    var cursor = requiredIndex(expectations_json, section_name);
    for (expectations) |expected| {
        const marker = try std.fmt.allocPrint(std.testing.allocator, "\"{s}\": {d}", .{ expected.name, expected.value });
        defer std.testing.allocator.free(marker);

        const relative = std.mem.indexOf(u8, expectations_json[cursor..], marker) orelse return error.MissingExpectationMarker;
        cursor += relative + marker.len;
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(expectations_json, marker));
    }
}

fn requiredIndex(haystack: []const u8, needle: []const u8) usize {
    return std.mem.indexOf(u8, haystack, needle) orelse @panic("missing required marker");
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |relative| {
        count += 1;
        cursor += relative + needle.len;
    }
    return count;
}
