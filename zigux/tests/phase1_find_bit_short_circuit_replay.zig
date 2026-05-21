const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "zero-sized scans ignore populated storage across primary and alias entrypoints" {
    const populated = [_]Word{
        ~@as(Word, 0),
        (@as(Word, 1) << 3) | (@as(Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstBit(&populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(&populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstAndBit(&populated, &populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstAndNotBit(&populated, &populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findLastBit(&populated, 0));

    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_bit(&populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_zero_bit(&populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_and_bit(&populated, &populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_andnot_bit(&populated, &populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_last_bit(&populated, 0));

    try std.testing.expectEqual(@as(usize, 0), find_bit._find_first_bit(&populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit._find_first_zero_bit(&populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit._find_first_and_bit(&populated, &populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit._find_first_andnot_bit(&populated, &populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit._find_last_bit(&populated, 0));
}

test "past-end next scans clamp to nbits on empty and populated storage" {
    const nbits = bits_per_long + 5;
    const empty = [_]Word{};
    const populated = [_]Word{
        (@as(Word, 1) << 7),
        (@as(Word, 1) << 3) | (@as(Word, 1) << 11),
    };
    const zero_map = [_]Word{
        ~(@as(Word, 1) << 4),
        find_bit.lastWordMask(nbits),
    };
    const and_lhs = [_]Word{
        (@as(Word, 1) << 7),
        (@as(Word, 1) << 3) | (@as(Word, 1) << 11),
    };
    const and_rhs = [_]Word{
        (@as(Word, 1) << 7),
        @as(Word, 1) << 3,
    };
    const andnot_rhs = [_]Word{
        (@as(Word, 1) << 7),
        (@as(Word, 1) << 3),
    };

    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&empty, nbits, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&empty, nbits, nbits + 4));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&empty, &empty, nbits, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&empty, &empty, nbits, nbits + 4));

    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&populated, nbits, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zero_map, nbits, nbits + 4));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&and_lhs, &andnot_rhs, nbits, nbits + 4));

    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_bit(&populated, nbits, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_zero_bit(&zero_map, nbits, nbits + 4));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_and_bit(&and_lhs, &and_rhs, nbits, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_andnot_bit(&and_lhs, &andnot_rhs, nbits, nbits + 4));

    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_bit(&populated, nbits, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_zero_bit(&zero_map, nbits, nbits + 4));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_and_bit(&and_lhs, &and_rhs, nbits, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_andnot_bit(&and_lhs, &andnot_rhs, nbits, nbits + 4));
}

test "tail masks hide out-of-range storage while keeping first and last scans aligned" {
    const nbits = bits_per_long + 5;
    var set_map = [_]Word{ 0, @as(Word, 1) << 9 };
    var and_lhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const and_rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const andnot_rhs = [_]Word{ 0, @as(Word, 1) << 9 };
    var zero_map = [_]Word{ ~@as(Word, 0), find_bit.lastWordMask(nbits) };

    try std.testing.expectEqual(@as(usize, nbits), find_bit.findFirstBit(&set_map, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findLastBit(&set_map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findFirstAndBit(&and_lhs, &and_rhs, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findFirstAndNotBit(&and_lhs, &andnot_rhs, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findFirstZeroBit(&zero_map, nbits));

    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_first_bit(&set_map, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_last_bit(&set_map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.find_first_and_bit(&and_lhs, &and_rhs, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.find_first_andnot_bit(&and_lhs, &andnot_rhs, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_first_zero_bit(&zero_map, nbits));

    set_map[1] |= @as(Word, 1) << 3;
    zero_map[1] &= ~(@as(Word, 1) << 2);
    and_lhs[1] &= ~(@as(Word, 1) << 3);

    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findFirstBit(&set_map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findLastBit(&set_map, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findFirstAndBit(&and_lhs, &and_rhs, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findFirstAndNotBit(&and_lhs, &andnot_rhs, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findFirstZeroBit(&zero_map, nbits));
}