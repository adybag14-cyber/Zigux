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

pub fn findNextOrBit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    if (start >= nbits) {
        return nbits;
    }

    assertBitmapLen(addr1, nbits);
    assertBitmapLen(addr2, nbits);

    if (nbits <= bits_per_long) {
        return singleWordBitIndex(addr1[0] | addr2[0], nbits, start);
    }

    var idx = start / bits_per_long;
    var value = maskWordInRange(idx, addr1[idx] | addr2[idx], nbits) & firstWordMask(start);

    while (value == 0) {
        idx += 1;
        if (idx * bits_per_long >= nbits) {
            return nbits;
        }
        value = maskWordInRange(idx, addr1[idx] | addr2[idx], nbits);
    }

    return bitIndex(idx, value, nbits);
}

pub fn find_next_or_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    return findNextOrBit(addr1, addr2, nbits, start);
}

pub fn _find_next_or_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    return findNextOrBit(addr1, addr2, nbits, start);
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

    const value = addr[idx] >> @intCast(shift);
    return @as(u8, @intCast(value & 0xff));
}

fn clumpMask(nbits: usize, offset: usize) u8 {
    if (offset >= nbits) {
        return 0;
    }

    const remaining = nbits - offset;
    if (remaining >= 8) {
        return 0xff;
    }

    return @as(u8, @intCast((@as(Word, 1) << @intCast(remaining)) - 1));
}

pub fn findNextClump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {
    if (offset >= nbits) {
        return nbits;
    }

    const next = findNextBit(addr, nbits, offset);
    if (next == nbits) {
        return nbits;
    }

    const clump_offset = next & ~@as(usize, 7);
    clump.* = getValue8(addr, clump_offset) & clumpMask(nbits, clump_offset);
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
        idx += 1;