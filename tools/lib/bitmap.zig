const std = @import("std");
const find_bit = @import("find_bit");

pub const Word = find_bit.Word;
pub const bits_per_long = find_bit.bits_per_long;

pub fn bitsToWords(nbits: usize) usize {
    return find_bit.bitsToWords(nbits);
}

pub fn bitmapSize(nbits: usize) usize {
    return bitsToWords(nbits) * @sizeOf(Word);
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
    if (nbits == 0) {
        return;
    }
    @memset(dst[0..bitsToWords(nbits)], 0);
}

pub fn fill(dst: []Word, nbits: usize) void {
    assertBitmapLen(dst, nbits);
    if (nbits == 0) {
        return;
    }

    const nwords = bitsToWords(nbits);
    @memset(dst[0..nwords], ~@as(Word, 0));
}

pub fn copy(dst: []Word, src: []const Word, nbits: usize) void {
    const nwords = bitsToWords(nbits);
    std.debug.assert(dst.len >= nwords);
    std.debug.assert(src.len >= nwords);
    if (nwords == 0) {
        return;
    }

    @memcpy(dst[0..nwords], src[0..nwords]);
}

pub fn copyClearTail(dst: []Word, src: []const Word, nbits: usize) void {
    copy(dst, src, nbits);
    if ((nbits & (bits_per_long - 1)) != 0) {
        dst[nbits / bits_per_long] &= lastWordMask(nbits);
    }
}

pub fn copyAndExtend(dst: []Word, src: []const Word, count: usize, size: usize) void {
    std.debug.assert(size >= count);
    assertBitmapLen(dst, size);
    assertBitmapLen(src, count);

    const copied_words = bitsToWords(count);
    if (copied_words != 0) {
        @memcpy(dst[0..copied_words], src[0..copied_words]);
        if ((count & (bits_per_long - 1)) != 0) {
            dst[copied_words - 1] &= lastWordMask(count);
        }
    }

    @memset(dst[copied_words..bitsToWords(size)], 0);
}

pub fn empty(src: []const Word, nbits: usize) bool {
    assertBitmapLen(src, nbits);
    if (nbits == 0) {
        return true;
    }
    return find_bit.findFirstBit(src, nbits) == nbits;
}

pub fn full(src: []const Word, nbits: usize) bool {
    assertBitmapLen(src, nbits);
    if (nbits == 0) {
        return true;
    }
    return find_bit.findFirstZeroBit(src, nbits) == nbits;
}

pub fn bitmap_zero(dst: []Word, nbits: usize) void {
    zero(dst, nbits);
}

pub fn bitmap_fill(dst: []Word, nbits: usize) void {
    fill(dst, nbits);
}

pub fn bitmap_copy(dst: []Word, src: []const Word, nbits: usize) void {
    copy(dst, src, nbits);
}

pub fn bitmap_copy_clear_tail(dst: []Word, src: []const Word, nbits: usize) void {
    copyClearTail(dst, src, nbits);
}

pub fn bitmap_copy_and_extend(dst: []Word, src: []const Word, count: usize, size: usize) void {
    copyAndExtend(dst, src, count, size);
}

pub fn bitmap_empty(src: []const Word, nbits: usize) bool {
    return empty(src, nbits);
}

pub fn bitmap_full(src: []const Word, nbits: usize) bool {
    return full(src, nbits);
}

pub fn weight(src: []const Word, nbits: usize) usize {
    assertBitmapLen(src, nbits);
    if (nbits == 0) {
        return 0;
    }

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
    if (nwords == 0) {
        return;
    }

    for (0..nwords) |idx| {
        dst[idx] = src1[idx] | src2[idx];
    }
}

