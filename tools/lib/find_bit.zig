const std = @import("std");

pub const Word = usize;
pub const bits_per_long = @bitSizeOf(Word);

pub fn bitsToWords(nbits: usize) usize {
    return if (nbits == 0) 0 else (nbits + bits_per_long - 1) / bits_per_long;
}

pub fn firstWordMask(start: usize) Word {
    const shift = start & (bits_per_long - 1);
    return ~@as(Word, 0) << @intCast(shift);
}

pub fn lastWordMask(nbits: usize) Word {
    if (nbits == 0) {
        return 0;
    }

    const rem = nbits & (bits_per_long - 1);
    if (rem == 0) {
        return ~@as(Word, 0);
    }

    return (@as(Word, 1) << @intCast(rem)) - 1;
}

fn assertBitmapLen(bitmap: []const Word, nbits: usize) void {
    std.debug.assert(bitmap.len >= bitsToWords(nbits));
}

fn tailWordMask(idx: usize, nbits: usize) Word {
    if (nbits == 0) {
        return 0;
    }

    const last_idx = bitsToWords(nbits) - 1;
    return if (idx == last_idx) lastWordMask(nbits) else ~@as(Word, 0);
}

fn maskWordInRange(idx: usize, value: Word, nbits: usize) Word {
    return value & tailWordMask(idx, nbits);
}

fn bitIndex(idx: usize, value: Word, nbits: usize) usize {
    const bit = idx * bits_per_long + @as(usize, @intCast(@ctz(value)));
    return if (bit < nbits) bit else nbits;
}

fn singleWordMask(nbits: usize, start: usize) Word {
    std.debug.assert(nbits <= bits_per_long);
    return firstWordMask(start) & lastWordMask(nbits);
}

fn singleWordBitIndex(value: Word, nbits: usize, start: usize) usize {
    const masked = value & singleWordMask(nbits, start);
    return if (masked != 0) bitIndex(0, masked, nbits) else nbits;
}

fn lastBitIndex(idx: usize, value: Word) usize {
    const bit = bits_per_long - 1 - @as(usize, @intCast(@clz(value)));
    return idx * bits_per_long + bit;
}

pub fn findFirstBit(addr: []const Word, nbits: usize) usize {
    if (nbits == 0) {
        return 0;
    }

    assertBitmapLen(addr, nbits);

    if (nbits <= bits_per_long) {
        return singleWordBitIndex(addr[0], nbits, 0);
    }

    var idx: usize = 0;
    while (idx * bits_per_long < nbits) : (idx += 1) {
        const value = maskWordInRange(idx, addr[idx], nbits);
        if (value != 0) {
            return bitIndex(idx, value, nbits);
        }
    }

    return nbits;
}

pub fn find_first_bit(addr: []const Word, nbits: usize) usize {
    return findFirstBit(addr, nbits);
}

pub fn _find_first_bit(addr: []const Word, nbits: usize) usize {
    return findFirstBit(addr, nbits);
}

pub fn findFirstAndBit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {
    if (nbits == 0) {
        return 0;
    }

    assertBitmapLen(addr1, nbits);
    assertBitmapLen(addr2, nbits);

    if (nbits <= bits_per_long) {
        return singleWordBitIndex(addr1[0] & addr2[0], nbits, 0);
    }

    var idx: usize = 0;
    while (idx * bits_per_long < nbits) : (idx += 1) {
        const value = maskWordInRange(idx, addr1[idx] & addr2[idx], nbits);
        if (value != 0) {
            return bitIndex(idx, value, nbits);
        }
    }

    return nbits;
}

pub fn find_first_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {
    return findFirstAndBit(addr1, addr2, nbits);
}

pub fn _find_first_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {
    return findFirstAndBit(addr1, addr2, nbits);
}

pub fn findFirstAndNotBit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {
    if (nbits == 0) {
        return 0;
    }

    assertBitmapLen(addr1, nbits);
    assertBitmapLen(addr2, nbits);

    if (nbits <= bits_per_long) {
        return singleWordBitIndex(addr1[0] & ~addr2[0], nbits, 0);
    }

    var idx: usize = 0;
    while (idx * bits_per_long < nbits) : (idx += 1) {
        const value = maskWordInRange(idx, addr1[idx] & ~addr2[idx], nbits);
        if (value != 0) {
            return bitIndex(idx, value, nbits);
        }
    }

    return nbits;
}

pub fn find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {
    return findFirstAndNotBit(addr1, addr2, nbits);
}

pub fn _find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {
    return findFirstAndNotBit(addr1, addr2, nbits);
}

