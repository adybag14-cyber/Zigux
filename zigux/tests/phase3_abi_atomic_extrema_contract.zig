const std = @import("std");
const atomic = @import("atomic_helpers");

test "atomic fetch-min preserves signed floor and old-value reporting" {
    var value: i16 = 42;

    try std.testing.expectEqual(@as(i16, 42), try atomic.fetchMin(i16, &value, -7, .release));
    try std.testing.expectEqual(@as(i16, -7), value);

    try std.testing.expectEqual(@as(i16, -7), try atomic.fetchMin(i16, &value, 11, .acquire));
    try std.testing.expectEqual(@as(i16, -7), value);

    try std.testing.expectEqual(@as(i16, -7), try atomic.fetchMin(i16, &value, -19, .seq_cst));
    try std.testing.expectEqual(@as(i16, -19), value);
}

test "atomic fetch-max preserves signed ceiling and old-value reporting" {
    var value: i16 = -42;

    try std.testing.expectEqual(@as(i16, -42), try atomic.fetchMax(i16, &value, 7, .release));
    try std.testing.expectEqual(@as(i16, 7), value);

    try std.testing.expectEqual(@as(i16, 7), try atomic.fetchMax(i16, &value, -11, .acquire));
    try std.testing.expectEqual(@as(i16, 7), value);

    try std.testing.expectEqual(@as(i16, 7), try atomic.fetchMax(i16, &value, 19, .seq_cst));
    try std.testing.expectEqual(@as(i16, 19), value);
}

test "atomic extrema preserve unsigned boundary behavior" {
    var low: u8 = 200;
    try std.testing.expectEqual(@as(u8, 200), try atomic.fetchMin(u8, &low, 0, .monotonic));
    try std.testing.expectEqual(@as(u8, 0), low);
    try std.testing.expectEqual(@as(u8, 0), try atomic.fetchMin(u8, &low, 255, .acq_rel));
    try std.testing.expectEqual(@as(u8, 0), low);

    var high: u8 = 3;
    try std.testing.expectEqual(@as(u8, 3), try atomic.fetchMax(u8, &high, 255, .monotonic));
    try std.testing.expectEqual(@as(u8, 255), high);
    try std.testing.expectEqual(@as(u8, 255), try atomic.fetchMax(u8, &high, 0, .acq_rel));
    try std.testing.expectEqual(@as(u8, 255), high);
}

test "atomic extrema fail closed for unordered RMW without mutation" {
    var min_value: i32 = 5;
    try std.testing.expectError(
        error.InvalidRmwOrdering,
        atomic.fetchMin(i32, &min_value, -5, .unordered),
    );
    try std.testing.expectEqual(@as(i32, 5), min_value);

    var max_value: u32 = 9;
    try std.testing.expectError(
        error.InvalidRmwOrdering,
        atomic.fetchMax(u32, &max_value, 99, .unordered),
    );
    try std.testing.expectEqual(@as(u32, 9), max_value);
}