pub fn xorBits(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {
    const nwords = bitsToWords(nbits);
    std.debug.assert(dst.len >= nwords);
    std.debug.assert(src1.len >= nwords);
    std.debug.assert(src2.len >= nwords);
    if (nwords == 0) {
        return;
    }

    for (0..nwords) |idx| {
        dst[idx] = src1[idx] ^ src2[idx];
    }
}

pub fn andBits(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {
    assertBitmapLen(dst, nbits);
    assertBitmapLen(src1, nbits);
    assertBitmapLen(src2, nbits);
    if (nbits == 0) {
        return false;
    }

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
    if (nbits == 0) {
        return false;
    }

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
    if (nbits == 0) {
        return true;
    }

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
    if (nbits == 0) {
        return false;
    }

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
    if (nbits == 0) {
        return true;
    }

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
    const end = start + len;
    const first = start / bits_per_long;
    const last = (end - 1) / bits_per_long;
    const first_mask = firstWordMask(start);
    const last_mask = lastWordMask(end);

    if (first == last) {
        map[first] |= first_mask & last_mask;
        return;
    }

    map[first] |= first_mask;
    if (last > first + 1) {
        @memset(map[first + 1 .. last], ~@as(Word, 0));
    }
    map[last] |= last_mask;
}

pub fn clearRange(map: []Word, start: usize, len: usize) void {
    if (len == 0) {
        return;
    }

    assertBitmapLen(map, start + len);
    const end = start + len;
    const first = start / bits_per_long;
    const last = (end - 1) / bits_per_long;
    const first_mask = firstWordMask(start);
    const last_mask = lastWordMask(end);

    if (first == last) {
        map[first] &= ~(first_mask & last_mask);
        return;
    }

    map[first] &= ~first_mask;
    if (last > first + 1) {
        @memset(map[first + 1 .. last], 0);
    }
    map[last] &= ~last_mask;
}

fn appendSlice(buffer: []u8, written: *usize, text: []const u8) void {
    if (buffer.len == 0) {
        return;
    }

    const available = (buffer.len - 1) -| written.*;
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
    if (nbits == 0) {
        return 0;
    }

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

    if (buffer.len != 0 and !first and written < buffer.len) {
        buffer[written] = 0;
    }

    return written;
}

pub fn bitmapAlloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {
    return allocator.alloc(Word, bitsToWords(nbits));
}

pub fn bitmapZalloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {
    const map = try bitmapAlloc(allocator, nbits);
    @memset(map, 0);
    return map;
}

pub fn bitmapFree(allocator: std.mem.Allocator, bitmap: *?[]Word) void {
    if (bitmap.*) |map| {
        allocator.free(map);
        bitmap.* = null;
    }
}

pub fn bitmap_weight(bitmap: []const Word, bits: usize) usize {
    return weight(bitmap, bits);
}

pub fn bitmap_or(dst: []Word, bitmap1: []const Word, bitmap2: []const Word, bits: usize) void {
    orBits(dst, bitmap1, bitmap2, bits);
}

pub fn bitmap_scnprintf(bitmap: []const Word, nbits: usize, buffer: []u8) usize {
    return scnprintf(bitmap, nbits, buffer);
}

pub fn bitmap_and(dst: []Word, bitmap1: []const Word, bitmap2: []const Word, bits: usize) bool {
    return andBits(dst, bitmap1, bitmap2, bits);
}

pub fn bitmap_equal(bitmap1: []const Word, bitmap2: []const Word, bits: usize) bool {
    return equal(bitmap1, bitmap2, bits);
}

pub fn bitmap_intersects(bitmap1: []const Word, bitmap2: []const Word, bits: usize) bool {
    return intersects(bitmap1, bitmap2, bits);
}

pub fn bitmap_set(map: []Word, start: usize, len: usize) void {
    setRange(map, start, len);
}

pub fn bitmap_clear(map: []Word, start: usize, len: usize) void {
    clearRange(map, start, len);
}

pub fn bitmap_andnot(dst: []Word, bitmap1: []const Word, bitmap2: []const Word, bits: usize) bool {
    return andNotBits(dst, bitmap1, bitmap2, bits);
}

pub fn bitmap_subset(bitmap1: []const Word, bitmap2: []const Word, bits: usize) bool {
    return subset(bitmap1, bitmap2, bits);
}

pub fn bitmap_xor(dst: []Word, bitmap1: []const Word, bitmap2: []const Word, bits: usize) void {
    xorBits(dst, bitmap1, bitmap2, bits);
}

pub fn bitmap_alloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {
    return bitmapAlloc(allocator, nbits);
}

pub fn bitmap_zalloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {
    return bitmapZalloc(allocator, nbits);
}

pub fn bitmap_free(allocator: std.mem.Allocator, bitmap: *?[]Word) void {
    bitmapFree(allocator, bitmap);
}

pub fn __bitmap_weight(bitmap: []const Word, bits: usize) usize {
    return weight(bitmap, bits);
}

pub fn __bitmap_or(dst: []Word, bitmap1: []const Word, bitmap2: []const Word, bits: usize) void {
    orBits(dst, bitmap1, bitmap2, bits);
}

pub fn __bitmap_and(dst: []Word, bitmap1: []const Word, bitmap2: []const Word, bits: usize) bool {
    return andBits(dst, bitmap1, bitmap2, bits);
}

pub fn __bitmap_equal(bitmap1: []const Word, bitmap2: []const Word, bits: usize) bool {
    return equal(bitmap1, bitmap2, bits);
}

pub fn __bitmap_intersects(bitmap1: []const Word, bitmap2: []const Word, bits: usize) bool {
    return intersects(bitmap1, bitmap2, bits);
}

pub fn __bitmap_set(map: []Word, start: usize, len: usize) void {
    setRange(map, start, len);
}

pub fn __bitmap_clear(map: []Word, start: usize, len: usize) void {
    clearRange(map, start, len);
}

pub fn __bitmap_andnot(dst: []Word, bitmap1: []const Word, bitmap2: []const Word, bits: usize) bool {
    return andNotBits(dst, bitmap1, bitmap2, bits);
}

pub fn __bitmap_subset(bitmap1: []const Word, bitmap2: []const Word, bits: usize) bool {
    return subset(bitmap1, bitmap2, bits);
}

pub fn __bitmap_xor(dst: []Word, bitmap1: []const Word, bitmap2: []const Word, bits: usize) void {
    xorBits(dst, bitmap1, bitmap2, bits);
}

pub fn bitmap_size(nbits: usize) usize {
    return bitmapSize(nbits);
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

test "bitmap fill rounds a partial tail up to the active word window while zero clears only the active word window" {
    const nbits = bits_per_long + 5;
    var map = [_]Word{ 0, 0, 0x55aa };

    fill(&map, nbits);
    try std.testing.expectEqual(~@as(Word, 0), map[0]);
    try std.testing.expectEqual(~@as(Word, 0), map[1]);
    try std.testing.expectEqual(@as(Word, 0x55aa), map[2]);

    zero(&map, nbits);
    try std.testing.expectEqual(@as(Word, 0), map[0]);
    try std.testing.expectEqual(@as(Word, 0), map[1]);
    try std.testing.expectEqual(@as(Word, 0x55aa), map[2]);
}

test "bitmap range helpers preserve edges across whole-word spans" {
    const start = bits_per_long - 2;
    const len = bits_per_long * 2 + 4;
    var map = [_]Word{
        0,
        0,
        0,
        0,
        0,
    };

    setRange(&map, start, len);
    try std.testing.expectEqual(@as(Word, firstWordMask(start)), map[0]);
    try std.testing.expectEqual(~@as(Word, 0), map[1]);
    try std.testing.expectEqual(~@as(Word, 0), map[2]);
    try std.testing.expectEqual(lastWordMask(start + len), map[3]);
    try std.testing.expectEqual(@as(Word, 0), map[4]);

    clearRange(&map, start, len);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, 0, 0, 0, 0 }, &map);
}

test "bitmap copy preserves source words and clears copied tail through source state" {
    var src = [_]Word{ 0, 0, 0 };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };

    setRange(&src, 0, bits_per_long + 45);
    copy(&dst, &src, bits_per_long + 45);
    try std.testing.expectEqualSlices(Word, src[0..2], dst[0..2]);
    try std.testing.expectEqual(~@as(Word, 0), dst[2]);

    fill(&dst, bits_per_long * 3);
    copy(&dst, &src, bits_per_long + 33);
    try std.testing.expectEqualSlices(Word, src[0..2], dst[0..2]);
    try std.testing.expectEqual(~@as(Word, 0), dst[2]);
}

