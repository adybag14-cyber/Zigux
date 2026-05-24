const std = @import("std");
const find_bit = @import("find_bit");

test "phase1 find_bit smoke keeps shared tail windows masked" {
    const word_bits = find_bit.bits_per_long;
    const nbits = word_bits + 5;

    const and_lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 7),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };
    const and_rhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 7),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 9),
    };
    try std.testing.expectEqual(@as(usize, 7), find_bit.findFirstAndBit(&and_lhs, &and_rhs, nbits));
    try std.testing.expectEqual(@as(usize, word_bits + 1), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, 8));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, word_bits + 2));

    const andnot_lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 7),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };
    const andnot_rhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 7),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 9),
    };
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits));
    try std.testing.expectEqual(@as(usize, word_bits + 4), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 3));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, word_bits + 5));

    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(find_bit.Word, 1) << 3),
    };
    try std.testing.expectEqual(@as(usize, word_bits + 3), find_bit.findFirstZeroBit(&zero_map, nbits));
    try std.testing.expectEqual(@as(usize, word_bits + 3), find_bit.findNextZeroBit(&zero_map, nbits, word_bits + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zero_map, nbits, word_bits + 4));

    var last_map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 8),
    };
    try std.testing.expectEqual(@as(usize, word_bits + 3), find_bit.findLastBit(&last_map, nbits));
    last_map[1] &= ~(@as(find_bit.Word, 1) << 3);
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findLastBit(&last_map, nbits));
}

test "phase1 find_bit smoke keeps alias entrypoints aligned" {
    const word_bits = find_bit.bits_per_long;
    const nbits = word_bits + 5;

    const and_lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 6),
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 7),
    };
    const and_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 7),
    };
    try std.testing.expectEqual(
        find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, 7),
        find_bit._find_next_and_bit(&and_lhs, &and_rhs, nbits, 7),
    );
    try std.testing.expectEqual(
        find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, word_bits + 3),
        find_bit.find_next_and_bit(&and_lhs, &and_rhs, nbits, word_bits + 3),
    );

    const andnot_lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 5),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4),
    };
    const andnot_rhs = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << 1,
    };
    try std.testing.expectEqual(
        find_bit.findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits),
        find_bit._find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits),
    );
    try std.testing.expectEqual(
        find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 6),
        find_bit.find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, 6),
    );

    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(find_bit.Word, 1) << 4),
    };
    try std.testing.expectEqual(
        find_bit.findNextZeroBit(&zero_map, nbits, word_bits),
        find_bit._find_next_zero_bit(&zero_map, nbits, word_bits),
    );
    try std.testing.expectEqual(
        find_bit.findLastBit(&and_lhs, nbits),
        find_bit.find_last_bit(&and_lhs, nbits),
    );
}
