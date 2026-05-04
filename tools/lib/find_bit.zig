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

fn maskTailWord(idx: usize, value: Word, last_idx: usize, last_mask: Word) Word {
    return if (idx == last_idx) value & last_mask else value;
}

fn bitIndex(idx: usize, value: Word, nbits: usize) usize {
    const bit = idx * bits_per_long + @as(usize, @intCast(@ctz(value)));
    return if (bit < nbits) bit else nbits;
}

const ScanKind = enum {
    set,
    and_bits,
    zero,
};

fn scanWord(comptime kind: ScanKind, idx: usize, addr1: []const Word, addr2: ?[]const Word) Word {
    return switch (kind) {
        .set => addr1[idx],
        .and_bits => addr1[idx] & addr2.?[idx],
        .zero => ~addr1[idx],
    };
}

fn smallBitmapMask(nbits: usize, start: usize) Word {
    if (start >= nbits) {
        return 0;
    }
    return lastWordMask(nbits) & firstWordMask(start);
}

fn findFirstImpl(comptime kind: ScanKind, addr1: []const Word, addr2: ?[]const Word, nbits: usize) usize {
    assertBitmapLen(addr1, nbits);
    if (kind == .and_bits) {
        assertBitmapLen(addr2.?, nbits);
    }
    if (nbits == 0) {
        return 0;
    }
    if (nbits <= bits_per_long) {
        const value = scanWord(kind, 0, addr1, addr2) & lastWordMask(nbits);
        return if (value != 0) @as(usize, @intCast(@ctz(value))) else nbits;
    }

    const last_idx = bitsToWords(nbits) - 1;
    const last_mask = lastWordMask(nbits);

    var idx: usize = 0;
    while (idx * bits_per_long < nbits) : (idx += 1) {
        const value = maskTailWord(idx, scanWord(kind, idx, addr1, addr2), last_idx, last_mask);
        if (value != 0) {
            return bitIndex(idx, value, nbits);
        }
    }

    return nbits;
}

fn findNextImpl(comptime kind: ScanKind, addr1: []const Word, addr2: ?[]const Word, nbits: usize, start: usize) usize {
    assertBitmapLen(addr1, nbits);
    if (kind == .and_bits) {
        assertBitmapLen(addr2.?, nbits);
    }
    if (start >= nbits) {
        return nbits;
    }
    if (nbits <= bits_per_long) {
        const value = scanWord(kind, 0, addr1, addr2) & smallBitmapMask(nbits, start);
        return if (value != 0) @as(usize, @intCast(@ctz(value))) else nbits;
    }

    const last_idx = bitsToWords(nbits) - 1;
    const last_mask = lastWordMask(nbits);

    var idx = start / bits_per_long;
    var value = maskTailWord(idx, scanWord(kind, idx, addr1, addr2), last_idx, last_mask) & firstWordMask(start);

    while (value == 0) {
        idx += 1;
        if (idx * bits_per_long >= nbits) {
            return nbits;
        }
        value = maskTailWord(idx, scanWord(kind, idx, addr1, addr2), last_idx, last_mask);
    }

    return bitIndex(idx, value, nbits);
}

pub fn findFirstBit(addr: []const Word, nbits: usize) usize {
    return findFirstImpl(.set, addr, null, nbits);
}

pub fn findFirstAndBit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {
    return findFirstImpl(.and_bits, addr1, addr2, nbits);
}

pub fn findFirstZeroBit(addr: []const Word, nbits: usize) usize {
    return findFirstImpl(.zero, addr, null, nbits);
}

pub fn findNextBit(addr: []const Word, nbits: usize, start: usize) usize {
    return findNextImpl(.set, addr, null, nbits, start);
}

pub fn findNextAndBit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    return findNextImpl(.and_bits, addr1, addr2, nbits, start);
}

pub fn findNextZeroBit(addr: []const Word, nbits: usize, start: usize) usize {
    return findNextImpl(.zero, addr, null, nbits, start);
}

pub fn find_first_bit(addr: []const Word, nbits: usize) usize {
    return findFirstBit(addr, nbits);
}

pub fn find_first_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {
    return findFirstAndBit(addr1, addr2, nbits);
}