test "bitmap copyClearTail clears out-of-range bits in the last copied word" {
    const nbits = bits_per_long + 5;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), 0 };
    var dst = [_]Word{ 0, 0, 0 };

    copy(&dst, &src, nbits);
    try std.testing.expectEqual(~@as(Word, 0), dst[1]);

    copyClearTail(&dst, &src, nbits);
    try std.testing.expectEqual(~@as(Word, 0), dst[0]);
    try std.testing.expectEqual(lastWordMask(nbits), dst[1]);
    try std.testing.expectEqual(@as(Word, 0), dst[2]);
}

test "bitmap copyAndExtend masks a partial tail and zeroes the extended words" {
    const count = bits_per_long + 5;
    const size = bits_per_long * 3;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    var dst = [_]Word{ 0xaa55, 0xaa55, 0xaa55 };

    copyAndExtend(&dst, &src, count, size);
    try std.testing.expectEqual(~@as(Word, 0), dst[0]);
    try std.testing.expectEqual(lastWordMask(count), dst[1]);
    try std.testing.expectEqual(@as(Word, 0), dst[2]);
}

test "bitmap copyAndExtend keeps whole copied words and clears the rest" {
    const count = bits_per_long * 2;
    const size = bits_per_long * 3;
    const src = [_]Word{ 0x55aa, 0xaa55, ~@as(Word, 0) };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };

    copyAndExtend(&dst, &src, count, size);
    try std.testing.expectEqual(src[0], dst[0]);
    try std.testing.expectEqual(src[1], dst[1]);
    try std.testing.expectEqual(@as(Word, 0), dst[2]);
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

