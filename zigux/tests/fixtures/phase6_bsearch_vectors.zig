const std = @import("std");

pub const representative_ascending_values = [_]u32{ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 };
pub const representative_descending_values = [_]u32{ 45, 42, 39, 36, 33, 30, 27, 24, 21, 18, 15, 12, 9, 6, 3 };
pub const representative_duplicate_values = [_]u32{ 3, 6, 9, 12, 21, 21, 21, 24, 27, 30, 33, 36, 39, 42, 45 };

pub const representative_hit_queries = [_]u32{ 3, 21, 24, 39, 45 };
pub const representative_miss_queries = [_]u32{ 1, 10, 26, 44, 50 };

pub const sorted_symbols = [_][]const u8{
    "do_exit",
    "kfree",
    "kmalloc",
    "schedule",
};

pub const RawRecord = extern struct {
    key: u32,
    value: u32,
};

pub const packed_record_values = [_]RawRecord{
    .{ .key = 3, .value = 0x3000 },
    .{ .key = 8, .value = 0x8000 },
    .{ .key = 13, .value = 0xd000 },
    .{ .key = 21, .value = 0x15000 },
    .{ .key = 34, .value = 0x22000 },
    .{ .key = 55, .value = 0x37000 },
    .{ .key = 89, .value = 0x59000 },
};

pub const dynamic_case_lengths = [_]usize{
    0,  1,  2,  3,  4,  5,  6,  7,  8,  9,  10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
    22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
};

pub const PerfCase = struct {
    label: []const u8,
    len: usize,
    reps: usize,
};

pub const perf_cases = [_]PerfCase{
    .{ .label = "len15", .len = representative_ascending_values.len, .reps = 4_000 },
    .{ .label = "len64", .len = 64, .reps = 2_000 },
    .{ .label = "len1024", .len = 1_024, .reps = 250 },
};

pub const query_count: usize = 16;

pub fn typedQuerySeed(index: usize) u32 {
    return representative_hit_queries[index % representative_hit_queries.len];
}

pub fn rawQuerySeed(index: usize) u32 {
    return representative_miss_queries[index % representative_miss_queries.len];
}

pub fn seedDeterministicQueries(len: usize, values: []const u32, queries: []u32, expected_hits: []bool) void {
    std.debug.assert(len != 0);
    std.debug.assert(values.len == len);
    std.debug.assert(queries.len == expected_hits.len);
    std.debug.assert(queries.len >= 8);

    @memset(queries, 0);
    @memset(expected_hits, false);

    const seed_indices = [_]usize{ 0, len / 4, len / 2, len - 1 };
    for (seed_indices, 0..) |index, slot| {
        queries[slot] = values[index];
        expected_hits[slot] = true;
    }

    for (seed_indices, 0..) |index, slot| {
        queries[4 + slot] = values[index] + 1;
        expected_hits[4 + slot] = false;
    }
}

test "phase 6 bsearch vectors stay deterministic, sorted, and duplicate-aware" {
    try std.testing.expectEqual(@as(usize, 15), representative_ascending_values.len);
    try std.testing.expectEqual(@as(usize, 15), representative_descending_values.len);
    try std.testing.expectEqual(@as(usize, 15), representative_duplicate_values.len);
    try std.testing.expectEqual(@as(usize, 33), dynamic_case_lengths.len);

    for (representative_ascending_values, 0..) |value, index| {
        if (index > 0) {
            try std.testing.expect(representative_ascending_values[index - 1] < value);
        }
        try std.testing.expectEqual(value, representative_descending_values[representative_descending_values.len - 1 - index]);
    }

    try std.testing.expectEqual(@as(u32, 21), representative_duplicate_values[4]);
    try std.testing.expectEqual(@as(u32, 21), representative_duplicate_values[5]);
    try std.testing.expectEqual(@as(u32, 21), representative_duplicate_values[6]);

    for (dynamic_case_lengths, 0..) |length, index| {
        try std.testing.expectEqual(index, length);
    }
}

test "phase 6 bsearch perf seeds stay deterministic" {
    try std.testing.expectEqual(@as(usize, 3), perf_cases.len);
    try std.testing.expectEqual(@as(usize, 16), query_count);

    var values: [representative_ascending_values.len]u32 = undefined;
    for (&values, 0..) |*slot, index| {
        slot.* = @as(u32, @intCast(index * 2));
    }

    var queries: [query_count]u32 = undefined;
    var expected_hits: [query_count]bool = undefined;
    seedDeterministicQueries(values.len, values[0..], &queries, &expected_hits);

    try std.testing.expect(expected_hits[0]);
    try std.testing.expect(expected_hits[1]);
    try std.testing.expect(expected_hits[2]);
    try std.testing.expect(expected_hits[3]);
    try std.testing.expect(!expected_hits[4]);
    try std.testing.expect(!expected_hits[5]);
    try std.testing.expect(!expected_hits[6]);
    try std.testing.expect(!expected_hits[7]);

    try std.testing.expectEqual(values[0], queries[0]);
    try std.testing.expectEqual(values[values.len / 4], queries[1]);
    try std.testing.expectEqual(values[values.len / 2], queries[2]);
    try std.testing.expectEqual(values[values.len - 1], queries[3]);
    try std.testing.expectEqual(values[0] + 1, queries[4]);
    try std.testing.expectEqual(values[values.len / 4] + 1, queries[5]);
    try std.testing.expectEqual(values[values.len / 2] + 1, queries[6]);
    try std.testing.expectEqual(values[values.len - 1] + 1, queries[7]);
}
