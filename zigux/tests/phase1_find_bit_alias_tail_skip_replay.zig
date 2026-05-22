const std = @import("std");
const find_bit = @import("find_bit");

test "phase1 find_bit alias tail skip replay keeps public next scans on the in-range tail window" {
    const nbits = find_bit.bits_per_long + 6;
    const set_map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };
    const and_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const and_rhs = and_lhs;
    const andnot_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const andnot_rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 1 };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextBit(&set_map, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextBit(&set_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&set_map, nbits, find_bit.bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 5));
}

test "phase1 find_bit alias tail skip replay keeps Linux-style aliases aligned" {
    const nbits = find_bit.bits_per_long + 6;
    const set_map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };
    const and_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const and_rhs = and_lhs;
    const andnot_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const andnot_rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 1 };

    try std.testing.expectEqual(find_bit.findNextBit(&set_map, nbits, find_bit.bits_per_long + 2), find_bit.find_next_bit(&set_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 2), find_bit.find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long + 2), find_bit.find_next_and_bit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 2), find_bit.find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(find_bit.findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits), find_bit.find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits));
}

test "phase1 find_bit alias tail skip replay keeps underscore aliases and andnot entrypoints aligned" {
    const nbits = find_bit.bits_per_long + 6;
    const set_map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };
    const and_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const and_rhs = and_lhs;
    const andnot_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const andnot_rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 1 };

    try std.testing.expectEqual(find_bit.findNextBit(&set_map, nbits, find_bit.bits_per_long + 2), find_bit._find_next_bit(&set_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 2), find_bit._find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long + 2), find_bit._find_next_and_bit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 2), find_bit._find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(find_bit.findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits), find_bit._find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits));
}
