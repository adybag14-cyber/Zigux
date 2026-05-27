const std = @import("std");
const find_bit = @import("../../tools/lib/find_bit.zig");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "inclusive boundary next scans keep the last in-range bit visible" {
    const boundary = bits_per_long - 1;
    const nbits = bits_per_long * 2;
    const set_map = [_]Word{ @as(Word, 1) << @intCast(boundary), 0 };
    const and_lhs = [_]Word{ @as(Word, 1) << @intCast(boundary), 0 };
    const and_rhs = [_]Word{ @as(Word, 1) << @intCast(boundary), 0 };
    const zero_map = [_]Word{ ~(@as(Word, 1) << @intCast(boundary)), ~@as(Word, 0) };

    try std.testing.expectEqual(@as(usize, 63), find_bit.findNextBit(&set_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, 63), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, 63), find_bit.findNextZeroBit(&zero_map, nbits, boundary));
}

test "tail-word next scans clamp out-of-range bits and keep the last live bit reachable" {
    const tail_nbits = bits_per_long + 5;
    const tail_boundary = tail_nbits - 1;
    const set_map = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 7) };
    const zero_map = [_]Word{ ~@as(Word, 0), find_bit.lastWordMask(tail_nbits) & ~(@as(Word, 1) << 4) };
    const and_lhs = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 7) };
    const and_rhs = and_lhs;
    var last_map = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 10) };

    try std.testing.expectEqual(@as(usize, 68), find_bit.findNextBit(&set_map, tail_nbits, tail_boundary));
    try std.testing.expectEqual(@as(usize, 68), find_bit.findNextAndBit(&and_lhs, &and_rhs, tail_nbits, tail_boundary));
    try std.testing.expectEqual(@as(usize, 68), find_bit.findNextZeroBit(&zero_map, tail_nbits, tail_boundary));
    try std.testing.expectEqual(@as(usize, 67), find_bit.findFirstBit(&last_map, tail_nbits));
    try std.testing.expectEqual(@as(usize, 69), find_bit.findNextBit(&last_map, tail_nbits, bits_per_long + 4));
    try std.testing.expectEqual(@as(usize, 67), find_bit.findLastBit(&last_map, tail_nbits));

    last_map[1] &= ~(@as(Word, 1) << 3);
    try std.testing.expectEqual(@as(usize, 69), find_bit.findLastBit(&last_map, tail_nbits));
}

test "past-end next scans return nbits without touching bitmap words" {
    const empty = [_]Word{};

    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextBit(&empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextBit(&empty, 7, 11));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextZeroBit(&empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextZeroBit(&empty, 7, 11));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextAndBit(&empty, &empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextAndBit(&empty, &empty, 7, 11));
}
