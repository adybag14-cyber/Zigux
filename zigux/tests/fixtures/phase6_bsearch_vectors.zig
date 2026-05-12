const std = @import("std");

pub const representative_ascending_values = [_]u32{ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 };
pub const representative_descending_values = [_]u32{ 45, 42, 39, 36, 33, 30, 27, 24, 21, 18, 15, 12, 9, 6, 3 };

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
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    31, 32,
};

pub fn typedQuerySeed(index: usize) u32 {
    return representative_hit_queries[index % representative_hit_queries.len];
}

pub fn rawQuerySeed(index: usize) u32 {
    return representative_miss_queries[index % representative_miss_queries.len];
}

test "phase 6 bsearch vectors stay deterministic and sorted" {
    try std.testing.expectEqual(@as(usize, 15), representative_ascending_values.len);
    try std.testing.expectEqual(@as(usize, 15), representative_descending_values.len);
    try std.testing.expectEqual(@as(usize, 33), dynamic_case_lengths.len);

    for (representative_ascending_values, 0..) |value, index| {
        if (index > 0) {
            try std.testing.expect(representative_ascending_values[index - 1] < value);
        }
        try std.testing.expectEqual(value, representative_descending_values[representative_descending_values.len - 1 - index]);
    }

    for (dynamic_case_lengths, 0..) |length, index| {
        try std.testing.expectEqual(index, length);
    }
}