pub fn findFirstZeroBit(addr: []const Word, nbits: usize) usize {
    if (nbits == 0) {
        return 0;
    }

    assertBitmapLen(addr, nbits);

    if (nbits <= bits_per_long) {
        return singleWordBitIndex(~addr[0], nbits, 0);
    }

    var idx: usize = 0;
    while (idx * bits_per_long < nbits) : (idx += 1) {
        const value = maskWordInRange(idx, ~addr[idx], nbits);
        if (value != 0) {
            return bitIndex(idx, value, nbits);
        }
    }

    return nbits;
}

pub fn find_first_zero_bit(addr: []const Word, nbits: usize) usize {
    return findFirstZeroBit(addr, nbits);
}

pub fn _find_first_zero_bit(addr: []const Word, nbits: usize) usize {
    return findFirstZeroBit(addr, nbits);
}

pub fn findNextBit(addr: []const Word, nbits: usize, start: usize) usize {
    if (start >= nbits) {
        return nbits;
    }

    assertBitmapLen(addr, nbits);

    if (nbits <= bits_per_long) {
        return singleWordBitIndex(addr[0], nbits, start);
    }

    var idx = start / bits_per_long;
    var value = maskWordInRange(idx, addr[idx], nbits) & firstWordMask(start);

    while (value == 0) {
        idx += 1;
        if (idx * bits_per_long >= nbits) {
            return nbits;
        }
        value = maskWordInRange(idx, addr[idx], nbits);
    }

    return bitIndex(idx, value, nbits);
}

pub fn find_next_bit(addr: []const Word, nbits: usize, start: usize) usize {
    return findNextBit(addr, nbits, start);
}

pub fn _find_next_bit(addr: []const Word, nbits: usize, start: usize) usize {
    return findNextBit(addr, nbits, start);
}

pub fn findNextAndBit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    if (start >= nbits) {
        return nbits;
    }

    assertBitmapLen(addr1, nbits);
    assertBitmapLen(addr2, nbits);

    if (nbits <= bits_per_long) {
        return singleWordBitIndex(addr1[0] & addr2[0], nbits, start);
    }

    var idx = start / bits_per_long;
    var value = maskWordInRange(idx, addr1[idx] & addr2[idx], nbits) & firstWordMask(start);

    while (value == 0) {
        idx += 1;
        if (idx * bits_per_long >= nbits) {
            return nbits;
        }
        value = maskWordInRange(idx, addr1[idx] & addr2[idx], nbits);
    }

    return bitIndex(idx, value, nbits);
}

pub fn find_next_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    return findNextAndBit(addr1, addr2, nbits, start);
}

pub fn _find_next_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    return findNextAndBit(addr1, addr2, nbits, start);
}

pub fn findNextAndNotBit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    if (start >= nbits) {
        return nbits;
    }

    assertBitmapLen(addr1, nbits);
    assertBitmapLen(addr2, nbits);

    if (nbits <= bits_per_long) {
        return singleWordBitIndex(addr1[0] & ~addr2[0], nbits, start);
    }

    var idx = start / bits_per_long;
    var value = maskWordInRange(idx, addr1[idx] & ~addr2[idx], nbits) & firstWordMask(start);

    while (value == 0) {
        idx += 1;
        if (idx * bits_per_long >= nbits) {
            return nbits;
        }
        value = maskWordInRange(idx, addr1[idx] & ~addr2[idx], nbits);
    }

    return bitIndex(idx, value, nbits);
}

pub fn find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    return findNextAndNotBit(addr1, addr2, nbits, start);
}

pub fn _find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    return findNextAndNotBit(addr1, addr2, nbits, start);
}

pub fn findNextZeroBit(addr: []const Word, nbits: usize, start: usize) usize {
    if (start >= nbits) {
        return nbits;
    }

    assertBitmapLen(addr, nbits);

    if (nbits <= bits_per_long) {
        return singleWordBitIndex(~addr[0], nbits, start);
    }

    var idx = start / bits_per_long;
    var value = maskWordInRange(idx, ~addr[idx], nbits) & firstWordMask(start);

    while (value == 0) {
        idx += 1;
        if (idx * bits_per_long >= nbits) {
            return nbits;
        }
        value = maskWordInRange(idx, ~addr[idx], nbits);
    }

    return bitIndex(idx, value, nbits);
}

pub fn find_next_zero_bit(addr: []const Word, nbits: usize, start: usize) usize {
    return findNextZeroBit(addr, nbits, start);
}

pub fn _find_next_zero_bit(addr: []const Word, nbits: usize, start: usize) usize {
    return findNextZeroBit(addr, nbits, start);
}

