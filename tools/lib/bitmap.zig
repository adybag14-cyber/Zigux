const std = @import("std");
const find_bit = @import("find_bit");

pub const Word = find_bit.Word;
pub const bits_per_long = find_bit.bits_per_long;

pub fn bitsToWords(nbits: usize) usize {
    return find_bit.bitsToWords(nbits);
}

pub fn firstWordMask(start: usize) Word {
    return find_bit.firstWordMask(start);
}

pub fn lastWordMask(nbits: usize) Word {
    return find_bit.lastWordMask(nbits);
}

fn assertBitmapLen(bitmap: []const Word, nbits: usize) void {
    std.debug.assert(bitmap.len >= bitsToWords(nbits));
}

pub fn zero(dst: []Word, nbits: usize) void {
    assertBitmapLen(dst, nbits);
    @memset(dst[0..bitsToWords(nbits)], 0);
}

pub fn fill(dst: []Word, nbits: usize) void {
    assertBitmapLen(dst, nbits);
    if (nbits == 0) {
        return;
    }

    const nwords = bitsToWords(nbits);
    @memset(dst[0..nwords], ~@as(Word, 0));
    dst[nwords - 1] = lastWordMask(nbits);
}

pub fn empty(src: []const Word, nbits: usize) bool {
    assertBitmapLen(src, nbits);
    return find_bit.findFirstBit(src, nbits) == nbits;
}

pub fn full(src: []const Word, nbits: usize) bool {
    assertBitmapLen(src, nbits);
    return find_bit.findFirstZeroBit(src, nbits) == nbits;
}

pub fn weight(src: []const Word, nbits: usize) usize {
    assertBitmapLen(src, nbits);

    var total: usize = 0;
    const lim = nbits / bits_per_long;

    var idx: usize = 0;
    while (idx < lim) : (idx += 1) {
        total += @popCount(src[idx]);
    }

    if ((nbits & (bits_per_long - 1)) != 0) {
        total += @popCount(src[idx] & lastWordMask(nbits));
    }

    return total;
}