pub fn find_first_zero_bit(addr: []const Word, nbits: usize) usize {
    return findFirstZeroBit(addr, nbits);
}

pub fn find_next_bit(addr: []const Word, nbits: usize, start: usize) usize {
    return findNextBit(addr, nbits, start);
}

pub fn find_next_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    return findNextAndBit(addr1, addr2, nbits, start);
}

pub fn find_next_zero_bit(addr: []const Word, nbits: usize, start: usize) usize {
    return findNextZeroBit(addr, nbits, start);
}

pub fn _find_first_bit(addr: []const Word, nbits: usize) usize {
    return findFirstBit(addr, nbits);
}

pub fn _find_first_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {
    return findFirstAndBit(addr1, addr2, nbits);
}

pub fn _find_first_zero_bit(addr: []const Word, nbits: usize) usize {
    return findFirstZeroBit(addr, nbits);
}

pub fn _find_next_bit(addr: []const Word, nbits: usize, start: usize) usize {
    return findNextBit(addr, nbits, start);
}

pub fn _find_next_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {
    return findNextAndBit(addr1, addr2, nbits, start);
}

pub fn _find_next_zero_bit(addr: []const Word, nbits: usize, start: usize) usize {
    return findNextZeroBit(addr, nbits, start);
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

test "find next bit skips earlier matches in the same word" {
    const nbits = bits_per_long + 6;
    var bitmap = [_]Word{ 0, 0 };
    bitmap[0] |= @as(Word, 1) << 1;
    bitmap[0] |= @as(Word, 1) << 6;
    bitmap[1] |= @as(Word, 1) << 4;

    try std.testing.expectEqual(@as(usize, 1), findNextBit(&bitmap, nbits, 1));
    try std.testing.expectEqual(@as(usize, 6), findNextBit(&bitmap, nbits, 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextBit(&bitmap, nbits, 7));
    try std.testing.expectEqual(@as(usize, nbits), findNextBit(&bitmap, nbits, bits_per_long + 5));
}

test "find next and bit skips earlier shared matches in the same word" {
    const nbits = bits_per_long + 6;
    const lhs = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << 6),
        @as(Word, 1) << 4,
    };
    const rhs = [_]Word{
        (@as(Word, 1) << 6) | (@as(Word, 1) << 9),
        @as(Word, 1) << 4,
    };

    try std.testing.expectEqual(@as(usize, 6), findNextAndBit(&lhs, &rhs, nbits, 2));
    try std.testing.expectEqual(@as(usize, 6), findNextAndBit(&lhs, &rhs, nbits, 6));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndBit(&lhs, &rhs, nbits, 7));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 5));
}

test "find zero bits respects the declared bit count" {
    var bitmap = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    bitmap[1] &= ~(@as(Word, 1) << 4);

    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findFirstZeroBit(&bitmap, bits_per_long * 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextZeroBit(&bitmap, bits_per_long * 2, bits_per_long));
    try std.testing.expectEqual(@as(usize, 3), findFirstZeroBit(&[_]Word{0b1111_0111}, 12));
}

test "find next zero bit skips earlier matches in the same word" {
    const nbits = bits_per_long + 6;
    var bitmap = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    bitmap[0] &= ~(@as(Word, 1) << 1);
    bitmap[0] &= ~(@as(Word, 1) << 6);
    bitmap[1] &= ~(@as(Word, 1) << 4);

    try std.testing.expectEqual(@as(usize, 1), findNextZeroBit(&bitmap, nbits, 1));
    try std.testing.expectEqual(@as(usize, 6), findNextZeroBit(&bitmap, nbits, 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextZeroBit(&bitmap, nbits, 7));
    try std.testing.expectEqual(@as(usize, nbits), findNextZeroBit(&bitmap, nbits, bits_per_long + 5));
}

test "find and bit returns the first shared set bit" {
    const lhs = [_]Word{ (@as(Word, 1) << 1) | (@as(Word, 1) << 9), @as(Word, 1) << 2 };
    const rhs = [_]Word{ (@as(Word, 1) << 9), @as(Word, 1) << 2 };

    try std.testing.expectEqual(@as(usize, 9), findFirstAndBit(&lhs, &rhs, bits_per_long * 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), findNextAndBit(&lhs, &rhs, bits_per_long * 2, 10));
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

test "find next zero bit masks earlier and out-of-range tail matches" {
    const nbits = bits_per_long + 5;
    var bitmap = [_]Word{ ~@as(Word, 0), lastWordMask(nbits) };
    bitmap[1] &= ~(@as(Word, 1) << 1);
    bitmap[1] &= ~(@as(Word, 1) << 4);

    try std.testing.expectEqual(@as(usize, bits_per_long + 1), findNextZeroBit(&bitmap, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextZeroBit(&bitmap, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextZeroBit(&bitmap, nbits, bits_per_long + 4));
    try std.testing.expectEqual(@as(usize, nbits), findNextZeroBit(&bitmap, nbits, bits_per_long + 5));
}

test "find next and bit masks earlier and out-of-range tail matches" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 12) };

    try std.testing.expectEqual(@as(usize, bits_per_long + 1), findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 4));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 5));
}

