const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "find_bit shared and andnot scans stay aligned across masked tail windows" {
    const boundary = bits_per_long - 1;
    const nbits = bits_per_long + 6;

    const shared_lhs = [_]Word{
        @as(Word, 1) << @intCast(boundary),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9),
    };
    const shared_rhs = [_]Word{
        @as(Word, 1) << @intCast(boundary),
        (@as(Word, 1) << 4) | (@as(Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findFirstAndBit(&shared_lhs, &shared_rhs, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextAndBit(&shared_lhs, &shared_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&shared_lhs, &shared_rhs, nbits, bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_first_and_bit(&shared_lhs, &shared_rhs, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.find_next_and_bit(&shared_lhs, &shared_rhs, nbits, boundary + 1));

    const andnot_lhs = [_]Word{
        @as(Word, 1) << @intCast(boundary),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9),
    };
    const andnot_rhs = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));
}

test "find_bit zero and last-bit scans clamp partial tails and ignore out-of-range storage" {
    const nbits = bits_per_long + 5;

    var zero_map = [_]Word{ ~@as(Word, 0), find_bit.lastWordMask(nbits) };
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findFirstZeroBit(&zero_map, nbits));

    zero_map[1] &= ~(@as(Word, 1) << 2);
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findFirstZeroBit(&zero_map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findNextZeroBit(&zero_map, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zero_map, nbits, bits_per_long + 3));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.find_first_zero_bit(&zero_map, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_zero_bit(&zero_map, nbits, bits_per_long + 3));

    var last_map = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findLastBit(&last_map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.find_last_bit(&last_map, nbits));

    last_map[1] &= ~(@as(Word, 1) << 3);
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findLastBit(&last_map, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_last_bit(&last_map, nbits));

    const empty = [_]Word{};
    try std.testing.expectEqual(@as(usize, 0), find_bit.findLastBit(&empty, 0));
}
