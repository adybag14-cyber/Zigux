const std = @import("std");

const atomic_helpers = @import("atomic_helpers");

test "phase3 atomic RMW wrappers return old values and publish updated storage" {
    var bits: u16 = 0x0104;

    try std.testing.expectEqual(@as(u16, 0x0104), try atomic_helpers.fetchAdd(u16, &bits, 0x0002, .monotonic));
    try std.testing.expectEqual(@as(u16, 0x0106), bits);

    try std.testing.expectEqual(@as(u16, 0x0106), try atomic_helpers.fetchSub(u16, &bits, 0x0004, .release));
    try std.testing.expectEqual(@as(u16, 0x0102), bits);

    try std.testing.expectEqual(@as(u16, 0x0102), try atomic_helpers.fetchOr(u16, &bits, 0x00F0, .acq_rel));
    try std.testing.expectEqual(@as(u16, 0x01F2), bits);

    try std.testing.expectEqual(@as(u16, 0x01F2), try atomic_helpers.fetchAnd(u16, &bits, 0x0F33, .acquire));
    try std.testing.expectEqual(@as(u16, 0x0132), bits);

    try std.testing.expectEqual(@as(u16, 0x0132), try atomic_helpers.fetchXor(u16, &bits, 0x00F0, .seq_cst));
    try std.testing.expectEqual(@as(u16, 0x01C2), bits);
}

test "phase3 atomic RMW wrappers keep nand and exchange behavior explicit" {
    var word: u8 = 0b1111_0000;

    try std.testing.expectEqual(@as(u8, 0b1111_0000), try atomic_helpers.fetchNand(u8, &word, 0b1100_1100, .seq_cst));
    try std.testing.expectEqual(@as(u8, 0b0011_1111), word);

    try std.testing.expectEqual(@as(u8, 0b0011_1111), try atomic_helpers.fetchNand(u8, &word, 0b0000_1111, .monotonic));
    try std.testing.expectEqual(@as(u8, 0b1111_0000), word);

    try std.testing.expectEqual(@as(u8, 0b1111_0000), try atomic_helpers.exchange(u8, &word, 0b0101_1010, .acq_rel));
    try std.testing.expectEqual(@as(u8, 0b0101_1010), word);
}

test "phase3 atomic RMW wrappers keep signed min max lanes explicit" {
    var signed_value: i16 = 14;

    try std.testing.expectEqual(@as(i16, 14), try atomic_helpers.fetchMin(i16, &signed_value, 9, .release));
    try std.testing.expectEqual(@as(i16, 9), signed_value);

    try std.testing.expectEqual(@as(i16, 9), try atomic_helpers.fetchMin(i16, &signed_value, 11, .acquire));
    try std.testing.expectEqual(@as(i16, 9), signed_value);

    try std.testing.expectEqual(@as(i16, 9), try atomic_helpers.fetchMax(i16, &signed_value, 17, .acq_rel));
    try std.testing.expectEqual(@as(i16, 17), signed_value);

    try std.testing.expectEqual(@as(i16, 17), try atomic_helpers.fetchMax(i16, &signed_value, -3, .seq_cst));
    try std.testing.expectEqual(@as(i16, 17), signed_value);
}

test "phase3 atomic RMW wrappers fail closed for unordered without touching storage" {
    var word: u16 = 0x00AA;

    try std.testing.expectError(error.InvalidRmwOrdering, atomic_helpers.exchange(u16, &word, 0x00BB, .unordered));
    try std.testing.expectEqual(@as(u16, 0x00AA), word);

    try std.testing.expectError(error.InvalidRmwOrdering, atomic_helpers.fetchAdd(u16, &word, 1, .unordered));
    try std.testing.expectError(error.InvalidRmwOrdering, atomic_helpers.fetchSub(u16, &word, 1, .unordered));
    try std.testing.expectError(error.InvalidRmwOrdering, atomic_helpers.fetchNand(u16, &word, 0x00FF, .unordered));
    try std.testing.expectError(error.InvalidRmwOrdering, atomic_helpers.fetchOr(u16, &word, 0x0001, .unordered));
    try std.testing.expectError(error.InvalidRmwOrdering, atomic_helpers.fetchAnd(u16, &word, 0x0001, .unordered));
    try std.testing.expectError(error.InvalidRmwOrdering, atomic_helpers.fetchXor(u16, &word, 0x0001, .unordered));
    try std.testing.expectError(error.InvalidRmwOrdering, atomic_helpers.fetchMin(u16, &word, 1, .unordered));
    try std.testing.expectError(error.InvalidRmwOrdering, atomic_helpers.fetchMax(u16, &word, 1, .unordered));

    try std.testing.expectEqual(@as(u16, 0x00AA), word);
}