test "tail scans honor an exact tail-word boundary start" {
    const nbits = bits_per_long + 5;
    const tail_start = bits_per_long;

    const set_bits = [_]Word{
        @as(Word, 1) << 7,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9),
    };
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), findNextBit(&set_bits, nbits, tail_start));

    var zero_bits = [_]Word{ ~@as(Word, 0), lastWordMask(nbits) };
    zero_bits[0] &= ~(@as(Word, 1) << 7);
    zero_bits[1] &= ~(@as(Word, 1) << 1);
    zero_bits[1] &= ~(@as(Word, 1) << 4);
    zero_bits[1] &= ~(@as(Word, 1) << 9);
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), findNextZeroBit(&zero_bits, nbits, tail_start));

    const lhs = [_]Word{
        @as(Word, 1) << 7,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9),
    };
    const rhs = [_]Word{
        @as(Word, 1) << 7,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 12),
    };
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), findNextAndBit(&lhs, &rhs, nbits, tail_start));
}

test "tail mask keeps the in-range shared bit for and scans" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 12) };

    try std.testing.expectEqual(@as(usize, bits_per_long + 3), findFirstAndBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), findNextAndBit(&lhs, &rhs, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 3), findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 4));
}

test "tail scans keep the last in-range bit reachable from an inclusive start" {
    const nbits = bits_per_long + 5;
    const tail_bit = bits_per_long + 4;

    const set_bits = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    try std.testing.expectEqual(@as(usize, tail_bit), findNextBit(&set_bits, nbits, tail_bit));
    try std.testing.expectEqual(@as(usize, nbits), findNextBit(&set_bits, nbits, tail_bit + 1));

    var zero_bits = [_]Word{ ~@as(Word, 0), lastWordMask(nbits) };
    zero_bits[1] &= ~(@as(Word, 1) << 4);
    zero_bits[1] &= ~(@as(Word, 1) << 9);
    try std.testing.expectEqual(@as(usize, tail_bit), findNextZeroBit(&zero_bits, nbits, tail_bit));
    try std.testing.expectEqual(@as(usize, nbits), findNextZeroBit(&zero_bits, nbits, tail_bit + 1));

    const lhs = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 10) };
    try std.testing.expectEqual(@as(usize, tail_bit), findNextAndBit(&lhs, &rhs, nbits, tail_bit));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&lhs, &rhs, nbits, tail_bit + 1));
}