pub fn orBits(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {
    const nwords = bitsToWords(nbits);
    std.debug.assert(dst.len >= nwords);
    std.debug.assert(src1.len >= nwords);
    std.debug.assert(src2.len >= nwords);

    for (0..nwords) |idx| {
        dst[idx] = src1[idx] | src2[idx];
    }
}

pub fn xorBits(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {
    const nwords = bitsToWords(nbits);
    std.debug.assert(dst.len >= nwords);
    std.debug.assert(src1.len >= nwords);
    std.debug.assert(src2.len >= nwords);

    for (0..nwords) |idx| {
        dst[idx] = src1[idx] ^ src2[idx];
    }
}

pub fn andBits(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {
    assertBitmapLen(dst, nbits);
    assertBitmapLen(src1, nbits);
    assertBitmapLen(src2, nbits);

    const lim = nbits / bits_per_long;
    var result: Word = 0;

    var idx: usize = 0;
    while (idx < lim) : (idx += 1) {
        dst[idx] = src1[idx] & src2[idx];
        result |= dst[idx];
    }

    if ((nbits & (bits_per_long - 1)) != 0) {
        dst[idx] = src1[idx] & src2[idx] & lastWordMask(nbits);
        result |= dst[idx];
    }

    return result != 0;
}

pub fn andNotBits(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {
    assertBitmapLen(dst, nbits);
    assertBitmapLen(src1, nbits);
    assertBitmapLen(src2, nbits);

    const lim = nbits / bits_per_long;
    var result: Word = 0;

    var idx: usize = 0;
    while (idx < lim) : (idx += 1) {
        dst[idx] = src1[idx] & ~src2[idx];
        result |= dst[idx];
    }

    if ((nbits & (bits_per_long - 1)) != 0) {
        dst[idx] = src1[idx] & ~src2[idx] & lastWordMask(nbits);
        result |= dst[idx];
    }

    return result != 0;
}

pub fn equal(src1: []const Word, src2: []const Word, nbits: usize) bool {
    assertBitmapLen(src1, nbits);
    assertBitmapLen(src2, nbits);

    const lim = nbits / bits_per_long;
    for (0..lim) |idx| {
        if (src1[idx] != src2[idx]) {
            return false;
        }
    }

    if ((nbits & (bits_per_long - 1)) != 0) {
        const idx = lim;
        if (((src1[idx] ^ src2[idx]) & lastWordMask(nbits)) != 0) {
            return false;
        }
    }

    return true;
}

pub fn intersects(src1: []const Word, src2: []const Word, nbits: usize) bool {
    assertBitmapLen(src1, nbits);
    assertBitmapLen(src2, nbits);

    const lim = nbits / bits_per_long;
    for (0..lim) |idx| {
        if ((src1[idx] & src2[idx]) != 0) {
            return true;
        }
    }

    if ((nbits & (bits_per_long - 1)) != 0) {
        const idx = lim;
        if (((src1[idx] & src2[idx]) & lastWordMask(nbits)) != 0) {
            return true;
        }
    }

    return false;
}

pub fn subset(src1: []const Word, src2: []const Word, nbits: usize) bool {
    assertBitmapLen(src1, nbits);
    assertBitmapLen(src2, nbits);

    const lim = nbits / bits_per_long;
    for (0..lim) |idx| {
        if ((src1[idx] & ~src2[idx]) != 0) {
            return false;
        }
    }

    if ((nbits & (bits_per_long - 1)) != 0) {
        const idx = lim;
        if (((src1[idx] & ~src2[idx]) & lastWordMask(nbits)) != 0) {
            return false;
        }
    }

    return true;
}

pub fn setRange(map: []Word, start: usize, len: usize) void {
    if (len == 0) {
        return;
    }

    assertBitmapLen(map, start + len);
    var ptr = start / bits_per_long;
    const size = start + len;
    var remaining = len;
    var bits_to_set = bits_per_long - (start % bits_per_long);
    var mask_to_set = firstWordMask(start);

    while (remaining >= bits_to_set) {
        map[ptr] |= mask_to_set;
        remaining -= bits_to_set;
        bits_to_set = bits_per_long;
        mask_to_set = ~@as(Word, 0);
        ptr += 1;
    }

    if (remaining != 0) {
        mask_to_set &= lastWordMask(size);
        map[ptr] |= mask_to_set;
    }
}

pub fn clearRange(map: []Word, start: usize, len: usize) void {
    if (len == 0) {
        return;
    }

    assertBitmapLen(map, start + len);
    var ptr = start / bits_per_long;
    const size = start + len;
    var remaining = len;
    var bits_to_clear = bits_per_long - (start % bits_per_long);
    var mask_to_clear = firstWordMask(start);

    while (remaining >= bits_to_clear) {
        map[ptr] &= ~mask_to_clear;
        remaining -= bits_to_clear;
        bits_to_clear = bits_per_long;
        mask_to_clear = ~@as(Word, 0);
        ptr += 1;
    }

    if (remaining != 0) {
        mask_to_clear &= lastWordMask(size);
        map[ptr] &= ~mask_to_clear;
    }
}

fn appendSlice(buffer: []u8, written: *usize, text: []const u8) void {
    if (buffer.len == 0) {
        return;
    }

    const available = (buffer.len -| written.*) -| 1;
    const count = @min(available, text.len);
    if (count != 0) {
        @memcpy(buffer[written.* .. written.* + count], text[0..count]);
        written.* += count;
    }
}

fn appendUnsigned(buffer: []u8, written: *usize, value: usize) void {
    var tmp: [32]u8 = undefined;
    const rendered = std.fmt.bufPrint(&tmp, "{d}", .{value}) catch unreachable;
    appendSlice(buffer, written, rendered);
}

pub fn scnprintf(bitmap: []const Word, nbits: usize, buffer: []u8) usize {
    assertBitmapLen(bitmap, nbits);

    var written: usize = 0;
    var first = true;
    var current = find_bit.findFirstBit(bitmap, nbits);
    var range_bottom = current;

    while (current < nbits) {
        var range_top = current;
        current = find_bit.findNextBit(bitmap, nbits, current + 1);
        if (current < nbits and current <= range_top + 1) {
            range_top = current;
            continue;
        }

        if (!first) {
            appendSlice(buffer, &written, ",");
        }
        first = false;

        appendUnsigned(buffer, &written, range_bottom);
        if (range_bottom < range_top) {
            appendSlice(buffer, &written, "-");
            appendUnsigned(buffer, &written, range_top);
        }

        range_bottom = current;
    }

    if (buffer.len != 0 and written < buffer.len) {
        buffer[written] = 0;
    }

    return written;
}

test "bitmap set clear weight and empty full helpers" {
    var map = [_]Word{ 0, 0, 0 };
    setRange(&map, 1, 3);
    setRange(&map, bits_per_long + 2, 2);

    try std.testing.expectEqual(@as(usize, 5), weight(&map, bits_per_long * 2));
    try std.testing.expect(!empty(&map, bits_per_long * 2));
    clearRange(&map, 1, 3);
    clearRange(&map, bits_per_long + 2, 2);
    try std.testing.expect(empty(&map, bits_per_long * 2));

    fill(&map, bits_per_long * 2);
    try std.testing.expect(full(&map, bits_per_long * 2));
}

test "bitmap and andnot equal intersects subset" {
    const lhs = [_]Word{ 0b1110, 0 };
    const rhs = [_]Word{ 0b1010, 0 };
    var dst = [_]Word{ 0, 0 };

    try std.testing.expect(andBits(&dst, &lhs, &rhs, 8));
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0b1010, 0 }, &dst);
    try std.testing.expect(andNotBits(&dst, &lhs, &rhs, 8));
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0b0100, 0 }, &dst);
    xorBits(&dst, &lhs, &rhs, 8);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0b0100, 0 }, &dst);
    try std.testing.expect(equal(&lhs, &[_]Word{ 0b1110, 0 }, 8));
    try std.testing.expect(intersects(&lhs, &rhs, 8));
    try std.testing.expect(subset(&rhs, &lhs, 8));
}

test "bitmap xor keeps caller-selected bit window" {
    const lhs = [_]Word{0b1_1111};
    const rhs = [_]Word{0b1_0001};
    var dst = [_]Word{0};

    xorBits(&dst, &lhs, &rhs, 4);
    try std.testing.expectEqual(@as(Word, 0b1110), dst[0] & lastWordMask(4));
}

test "bitmap scnprintf collapses contiguous ranges" {
    var map = [_]Word{ 0, 0 };
    setRange(&map, 1, 3);
    setRange(&map, 7, 1);
    setRange(&map, 10, 2);

    var buffer: [64]u8 = undefined;
    const len = scnprintf(&map, 32, &buffer);
    try std.testing.expectEqualStrings("1-3,7,10-11", buffer[0..len]);
}

test "bitmap scnprintf reports full length while truncating the buffer" {
    var map = [_]Word{0};
    setRange(&map, 1, 3);
    setRange(&map, 7, 1);
    setRange(&map, 10, 3);

    var buffer = [_]u8{0} ** 8;
    const len = scnprintf(&map, 32, &buffer);

    try std.testing.expectEqual(@as(usize, 7), len);
    try std.testing.expectEqualStrings("1-3,7,1", buffer[0 .. buffer.len - 1]);
    try std.testing.expectEqual(@as(u8, 0), buffer[buffer.len - 1]);
}
