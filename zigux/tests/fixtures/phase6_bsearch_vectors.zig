const std = @import("std");

pub const PerfCase = struct {
    label: []const u8,
    len: usize,
    reps: usize,
};

pub const query_count = 32;
pub const deterministic_probe_count = 8;
pub const seeded_probe_count = query_count - deterministic_probe_count;
pub const perf_prng_seed: u64 = 0x5a17_2026_0700_0007;

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

pub fn seedPerfQueries(
    len: usize,
    values: []const u32,
    queries: *[query_count]u32,
    expected_hits: *[query_count]bool,
) void {
    seedDeterministicQueries(len, values, queries, expected_hits);

    var prng = std.Random.DefaultPrng.init(perf_prng_seed);
    const random = prng.random();

    for (queries[deterministic_probe_count..], expected_hits[deterministic_probe_count..], deterministic_probe_count..) |*query, *hit, idx| {
        const value_index = random.uintLessThan(usize, len);
        const base_value = values[value_index];
        if ((idx & 1) == 0) {
            query.* = base_value;
            hit.* = true;
        } else {
            query.* = base_value + 1;
            hit.* = false;
        }
    }
}

test "phase 6 bsearch perf fixture preserves the documented case matrix" {
    try std.testing.expectEqual(@as(usize, 32), query_count);
    try std.testing.expectEqual(@as(usize, 8), deterministic_probe_count);
    try std.testing.expectEqual(@as(usize, 24), seeded_probe_count);
    try std.testing.expectEqual(@as(u64, 0x5a17_2026_0700_0007), perf_prng_seed);
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

test "phase 6 bsearch perf fixture owns the seeded interior replay and keeps it deterministic" {
    const values = [_]u32{ 0, 2, 4, 6, 8, 10, 12, 14 };
    var queries_a: [query_count]u32 = undefined;
    var expected_hits_a: [query_count]bool = undefined;
    var queries_b: [query_count]u32 = undefined;
    var expected_hits_b: [query_count]bool = undefined;

    seedPerfQueries(values.len, values[0..], &queries_a, &expected_hits_a);
    seedPerfQueries(values.len, values[0..], &queries_b, &expected_hits_b);

    try std.testing.expectEqualSlices(u32, queries_a[0..], queries_b[0..]);
    try std.testing.expectEqualSlices(bool, expected_hits_a[0..], expected_hits_b[0..]);

    for (queries_a[deterministic_probe_count..], expected_hits_a[deterministic_probe_count..], deterministic_probe_count..) |query, hit, idx| {
        if ((idx & 1) == 0) {
            try std.testing.expect(hit);
            try std.testing.expect((query & 1) == 0);
        } else {
            try std.testing.expect(!hit);
            try std.testing.expect((query & 1) == 1);
        }
    }
}