test "single-word scans keep linux small-bitmap semantics" {
    const nbits: usize = 12;

    const set_bits = [_]Word{(@as(Word, 1) << 3) | (@as(Word, 1) << 9) | (@as(Word, 1) << 15)};
    try std.testing.expectEqual(@as(usize, 3), findFirstBit(&set_bits, nbits));
    try std.testing.expectEqual(@as(usize, 9), findNextBit(&set_bits, nbits, 4));
    try std.testing.expectEqual(@as(usize, 9), findNextBit(&set_bits, nbits, 9));
    try std.testing.expectEqual(@as(usize, nbits), findNextBit(&set_bits, nbits, 10));

    const zero_bits = [_]Word{(~@as(Word, 0) & ~(@as(Word, 1) << 2) & ~(@as(Word, 1) << 8)) & ~(@as(Word, 1) << 14)};
    try std.testing.expectEqual(@as(usize, 2), findFirstZeroBit(&zero_bits, nbits));
    try std.testing.expectEqual(@as(usize, 8), findNextZeroBit(&zero_bits, nbits, 3));
    try std.testing.expectEqual(@as(usize, 8), findNextZeroBit(&zero_bits, nbits, 8));
    try std.testing.expectEqual(@as(usize, nbits), findNextZeroBit(&zero_bits, nbits, 9));

    const lhs = [_]Word{(@as(Word, 1) << 4) | (@as(Word, 1) << 9) | (@as(Word, 1) << 15)};
    const rhs = [_]Word{(@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9)};
    try std.testing.expectEqual(@as(usize, 4), findFirstAndBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 9), findNextAndBit(&lhs, &rhs, nbits, 5));
    try std.testing.expectEqual(@as(usize, 9), findNextAndBit(&lhs, &rhs, nbits, 9));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&lhs, &rhs, nbits, 10));
}

test "single-word next scans stay inclusive from bit zero" {
    const nbits: usize = 12;

    const set_bits = [_]Word{(@as(Word, 1) << 3) | (@as(Word, 1) << 9) | (@as(Word, 1) << 15)};
    try std.testing.expectEqual(@as(usize, 3), findNextBit(&set_bits, nbits, 0));

    const zero_bits = [_]Word{(~@as(Word, 0) & ~(@as(Word, 1) << 2) & ~(@as(Word, 1) << 8)) & ~(@as(Word, 1) << 14)};
    try std.testing.expectEqual(@as(usize, 2), findNextZeroBit(&zero_bits, nbits, 0));

    const lhs = [_]Word{(@as(Word, 1) << 4) | (@as(Word, 1) << 9) | (@as(Word, 1) << 15)};
    const rhs = [_]Word{(@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9)};
    try std.testing.expectEqual(@as(usize, 4), findNextAndBit(&lhs, &rhs, nbits, 0));
}

test "small bitmap mask keeps in-range bits and clears exhausted starts" {
    const nbits: usize = 12;
    const tail_bit: usize = nbits - 1;

    try std.testing.expectEqual(lastWordMask(nbits), smallBitmapMask(nbits, 0));
    try std.testing.expectEqual(lastWordMask(nbits) & firstWordMask(3), smallBitmapMask(nbits, 3));
    try std.testing.expectEqual(@as(Word, 1) << tail_bit, smallBitmapMask(nbits, tail_bit));
    try std.testing.expectEqual(@as(Word, 0), smallBitmapMask(nbits, nbits));
    try std.testing.expectEqual(@as(Word, 0), smallBitmapMask(0, 0));
    try std.testing.expectEqual(@as(Word, 0), smallBitmapMask(nbits, nbits + 4));
}

test "single-word scans keep the last in-range bit reachable from an inclusive start" {
    const nbits: usize = 12;
    const tail_bit: usize = nbits - 1;
    const out_of_range_bit: usize = 15;

    const set_bits = [_]Word{(@as(Word, 1) << tail_bit) | (@as(Word, 1) << out_of_range_bit)};
    try std.testing.expectEqual(@as(usize, tail_bit), findFirstBit(&set_bits, nbits));
    try std.testing.expectEqual(@as(usize, tail_bit), findNextBit(&set_bits, nbits, tail_bit));
    try std.testing.expectEqual(@as(usize, nbits), findNextBit(&set_bits, nbits, tail_bit + 1));

    const zero_bits = [_]Word{(~@as(Word, 0) & ~(@as(Word, 1) << tail_bit)) & ~(@as(Word, 1) << out_of_range_bit)};
    try std.testing.expectEqual(@as(usize, tail_bit), findFirstZeroBit(&zero_bits, nbits));
    try std.testing.expectEqual(@as(usize, tail_bit), findNextZeroBit(&zero_bits, nbits, tail_bit));
    try std.testing.expectEqual(@as(usize, nbits), findNextZeroBit(&zero_bits, nbits, tail_bit + 1));

    const lhs = [_]Word{(@as(Word, 1) << tail_bit) | (@as(Word, 1) << out_of_range_bit)};
    const rhs = [_]Word{(@as(Word, 1) << tail_bit) | (@as(Word, 1) << out_of_range_bit)};
    try std.testing.expectEqual(@as(usize, tail_bit), findFirstAndBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, tail_bit), findNextAndBit(&lhs, &rhs, nbits, tail_bit));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&lhs, &rhs, nbits, tail_bit + 1));
}

