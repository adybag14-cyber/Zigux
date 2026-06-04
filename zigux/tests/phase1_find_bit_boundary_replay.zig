const std = @import("std");
const find_bit = @import("find_bit");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

fn bit(idx: usize) Word {
    return @as(Word, 1) << @intCast(idx);
}

test "inclusive starts keep head and tail boundary bits reachable" {
    const tail_bits: usize = 6;
    const nbits = bits_per_long + tail_bits;
    const head_boundary = bits_per_long - 1;
    const tail_boundary = nbits - 1;
    const map = [_]Word{
        bit(head_boundary),
        bit(tail_boundary - bits_per_long) | bit(tail_bits + 2),
    };
    const zero_map = [_]Word{
        ~bit(head_boundary),
        find_bit.lastWordMask(nbits) & ~bit(tail_boundary - bits_per_long),
    };

    try std.testing.expectEqual(head_boundary, find_bit.findNextBit(&map, nbits, head_boundary));
    try std.testing.expectEqual(tail_boundary, find_bit.findNextBit(&map, nbits, head_boundary + 1));
    try std.testing.expectEqual(tail_boundary, find_bit.findNextBit(&map, nbits, tail_boundary));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&map, nbits, tail_boundary + 1));

    try std.testing.expectEqual(head_boundary, find_bit.findNextZeroBit(&zero_map, nbits, head_boundary));
    try std.testing.expectEqual(tail_boundary, find_bit.findNextZeroBit(&zero_map, nbits, head_boundary + 1));
    try std.testing.expectEqual(tail_boundary, find_bit.findNextZeroBit(&zero_map, nbits, tail_boundary));
    try std.testing.expectEqual(nbits, find_bit.findNextZeroBit(&zero_map, nbits, tail_boundary + 1));
}

test "combined scans clamp junk beyond the declared tail" {
    const tail_bits: usize = 5;
    const nbits = bits_per_long + tail_bits;
    const tail_mask = find_bit.lastWordMask(nbits);
    const tail_junk = ~tail_mask;
    const lhs = [_]Word{
        bit(3),
        bit(1) | bit(4) | tail_junk,
    };
    const rhs = [_]Word{
        bit(3),
        bit(4) | bit(tail_bits + 3),
    };
    const blocker = [_]Word{
        0,
        bit(1) | tail_junk,
    };

    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstAndBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(bits_per_long + 4, find_bit.findNextAndBit(&lhs, &rhs, nbits, 4));
    try std.testing.expectEqual(nbits, find_bit.findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstAndNotBit(&lhs, &blocker, nbits));
    try std.testing.expectEqual(bits_per_long + 4, find_bit.findNextAndNotBit(&lhs, &blocker, nbits, 4));
    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(&lhs, &blocker, nbits, bits_per_long + 5));
}

test "last-bit and clump scans honor exhausted windows" {
    const nbits = bits_per_long + 5;
    const map = [_]Word{
        bit(7),
        bit(3) | bit(9),
    };

    try std.testing.expectEqual(bits_per_long + 3, find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findLastBit(&map, bits_per_long));
    try std.testing.expectEqual(nbits, find_bit.findLastBit(&[_]Word{ 0, bit(9) }, nbits));

    var clump: u8 = 0xa5;
    try std.testing.expectEqual(nbits, find_bit.findNextClump8(&clump, &map, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0xa5), clump);
    try std.testing.expectEqual(nbits, find_bit.find_next_clump8(&clump, &map, nbits, nbits + 3));
    try std.testing.expectEqual(@as(u8, 0xa5), clump);
}
