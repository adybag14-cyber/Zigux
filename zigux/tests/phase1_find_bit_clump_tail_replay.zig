const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "tail clump replay keeps aligned tail bytes stable across advancing starts" {
    const nbits = bits_per_long + 8;
    const bitmap = [_]Word{
        0,
        (@as(Word, 1) << 1) |
            (@as(Word, 1) << 3) |
            (@as(Word, 1) << 6),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findFirstClump8(&clump, &bitmap, nbits));
    try std.testing.expectEqual(@as(u8, 0b0100_1010), clump);

    clump = 0;
    try std.testing.expectEqual(
        @as(usize, bits_per_long),
        find_bit.findNextClump8(&clump, &bitmap, nbits, bits_per_long + 2),
    );
    try std.testing.expectEqual(@as(u8, 0b0100_1010), clump);

    clump = 0;
    try std.testing.expectEqual(
        @as(usize, bits_per_long),
        find_bit.find_next_clump8(&clump, &bitmap, nbits, bits_per_long + 3),
    );
    try std.testing.expectEqual(@as(u8, 0b0100_1010), clump);
}

test "tail replay keeps next scans inside the declared tail window" {
    const nbits = bits_per_long + 8;
    const lhs = [_]Word{
        0,
        (@as(Word, 1) << 1) |
            (@as(Word, 1) << 3) |
            (@as(Word, 1) << 6),
    };
    const rhs = [_]Word{
        0,
        (@as(Word, 1) << 3) |
            (@as(Word, 1) << 6),
    };

    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextBit(&lhs, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findLastBit(&lhs, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 6), find_bit.findLastBit(&lhs, nbits));

    const zero_map = [_]Word{ ~@as(Word, 0), find_bit.lastWordMask(nbits) & ~(@as(Word, 1) << 3) };
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findNextZeroBit(&zero_map, nbits, bits_per_long + 2));
}

test "tail replay preserves caller clumps once every in-range bit is exhausted" {
    const nbits = bits_per_long + 8;
    const bitmap = [_]Word{
        0,
        (@as(Word, 1) << 1) |
            (@as(Word, 1) << 3) |
            (@as(Word, 1) << 6),
    };

    var clump: u8 = 0x5a;
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextClump8(&clump, &bitmap, nbits, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0x5a), clump);

    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&bitmap, nbits, bits_per_long + 11));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_bit(&bitmap, nbits, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_bit(&bitmap, nbits, nbits + 4));
}