pub fn getValue8(addr: []const Word, offset: usize) u8 {
    std.debug.assert((offset & 7) == 0);

    const idx = offset / bits_per_long;
    const shift = offset & (bits_per_long - 1);
    std.debug.assert(idx < addr.len);

    var value = addr[idx] >> @intCast(shift);
    if (shift > bits_per_long - 8 and idx + 1 < addr.len) {
        value |= addr[idx + 1] << @intCast(bits_per_long - shift);
    }

    return @as(u8, @intCast(value & 0xff));
}

pub fn findNextClump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {
    const next = findNextBit(addr, nbits, offset);
    if (next == nbits) {
        return nbits;
    }

    const clump_offset = next & ~@as(usize, 7);
    clump.* = getValue8(addr, clump_offset);
    return clump_offset;
}

pub fn find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {
    return findNextClump8(clump, addr, nbits, offset);
}

pub fn _find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {
    return findNextClump8(clump, addr, nbits, offset);
}

pub fn findFirstClump8(clump: *u8, addr: []const Word, nbits: usize) usize {
    return findNextClump8(clump, addr, nbits, 0);
}

pub fn find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {
    return findFirstClump8(clump, addr, nbits);
}

pub fn _find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {
    return findFirstClump8(clump, addr, nbits);
}

pub fn findLastBit(addr: []const Word, nbits: usize) usize {
    assertBitmapLen(addr, nbits);

    if (nbits == 0) {
        return 0;
    }

    var idx = bitsToWords(nbits) - 1;
    var value = maskWordInRange(idx, addr[idx], nbits);

    while (value == 0) {
        if (idx == 0) {
            return nbits;
        }
        idx -= 1;
        value = addr[idx];
    }

    return lastBitIndex(idx, value);
}

pub fn find_last_bit(addr: []const Word, nbits: usize) usize {
    return findLastBit(addr, nbits);
}

pub fn _find_last_bit(addr: []const Word, nbits: usize) usize {
    return findLastBit(addr, nbits);
}

test "find first and next set bits across words" {
    var bitmap = [_]Word{ 0, 0, 0 };
    bitmap[0] |= @as(Word, 1) << 5;
    bitmap[1] |= @as(Word, 1) << 3;
    bitmap[2] |= @as(Word, 1) << 7;

    try std.testing.expectEqual(@as(usize, 5), findFirstBit(&bitmap, bits_per_long * 3));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), findNextBit(&bitmap, bits_per_long * 3, 6));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 7), findNextBit(&bitmap, bits_per_long * 3, bits_per_long + 4));

    const andnot_lhs = [_]Word{
        (@as(Word, 1) << 5) | (@as(Word, 1) << 11),
        (@as(Word, 1) << 3) | (@as(Word, 1) << 6),
        @as(Word, 1) << 7,
    };
    const andnot_rhs = [_]Word{
        @as(Word, 1) << 5,
        @as(Word, 1) << 6,
        @as(Word, 1) << 7,
    };
    try std.testing.expectEqual(@as(usize, 11), findFirstAndNotBit(&andnot_lhs, &andnot_rhs, bits_per_long * 3));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), findNextAndNotBit(&andnot_lhs, &andnot_rhs, bits_per_long * 3, 12));
}

test "find zero bits respects the declared bit count" {
    var bitmap = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    bitmap[1] &= ~(@as(Word, 1) << 4);

    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findFirstZeroBit(&bitmap, bits_per_long * 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextZeroBit(&bitmap, bits_per_long * 2, bits_per_long));
    try std.testing.expectEqual(@as(usize, 3), findFirstZeroBit(&[_]Word{0b1111_0111}, 12));
}

test "find and bit returns the first shared set bit" {
    const lhs = [_]Word{ (@as(Word, 1) << 1) | (@as(Word, 1) << 9), @as(Word, 1) << 2 };
    const rhs = [_]Word{ (@as(Word, 1) << 9), @as(Word, 1) << 2 };

    try std.testing.expectEqual(@as(usize, 9), findFirstAndBit(&lhs, &rhs, bits_per_long * 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), findNextAndBit(&lhs, &rhs, bits_per_long * 2, 10));
}