test "bitmap tail-masked helpers ignore out-of-range differences" {
    const nbits = bits_per_long + 5;
    const in_range_tail = @as(Word, 1) << 3;
    const out_of_range_lhs = @as(Word, 1) << 9;
    const out_of_range_rhs = @as(Word, 1) << 11;
    const lhs = [_]Word{ 0b1010, in_range_tail | out_of_range_lhs };
    const rhs = [_]Word{ 0b1010, in_range_tail | out_of_range_rhs };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };

    try std.testing.expect(equal(&lhs, &rhs, nbits));
    try std.testing.expect(intersects(&lhs, &rhs, nbits));
    try std.testing.expect(subset(&lhs, &rhs, nbits));

    try std.testing.expect(andBits(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0b1010, in_range_tail }, &dst);

    try std.testing.expect(!andNotBits(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, 0 }, &dst);

    const outside_only = [_]Word{ 0, out_of_range_lhs };
    try std.testing.expect(equal(&outside_only, &[_]Word{ 0, 0 }, nbits));
    try std.testing.expect(!intersects(&outside_only, &outside_only, nbits));
    try std.testing.expect(subset(&outside_only, &[_]Word{ 0, 0 }, nbits));
}

test "bitmap xor keeps caller-selected bit window" {
    const lhs = [_]Word{0b1_1111};
    const rhs = [_]Word{0b1_0001};
    var dst = [_]Word{0};

    xorBits(&dst, &lhs, &rhs, 4);
    try std.testing.expectEqual(@as(Word, 0b1110), dst[0] & lastWordMask(4));
}

test "bitmap xor across a multiword tail still lets callers clamp the last word" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0b11_1001, 0b10_1110 };
    const rhs = [_]Word{ 0b10_1010, 0b00_1001 };
    var dst = [_]Word{ 0, 0 };

    xorBits(&dst, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0b01_0011, 0b00_0111 }, &[_]Word{ dst[0], dst[1] & lastWordMask(nbits) });
}