test "single-word scans ignore matches that exist only beyond nbits" {
    const nbits: usize = 12;
    const out_of_range_bit = 15;

    const set_bits = [_]Word{@as(Word, 1) << out_of_range_bit};
    try std.testing.expectEqual(@as(usize, nbits), findFirstBit(&set_bits, nbits));
    try std.testing.expectEqual(@as(usize, nbits), findNextBit(&set_bits, nbits, 0));

    const zero_bits = [_]Word{~@as(Word, 0) & ~(@as(Word, 1) << out_of_range_bit)};
    try std.testing.expectEqual(@as(usize, nbits), findFirstZeroBit(&zero_bits, nbits));
    try std.testing.expectEqual(@as(usize, nbits), findNextZeroBit(&zero_bits, nbits, 0));

    const lhs = [_]Word{@as(Word, 1) << out_of_range_bit};
    const rhs = [_]Word{@as(Word, 1) << out_of_range_bit};
    try std.testing.expectEqual(@as(usize, nbits), findFirstAndBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, nbits), findNextAndBit(&lhs, &rhs, nbits, 0));
}

test "word helpers keep linux-style mask and sizing boundaries" {
    try std.testing.expectEqual(@as(usize, 0), bitsToWords(0));
    try std.testing.expectEqual(@as(usize, 1), bitsToWords(1));
    try std.testing.expectEqual(@as(usize, 1), bitsToWords(bits_per_long));
    try std.testing.expectEqual(@as(usize, 2), bitsToWords(bits_per_long + 1));

    try std.testing.expectEqual(~@as(Word, 0), firstWordMask(0));
    try std.testing.expectEqual((~@as(Word, 0)) << 1, firstWordMask(1));
    try std.testing.expectEqual((~@as(Word, 0)) << 5, firstWordMask(bits_per_long + 5));
    try std.testing.expectEqual(~@as(Word, 0), firstWordMask(bits_per_long));

    try std.testing.expectEqual(@as(Word, 0), lastWordMask(0));
    try std.testing.expectEqual(@as(Word, 1), lastWordMask(1));
    try std.testing.expectEqual((@as(Word, 1) << 5) - 1, lastWordMask(bits_per_long + 5));
    try std.testing.expectEqual(~@as(Word, 0), lastWordMask(bits_per_long));
    try std.testing.expectEqual(~@as(Word, 0), lastWordMask(bits_per_long * 2));
}

test "empty and boundary scans return nbits" {
    const empty = [_]Word{};
    try std.testing.expectEqual(@as(usize, 0), findFirstBit(&empty, 0));
    try std.testing.expectEqual(@as(usize, 0), findFirstAndBit(&empty, &empty, 0));
    try std.testing.expectEqual(@as(usize, 0), findFirstZeroBit(&empty, 0));
    try std.testing.expectEqual(@as(usize, 0), findNextBit(&empty, 0, 0));
    try std.testing.expectEqual(@as(usize, 0), findNextAndBit(&empty, &empty, 0, 0));
    try std.testing.expectEqual(@as(usize, 0), findNextZeroBit(&empty, 0, 0));

    const bitmap = [_]Word{ (@as(Word, 1) << 5) | (@as(Word, 1) << 9), @as(Word, 1) << 2 };
    try std.testing.expectEqual(@as(usize, 5), findNextBit(&bitmap, bits_per_long * 2, 5));
    try std.testing.expectEqual(@as(usize, 9), findNextAndBit(&bitmap, &bitmap, bits_per_long * 2, 9));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2), findNextBit(&bitmap, bits_per_long * 2, bits_per_long * 2));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2), findNextAndBit(&bitmap, &bitmap, bits_per_long * 2, bits_per_long * 2));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2), findNextZeroBit(&[_]Word{ ~@as(Word, 0), ~@as(Word, 0) }, bits_per_long * 2, bits_per_long * 2));
}