test "underscore entry points reuse the public helper behavior" {
    const nbits = bits_per_long * 2;
    const set_map = [_]Word{ (@as(Word, 1) << 5) | (@as(Word, 1) << 9), @as(Word, 1) << 3 };
    const zero_map = [_]Word{ ~(@as(Word, 1) << 7), ~@as(Word, 0) };
    const and_lhs = [_]Word{ (@as(Word, 1) << 9), @as(Word, 1) << 3 };
    const and_rhs = [_]Word{ (@as(Word, 1) << 9), @as(Word, 1) << 3 };
    const andnot_lhs = [_]Word{ (@as(Word, 1) << 7) | (@as(Word, 1) << 11), (@as(Word, 1) << 2) | (@as(Word, 1) << 5) };
    const andnot_rhs = [_]Word{ (@as(Word, 1) << 11), @as(Word, 1) << 5 };

    try std.testing.expectEqual(findFirstBit(&set_map, nbits), _find_first_bit(&set_map, nbits));
    try std.testing.expectEqual(findFirstZeroBit(&zero_map, nbits), _find_first_zero_bit(&zero_map, nbits));
    try std.testing.expectEqual(findFirstAndBit(&and_lhs, &and_rhs, nbits), _find_first_and_bit(&and_lhs, &and_rhs, nbits));
    try std.testing.expectEqual(findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits), _find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits));
    try std.testing.expectEqual(findNextBit(&set_map, nbits, 6), _find_next_bit(&set_map, nbits, 6));
    try std.testing.expectEqual(findNextZeroBit(&zero_map, nbits, 7), _find_next_zero_bit(&zero_map, nbits, 7));
    try std.testing.expectEqual(findNextAndBit(&and_lhs, &and_rhs, nbits, 10), _find_next_and_bit(&and_lhs, &and_rhs, nbits, 10));
    try std.testing.expectEqual(findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 8), _find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, 8));
    try std.testing.expectEqual(findLastBit(&set_map, nbits), _find_last_bit(&set_map, nbits));
}

test "single-word next scans honor start masks" {
    const nbits = bits_per_long;
    const set_bits = [_]Word{(@as(Word, 1) << 2) | (@as(Word, 1) << 7) | (@as(Word, 1) << 11)};
    const zero_bits = [_]Word{~((@as(Word, 1) << 4) | (@as(Word, 1) << 9))};
    const and_lhs = [_]Word{(@as(Word, 1) << 1) | (@as(Word, 1) << 9) | (@as(Word, 1) << 12)};
    const and_rhs = [_]Word{(@as(Word, 1) << 0) | (@as(Word, 1) << 9) | (@as(Word, 1) << 12)};
    const andnot_lhs = [_]Word{(@as(Word, 1) << 1) | (@as(Word, 1) << 9) | (@as(Word, 1) << 12)};
    const andnot_rhs = [_]Word{(@as(Word, 1) << 1) | (@as(Word, 1) << 12)};

    try std.testing.expectEqual(@as(usize, 7), findNextBit(&set_bits, nbits, 3));
    try std.testing.expectEqual(@as(usize, 11), findNextBit(&set_bits, nbits, 8));
    try std.testing.expectEqual(@as(usize, 4), findNextZeroBit(&zero_bits, nbits, 1));
    try std.testing.expectEqual(@as(usize, 9), findNextZeroBit(&zero_bits, nbits, 5));
    try std.testing.expectEqual(@as(usize, 9), findNextAndBit(&and_lhs, &and_rhs, nbits, 2));
    try std.testing.expectEqual(@as(usize, 12), findNextAndBit(&and_lhs, &and_rhs, nbits, 10));
    try std.testing.expectEqual(@as(usize, 9), findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 2));
    try std.testing.expectEqual(nbits, findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 10));
    try std.testing.expectEqual(nbits, findNextBit(&set_bits, nbits, nbits));
    try std.testing.expectEqual(nbits, findNextZeroBit(&zero_bits, nbits, nbits));
    try std.testing.expectEqual(nbits, findNextAndBit(&and_lhs, &and_rhs, nbits, nbits));
    try std.testing.expectEqual(nbits, findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, nbits));
}

test "single-word first scans clamp to the declared bit window" {
    const nbits = 11;
    const in_range_set = [_]Word{(@as(Word, 1) << 2) | (@as(Word, 1) << 13)};
    const out_of_range_set = [_]Word{@as(Word, 1) << 13};
    const in_range_zero = [_]Word{lastWordMask(nbits) & ~(@as(Word, 1) << 5)};
    const out_of_range_zero = [_]Word{lastWordMask(nbits)};
    const in_range_and_lhs = [_]Word{(@as(Word, 1) << 4) | (@as(Word, 1) << 13)};
    const in_range_and_rhs = [_]Word{(@as(Word, 1) << 4) | (@as(Word, 1) << 13)};
    const out_of_range_and = [_]Word{@as(Word, 1) << 13};
    const in_range_andnot_lhs = [_]Word{(@as(Word, 1) << 6) | (@as(Word, 1) << 13)};
    const in_range_andnot_rhs = [_]Word{@as(Word, 1) << 13};
    const out_of_range_andnot_lhs = [_]Word{@as(Word, 1) << 13};
    const out_of_range_andnot_rhs = [_]Word{0};

    try std.testing.expectEqual(@as(usize, 2), findFirstBit(&in_range_set, nbits));
    try std.testing.expectEqual(@as(usize, nbits), findFirstBit(&out_of_range_set, nbits));
    try std.testing.expectEqual(@as(usize, 5), findFirstZeroBit(&in_range_zero, nbits));
    try std.testing.expectEqual(@as(usize, nbits), findFirstZeroBit(&out_of_range_zero, nbits));
    try std.testing.expectEqual(@as(usize, 4), findFirstAndBit(&in_range_and_lhs, &in_range_and_rhs, nbits));
    try std.testing.expectEqual(@as(usize, nbits), findFirstAndBit(&out_of_range_and, &out_of_range_and, nbits));
    try std.testing.expectEqual(@as(usize, 6), findFirstAndNotBit(&in_range_andnot_lhs, &in_range_andnot_rhs, nbits));
    try std.testing.expectEqual(@as(usize, nbits), findFirstAndNotBit(&out_of_range_andnot_lhs, &out_of_range_andnot_rhs, nbits));
}

