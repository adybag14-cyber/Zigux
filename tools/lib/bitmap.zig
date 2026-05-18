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

pub fn bitmapSize(nbits: usize) usize {
    return bitsToWords(nbits) * @sizeOf(Word);
}

pub fn bitmap_size(nbits: usize) usize {
    return bitmapSize(nbits);
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

pub fn bitmap_zero(dst: []Word, nbits: usize) void {
    zero(dst, nbits);
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

pub fn bitmap_fill(dst: []Word, nbits: usize) void {
    fill(dst, nbits);
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

pub fn bitmap_copy(dst: []Word, src: []const Word, nbits: usize) void {
    copy(dst, src, nbits);
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

pub fn bitmap_copy_clear_tail(dst: []Word, src: []const Word, nbits: usize) void {
    copyClearTail(dst, src, nbits);
}

pub fn bitmap_copy_and_extend(dst: []Word, src: []const Word, count: usize, size: usize) void {
    copyAndExtend(dst, src, count, size);
}

pub fn empty(src: []const Word, nbits: usize) bool {
    assertBitmapLen(src, nbits);
    if (nbits == 0) {
        return true;
    }
    return find_bit.findFirstBit(src, nbits) == nbits;
}

pub fn bitmap_empty(src: []const Word, nbits: usize) bool {
    return empty(src, nbits);
}

pub fn full(src: []const Word, nbits: usize) bool {
    assertBitmapLen(src, nbits);
    if (nbits == 0) {
        return true;
    }
    return find_bit.findFirstZeroBit(src, nbits) == nbits;
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

pub fn bitmap_weight(src: []const Word, nbits: usize) usize {
    return weight(src, nbits);
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

pub fn bitmap_or(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {
    orBits(dst, src1, src2, nbits);
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

pub fn bitmap_xor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {
    xorBits(dst, src1, src2, nbits);
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

pub fn bitmap_and(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {
    return andBits(dst, src1, src2, nbits);
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

pub fn bitmap_andnot(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {
    return andNotBits(dst, src1, src2, nbits);
}

pub fn equal(src1: []const Word, src2: []const Word, nbits: usize) bool {
    assertBitmapLen(src1, nbits);
    assertBitmapLen(src2, nbits);
    if (nbits == 0) {
        return true;
    }

    const lim = nbits / bits_per_long;
    if ((nbits & (bits_per_long - 1)) == 0) {
        return std.mem.eql(Word, src1[0..lim], src2[0..lim]);
    }

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

pub fn bitmap_equal(src1: []const Word, src2: []const Word, nbits: usize) bool {
    return equal(src1, src2, nbits);
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

pub fn bitmap_intersects(src1: []const Word, src2: []const Word, nbits: usize) bool {
    return intersects(src1, src2, nbits);
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

pub fn bitmap_subset(src1: []const Word, src2: []const Word, nbits: usize) bool {
    return subset(src1, src2, nbits);
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

pub fn bitmap_set(map: []Word, start: usize, len: usize) void {
    setRange(map, start, len);
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

pub fn bitmap_clear(map: []Word, start: usize, len: usize) void {
    clearRange(map, start, len);
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

pub fn bitmap_scnprintf(bitmap: []const Word, nbits: usize, buffer: []u8) usize {
    return scnprintf(bitmap, nbits, buffer);
}

pub fn bitmapAlloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {
    return allocator.alloc(Word, bitsToWords(nbits));
}

pub fn bitmap_alloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {
    return bitmapAlloc(allocator, nbits);
}

pub fn bitmapZalloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {
    const map = try bitmapAlloc(allocator, nbits);
    @memset(map, 0);
    return map;
}

pub fn bitmap_zalloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {
    return bitmapZalloc(allocator, nbits);
}

pub fn bitmapFree(allocator: std.mem.Allocator, bitmap: *?[]Word) void {
    if (bitmap.*) |map| {
        allocator.free(map);
        bitmap.* = null;
    }
}

pub fn bitmap_free(allocator: std.mem.Allocator, bitmap: *?[]Word) void {
    bitmapFree(allocator, bitmap);
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

test "bitmap copy alias preserves raw source words without tail clearing" {
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

test "bitmap copy aliases preserve tail clearing and extension semantics" {
    const count = bits_per_long + 5;
    const size = bits_per_long * 3;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), 0 };

    var direct_tail = [_]Word{ 0, 0, 0 };
    var alias_tail = [_]Word{ 0, 0, 0 };
    copyClearTail(&direct_tail, src[0..2], count);
    bitmap_copy_clear_tail(&alias_tail, src[0..2], count);
    try std.testing.expectEqualSlices(Word, &direct_tail, &alias_tail);

    var direct_extend = [_]Word{ 0xaa55, 0xaa55, 0xaa55 };
    var alias_extend = [_]Word{ 0xaa55, 0xaa55, 0xaa55 };
    copyAndExtend(&direct_extend, src[0..2], count, size);
    bitmap_copy_and_extend(&alias_extend, src[0..2], count, size);
    try std.testing.expectEqualSlices(Word, &direct_extend, &alias_extend);
}

test "bitmap copy and extend handles zero and aligned counts" {
    var zero_src = [_]Word{0x1234};
    var zero_dst = [_]Word{0xbeef};

    copyAndExtend(zero_dst[0..0], zero_src[0..0], 0, 0);
    try std.testing.expectEqual(@as(Word, 0xbeef), zero_dst[0]);

    const count = bits_per_long * 2;
    const size = bits_per_long * 3;
    const src = [_]Word{ 0x55aa, 0xaa55, ~@as(Word, 0) };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };

    copyAndExtend(&dst, &src, count, size);
    try std.testing.expectEqual(src[0], dst[0]);
    try std.testing.expectEqual(src[1], dst[1]);
    try std.testing.expectEqual(@as(Word, 0), dst[2]);
}

test "bitmap copy helpers keep zero-sized destination views untouched" {
    var src = [_]Word{~@as(Word, 0)};
    var copy_dst = [_]Word{0x55aa};
    var clear_dst = [_]Word{0xaa55};
    var extend_dst = [_]Word{0xf0f0};

    copy(copy_dst[0..0], src[0..0], 0);
    try std.testing.expectEqual(@as(Word, 0x55aa), copy_dst[0]);

    copyClearTail(clear_dst[0..0], src[0..0], 0);
    try std.testing.expectEqual(@as(Word, 0xaa55), clear_dst[0]);

    copyAndExtend(extend_dst[0..0], src[0..0], 0, 0);
    try std.testing.expectEqual(@as(Word, 0xf0f0), extend_dst[0]);
}

test "bitmap zero-bit logical helpers stay explicit" {
    const lhs = [_]Word{~@as(Word, 0)};
    const rhs = [_]Word{0x1234};
    var and_dst = [_]Word{0x55aa};
    var andnot_dst = [_]Word{0xaa55};
    var buffer = [_]u8{ 0xcc, 0xcc, 0xcc };

    try std.testing.expect(!andBits(and_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(@as(Word, 0x55aa), and_dst[0]);

    try std.testing.expect(!andNotBits(andnot_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(@as(Word, 0xaa55), andnot_dst[0]);

    try std.testing.expect(empty(lhs[0..0], 0));
    try std.testing.expect(full(lhs[0..0], 0));
    try std.testing.expectEqual(@as(usize, 0), weight(lhs[0..0], 0));
    try std.testing.expect(equal(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(!intersects(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(subset(lhs[0..0], rhs[0..0], 0));

    const len = scnprintf(lhs[0..0], 0, &buffer);
    try std.testing.expectEqual(@as(usize, 0), len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 0xcc }, &buffer);
}

test "bitmap equal fast path ignores storage beyond an exact word boundary" {
    const nbits = bits_per_long;
    const lhs = [_]Word{ 0b1011, @as(Word, 1) << 7 };
    const rhs = [_]Word{ 0b1011, @as(Word, 1) << 13 };
    const changed = [_]Word{ 0b1001, lhs[1] };

    try std.testing.expect(equal(&lhs, &rhs, nbits));
    try std.testing.expect(!equal(&lhs, &changed, nbits));
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

test "bitmap full empty and weight ignore out-of-range tail bits" {
    const nbits = bits_per_long + 5;
    const out_of_range_noise = (@as(Word, 1) << 8) | (@as(Word, 1) << 11);
    const full_map = [_]Word{ ~@as(Word, 0), lastWordMask(nbits) | out_of_range_noise };
    const empty_map = [_]Word{ 0, out_of_range_noise };
    const one_bit_map = [_]Word{ 0, (@as(Word, 1) << 2) | out_of_range_noise };

    try std.testing.expect(full(&full_map, nbits));
    try std.testing.expectEqual(bits_per_long + 5, weight(&full_map, nbits));

    try std.testing.expect(empty(&empty_map, nbits));
    try std.testing.expectEqual(@as(usize, 0), weight(&empty_map, nbits));

    try std.testing.expect(!empty(&one_bit_map, nbits));
    try std.testing.expect(!full(&one_bit_map, nbits));
    try std.testing.expectEqual(@as(usize, 1), weight(&one_bit_map, nbits));
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

test "bitmap or keeps caller-selected bit window" {
    const lhs = [_]Word{0b1_0011};
    const rhs = [_]Word{0b1_1100};
    var dst = [_]Word{0};

    orBits(&dst, &lhs, &rhs, 4);
    try std.testing.expectEqual(@as(Word, 0b1111), dst[0] & lastWordMask(4));
}

test "bitmap or across a multiword tail still lets callers clamp the last word" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0b10_0101, 0b10_0010 };
    const rhs = [_]Word{ 0b01_1000, 0b01_0101 };
    var dst = [_]Word{ 0, 0 };

    orBits(&dst, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0b11_1101, 0b01_0111 }, &[_]Word{ dst[0], dst[1] & lastWordMask(nbits) });
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

test "bitmap scnprintf keeps contiguous ranges merged across word boundaries" {
    const nbits = bits_per_long + 8;
    var map = [_]Word{ 0, 0 };
    setRange(&map, bits_per_long - 2, 5);
    setRange(&map, bits_per_long + 6, 1);

    var buffer: [64]u8 = undefined;
    const len = scnprintf(&map, nbits, &buffer);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{ bits_per_long - 2, bits_per_long + 2, bits_per_long + 6 },
    );
    try std.testing.expectEqualStrings(expected_text, buffer[0..len]);
}

test "bitmap scnprintf truncates and keeps a terminator slot" {
    var map = [_]Word{0};
    setRange(&map, 1, 3);

    var buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const len = scnprintf(&map, 8, &buffer);
    try std.testing.expectEqual(@as(usize, 3), len);
    try std.testing.expectEqualStrings("1-3", buffer[0..len]);
    try std.testing.expectEqual(@as(u8, 0), buffer[len]);
}

test "bitmap scnprintf handles terminator-only and zero-length caller views" {
    var map = [_]Word{0};
    setRange(&map, 1, 3);

    var terminator_only = [_]u8{0xaa};
    const terminator_only_len = scnprintf(&map, 8, terminator_only[0..1]);
    try std.testing.expectEqual(@as(usize, 0), terminator_only_len);
    try std.testing.expectEqual(@as(u8, 0), terminator_only[0]);

    var zero_length_backing = [_]u8{0xbb};
    const zero_length_len = scnprintf(&map, 8, zero_length_backing[0..0]);
    try std.testing.expectEqual(@as(usize, 0), zero_length_len);
    try std.testing.expectEqual(@as(u8, 0xbb), zero_length_backing[0]);
}

test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap" {
    const map = [_]Word{0};
    var buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };

    const len = scnprintf(&map, 8, &buffer);
    try std.testing.expectEqual(@as(usize, 0), len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa, 0xaa }, &buffer);
}

test "bitmap Linux-style aliases mirror copy logical range and format helpers" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0b1110, (@as(Word, 1) << 2) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0b1010, (@as(Word, 1) << 2) | (@as(Word, 1) << 11) };
    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    copy(&direct, &lhs, nbits);
    bitmap_copy(&alias, &lhs, nbits);
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    orBits(&direct, &lhs, &rhs, nbits);
    bitmap_or(&alias, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    xorBits(&direct, &lhs, &rhs, nbits);
    bitmap_xor(&alias, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    try std.testing.expectEqual(andBits(&direct, &lhs, &rhs, nbits), bitmap_and(&alias, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    try std.testing.expectEqual(andNotBits(&direct, &lhs, &rhs, nbits), bitmap_andnot(&alias, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    try std.testing.expectEqual(equal(&lhs, &rhs, nbits), bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expectEqual(intersects(&lhs, &rhs, nbits), bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expectEqual(subset(&rhs, &lhs, nbits), bitmap_subset(&rhs, &lhs, nbits));

    var direct_range = [_]Word{ 0, 0 };
    var alias_range = [_]Word{ 0, 0 };
    setRange(&direct_range, 1, 3);
    bitmap_set(&alias_range, 1, 3);
    try std.testing.expectEqualSlices(Word, &direct_range, &alias_range);

    clearRange(&direct_range, 2, 1);
    bitmap_clear(&alias_range, 2, 1);
    try std.testing.expectEqualSlices(Word, &direct_range, &alias_range);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = scnprintf(&direct_range, nbits, &direct_buffer);
    const alias_len = bitmap_scnprintf(&alias_range, nbits, &alias_buffer);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);
}

test "bitmap Linux-style aliases mirror size state and allocation helpers" {
    const allocator = std.testing.allocator;
    const nbits = bits_per_long + 5;

    try std.testing.expectEqual(bitmapSize(nbits), bitmap_size(nbits));

    var direct = [_]Word{ 0xaa55, 0xaa55 };
    var alias = [_]Word{ 0xaa55, 0xaa55 };
    zero(&direct, nbits);
    bitmap_zero(&alias, nbits);
    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expectEqual(empty(&direct, nbits), bitmap_empty(&alias, nbits));

    fill(&direct, nbits);
    bitmap_fill(&alias, nbits);
    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expectEqual(full(&direct, nbits), bitmap_full(&alias, nbits));
    try std.testing.expectEqual(weight(&direct, nbits), bitmap_weight(&alias, nbits));

    var plain_direct: ?[]Word = try bitmapAlloc(allocator, nbits);
    defer bitmapFree(allocator, &plain_direct);
    var plain_alias: ?[]Word = try bitmap_alloc(allocator, nbits);
    defer bitmap_free(allocator, &plain_alias);
    try std.testing.expectEqual(plain_direct.?.len, plain_alias.?.len);

    var zeroed_direct: ?[]Word = try bitmapZalloc(allocator, nbits);
    defer bitmapFree(allocator, &zeroed_direct);
    var zeroed_alias: ?[]Word = try bitmap_zalloc(allocator, nbits);
    defer bitmap_free(allocator, &zeroed_alias);
    try std.testing.expectEqual(zeroed_direct.?.len, zeroed_alias.?.len);
    for (zeroed_alias.?) |word| {
        try std.testing.expectEqual(@as(Word, 0), word);
    }

    bitmap_free(allocator, &plain_alias);
    bitmap_free(allocator, &zeroed_alias);
    try std.testing.expect(plain_alias == null);
    try std.testing.expect(zeroed_alias == null);
}

test "bitmap allocation helpers size zero fill and reset optionals" {
    const allocator = std.testing.allocator;
    const nbits = bits_per_long + 5;

    try std.testing.expectEqual(@as(usize, 0), bitmapSize(0));
    try std.testing.expectEqual(@as(usize, @sizeOf(Word)), bitmapSize(1));
    try std.testing.expectEqual(@as(usize, @sizeOf(Word)), bitmapSize(bits_per_long));
    try std.testing.expectEqual(@as(usize, @sizeOf(Word) * 2), bitmapSize(nbits));

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
