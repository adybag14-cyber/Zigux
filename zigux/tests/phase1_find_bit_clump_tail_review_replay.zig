const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "phase1 find_bit clump replay keeps tail-masked aligned bytes and caller-byte contracts" {
    const tail_bits: usize = 5;
    const nbits = bits_per_long + tail_bits;
    const tail_map = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 6),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findFirstClump8(&clump, &tail_map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.find_next_clump8(&clump, &tail_map, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&clump, &tail_map, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);

    const last_aligned_byte = bits_per_long - 8;
    const boundary_map = [_]Word{
        @as(Word, 0xa5) << @intCast(last_aligned_byte),
        @as(Word, 0x11),
    };
    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&boundary_map, last_aligned_byte));
    try std.testing.expectEqual(@as(u8, 0x11), find_bit.getValue8(&boundary_map, bits_per_long));
}

test "phase1 find_bit tail-word boundary replay keeps inclusive next scans reachable" {
    const tail_bits: usize = 5;
    const boundary = bits_per_long + tail_bits - 1;
    const nbits = boundary + 1;
    const set_map = [_]Word{
        0,
        (@as(Word, 1) << @intCast(tail_bits - 1)) | (@as(Word, 1) << @intCast(tail_bits + 2)),
    };
    const and_rhs = set_map;
    const andnot_rhs = [_]Word{ 0, @as(Word, 1) << @intCast(tail_bits + 2) };
    const zero_map = [_]Word{
        ~@as(Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(Word, 1) << @intCast(tail_bits - 1)),
    };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextBit(&set_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndBit(&set_map, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndNotBit(&set_map, &andnot_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextZeroBit(&zero_map, nbits, boundary));

    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&set_map, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_andnot_bit(&set_map, &andnot_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_zero_bit(&zero_map, nbits, boundary + 1));
}

test "phase1 find_bit last-bit replay clamps exact-word and tail-word storage" {
    const exact_nbits = bits_per_long;
    const exact_boundary = bits_per_long - 1;
    var exact_word = [_]Word{
        @as(Word, 1) << @intCast(exact_boundary),
        @as(Word, 1) << 5,
    };
    try std.testing.expectEqual(@as(usize, exact_boundary), find_bit.findLastBit(&exact_word, exact_nbits));
    try std.testing.expectEqual(@as(usize, exact_boundary), find_bit.find_last_bit(&exact_word, exact_nbits));

    exact_word[0] = 0;
    try std.testing.expectEqual(@as(usize, exact_nbits), find_bit._find_last_bit(&exact_word, exact_nbits));

    const tail_nbits = bits_per_long + 5;
    var tail_word = [_]Word{
        0,
        (@as(Word, 1) << 3) | (@as(Word, 1) << 9),
    };
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), find_bit.findLastBit(&tail_word, tail_nbits));

    tail_word[1] &= ~(@as(Word, 1) << 3);
    try std.testing.expectEqual(@as(usize, tail_nbits), find_bit.findLastBit(&tail_word, tail_nbits));
}