test "single-word next scans clamp partial windows before returning nbits" {
    const nbits = 11;
    const set_map = [_]Word{(@as(Word, 1) << 4) | (@as(Word, 1) << 13)};
    const zero_map = [_]Word{lastWordMask(nbits) & ~(@as(Word, 1) << 7)};
    const and_lhs = [_]Word{(@as(Word, 1) << 3) | (@as(Word, 1) << 8) | (@as(Word, 1) << 13)};
    const and_rhs = [_]Word{(@as(Word, 1) << 3) | (@as(Word, 1) << 8) | (@as(Word, 1) << 13)};
    const andnot_lhs = [_]Word{(@as(Word, 1) << 2) | (@as(Word, 1) << 8) | (@as(Word, 1) << 13)};
    const andnot_rhs = [_]Word{@as(Word, 1) << 2};

    try std.testing.expectEqual(@as(usize, 4), findNextBit(&set_map, nbits, 4));
    try std.testing.expectEqual(@as(usize, nbits), findNextBit(&set_map, nbits, 5));
    try std.testing.expectEqual(@as(usize, 7), findNextZeroBit(&zero_map, nbits, 7));
    try std.testing.expectEqual(@as(usize, nbits), findNextZeroBit(&zero_map, nbits, 8));
    try std.testing.expectEqual(@as(usize, 8), findNextAndBit(&and_lhs, &and_rhs, nbits, 4));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&and_lhs, &and_rhs, nbits, 9));
    try std.testing.expectEqual(@as(usize, 8), findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 3));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, 9));
}

test "word-boundary next scans start fresh on the next word" {
    const nbits = bits_per_long * 2;
    const boundary = bits_per_long;
    const set_map = [_]Word{
        @as(Word, 1) << @intCast(bits_per_long - 1),
        (@as(Word, 1) << 0) | (@as(Word, 1) << 5),
    };
    const zero_map = [_]Word{
        0,
        ~((@as(Word, 1) << 0) | (@as(Word, 1) << 5)),
    };
    const and_lhs = [_]Word{
        @as(Word, 1) << @intCast(bits_per_long - 1),
        (@as(Word, 1) << 0) | (@as(Word, 1) << 5),
    };
    const and_rhs = and_lhs;

    try std.testing.expectEqual(boundary, findNextBit(&set_map, nbits, boundary));
    try std.testing.expectEqual(boundary + 5, findNextBit(&set_map, nbits, boundary + 1));
    try std.testing.expectEqual(boundary, findNextZeroBit(&zero_map, nbits, boundary));
    try std.testing.expectEqual(boundary + 5, findNextZeroBit(&zero_map, nbits, boundary + 1));
    try std.testing.expectEqual(boundary, findNextAndBit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(boundary + 5, findNextAndBit(&and_lhs, &and_rhs, nbits, boundary + 1));
}

test "zero-bit windows return without reading bitmap words" {
    const empty = [_]Word{};

    try std.testing.expectEqual(@as(usize, 0), findFirstBit(&empty, 0));
    try std.testing.expectEqual(@as(usize, 0), findFirstZeroBit(&empty, 0));
    try std.testing.expectEqual(@as(usize, 0), findFirstAndBit(&empty, &empty, 0));
    try std.testing.expectEqual(@as(usize, 0), findFirstAndNotBit(&empty, &empty, 0));
}

test "zero-sized scans ignore populated backing words" {
    const populated = [_]Word{~@as(Word, 0)};

    try std.testing.expectEqual(@as(usize, 0), findFirstBit(&populated, 0));
    try std.testing.expectEqual(@as(usize, 0), findFirstZeroBit(&populated, 0));
    try std.testing.expectEqual(@as(usize, 0), findFirstAndBit(&populated, &populated, 0));
    try std.testing.expectEqual(@as(usize, 0), findFirstAndNotBit(&populated, &populated, 0));
    try std.testing.expectEqual(@as(usize, 0), findLastBit(&populated, 0));
}

test "next scans past nbits return without reading bitmap words" {
    const empty = [_]Word{};

    try std.testing.expectEqual(@as(usize, 7), findNextBit(&empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), findNextBit(&empty, 7, 11));
    try std.testing.expectEqual(@as(usize, 7), findNextZeroBit(&empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), findNextZeroBit(&empty, 7, 11));
    try std.testing.expectEqual(@as(usize, 7), findNextAndBit(&empty, &empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), findNextAndBit(&empty, &empty, 7, 11));
    try std.testing.expectEqual(@as(usize, 7), findNextAndNotBit(&empty, &empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), findNextAndNotBit(&empty, &empty, 7, 11));
}

test "tail mask ignores set bits beyond nbits" {
    const nbits = bits_per_long + 5;
    var bitmap = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 10) };
    var andnot_lhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const andnot_rhs = [_]Word{ 0, @as(Word, 1) << 9 };

    try std.testing.expectEqual(@as(usize, bits_per_long + 3), findFirstBit(&bitmap, nbits));
    try std.testing.expectEqual(@as(usize, nbits), findNextBit(&bitmap, nbits, bits_per_long + 4));

    bitmap[1] &= ~(@as(Word, 1) << 3);
    try std.testing.expectEqual(@as(usize, nbits), findFirstBit(&bitmap, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long + 4));
    andnot_lhs[1] &= ~(@as(Word, 1) << 3);
    try std.testing.expectEqual(@as(usize, nbits), findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits));
}

