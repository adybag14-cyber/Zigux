const std = @import("std");
const find_bit = @import("find_bit");

test "phase1 find_bit tail-word next set and andnot scans skip earlier matches before clamp" {
    const nbits = find_bit.bits_per_long + 6;
    const tail_map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const tail_andnot_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const tail_andnot_rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 1 };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextBit(&tail_map, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextBit(&tail_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&tail_map, nbits, find_bit.bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, find_bit.bits_per_long + 5));
}

test "phase1 find_bit tail-word next zero and shared scans skip earlier matches before clamp" {
    const nbits = find_bit.bits_per_long + 6;
    const tail_zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };
    const tail_and_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const tail_and_rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextZeroBit(&tail_zero_map, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextZeroBit(&tail_zero_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&tail_zero_map, nbits, find_bit.bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, find_bit.bits_per_long + 5));
}

test "phase1 find_bit tail-word skip aliases mirror the primary helpers" {
    const nbits = find_bit.bits_per_long + 6;
    const tail_map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const tail_zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };
    const tail_and_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const tail_and_rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const tail_andnot_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const tail_andnot_rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 1 };

    try std.testing.expectEqual(find_bit.findNextBit(&tail_map, nbits, find_bit.bits_per_long + 2), find_bit.find_next_bit(&tail_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(find_bit.findNextBit(&tail_map, nbits, find_bit.bits_per_long + 2), find_bit._find_next_bit(&tail_map, nbits, find_bit.bits_per_long + 2));

    try std.testing.expectEqual(find_bit.findNextZeroBit(&tail_zero_map, nbits, find_bit.bits_per_long + 2), find_bit.find_next_zero_bit(&tail_zero_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(find_bit.findNextZeroBit(&tail_zero_map, nbits, find_bit.bits_per_long + 2), find_bit._find_next_zero_bit(&tail_zero_map, nbits, find_bit.bits_per_long + 2));

    try std.testing.expectEqual(find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, find_bit.bits_per_long + 2), find_bit.find_next_and_bit(&tail_and_lhs, &tail_and_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, find_bit.bits_per_long + 2), find_bit._find_next_and_bit(&tail_and_lhs, &tail_and_rhs, nbits, find_bit.bits_per_long + 2));

    try std.testing.expectEqual(find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, find_bit.bits_per_long + 2), find_bit.find_next_andnot_bit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, find_bit.bits_per_long + 2), find_bit._find_next_andnot_bit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, find_bit.bits_per_long + 2));
}
