const std = @import("std");
const find_bit = @import("find_bit");

fn bitMask(bit: usize) find_bit.Word {
    return @as(find_bit.Word, 1) << @intCast(bit % find_bit.bits_per_long);
}

test "phase1 find_bit or scan stays clamped to the declared tail window" {
    const word_bits = find_bit.bits_per_long;
    const nbits = word_bits + 5;

    var lhs = [_]find_bit.Word{
        bitMask(2),
        bitMask(word_bits + 1),
    };
    var rhs = [_]find_bit.Word{
        bitMask(word_bits - 1),
        bitMask(word_bits + 6),
    };

    try std.testing.expectEqual(@as(usize, 2), find_bit.findNextOrBit(&lhs, &rhs, nbits, 0));
    try std.testing.expectEqual(@as(usize, word_bits - 1), find_bit.findNextOrBit(&lhs, &rhs, nbits, 3));
    try std.testing.expectEqual(@as(usize, word_bits + 1), find_bit.findNextOrBit(&lhs, &rhs, nbits, word_bits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextOrBit(&lhs, &rhs, nbits, word_bits + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextOrBit(&lhs, &rhs, nbits, nbits));
}

test "phase1 find_bit or aliases mirror the primary helper in single-word windows" {
    const nbits = 9;
    var lhs = [_]find_bit.Word{bitMask(5)};
    var rhs = [_]find_bit.Word{bitMask(8) | bitMask(12)};

    const primary = find_bit.findNextOrBit(&lhs, &rhs, nbits, 6);
    try std.testing.expectEqual(@as(usize, 8), primary);
    try std.testing.expectEqual(primary, find_bit.find_next_or_bit(&lhs, &rhs, nbits, 6));
    try std.testing.expectEqual(primary, find_bit._find_next_or_bit(&lhs, &rhs, nbits, 6));

    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextOrBit(&lhs, &rhs, nbits, 9));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_or_bit(&lhs, &rhs, nbits, 9));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_or_bit(&lhs, &rhs, nbits, 9));
}