test "bitmap or across a multiword tail still lets callers clamp the last word" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0b11_1001, 0b10_1110 };
    const rhs = [_]Word{ 0b10_1010, 0b00_1001 };
    var dst = [_]Word{ 0, 0 };

    orBits(&dst, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0b11_1011, 0b00_1111 }, &[_]Word{ dst[0], dst[1] & lastWordMask(nbits) });
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

test "bitmap scnprintf preserves contiguous ranges across word boundaries" {
    const nbits = bits_per_long + 6;
    var map = [_]Word{ 0, 0 };
    setRange(&map, 3, 1);
    setRange(&map, bits_per_long - 2, 5);
    setRange(&map, nbits - 1, 1);

    var buffer: [64]u8 = undefined;
    var expected: [32]u8 = undefined;
    const len = scnprintf(&map, nbits, &buffer);
    const expected_text = try std.fmt.bufPrint(&expected, "3,{d}-{d},{d}", .{ bits_per_long - 2, bits_per_long + 2, nbits - 1 });
    try std.testing.expectEqualStrings(expected_text, buffer[0..len]);
}

test "bitmap scnprintf truncates and keeps a terminator slot" {
    var map = [_]Word{0};
    setRange(&map, 1, 3);
    setRange(&map, 7, 1);

    var buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const len = scnprintf(&map, 8, &buffer);
    try std.testing.expectEqual(@as(usize, 3), len);
    try std.testing.expectEqualStrings("1-3", buffer[0..len]);
    try std.testing.expectEqual(@as(u8, 0), buffer[len]);
}

test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap" {
    const map = [_]Word{0};
    var buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };

    const len = scnprintf(&map, 8, &buffer);
    try std.testing.expectEqual(@as(usize, 0), len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa, 0xaa }, &buffer);
}

test "bitmap allocation helpers size zero fill and reset optionals" {
    const allocator = std.testing.allocator;
    const nbits = bits_per_long + 5;

    var plain: ?[]Word = try bitmapAlloc(allocator, nbits);
    defer bitmapFree(allocator, &plain);
    try std.testing.expectEqual(@as(usize, bitsToWords(nbits)), plain.?.len);
    @memset(plain.?, ~@as(Word, 0));

    var zeroed: ?[]Word = try bitmapZalloc(allocator, nbits);
    defer bitmapFree(allocator, &zeroed);
    try std.testing.expectEqual(@as(usize, bitsToWords(nbits)), zeroed.?.len);
    for (zeroed.?) |word| {
        try std.testing.expectEqual(@as(Word, 0), word);
    }

    bitmapFree(allocator, &plain);
    try std.testing.expect(plain == null);
    bitmapFree(allocator, &zeroed);
    try std.testing.expect(zeroed == null);
}

test "bitmap size helpers round up to full words in bytes" {
    try std.testing.expectEqual(@as(usize, 0), bitmapSize(0));
    try std.testing.expectEqual(@as(usize, @sizeOf(Word)), bitmapSize(1));
    try std.testing.expectEqual(@as(usize, @sizeOf(Word)), bitmapSize(bits_per_long));
    try std.testing.expectEqual(@as(usize, @sizeOf(Word) * 2), bitmapSize(bits_per_long + 1));
    try std.testing.expectEqual(bitmapSize(bits_per_long + 5), bitmap_size(bits_per_long + 5));
}

