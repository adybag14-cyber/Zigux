const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

fn bit(idx: usize) Word {
    return @as(Word, 1) << @intCast(idx);
}

test "weighted xor counts only in-range tail bits" {
    const nbits = bits_per_long + 5;
    const tail_mask = bitmap.lastWordMask(nbits);
    const tail_junk = ~tail_mask;
    const lhs = [_]Word{
        bit(1) | bit(3),
        bit(1) | tail_junk,
    };
    const rhs = [_]Word{
        bit(2) | bit(3),
        bit(3) | bit(9),
    };
    var dst = [_]Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 4), bitmap.weightedXor(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&dst, nbits));
    try std.testing.expectEqual(bit(1) | bit(2), dst[0]);
    try std.testing.expectEqual(bit(1) | bit(3), dst[1] & tail_mask);
    try std.testing.expect((dst[1] & tail_junk) != 0);
}

test "and-not window drops masked partner bits at the valid tail" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{
        bit(bits_per_long - 2),
        bit(2) | bit(4) | bit(8),
    };
    const rhs = [_]Word{
        0,
        bit(2) | bit(8),
    };
    var dst = [_]Word{ 0, 0 };

    try std.testing.expect(bitmap.andNotBits(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&dst, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long - 2), find_bit.findFirstBit(&dst, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findLastBit(&dst, nbits));
    try std.testing.expectEqual(@as(Word, 0), dst[1] & ~bitmap.lastWordMask(nbits));
}

test "range mutation crossing a word boundary preserves surviving bits" {
    const nbits = bits_per_long + 6;
    var map = [_]Word{ 0, 0 };

    bitmap.setRange(&map, bits_per_long - 2, 5);
    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long - 2), find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findLastBit(&map, nbits));

    bitmap.clearRange(&map, bits_per_long - 1, 3);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long - 2), find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findNextBit(&map, nbits, bits_per_long - 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&map, nbits, bits_per_long + 3));
}