test "zero-sized scans ignore populated backing words" {
    const lhs = [_]Word{ (@as(Word, 1) << 5) | (@as(Word, 1) << 17), ~@as(Word, 0) };
    const rhs = [_]Word{ (@as(Word, 1) << 5), @as(Word, 1) << 1 };

    try std.testing.expectEqual(@as(usize, 0), findFirstBit(&lhs, 0));
    try std.testing.expectEqual(@as(usize, 0), findFirstAndBit(&lhs, &rhs, 0));
    try std.testing.expectEqual(@as(usize, 0), findFirstZeroBit(&lhs, 0));
    try std.testing.expectEqual(@as(usize, 0), findNextBit(&lhs, 0, 0));
    try std.testing.expectEqual(@as(usize, 0), findNextAndBit(&lhs, &rhs, 0, bits_per_long));
    try std.testing.expectEqual(@as(usize, 0), findNextZeroBit(&lhs, 0, 1));
}

test "find underscore aliases preserve scan semantics" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ (@as(Word, 1) << 2) | (@as(Word, 1) << 7), (@as(Word, 1) << 1) | (@as(Word, 1) << 8) };
    const rhs = [_]Word{ (@as(Word, 1) << 7), (@as(Word, 1) << 1) | (@as(Word, 1) << 9) };
    const full = [_]Word{ ~@as(Word, 0), lastWordMask(nbits) };

    try std.testing.expectEqual(findFirstBit(&lhs, nbits), find_first_bit(&lhs, nbits));
    try std.testing.expectEqual(findFirstAndBit(&lhs, &rhs, nbits), find_first_and_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(findFirstZeroBit(&full, nbits), find_first_zero_bit(&full, nbits));
    try std.testing.expectEqual(findNextBit(&lhs, nbits, 3), find_next_bit(&lhs, nbits, 3));
    try std.testing.expectEqual(findNextAndBit(&lhs, &rhs, nbits, 3), find_next_and_bit(&lhs, &rhs, nbits, 3));
    try std.testing.expectEqual(findNextZeroBit(&full, nbits, bits_per_long), find_next_zero_bit(&full, nbits, bits_per_long));
}

test "find underscore aliases preserve empty and out-of-range boundaries" {
    const empty = [_]Word{};
    try std.testing.expectEqual(findFirstBit(&empty, 0), find_first_bit(&empty, 0));
    try std.testing.expectEqual(findFirstAndBit(&empty, &empty, 0), find_first_and_bit(&empty, &empty, 0));
    try std.testing.expectEqual(findFirstZeroBit(&empty, 0), find_first_zero_bit(&empty, 0));
    try std.testing.expectEqual(findNextBit(&empty, 0, 0), find_next_bit(&empty, 0, 0));
    try std.testing.expectEqual(findNextAndBit(&empty, &empty, 0, 0), find_next_and_bit(&empty, &empty, 0, 0));
    try std.testing.expectEqual(findNextZeroBit(&empty, 0, 0), find_next_zero_bit(&empty, 0, 0));

    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ (@as(Word, 1) << 2) | (@as(Word, 1) << 7), (@as(Word, 1) << 1) };
    const rhs = [_]Word{ (@as(Word, 1) << 7), (@as(Word, 1) << 1) };
    const full = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    const out_of_range = nbits + 3;

    try std.testing.expectEqual(findNextBit(&lhs, nbits, nbits), find_next_bit(&lhs, nbits, nbits));
    try std.testing.expectEqual(findNextBit(&lhs, nbits, out_of_range), find_next_bit(&lhs, nbits, out_of_range));
    try std.testing.expectEqual(findNextAndBit(&lhs, &rhs, nbits, nbits), find_next_and_bit(&lhs, &rhs, nbits, nbits));
    try std.testing.expectEqual(findNextAndBit(&lhs, &rhs, nbits, out_of_range), find_next_and_bit(&lhs, &rhs, nbits, out_of_range));
    try std.testing.expectEqual(findNextZeroBit(&full, nbits, nbits), find_next_zero_bit(&full, nbits, nbits));
    try std.testing.expectEqual(findNextZeroBit(&full, nbits, out_of_range), find_next_zero_bit(&full, nbits, out_of_range));
}