test "bitmap zero-bit helpers stay explicit no-ops" {
    var dst = [_]Word{0xaaaa};
    const src = [_]Word{0x5555};

    zero(&dst, 0);
    try std.testing.expectEqual(@as(Word, 0xaaaa), dst[0]);

    fill(&dst, 0);
    try std.testing.expectEqual(@as(Word, 0xaaaa), dst[0]);

    copy(&dst, &src, 0);
    try std.testing.expectEqual(@as(Word, 0xaaaa), dst[0]);

    copyClearTail(&dst, &src, 0);
    try std.testing.expectEqual(@as(Word, 0xaaaa), dst[0]);

    orBits(&dst, &src, &src, 0);
    try std.testing.expectEqual(@as(Word, 0xaaaa), dst[0]);

    xorBits(&dst, &src, &src, 0);
    try std.testing.expectEqual(@as(Word, 0xaaaa), dst[0]);

    try std.testing.expect(empty(&[_]Word{}, 0));
    try std.testing.expect(full(&[_]Word{}, 0));
    try std.testing.expectEqual(@as(usize, 0), weight(&[_]Word{}, 0));
    try std.testing.expect(andBits(&dst, &src, &src, 0) == false);
    try std.testing.expect(andNotBits(&dst, &src, &src, 0) == false);
    try std.testing.expect(equal(&[_]Word{}, &[_]Word{}, 0));
    try std.testing.expect(intersects(&[_]Word{}, &[_]Word{}, 0) == false);
    try std.testing.expect(subset(&[_]Word{}, &[_]Word{}, 0));

    var buffer = [_]u8{ 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(usize, 0), scnprintf(&[_]Word{}, 0, &buffer));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa }, &buffer);
}

test "bitmap header-style aliases preserve zero fill copy and predicate semantics" {
    const nbits = bits_per_long + 5;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), 0x55aa };
    var zero_map = [_]Word{ 0x1111, 0x2222, 0x3333 };
    var fill_map = [_]Word{ 0, 0, 0x55aa };
    var copy_map = [_]Word{ 0, 0, 0x55aa };

    bitmap_zero(&zero_map, nbits);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, 0, 0x3333 }, &zero_map);
    try std.testing.expect(bitmap_empty(&zero_map, nbits));

    bitmap_fill(&fill_map, nbits);
    try std.testing.expectEqualSlices(Word, &[_]Word{ ~@as(Word, 0), ~@as(Word, 0), 0x55aa }, &fill_map);
    try std.testing.expect(bitmap_full(&fill_map, nbits));

    bitmap_copy(&copy_map, &src, nbits);
    try std.testing.expectEqualSlices(Word, &[_]Word{ src[0], src[1], 0x55aa }, &copy_map);
    try std.testing.expect(!bitmap_empty(&copy_map, nbits));
    try std.testing.expect(bitmap_full(&copy_map, nbits));
}

test "bitmap copy aliases preserve tail clearing and extension semantics" {
    const nbits = bits_per_long + 5;
    const count = bits_per_long + 5;
    const size = bits_per_long * 3;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    var cleared = [_]Word{ 0, 0, 0 };
    var extended = [_]Word{ 0xaa55, 0xaa55, 0xaa55 };

    bitmap_copy_clear_tail(&cleared, &src, nbits);
    try std.testing.expectEqual(~@as(Word, 0), cleared[0]);
    try std.testing.expectEqual(lastWordMask(nbits), cleared[1]);
    try std.testing.expectEqual(@as(Word, 0), cleared[2]);

    bitmap_copy_and_extend(&extended, &src, count, size);
    try std.testing.expectEqual(~@as(Word, 0), extended[0]);
    try std.testing.expectEqual(lastWordMask(count), extended[1]);
    try std.testing.expectEqual(@as(Word, 0), extended[2]);
}

