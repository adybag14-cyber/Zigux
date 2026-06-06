const std = @import("std");
const atomic = @import("atomic_helpers");

test "phase3 atomic RMW bitwise helpers return previous values" {
    var word: u16 = 0b1010_0101_0011_1100;

    try std.testing.expectEqual(@as(u16, 0b1010_0101_0011_1100), try atomic.fetchAnd(u16, &word, 0b1111_0000_1111_0000, .acquire));
    try std.testing.expectEqual(@as(u16, 0b1010_0000_0011_0000), word);

    try std.testing.expectEqual(@as(u16, 0b1010_0000_0011_0000), try atomic.fetchOr(u16, &word, 0b0000_1111_0000_0101, .release));
    try std.testing.expectEqual(@as(u16, 0b1010_1111_0011_0101), word);

    try std.testing.expectEqual(@as(u16, 0b1010_1111_0011_0101), try atomic.fetchXor(u16, &word, 0b0011_0011_1111_0000, .acq_rel));
    try std.testing.expectEqual(@as(u16, 0b1001_1100_1100_0101), word);

    try std.testing.expectEqual(@as(u16, 0b1001_1100_1100_0101), try atomic.fetchNand(u16, &word, 0b1111_0000_0000_1111, .seq_cst));
    try std.testing.expectEqual(@as(u16, 0b0110_1111_1111_1010), word);
}

test "phase3 atomic RMW min and max preserve signed ordering" {
    var signed: i16 = 14;

    try std.testing.expectEqual(@as(i16, 14), try atomic.fetchMin(i16, &signed, -3, .release));
    try std.testing.expectEqual(@as(i16, -3), signed);

    try std.testing.expectEqual(@as(i16, -3), try atomic.fetchMax(i16, &signed, 9, .acquire));
    try std.testing.expectEqual(@as(i16, 9), signed);

    try std.testing.expectEqual(@as(i16, 9), try atomic.fetchMin(i16, &signed, 12, .acq_rel));
    try std.testing.expectEqual(@as(i16, 9), signed);

    try std.testing.expectEqual(@as(i16, 9), try atomic.fetchMax(i16, &signed, 5, .seq_cst));
    try std.testing.expectEqual(@as(i16, 9), signed);
}

test "phase3 atomic RMW min and max preserve unsigned ordering" {
    var unsigned: u16 = 40;

    try std.testing.expectEqual(@as(u16, 40), try atomic.fetchMin(u16, &unsigned, 7, .monotonic));
    try std.testing.expectEqual(@as(u16, 7), unsigned);

    try std.testing.expectEqual(@as(u16, 7), try atomic.fetchMax(u16, &unsigned, 512, .release));
    try std.testing.expectEqual(@as(u16, 512), unsigned);

    try std.testing.expectEqual(@as(u16, 512), try atomic.fetchMin(u16, &unsigned, 1024, .acquire));
    try std.testing.expectEqual(@as(u16, 512), unsigned);

    try std.testing.expectEqual(@as(u16, 512), try atomic.fetchMax(u16, &unsigned, 128, .acq_rel));
    try std.testing.expectEqual(@as(u16, 512), unsigned);
}

test "phase3 atomic RMW helpers reject unordered without mutation" {
    var value: u32 = 0x00ff_00ff;

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.exchange(u32, &value, 0, .unordered));
    try std.testing.expectEqual(@as(u32, 0x00ff_00ff), value);

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.fetchAdd(u32, &value, 1, .unordered));
    try std.testing.expectEqual(@as(u32, 0x00ff_00ff), value);

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.fetchSub(u32, &value, 1, .unordered));
    try std.testing.expectEqual(@as(u32, 0x00ff_00ff), value);

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.fetchAnd(u32, &value, 0, .unordered));
    try std.testing.expectEqual(@as(u32, 0x00ff_00ff), value);

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.fetchOr(u32, &value, 0xffff_0000, .unordered));
    try std.testing.expectEqual(@as(u32, 0x00ff_00ff), value);

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.fetchXor(u32, &value, 0xffff_ffff, .unordered));
    try std.testing.expectEqual(@as(u32, 0x00ff_00ff), value);

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.fetchNand(u32, &value, 0, .unordered));
    try std.testing.expectEqual(@as(u32, 0x00ff_00ff), value);

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.fetchMin(u32, &value, 1, .unordered));
    try std.testing.expectEqual(@as(u32, 0x00ff_00ff), value);

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.fetchMax(u32, &value, 0xffff_ffff, .unordered));
    try std.testing.expectEqual(@as(u32, 0x00ff_00ff), value);
}