test "find underscore aliases preserve tail-start and populated zero-sized boundaries" {
    const nbits = bits_per_long + 5;
    const tail_bit = bits_per_long + 4;

    const set_bits = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    var zero_bits = [_]Word{ ~@as(Word, 0), lastWordMask(nbits) };
    zero_bits[1] &= ~(@as(Word, 1) << 4);
    zero_bits[1] &= ~(@as(Word, 1) << 9);
    const lhs = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 10) };
    const populated = [_]Word{ (@as(Word, 1) << 5) | (@as(Word, 1) << 17), ~@as(Word, 0) };
    const populated_rhs = [_]Word{ (@as(Word, 1) << 5), @as(Word, 1) << 1 };

    try std.testing.expectEqual(findNextBit(&set_bits, nbits, tail_bit), find_next_bit(&set_bits, nbits, tail_bit));
    try std.testing.expectEqual(findNextBit(&set_bits, nbits, tail_bit + 1), find_next_bit(&set_bits, nbits, tail_bit + 1));
    try std.testing.expectEqual(findNextZeroBit(&zero_bits, nbits, tail_bit), find_next_zero_bit(&zero_bits, nbits, tail_bit));
    try std.testing.expectEqual(findNextZeroBit(&zero_bits, nbits, tail_bit + 1), find_next_zero_bit(&zero_bits, nbits, tail_bit + 1));
    try std.testing.expectEqual(findNextAndBit(&lhs, &rhs, nbits, tail_bit), find_next_and_bit(&lhs, &rhs, nbits, tail_bit));
    try std.testing.expectEqual(findNextAndBit(&lhs, &rhs, nbits, tail_bit + 1), find_next_and_bit(&lhs, &rhs, nbits, tail_bit + 1));

    try std.testing.expectEqual(findFirstBit(&populated, 0), find_first_bit(&populated, 0));
    try std.testing.expectEqual(findFirstAndBit(&populated, &populated_rhs, 0), find_first_and_bit(&populated, &populated_rhs, 0));
    try std.testing.expectEqual(findFirstZeroBit(&populated, 0), find_first_zero_bit(&populated, 0));
    try std.testing.expectEqual(findNextBit(&populated, 0, 0), find_next_bit(&populated, 0, 0));
    try std.testing.expectEqual(findNextAndBit(&populated, &populated_rhs, 0, bits_per_long), find_next_and_bit(&populated, &populated_rhs, 0, bits_per_long));
    try std.testing.expectEqual(findNextZeroBit(&populated, 0, 1), find_next_zero_bit(&populated, 0, 1));
}

test "find low-level underscore entry points preserve same-word and tail-clamped scan semantics" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ (@as(Word, 1) << 2) | (@as(Word, 1) << 7), (@as(Word, 1) << 1) | (@as(Word, 1) << 8) };
    const rhs = [_]Word{ (@as(Word, 1) << 7), (@as(Word, 1) << 1) | (@as(Word, 1) << 9) };
    const full = [_]Word{ ~@as(Word, 0), lastWordMask(nbits) };

    try std.testing.expectEqual(findFirstBit(&lhs, nbits), _find_first_bit(&lhs, nbits));
    try std.testing.expectEqual(findFirstAndBit(&lhs, &rhs, nbits), _find_first_and_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(findFirstZeroBit(&full, nbits), _find_first_zero_bit(&full, nbits));
    try std.testing.expectEqual(findNextBit(&lhs, nbits, 3), _find_next_bit(&lhs, nbits, 3));
    try std.testing.expectEqual(findNextAndBit(&lhs, &rhs, nbits, 3), _find_next_and_bit(&lhs, &rhs, nbits, 3));
    try std.testing.expectEqual(findNextZeroBit(&full, nbits, bits_per_long), _find_next_zero_bit(&full, nbits, bits_per_long));
}

