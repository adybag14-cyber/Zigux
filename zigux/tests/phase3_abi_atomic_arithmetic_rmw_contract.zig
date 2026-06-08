const std = @import("std");
const atomic = @import("atomic_helpers");

test "atomic arithmetic RMW reports old values while accumulating" {
    var value: u16 = 12;

    try std.testing.expectEqual(@as(u16, 12), try atomic.fetchAdd(u16, &value, 5, .monotonic));
    try std.testing.expectEqual(@as(u16, 17), value);

    try std.testing.expectEqual(@as(u16, 17), try atomic.fetchAdd(u16, &value, 8, .acq_rel));
    try std.testing.expectEqual(@as(u16, 25), value);

    try std.testing.expectEqual(@as(u16, 25), try atomic.fetchSub(u16, &value, 6, .release));
    try std.testing.expectEqual(@as(u16, 19), value);

    try std.testing.expectEqual(@as(u16, 19), try atomic.fetchSub(u16, &value, 4, .seq_cst));
    try std.testing.expectEqual(@as(u16, 15), value);
}

test "atomic arithmetic RMW preserves unsigned wrap boundaries" {
    var add_value: u8 = 250;

    try std.testing.expectEqual(@as(u8, 250), try atomic.fetchAdd(u8, &add_value, 10, .release));
    try std.testing.expectEqual(@as(u8, 4), add_value);

    var sub_value: u8 = 3;

    try std.testing.expectEqual(@as(u8, 3), try atomic.fetchSub(u8, &sub_value, 7, .acquire));
    try std.testing.expectEqual(@as(u8, 252), sub_value);
}

test "atomic arithmetic RMW accepts the shared RMW ordering set" {
    var add_value: u32 = 0;
    var sub_value: u32 = 16;

    try std.testing.expectEqual(@as(u32, 0), try atomic.fetchAdd(u32, &add_value, 1, .monotonic));
    try std.testing.expectEqual(@as(u32, 1), try atomic.fetchAdd(u32, &add_value, 1, .acquire));
    try std.testing.expectEqual(@as(u32, 2), try atomic.fetchAdd(u32, &add_value, 1, .release));
    try std.testing.expectEqual(@as(u32, 3), try atomic.fetchAdd(u32, &add_value, 1, .acq_rel));
    try std.testing.expectEqual(@as(u32, 4), try atomic.fetchAdd(u32, &add_value, 1, .seq_cst));
    try std.testing.expectEqual(@as(u32, 5), add_value);

    try std.testing.expectEqual(@as(u32, 16), try atomic.fetchSub(u32, &sub_value, 1, .monotonic));
    try std.testing.expectEqual(@as(u32, 15), try atomic.fetchSub(u32, &sub_value, 1, .acquire));
    try std.testing.expectEqual(@as(u32, 14), try atomic.fetchSub(u32, &sub_value, 1, .release));
    try std.testing.expectEqual(@as(u32, 13), try atomic.fetchSub(u32, &sub_value, 1, .acq_rel));
    try std.testing.expectEqual(@as(u32, 12), try atomic.fetchSub(u32, &sub_value, 1, .seq_cst));
    try std.testing.expectEqual(@as(u32, 11), sub_value);
}

test "atomic arithmetic RMW rejects unordered without mutation" {
    var add_value: u16 = 7;
    var sub_value: u16 = 11;

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.fetchAdd(u16, &add_value, 5, .unordered));
    try std.testing.expectEqual(@as(u16, 7), add_value);

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.fetchSub(u16, &sub_value, 3, .unordered));
    try std.testing.expectEqual(@as(u16, 11), sub_value);
}