test "tail mask ignores zero bits beyond nbits" {
    const nbits = bits_per_long + 5;
    const bitmap = [_]Word{ ~@as(Word, 0), lastWordMask(nbits) };

    try std.testing.expectEqual(@as(usize, nbits), findFirstZeroBit(&bitmap, nbits));
    try std.testing.expectEqual(@as(usize, nbits), findNextZeroBit(&bitmap, nbits, bits_per_long));

    var with_clear = bitmap;
    with_clear[1] &= ~(@as(Word, 1) << 2);
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), findFirstZeroBit(&with_clear, nbits));
}

test "tail mask ignores shared bits beyond nbits" {
    const nbits = bits_per_long + 5;
    var lhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };

    try std.testing.expectEqual(@as(usize, bits_per_long + 3), findFirstAndBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 3));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 4));

    lhs[1] &= ~(@as(Word, 1) << 3);
    try std.testing.expectEqual(@as(usize, nbits), findFirstAndBit(&lhs, &rhs, nbits));
}

test "tail-word next set scans skip earlier in-range matches before clamping" {
    const nbits = bits_per_long + 6;
    const tail_map = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const tail_andnot_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const tail_andnot_rhs = [_]Word{ 0, @as(Word, 1) << 1 };

    try std.testing.expectEqual(@as(usize, bits_per_long + 1), findNextBit(&tail_map, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextBit(&tail_map, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), findNextBit(&tail_map, nbits, bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 5));
}

test "clump8 scans align to the containing byte and return its value" {
    const nbits = bits_per_long * 2;
    var bitmap = [_]Word{ 0, 0 };
    bitmap[0] |= @as(Word, 1) << 9;
    bitmap[0] |= @as(Word, 1) << 14;
    bitmap[1] |= @as(Word, 1) << 8;

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 8), findFirstClump8(&clump, &bitmap, nbits));
    try std.testing.expectEqual(@as(u8, 0b0100_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, 8), findNextClump8(&clump, &bitmap, nbits, 10));
    try std.testing.expectEqual(@as(u8, 0b0100_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long + 8), findNextClump8(&clump, &bitmap, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_0001), clump);
}

test "clump8 scans keep tail bytes reachable from partial final words" {
    const nbits = bits_per_long + 5;
    const bitmap = [_]Word{ 0, @as(Word, 1) << 3 };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long), findFirstClump8(&clump, &bitmap, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);
}

test "clump8 scans leave the caller byte untouched when no set bit remains" {
    const empty = [_]Word{0};
    var clump: u8 = 0xaa;

    try std.testing.expectEqual(@as(usize, 8), findFirstClump8(&clump, &empty, 8));
    try std.testing.expectEqual(@as(u8, 0xaa), clump);

    try std.testing.expectEqual(@as(usize, 8), findNextClump8(&clump, &empty, 8, 4));
    try std.testing.expectEqual(@as(u8, 0xaa), clump);
}

