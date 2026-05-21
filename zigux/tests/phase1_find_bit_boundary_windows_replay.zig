const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "head-word and exact-word boundary next scans keep inclusive starts reachable" {
    const boundary = bits_per_long - 1;
    const nbits = bits_per_long * 2;

    const set_map = [_]Word{
        (@as(Word, 1) << @intCast(boundary)) | (@as(Word, 1) << 5),
        (@as(Word, 1) << 0) | (@as(Word, 1) << 5),
    };
    const and_lhs = [_]Word{
        (@as(Word, 1) << @intCast(boundary)) | (@as(Word, 1) << 5),
        (@as(Word, 1) << @intCast(bits_per_long))
    };
    const and_rhs = [_]Word{
        (@as(Word, 1) << @intCast(boundary)) | (@as(Word, 1) << 5),
        (@as(Word, 1) << @intCast(bits_per_long))
    };
    const andnot_lhs = [_]Word{
        (@as(Word, 1) << 5) | (@as(Word, 1) << @intCast(boundary)),
        (@as(Word, 1) << 0) | (@as(Word, 1) << 5),
    };
    const andnot_rhs = [_]Word{
        @as(Word, 1) << 5,
        0,
    };
    const zero_map = [_]Word{
        ~(@as(Word, 1) << @intCast(boundary)),
        ~((@as(Word, 1) << 0) | (@as(Word, 1) << 5)),
    };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextBit(&set_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextBit(&set_map, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextZeroBit(&zero_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextZeroBit(&zero_map, nbits, bits_per_long));
}

test "tail-word boundary windows clamp after the last in-range bit" {
    const tail_bits: usize = 5;
    const boundary = bits_per_long + tail_bits - 1;
    const nbits = boundary + 1;

    const set_map = [_]Word{
        0,
        (@as(Word, 1) << @intCast(tail_bits - 1)) | (@as(Word, 1) << @intCast(tail_bits + 2)),
    };
    const and_lhs = [_]Word{
        0,
        (@as(Word, 1) << @intCast(tail_bits - 1)) | (@as(Word, 1) << @intCast(tail_bits + 2)),
    };
    const and_rhs = and_lhs;
    const andnot_lhs = [_]Word{
        0,
        (@as(Word, 1) << @intCast(tail_bits - 1)) | (@as(Word, 1) << @intCast(tail_bits + 2)),
    };
    const andnot_rhs = [_]Word{
        0,
        @as(Word, 1) << @intCast(tail_bits + 2),
    };
    const zero_map = [_]Word{
        ~@as(Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(Word, 1) << @intCast(tail_bits - 1)),
    };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextBit(&set_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&set_map, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextZeroBit(&zero_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zero_map, nbits, boundary + 1));
}

test "single-word partial tails keep alias entrypoints aligned at inclusive starts" {
    const nbits = 11;
    const boundary = nbits - 1;

    const set_map = [_]Word{(@as(Word, 1) << @intCast(boundary)) | (@as(Word, 1) << 13)};
    const and_lhs = [_]Word{(@as(Word, 1) << @intCast(boundary)) | (@as(Word, 1) << 13)};
    const and_rhs = and_lhs;
    const andnot_lhs = [_]Word{
        (@as(Word, 1) << 2) | (@as(Word, 1) << @intCast(boundary)) | (@as(Word, 1) << 13),
    };
    const andnot_rhs = [_]Word{
        (@as(Word, 1) << 2) | (@as(Word, 1) << 13),
    };
    const zero_map = [_]Word{find_bit.lastWordMask(nbits) & ~(@as(Word, 1) << @intCast(boundary))};

    try std.testing.expectEqual(
        find_bit.findNextBit(&set_map, nbits, boundary),
        find_bit.find_next_bit(&set_map, nbits, boundary),
    );
    try std.testing.expectEqual(
        find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary),
        find_bit.find_next_and_bit(&and_lhs, &and_rhs, nbits, boundary),
    );
    try std.testing.expectEqual(
        find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary),
        find_bit.find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, boundary),
    );
    try std.testing.expectEqual(
        find_bit.findNextZeroBit(&zero_map, nbits, boundary),
        find_bit.find_next_zero_bit(&zero_map, nbits, boundary),
    );

    try std.testing.expectEqual(@as(usize, boundary), find_bit._find_next_bit(&set_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit._find_next_and_bit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit._find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit._find_next_zero_bit(&zero_map, nbits, boundary));

    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_bit(&set_map, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_and_bit(&and_lhs, &and_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_zero_bit(&zero_map, nbits, boundary + 1));
}
