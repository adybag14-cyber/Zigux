const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "zero scans stop at the declared final-word tail" {
    const nbits = bits_per_long + 5;
    const full_declared = [_]Word{ ~@as(Word, 0), find_bit.lastWordMask(nbits) };

    try std.testing.expectEqual(@as(usize, nbits), find_bit.findFirstZeroBit(&full_declared, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&full_declared, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_zero_bit(&full_declared, nbits, bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_zero_bit(&full_declared, nbits, bits_per_long + 9));

    const gap_at_tail = [_]Word{
        ~@as(Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(Word, 1) << 3),
    };
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findFirstZeroBit(&gap_at_tail, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findNextZeroBit(&gap_at_tail, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&gap_at_tail, nbits, bits_per_long + 4));
}

test "next and last set scans ignore tail noise past nbits" {
    const nbits = bits_per_long + 5;
    const tail_noise = [_]Word{
        0,
        (@as(Word, 1) << 2) | (@as(Word, 1) << 7),
    };

    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findNextBit(&tail_noise, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.find_next_bit(&tail_noise, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&tail_noise, nbits, bits_per_long + 3));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findLastBit(&tail_noise, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.find_last_bit(&tail_noise, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit._find_last_bit(&tail_noise, nbits));
}

test "andnot scans mask the final word before applying start windows" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 8),
    };
    const rhs = [_]Word{
        0,
        (@as(Word, 1) << 1),
    };

    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_andnot_bit(&lhs, &rhs, nbits, bits_per_long + 8));
}
