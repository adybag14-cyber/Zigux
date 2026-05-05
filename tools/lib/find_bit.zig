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

pub fn findFirstBit(addr: []const Word, nbits: usize) usize {
    assertBitmapLen(addr, nbits);

    var idx: usize = 0;
    while (idx * bits_per_long < nbits) : (idx += 1) {
        const value = maskWordInRange(idx, addr[idx], nbits);
        if (value != 0) {
            return bitIndex(idx, value, nbits);
        }
    }

    return nbits;
}

pub fn findFirstAndBit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {
    assertBitmapLen(addr1, nbits);
    assertBitmapLen(addr2, nbits);

    var idx: usize = 0;
    while (idx * bits_per_long < nbits) : (idx += 1) {
        const value = maskWordInRange(idx, addr1[idx] & addr2[idx], nbits);
        if (value != 0) {
            return bitIndex(idx, value, nbits);
        }
    }

    return nbits;
}

pub fn findFirstZeroBit(addr: []const Word, nbits: usize) usize {
    assertBitmapLen(addr, nbits);

    var idx: usize = 0;
    while (idx * bits_per_long < nbits) : (idx += 1) {
        const value = maskWordInRange(idx, ~addr[idx], nbits);
        if (value != 0) {
            return bitIndex(idx, value, nbits);
        }
    }

    return nbits;
}

pub fn findNextBit(addr: []const Word, nbits: usize, start: usize) usize {
    if (start >= nbits) {
        return nbits;
    }

    assertBitmapLen(addr, nbits);

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

pub fn findNextAndBit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    if (start >= nbits) {
        return nbits;
    }

    assertBitmapLen(addr1, nbits);
    assertBitmapLen(addr2, nbits);

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

pub fn findNextZeroBit(addr: []const Word, nbits: usize, start: usize) usize {
    if (start >= nbits) {
        return nbits;
    }

    assertBitmapLen(addr, nbits);

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

test "find first and next set bits across words" {
    var bitmap = [_]Word{ 0, 0, 0 };
    bitmap[0] |= @as(Word, 1) << 5;
    bitmap[1] |= @as(Word, 1) << 3;
    bitmap[2] |= @as(Word, 1) << 7;

    try std.testing.expectEqual(@as(usize, 5), findFirstBit(&bitmap, bits_per_long * 3));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), findNextBit(&bitmap, bits_per_long * 3, 6));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 7), findNextBit(&bitmap, bits_per_long * 3, bits_per_long + 4));
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

test "single-word next scans honor start masks" {
    const nbits = bits_per_long;
    const set_bits = [_]Word{(@as(Word, 1) << 2) | (@as(Word, 1) << 7) | (@as(Word, 1) << 11)};
    const zero_bits = [_]Word{~((@as(Word, 1) << 4) | (@as(Word, 1) << 9))};
    const and_lhs = [_]Word{(@as(Word, 1) << 1) | (@as(Word, 1) << 9) | (@as(Word, 1) << 12)};
    const and_rhs = [_]Word{(@as(Word, 1) << 0) | (@as(Word, 1) << 9) | (@as(Word, 1) << 12)};

    try std.testing.expectEqual(@as(usize, 7), findNextBit(&set_bits, nbits, 3));
    try std.testing.expectEqual(@as(usize, 11), findNextBit(&set_bits, nbits, 8));
    try std.testing.expectEqual(@as(usize, 4), findNextZeroBit(&zero_bits, nbits, 1));
    try std.testing.expectEqual(@as(usize, 9), findNextZeroBit(&zero_bits, nbits, 5));
    try std.testing.expectEqual(@as(usize, 9), findNextAndBit(&and_lhs, &and_rhs, nbits, 2));
    try std.testing.expectEqual(@as(usize, 12), findNextAndBit(&and_lhs, &and_rhs, nbits, 10));
    try std.testing.expectEqual(nbits, findNextBit(&set_bits, nbits, nbits));
    try std.testing.expectEqual(nbits, findNextZeroBit(&zero_bits, nbits, nbits));
    try std.testing.expectEqual(nbits, findNextAndBit(&and_lhs, &and_rhs, nbits, nbits));
}

test "next scans past nbits return without reading bitmap words" {
    const empty = [_]Word{};

    try std.testing.expectEqual(@as(usize, 7), findNextBit(&empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), findNextBit(&empty, 7, 11));
    try std.testing.expectEqual(@as(usize, 7), findNextZeroBit(&empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), findNextZeroBit(&empty, 7, 11));
    try std.testing.expectEqual(@as(usize, 7), findNextAndBit(&empty, &empty, 7, 7));
    try std.testing.expectEqual(@as(usize, 7), findNextAndBit(&empty, &empty, 7, 11));
}

test "tail mask ignores set bits beyond nbits" {
    const nbits = bits_per_long + 5;
    var bitmap = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 10) };

    try std.testing.expectEqual(@as(usize, bits_per_long + 3), findFirstBit(&bitmap, nbits));
    try std.testing.expectEqual(@as(usize, nbits), findNextBit(&bitmap, nbits, bits_per_long + 4));

    bitmap[1] &= ~(@as(Word, 1) << 3);
    try std.testing.expectEqual(@as(usize, nbits), findFirstBit(&bitmap, nbits));
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

test "find next and bit masks earlier and out-of-range tail matches" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0, (@as(Word, 1) << 2) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 2) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };

    try std.testing.expectEqual(@as(usize, bits_per_long + 2), findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 3));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 5));
}