test "getValue8 reads aligned bytes from bitmap words" {
    const bitmap = [_]Word{
        (@as(Word, 0x42) << 8) | (@as(Word, 0xa5) << 24),
        @as(Word, 0x11) << 8,
    };

    try std.testing.expectEqual(@as(u8, 0x42), getValue8(&bitmap, 8));
    try std.testing.expectEqual(@as(u8, 0xa5), getValue8(&bitmap, 24));
    try std.testing.expectEqual(@as(u8, 0x11), getValue8(&bitmap, bits_per_long + 8));
}

test "head-word boundary scans keep the last in-range bit reachable from an inclusive start" {
    const boundary = bits_per_long - 1;
    const nbits = bits_per_long * 2;
    const set_map = [_]Word{ (@as(Word, 1) << @intCast(boundary)), 0 };
    const and_lhs = [_]Word{ (@as(Word, 1) << @intCast(boundary)), 0 };
    const and_rhs = [_]Word{ (@as(Word, 1) << @intCast(boundary)), 0 };
    const zero_map = [_]Word{ ~(@as(Word, 1) << @intCast(boundary)), ~@as(Word, 0) };

    try std.testing.expectEqual(@as(usize, boundary), findNextBit(&set_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), findNextAndBit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), findNextZeroBit(&zero_map, nbits, boundary));
}

test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start" {
    const tail_bits: usize = 5;
    const boundary = bits_per_long + tail_bits - 1;
    const nbits = boundary + 1;
    const set_map = [_]Word{ 0, (@as(Word, 1) << @intCast(tail_bits - 1)) | (@as(Word, 1) << @intCast(tail_bits + 2)) };
    const and_lhs = [_]Word{ 0, (@as(Word, 1) << @intCast(tail_bits - 1)) | (@as(Word, 1) << @intCast(tail_bits + 2)) };
    const and_rhs = [_]Word{ 0, (@as(Word, 1) << @intCast(tail_bits - 1)) | (@as(Word, 1) << @intCast(tail_bits + 2)) };
    const zero_map = [_]Word{ ~@as(Word, 0), lastWordMask(nbits) & ~(@as(Word, 1) << @intCast(tail_bits - 1)) };

    try std.testing.expectEqual(@as(usize, boundary), findNextBit(&set_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), findNextAndBit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), findNextZeroBit(&zero_map, nbits, boundary));
}

test "find last bit scans backward across words" {
    const nbits = bits_per_long * 3;
    var bitmap = [_]Word{ 0, 0, 0 };
    bitmap[0] |= @as(Word, 1) << 5;
    bitmap[1] |= @as(Word, 1) << 3;
    bitmap[2] |= @as(Word, 1) << 7;

    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 7), findLastBit(&bitmap, nbits));
    bitmap[2] = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), findLastBit(&bitmap, nbits));
}

test "find last bit ignores storage beyond an exact word boundary" {
    const nbits = bits_per_long;
    const boundary = bits_per_long - 1;
    var bitmap = [_]Word{
        @as(Word, 1) << @intCast(boundary),
        @as(Word, 1) << 5,
    };

    try std.testing.expectEqual(@as(usize, boundary), findLastBit(&bitmap, nbits));

    bitmap[0] = 0;
    try std.testing.expectEqual(@as(usize, nbits), findLastBit(&bitmap, nbits));
}

test "find last bit clamps tail words to nbits" {
    const nbits = bits_per_long + 5;
    var bitmap = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 10) };

    try std.testing.expectEqual(@as(usize, bits_per_long + 3), findLastBit(&bitmap, nbits));
    bitmap[1] &= ~(@as(Word, 1) << 3);
    try std.testing.expectEqual(@as(usize, nbits), findLastBit(&bitmap, nbits));

    const single_word_nbits = 11;
    var single_word = [_]Word{(@as(Word, 1) << 4) | (@as(Word, 1) << 13)};
    try std.testing.expectEqual(@as(usize, 4), findLastBit(&single_word, single_word_nbits));
    single_word[0] &= ~(@as(Word, 1) << 4);
    try std.testing.expectEqual(@as(usize, single_word_nbits), findLastBit(&single_word, single_word_nbits));
}

test "find last bit returns nbits when no set bits remain" {
    const nbits = bits_per_long * 2;
    const bitmap = [_]Word{ 0, 0 };
    const empty = [_]Word{};

    try std.testing.expectEqual(@as(usize, nbits), findLastBit(&bitmap, nbits));
    try std.testing.expectEqual(@as(usize, 0), findLastBit(&empty, 0));
}

test "tail-word next zero and shared scans skip earlier in-range matches before clamping" {
    const nbits = bits_per_long + 6;
    const tail_zero_map = [_]Word{
        ~@as(Word, 0),
        lastWordMask(nbits) & ~((@as(Word, 1) << 1) | (@as(Word, 1) << 4)),
    };
    const tail_and_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const tail_and_rhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };

    try std.testing.expectEqual(@as(usize, bits_per_long + 1), findNextZeroBit(&tail_zero_map, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextZeroBit(&tail_zero_map, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), findNextZeroBit(&tail_zero_map, nbits, bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, bits_per_long + 1), findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&tail_and_lhs, &tail_and_rhs, nbits, bits_per_long + 5));
}

