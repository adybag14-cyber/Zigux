const std = @import("std");
const find_bit = @import("find_bit");

test "phase 1 find_bit review anchor replay keeps inclusive tail boundaries and andnot aliases aligned" {
    const tail_bits: usize = 5;
    const nbits = find_bit.bits_per_long + tail_bits;
    const boundary = nbits - 1;
    const and_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << @intCast(tail_bits - 1)) |
            (@as(find_bit.Word, 1) << @intCast(tail_bits + 2)),
    };
    const and_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << @intCast(tail_bits - 1)) |
            (@as(find_bit.Word, 1) << @intCast(tail_bits + 2)),
    };
    const andnot_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << @intCast(tail_bits - 1)) |
            (@as(find_bit.Word, 1) << @intCast(tail_bits + 2)),
    };
    const andnot_rhs = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << @intCast(tail_bits + 2),
    };
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(find_bit.Word, 1) << @intCast(tail_bits - 1)),
    };

    try std.testing.expectEqual(boundary, find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(boundary, find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary));
    try std.testing.expectEqual(boundary, find_bit.find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, boundary));
    try std.testing.expectEqual(boundary, find_bit._find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, boundary));
    try std.testing.expectEqual(boundary, find_bit.findNextZeroBit(&zero_map, nbits, boundary));

    try std.testing.expectEqual(nbits, find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(nbits, find_bit.findNextZeroBit(&zero_map, nbits, boundary + 1));

    const single_word_nbits = 11;
    const single_boundary = single_word_nbits - 1;
    const single_andnot_lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << @intCast(single_boundary)) |
            (@as(find_bit.Word, 1) << 13),
    };
    const single_andnot_rhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 13,
    };
    try std.testing.expectEqual(
        single_boundary,
        find_bit.findNextAndNotBit(&single_andnot_lhs, &single_andnot_rhs, single_word_nbits, single_boundary),
    );
    try std.testing.expectEqual(
        single_boundary,
        find_bit.find_next_andnot_bit(&single_andnot_lhs, &single_andnot_rhs, single_word_nbits, single_boundary),
    );
    try std.testing.expectEqual(
        single_word_nbits,
        find_bit._find_next_andnot_bit(&single_andnot_lhs, &single_andnot_rhs, single_word_nbits, single_boundary + 1),
    );
}

test "phase 1 find_bit review anchor replay keeps clump8 and getValue8 byte boundaries review-visible" {
    const last_aligned_byte = find_bit.bits_per_long - 8;
    const nbits = find_bit.bits_per_long + 5;
    const bitmap = [_]find_bit.Word{
        @as(find_bit.Word, 0xa5) << @intCast(last_aligned_byte),
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6),
    };

    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&bitmap, last_aligned_byte));
    try std.testing.expectEqual(@as(u8, 0x48), find_bit.getValue8(&bitmap, find_bit.bits_per_long));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, last_aligned_byte), find_bit.findFirstClump8(&clump, &bitmap, find_bit.bits_per_long * 2));
    try std.testing.expectEqual(@as(u8, 0xa5), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&clump, &bitmap, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_clump8(&clump, &bitmap, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&clump, &bitmap, nbits, nbits + 4));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "phase 1 find_bit review anchor replay keeps backward scans and zero-sized short-circuits explicit" {
    const nbits = find_bit.bits_per_long + 5;
    var bitmap = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 7,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 10),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findLastBit(&bitmap, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.find_last_bit(&bitmap, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit._find_last_bit(&bitmap, nbits));

    bitmap[1] &= ~(@as(find_bit.Word, 1) << 3);
    try std.testing.expectEqual(@as(usize, 7), find_bit.findLastBit(&bitmap, nbits));
    bitmap[0] = 0;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findLastBit(&bitmap, nbits));

    const populated = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 5) | (@as(find_bit.Word, 1) << 9),
        @as(find_bit.Word, 1) << 3,
    };
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstBit(&populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(&populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstAndBit(&populated, &populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstAndNotBit(&populated, &populated, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findLastBit(&populated, 0));
}
