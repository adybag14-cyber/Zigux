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

fn bitIndex(idx: usize, value: Word, nbits: usize) usize {
    const bit = idx * bits_per_long + @as(usize, @intCast(@ctz(value)));
    return if (bit < nbits) bit else nbits;
}

pub fn findFirstBit(addr: []const Word, nbits: usize) usize {
    assertBitmapLen(addr, nbits);

    var idx: usize = 0;
    while (idx * bits_per_long < nbits) : (idx += 1) {
        const value = addr[idx];
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
        const value = addr1[idx] & addr2[idx];
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
        const value = ~addr[idx];
        if (value != 0) {
            return bitIndex(idx, value, nbits);
        }
    }

    return nbits;
}

pub fn findNextBit(addr: []const Word, nbits: usize, start: usize) usize {
    assertBitmapLen(addr, nbits);
    if (start >= nbits) {
        return nbits;
    }

    var idx = start / bits_per_long;
    var value = addr[idx] & firstWordMask(start);

    while (value == 0) {
        idx += 1;
        if (idx * bits_per_long >= nbits) {
            return nbits;
        }
        value = addr[idx];
    }

    return bitIndex(idx, value, nbits);
}

pub fn findNextAndBit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    assertBitmapLen(addr1, nbits);
    assertBitmapLen(addr2, nbits);
    if (start >= nbits) {
        return nbits;
    }

    var idx = start / bits_per_long;
    var value = (addr1[idx] & addr2[idx]) & firstWordMask(start);

    while (value == 0) {
        idx += 1;
        if (idx * bits_per_long >= nbits) {
            return nbits;
        }
        value = addr1[idx] & addr2[idx];
    }

    return bitIndex(idx, value, nbits);
}

pub fn findNextZeroBit(addr: []const Word, nbits: usize, start: usize) usize {
    assertBitmapLen(addr, nbits);
    if (start >= nbits) {
        return nbits;
    }

    var idx = start / bits_per_long;
    var value = ~addr[idx] & firstWordMask(start);

    while (value == 0) {
        idx += 1;
        if (idx * bits_per_long >= nbits) {
            return nbits;
        }
        value = ~addr[idx];
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
    try std.testing.expectEqual(@as(usize, 11), findFirstZeroBit(&[_]Word{0b1111_0111}, 12));
}

test "find and bit returns the first shared set bit" {
    const lhs = [_]Word{ (@as(Word, 1) << 1) | (@as(Word, 1) << 9), @as(Word, 1) << 2 };
    const rhs = [_]Word{ (@as(Word, 1) << 9), @as(Word, 1) << 2 };

    try std.testing.expectEqual(@as(usize, 9), findFirstAndBit(&lhs, &rhs, bits_per_long * 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), findNextAndBit(&lhs, &rhs, bits_per_long * 2, 10));
}