test "low-level underscore aliases mirror the primary find helpers" {
    const nbits = bits_per_long + 5;
    const bitmap = [_]Word{ (@as(Word, 1) << 7), (@as(Word, 1) << 3) | (@as(Word, 1) << 10) };
    const zero_map = [_]Word{ ~(@as(Word, 1) << 4), lastWordMask(nbits) };
    const and_lhs = [_]Word{ (@as(Word, 1) << 5), (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const and_rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const andnot_lhs = [_]Word{ (@as(Word, 1) << 5), (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const andnot_rhs = [_]Word{ @as(Word, 1) << 5, @as(Word, 1) << 9 };
    const clump_map = [_]Word{@as(Word, 1)};

    try std.testing.expectEqual(findFirstBit(&bitmap, nbits), _find_first_bit(&bitmap, nbits));
    try std.testing.expectEqual(findFirstAndBit(&and_lhs, &and_rhs, nbits), _find_first_and_bit(&and_lhs, &and_rhs, nbits));
    try std.testing.expectEqual(findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits), _find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits));
    try std.testing.expectEqual(findFirstZeroBit(&zero_map, nbits), _find_first_zero_bit(&zero_map, nbits));
    try std.testing.expectEqual(findNextBit(&bitmap, nbits, 8), _find_next_bit(&bitmap, nbits, 8));
    try std.testing.expectEqual(findNextAndBit(&and_lhs, &and_rhs, nbits, bits_per_long), _find_next_and_bit(&and_lhs, &and_rhs, nbits, bits_per_long));
    try std.testing.expectEqual(findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long), _find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long));
    try std.testing.expectEqual(findNextZeroBit(&zero_map, nbits, 5), _find_next_zero_bit(&zero_map, nbits, 5));
    try std.testing.expectEqual(findLastBit(&bitmap, nbits), _find_last_bit(&bitmap, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), _find_first_clump8(&clump, &clump_map, 8));
    try std.testing.expectEqual(@as(u8, 0b0000_0001), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, 0), _find_next_clump8(&clump, &clump_map, 8, 0));
    try std.testing.expectEqual(@as(u8, 0b0000_0001), clump);
}

test "Linux-style aliases mirror the primary find helpers" {
    const nbits = bits_per_long + 5;
    const bitmap = [_]Word{ (@as(Word, 1) << 7), (@as(Word, 1) << 3) | (@as(Word, 1) << 10) };
    const zero_map = [_]Word{ ~(@as(Word, 1) << 4), lastWordMask(nbits) };
    const and_lhs = [_]Word{ (@as(Word, 1) << 5), (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const and_rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const andnot_lhs = [_]Word{ (@as(Word, 1) << 5), (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const andnot_rhs = [_]Word{ @as(Word, 1) << 5, @as(Word, 1) << 9 };

    try std.testing.expectEqual(findFirstBit(&bitmap, nbits), find_first_bit(&bitmap, nbits));
    try std.testing.expectEqual(findFirstAndBit(&and_lhs, &and_rhs, nbits), find_first_and_bit(&and_lhs, &and_rhs, nbits));
    try std.testing.expectEqual(findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits), find_first_andnot_bit(&andnot_lhs, &andnot_rhs, nbits));
    try std.testing.expectEqual(findFirstZeroBit(&zero_map, nbits), find_first_zero_bit(&zero_map, nbits));
    try std.testing.expectEqual(findNextBit(&bitmap, nbits, 8), find_next_bit(&bitmap, nbits, 8));
    try std.testing.expectEqual(findNextAndBit(&and_lhs, &and_rhs, nbits, bits_per_long), find_next_and_bit(&and_lhs, &and_rhs, nbits, bits_per_long));
    try std.testing.expectEqual(findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long), find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long));
    try std.testing.expectEqual(findNextZeroBit(&zero_map, nbits, 5), find_next_zero_bit(&zero_map, nbits, 5));
    try std.testing.expectEqual(findLastBit(&bitmap, nbits), find_last_bit(&bitmap, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_first_clump8(&clump, &[_]Word{@as(Word, 1)}, 8));
    try std.testing.expectEqual(@as(u8, 0b0000_0001), clump);
    try std.testing.expectEqual(@as(usize, 0), find_next_clump8(&clump, &[_]Word{@as(Word, 1)}, 8, 0));
    try std.testing.expectEqual(@as(u8, 0b0000_0001), clump);
}