test "bitmap underscore aliases preserve bitmap helper semantics" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0b1110, (@as(Word, 1) << 2) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0b1010, @as(Word, 1) << 2 };
    var dst = [_]Word{ 0, 0 };
    var range = [_]Word{ 0, 0 };
    var buffer = [_]u8{0} ** 32;

    try std.testing.expectEqual(weight(&lhs, nbits), bitmap_weight(&lhs, nbits));

    bitmap_or(&dst, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &[_]Word{ lhs[0] | rhs[0], (lhs[1] | rhs[1]) & lastWordMask(nbits) }, &[_]Word{ dst[0], dst[1] & lastWordMask(nbits) });

    try std.testing.expect(andBits(&dst, &lhs, &rhs, nbits) == bitmap_and(&dst, &lhs, &rhs, nbits));
    try std.testing.expect(andNotBits(&dst, &lhs, &rhs, nbits) == bitmap_andnot(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(equal(&lhs, &rhs, nbits), bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expectEqual(intersects(&lhs, &rhs, nbits), bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expectEqual(subset(&rhs, &lhs, nbits), bitmap_subset(&rhs, &lhs, nbits));

    bitmap_xor(&dst, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &[_]Word{ lhs[0] ^ rhs[0], (lhs[1] ^ rhs[1]) & lastWordMask(nbits) }, &[_]Word{ dst[0], dst[1] & lastWordMask(nbits) });

    bitmap_set(&range, 1, 3);
    bitmap_set(&range, bits_per_long + 1, 2);
    try std.testing.expectEqual(@as(usize, 5), bitmap_weight(&range, nbits));
    bitmap_clear(&range, 1, 3);
    bitmap_clear(&range, bits_per_long + 1, 2);
    try std.testing.expect(empty(&range, nbits));

    const rendered_len = scnprintf(&lhs, nbits, &buffer);
    try std.testing.expectEqual(rendered_len, bitmap_scnprintf(&lhs, nbits, &buffer));
}

test "bitmap double-underscore aliases preserve core helper semantics" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0b1110, (@as(Word, 1) << 2) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0b1010, @as(Word, 1) << 2 };
    var dst = [_]Word{ 0, 0 };
    var range = [_]Word{ 0, 0, 0 };

    try std.testing.expectEqual(weight(&lhs, nbits), __bitmap_weight(&lhs, nbits));

    __bitmap_or(&dst, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &[_]Word{ lhs[0] | rhs[0], (lhs[1] | rhs[1]) & lastWordMask(nbits) }, &[_]Word{ dst[0], dst[1] & lastWordMask(nbits) });

    try std.testing.expect(andBits(&dst, &lhs, &rhs, nbits) == __bitmap_and(&dst, &lhs, &rhs, nbits));
    try std.testing.expect(andNotBits(&dst, &lhs, &rhs, nbits) == __bitmap_andnot(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(equal(&lhs, &rhs, nbits), __bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expectEqual(intersects(&lhs, &rhs, nbits), __bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expectEqual(subset(&rhs, &lhs, nbits), __bitmap_subset(&rhs, &lhs, nbits));

    __bitmap_xor(&dst, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &[_]Word{ lhs[0] ^ rhs[0], (lhs[1] ^ rhs[1]) & lastWordMask(nbits) }, &[_]Word{ dst[0], dst[1] & lastWordMask(nbits) });

    __bitmap_set(&range, 1, 3);
    __bitmap_set(&range, bits_per_long + 1, 2);
    try std.testing.expectEqual(@as(usize, 5), __bitmap_weight(&range, nbits));
    __bitmap_clear(&range, 1, 3);
    __bitmap_clear(&range, bits_per_long + 1, 2);
    try std.testing.expect(empty(&range, nbits));
}

test "bitmap underscore allocator aliases preserve allocation and ownership semantics" {
    const allocator = std.testing.allocator;
    const nbits = bits_per_long + 5;

    var plain: ?[]Word = try bitmap_alloc(allocator, nbits);
    defer bitmap_free(allocator, &plain);
    try std.testing.expectEqual(@as(usize, bitsToWords(nbits)), plain.?.len);
    @memset(plain.?, ~@as(Word, 0));

    var zeroed: ?[]Word = try bitmap_zalloc(allocator, nbits);
    defer bitmap_free(allocator, &zeroed);
    try std.testing.expectEqual(@as(usize, bitsToWords(nbits)), zeroed.?.len);
    for (zeroed.?) |word| {
        try std.testing.expectEqual(@as(Word, 0), word);
    }

    bitmap_free(allocator, &plain);
    try std.testing.expect(plain == null);
    bitmap_free(allocator, &zeroed);
    try std.testing.expect(zeroed == null);
}
