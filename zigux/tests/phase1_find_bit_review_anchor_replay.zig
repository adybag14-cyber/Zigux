const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "phase1 find_bit review anchor keeps tail-window scans aligned" {
    const nbits = bits_per_long + 6;
    const tail_bit = bits_per_long + 4;
    const out_of_range_tail_bit = bits_per_long + 7;

    const set_map = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 7),
    };
    const zero_map = [_]Word{
        ~@as(Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(Word, 1) << 5),
    };
    const and_lhs = [_]Word{
        0,
        (@as(Word, 1) << 2) | (@as(Word, 1) << 4),
    };
    const and_rhs = [_]Word{
        0,
        (@as(Word, 1) << 4) | (@as(Word, 1) << 5),
    };
    const andnot_lhs = [_]Word{
        0,
        (@as(Word, 1) << 3) | (@as(Word, 1) << 4),
    };
    const andnot_rhs = [_]Word{
        0,
        (@as(Word, 1) << 3),
    };
    const tail_masked = [_]Word{
        0,
        (@as(Word, 1) << 4) | (@as(Word, 1) << 7),
    };

    try std.testing.expectEqual(tail_bit, find_bit.findNextBit(&set_map, nbits, bits_per_long + 2));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&set_map, nbits, tail_bit + 1));
    try std.testing.expectEqual(bits_per_long + 5, find_bit.findNextZeroBit(&zero_map, nbits, bits_per_long));
    try std.testing.expectEqual(tail_bit, find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, bits_per_long + 2));
    try std.testing.expectEqual(tail_bit, find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long + 2));
    try std.testing.expectEqual(tail_bit, find_bit.findLastBit(&tail_masked, nbits));
    try std.testing.expectEqual(nbits, find_bit.findLastBit(&[_]Word{ 0, @as(Word, 1) << 7 }, nbits));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&set_map, nbits, out_of_range_tail_bit));
}

test "phase1 find_bit review anchor keeps clump bytes reachable from final partial words" {
    const nbits = bits_per_long + 5;
    const cross_word = [_]Word{
        (@as(Word, 1) << 56) | (@as(Word, 1) << 60),
        (@as(Word, 1) << 2),
    };
    var clump: u8 = 0xaa;

    try std.testing.expectEqual(@as(u8, 0x11), find_bit.getValue8(&cross_word, 56));
    try std.testing.expectEqual(bits_per_long - 8, find_bit.findFirstClump8(&clump, &cross_word, nbits));
    try std.testing.expectEqual(@as(u8, 0x11), clump);
    try std.testing.expectEqual(bits_per_long, find_bit.findNextClump8(&clump, &cross_word, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x04), clump);

    clump = 0x5c;
    try std.testing.expectEqual(nbits, find_bit.findNextClump8(&clump, &cross_word, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5c), clump);
}

test "phase1 find_bit review anchor keeps alias entry points in sync" {
    const nbits = bits_per_long + 6;
    const lhs = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4),
    };
    const rhs = [_]Word{
        0,
        @as(Word, 1) << 1,
    };
    const set_map = [_]Word{
        0,
        (@as(Word, 1) << 4),
    };
    var clump_public: u8 = 0;
    var clump_linux: u8 = 0;
    var clump_underscore: u8 = 0;

    try std.testing.expectEqual(
        find_bit.findFirstAndNotBit(&lhs, &rhs, nbits),
        find_bit.find_first_andnot_bit(&lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        find_bit.findNextAndNotBit(&lhs, &rhs, nbits, bits_per_long),
        find_bit._find_next_andnot_bit(&lhs, &rhs, nbits, bits_per_long),
    );
    try std.testing.expectEqual(
        find_bit.findLastBit(&set_map, nbits),
        find_bit.find_last_bit(&set_map, nbits),
    );
    try std.testing.expectEqual(
        find_bit.findLastBit(&set_map, nbits),
        find_bit._find_last_bit(&set_map, nbits),
    );

    const clump_offset = find_bit.findFirstClump8(&clump_public, &set_map, nbits);
    try std.testing.expectEqual(clump_offset, find_bit.find_first_clump8(&clump_linux, &set_map, nbits));
    try std.testing.expectEqual(clump_offset, find_bit._find_first_clump8(&clump_underscore, &set_map, nbits));
    try std.testing.expectEqual(clump_public, clump_linux);
    try std.testing.expectEqual(clump_public, clump_underscore);
}
