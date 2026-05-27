const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "phase1 find_bit last-bit replay keeps tail-clamped aliases aligned" {
    const nbits = bits_per_long + 6;
    const last_map = [_]Word{
        (@as(Word, 1) << 7) | (@as(Word, 1) << 14),
        (@as(Word, 1) << 3) | (@as(Word, 1) << 9),
    };
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findLastBit(&last_map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.find_last_bit(&last_map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit._find_last_bit(&last_map, nbits));

    const outside_only = [_]Word{
        0,
        @as(Word, 1) << 9,
    };
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findLastBit(&outside_only, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_last_bit(&outside_only, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_last_bit(&outside_only, nbits));

    const single_word_nbits = 11;
    const single_word = [_]Word{
        (@as(Word, 1) << 4) | (@as(Word, 1) << 15),
    };
    try std.testing.expectEqual(@as(usize, 4), find_bit.findLastBit(&single_word, single_word_nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.find_last_bit(&single_word, single_word_nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit._find_last_bit(&single_word, single_word_nbits));
}

test "phase1 find_bit clump replay keeps first and next aliases byte-aligned" {
    const nbits = bits_per_long;
    const bitmap = [_]Word{
        (@as(Word, 1) << 9) |
            (@as(Word, 1) << 14) |
            (@as(Word, 1) << 25) |
            (@as(Word, 1) << 29),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstClump8(&clump, &bitmap, nbits));
    try std.testing.expectEqual(@as(u8, 0b0100_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.find_first_clump8(&clump, &bitmap, nbits));
    try std.testing.expectEqual(@as(u8, 0b0100_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit._find_first_clump8(&clump, &bitmap, nbits));
    try std.testing.expectEqual(@as(u8, 0b0100_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, 24), find_bit.findNextClump8(&clump, &bitmap, nbits, 16));
    try std.testing.expectEqual(@as(u8, 0b0010_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, 24), find_bit.find_next_clump8(&clump, &bitmap, nbits, 25));
    try std.testing.expectEqual(@as(u8, 0b0010_0010), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, &bitmap, nbits, 30));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);

    clump = 0x33;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_clump8(&clump, &bitmap, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x33), clump);
}
