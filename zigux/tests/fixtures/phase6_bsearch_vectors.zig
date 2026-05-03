const std = @import("std");

pub const PerfCase = struct {
    label: []const u8,
    len: usize,
    reps: usize,
};

pub const query_count = 32;

pub const perf_cases = [_]PerfCase{
    .{ .label = "256", .len = 256, .reps = 2_000 },
    .{ .label = "4096", .len = 4096, .reps = 500 },
    .{ .label = "65536", .len = 65536, .reps = 64 },
};

pub fn seedDeterministicQueries(
    len: usize,
    values: []const u32,
    queries: *[query_count]u32,
    expected_hits: *[query_count]bool,
) void {
    const quarter = len / 4;
    const middle = len / 2;
    const last = len - 1;
    const deterministic_pairs = [_]struct {
        query: u32,
        hit: bool,
    }{
        .{ .query = values[0], .hit = true },
        .{ .query = values[0] + 1, .hit = false },
        .{ .query = values[quarter], .hit = true },
        .{ .query = values[quarter] + 1, .hit = false },
        .{ .query = values[middle], .hit = true },
        .{ .query = values[middle] + 1, .hit = false },
        .{ .query = values[last], .hit = true },
        .{ .query = values[last] + 1, .hit = false },
    };

    for (deterministic_pairs, 0..) |pair, idx| {
        queries[idx] = pair.query;
        expected_hits[idx] = pair.hit;
    }
}

test "phase 6 bsearch perf fixture preserves the documented case matrix" {
    try std.testing.expectEqual(@as(usize, 32), query_count);
    try std.testing.expectEqual(@as(usize, 3), perf_cases.len);

    const expected = [_]PerfCase{
        .{ .label = "256", .len = 256, .reps = 2_000 },
        .{ .label = "4096", .len = 4096, .reps = 500 },
        .{ .label = "65536", .len = 65536, .reps = 64 },
    };

    for (perf_cases, expected, 0..) |actual, wanted, idx| {
        try std.testing.expectEqualStrings(wanted.label, actual.label);
        try std.testing.expectEqual(wanted.len, actual.len);
        try std.testing.expectEqual(wanted.reps, actual.reps);
        if (idx > 0) {
            try std.testing.expect(perf_cases[idx - 1].len < actual.len);
            try std.testing.expect(perf_cases[idx - 1].reps > actual.reps);
        }
    }
}

test "phase 6 bsearch perf fixture seeds fixed edge quarter midpoint and tail probes first" {
    const values = [_]u32{ 0, 2, 4, 6, 8, 10, 12, 14 };
    var queries: [query_count]u32 = undefined;
    var expected_hits: [query_count]bool = undefined;

    seedDeterministicQueries(values.len, values[0..], &queries, &expected_hits);

    const expected_queries = [_]u32{ 0, 1, 4, 5, 8, 9, 14, 15 };
    const expected_probe_hits = [_]bool{ true, false, true, false, true, false, true, false };

    for (expected_queries, expected_probe_hits, 0..) |expected_query, expected_hit, idx| {
        try std.testing.expectEqual(expected_query, queries[idx]);
        try std.testing.expectEqual(expected_hit, expected_hits[idx]);
    }
}
