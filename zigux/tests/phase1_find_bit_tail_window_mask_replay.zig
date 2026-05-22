const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "phase 1 find_bit tail windows keep inclusive boundaries and clamp past nbits" {
    const nbits = bits_per_long + 6;
    const tail_zero_map = [_]Word{
        ~@as(Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(Word, 1) << 1) | (@as(Word, 1) << 4)),
    };
    const tail_and_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const tail_and_rhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const tail_andnot_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const tail_andnot_rhs = [_]Word{ 0, @as(Word, 1) << 1 };
    const inclusive_set = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };

    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextBit(&inclusive_set, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextBit(&inclusive_set, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&inclusive_set, nbits, bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextZeroBit(&tail_zero_map, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextZeroBit(&tail_zero_map, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&tail_zero_map, nbits, bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 5));
}

test "phase 1 find_bit single-word tail windows keep the last in-range matches reachable" {
    const nbits = 11;
    const boundary = nbits - 1;
    const set_map = [_]Word{(@as(Word, 1) << @intCast(boundary)) | (@as(Word, 1) << 13)};
    const and_lhs = [_]Word{(@as(Word, 1) << @intCast(boundary)) | (@as(Word, 1) << 13)};
    const and_rhs = [_]Word{(@as(Word, 1) << @intCast(boundary)) | (@as(Word, 1) << 13)};
    const andnot_lhs = [_]Word{(@as(Word, 1) << 2) | (@as(Word, 1) << @intCast(boundary)) | (@as(Word, 1) << 13)};
    const andnot_rhs = [_]Word{(@as(Word, 1) << 2) | (@as(Word, 1) << 13)};
    const zero_map = [_]Word{find_bit.lastWordMask(nbits) & ~(@as(Word, 1) << @intCast(boundary))};

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextBit(&set_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&set_map, nbits, boundary + 1));

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary + 1));

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextZeroBit(&zero_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zero_map, nbits, boundary + 1));
}

test "phase 1 find_bit word-boundary scans restart cleanly on the next word" {
    const nbits = bits_per_long * 2;
    const boundary = bits_per_long;
    const set_map = [_]Word{
        @as(Word, 1) << @intCast(bits_per_long - 1),
        (@as(Word, 1) << 0) | (@as(Word, 1) << 5),
    };
    const zero_map = [_]Word{
        0,
        ~((@as(Word, 1) << 0) | (@as(Word, 1) << 5)),
    };
    const and_lhs = [_]Word{
        @as(Word, 1) << @intCast(bits_per_long - 1),
        (@as(Word, 1) << 0) | (@as(Word, 1) << 5),
    };
    const and_rhs = and_lhs;
    const andnot_lhs = [_]Word{
        @as(Word, 1) << @intCast(bits_per_long - 1),
        (@as(Word, 1) << 0) | (@as(Word, 1) << 5),
    };
    const andnot_rhs = [_]Word{
        @as(Word, 1) << @intCast(bits_per_long - 1),
        0,
    };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextBit(&set_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 5), find_bit.findNextBit(&set_map, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_next_bit(&set_map, nbits, boundary));

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextZeroBit(&zero_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 5), find_bit.findNextZeroBit(&zero_map, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_next_zero_bit(&zero_map, nbits, boundary));

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 5), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_next_and_bit(&and_lhs, &and_rhs, nbits, boundary));

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 5), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, boundary));
}