test "find low-level underscore entry points preserve empty and out-of-range boundaries" {
    const empty = [_]Word{};
    try std.testing.expectEqual(findFirstBit(&empty, 0), _find_first_bit(&empty, 0));
    try std.testing.expectEqual(findFirstAndBit(&empty, &empty, 0), _find_first_and_bit(&empty, &empty, 0));
    try std.testing.expectEqual(findFirstZeroBit(&empty, 0), _find_first_zero_bit(&empty, 0));
    try std.testing.expectEqual(findNextBit(&empty, 0, 0), _find_next_bit(&empty, 0, 0));
    try std.testing.expectEqual(findNextAndBit(&empty, &empty, 0, 0), _find_next_and_bit(&empty, &empty, 0, 0));
    try std.testing.expectEqual(findNextZeroBit(&empty, 0, 0), _find_next_zero_bit(&empty, 0, 0));

    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ (@as(Word, 1) << 2) | (@as(Word, 1) << 7), (@as(Word, 1) << 1) };
    const rhs = [_]Word{ (@as(Word, 1) << 7), (@as(Word, 1) << 1) };
    const full = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    const out_of_range = nbits + 3;

    try std.testing.expectEqual(findNextBit(&lhs, nbits, nbits), _find_next_bit(&lhs, nbits, nbits));
    try std.testing.expectEqual(findNextBit(&lhs, nbits, out_of_range), _find_next_bit(&lhs, nbits, out_of_range));
    try std.testing.expectEqual(findNextAndBit(&lhs, &rhs, nbits, nbits), _find_next_and_bit(&lhs, &rhs, nbits, nbits));
    try std.testing.expectEqual(findNextAndBit(&lhs, &rhs, nbits, out_of_range), _find_next_and_bit(&lhs, &rhs, nbits, out_of_range));
    try std.testing.expectEqual(findNextZeroBit(&full, nbits, nbits), _find_next_zero_bit(&full, nbits, nbits));
    try std.testing.expectEqual(findNextZeroBit(&full, nbits, out_of_range), _find_next_zero_bit(&full, nbits, out_of_range));
}

test "find low-level underscore entry points preserve tail-start and populated zero-sized boundaries" {
    const nbits = bits_per_long + 5;
    const tail_bit = bits_per_long + 4;

    const set_bits = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    var zero_bits = [_]Word{ ~@as(Word, 0), lastWordMask(nbits) };
    zero_bits[1] &= ~(@as(Word, 1) << 4);
    zero_bits[1] &= ~(@as(Word, 1) << 9);
    const lhs = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 10) };
    const populated = [_]Word{ (@as(Word, 1) << 5) | (@as(Word, 1) << 17), ~@as(Word, 0) };
    const populated_rhs = [_]Word{ (@as(Word, 1) << 5), @as(Word, 1) << 1 };

    try std.testing.expectEqual(findNextBit(&set_bits, nbits, tail_bit), _find_next_bit(&set_bits, nbits, tail_bit));
    try std.testing.expectEqual(findNextBit(&set_bits, nbits, tail_bit + 1), _find_next_bit(&set_bits, nbits, tail_bit + 1));
    try std.testing.expectEqual(findNextZeroBit(&zero_bits, nbits, tail_bit), _find_next_zero_bit(&zero_bits, nbits, tail_bit));
    try std.testing.expectEqual(findNextZeroBit(&zero_bits, nbits, tail_bit + 1), _find_next_zero_bit(&zero_bits, nbits, tail_bit + 1));
    try std.testing.expectEqual(findNextAndBit(&lhs, &rhs, nbits, tail_bit), _find_next_and_bit(&lhs, &rhs, nbits, tail_bit));
    try std.testing.expectEqual(findNextAndBit(&lhs, &rhs, nbits, tail_bit + 1), _find_next_and_bit(&lhs, &rhs, nbits, tail_bit + 1));

    try std.testing.expectEqual(findFirstBit(&populated, 0), _find_first_bit(&populated, 0));
    try std.testing.expectEqual(findFirstAndBit(&populated, &populated_rhs, 0), _find_first_and_bit(&populated, &populated_rhs, 0));
    try std.testing.expectEqual(findFirstZeroBit(&populated, 0), _find_first_zero_bit(&populated, 0));
    try std.testing.expectEqual(findNextBit(&populated, 0, 0), _find_next_bit(&populated, 0, 0));
    try std.testing.expectEqual(findNextAndBit(&populated, &populated_rhs, 0, bits_per_long), _find_next_and_bit(&populated, &populated_rhs, 0, bits_per_long));
    try std.testing.expectEqual(findNextZeroBit(&populated, 0, 1), _find_next_zero_bit(&populated, 0, 1));
}
