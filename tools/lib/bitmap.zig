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

pub fn sizeBytes(nbits: usize) usize {
    return bitsToWords(nbits) * @sizeOf(Word);
}

pub fn bitmap_size(nbits: usize) usize {
    return sizeBytes(nbits);
}

fn assertBitmapLen(bitmap: []const Word, nbits: usize) void {
    std.debug.assert(bitmap.len >= bitsToWords(nbits));
}

pub fn alloc(allocator: std.mem.Allocator, nbits: usize) !?[]Word {
    const nwords = bitsToWords(nbits);
    if (nwords == 0) {
        return null;
    }

    return try allocator.alloc(Word, nwords);
}

pub fn bitmap_alloc(allocator: std.mem.Allocator, nbits: usize) !?[]Word {
    return alloc(allocator, nbits);
}

pub fn zalloc(allocator: std.mem.Allocator, nbits: usize) !?[]Word {
    const nwords = bitsToWords(nbits);
    if (nwords == 0) {
        return null;
    }

    const bitmap = try allocator.alloc(Word, nwords);
    @memset(bitmap, 0);
    return bitmap;
}

pub fn bitmap_zalloc(allocator: std.mem.Allocator, nbits: usize) !?[]Word {
    return zalloc(allocator, nbits);
}

pub fn free(allocator: std.mem.Allocator, bitmap: *?[]Word) void {
    if (bitmap.*) |slice| {
        allocator.free(slice);
    }
    bitmap.* = null;
}

pub fn bitmap_free(allocator: std.mem.Allocator, bitmap: *?[]Word) void {
    free(allocator, bitmap);
}

pub fn zero(dst: []Word, nbits: usize) void {
    assertBitmapLen(dst, nbits);

    const nwords = bitsToWords(nbits);
    if (nwords == 0) {
        return;
    }

    @memset(dst[0..nwords], 0);
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

pub fn empty(src: []const Word, nbits: usize) bool {
    assertBitmapLen(src, nbits);
    return find_bit.findFirstBit(src, nbits) == nbits;
}

pub fn bitmap_empty(src: []const Word, nbits: usize) bool {
    return empty(src, nbits);
}

pub fn full(src: []const Word, nbits: usize) bool {
    assertBitmapLen(src, nbits);
    return find_bit.findFirstZeroBit(src, nbits) == nbits;
}

pub fn bitmap_full(src: []const Word, nbits: usize) bool {
    return full(src, nbits);
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

pub fn weightedOr(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {
    orBits(dst, src1, src2, nbits);
    return weight(dst, nbits);
}

pub fn bitmap_weighted_or(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {
    return weightedOr(dst, src1, src2, nbits);
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

pub fn weightedXor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {
    xorBits(dst, src1, src2, nbits);
    return weight(dst, nbits);
}

pub fn bitmap_weighted_xor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {
    return weightedXor(dst, src1, src2, nbits);
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

pub fn bitmap_and(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {
    return andBits(dst, src1, src2, nbits);
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

pub fn bitmap_andnot(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {
    return andNotBits(dst, src1, src2, nbits);
}

pub fn complement(dst: []Word, src: []const Word, nbits: usize) void {
    assertBitmapLen(dst, nbits);
    assertBitmapLen(src, nbits);

    const lim = nbits / bits_per_long;
    for (0..lim) |idx| {
        dst[idx] = ~src[idx];
    }

    if ((nbits & (bits_per_long - 1)) != 0) {
        dst[lim] = ~src[lim] & lastWordMask(nbits);
    }
}

pub fn bitmap_complement(dst: []Word, src: []const Word, nbits: usize) void {
    complement(dst, src, nbits);
}

pub fn replace(dst: []Word, old: []const Word, new: []const Word, mask: []const Word, nbits: usize) void {
    assertBitmapLen(dst, nbits);
    assertBitmapLen(old, nbits);
    assertBitmapLen(new, nbits);
    assertBitmapLen(mask, nbits);

    const lim = nbits / bits_per_long;
    for (0..lim) |idx| {
        dst[idx] = (old[idx] & ~mask[idx]) | (new[idx] & mask[idx]);
    }

    if ((nbits & (bits_per_long - 1)) != 0) {
        const idx = lim;
        dst[idx] = ((old[idx] & ~mask[idx]) | (new[idx] & mask[idx])) & lastWordMask(nbits);
    }
}

pub fn bitmap_replace(dst: []Word, old: []const Word, new: []const Word, mask: []const Word, nbits: usize) void {
    replace(dst, old, new, mask, nbits);
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

pub fn bitmap_equal(src1: []const Word, src2: []const Word, nbits: usize) bool {
    return equal(src1, src2, nbits);
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

pub fn bitmap_intersects(src1: []const Word, src2: []const Word, nbits: usize) bool {
    return intersects(src1, src2, nbits);
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

pub fn bitmap_subset(src1: []const Word, src2: []const Word, nbits: usize) bool {
    return subset(src1, src2, nbits);
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

pub fn bitmap_set(map: []Word, start: usize, len: usize) void {
    setRange(map, start, len);
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

pub fn bitmap_clear(map: []Word, start: usize, len: usize) void {
    clearRange(map, start, len);
}

pub fn copy(dst: []Word, src: []const Word, nbits: usize) void {
    assertBitmapLen(dst, nbits);
    assertBitmapLen(src, nbits);

    const nwords = bitsToWords(nbits);
    if (nwords == 0) {
        return;
    }

    @memcpy(dst[0..nwords], src[0..nwords]);
}

pub fn bitmap_copy(dst: []Word, src: []const Word, nbits: usize) void {
    copy(dst, src, nbits);
}

pub fn copyClearTail(dst: []Word, src: []const Word, nbits: usize) void {
    assertBitmapLen(dst, nbits);
    assertBitmapLen(src, nbits);

    const nwords = bitsToWords(nbits);
    if (nwords == 0) {
        return;
    }

    @memcpy(dst[0..nwords], src[0..nwords]);
    if ((nbits & (bits_per_long - 1)) != 0) {
        dst[nwords - 1] &= lastWordMask(nbits);
    }
}

pub fn bitmap_copy_clear_tail(dst: []Word, src: []const Word, nbits: usize) void {
    copyClearTail(dst, src, nbits);
}

pub fn copyAndExtend(dst: []Word, src: []const Word, count: usize, size: usize) void {
    std.debug.assert(size >= count);
    assertBitmapLen(dst, size);
    assertBitmapLen(src, count);

    const copy_words = bitsToWords(count);
    if (copy_words != 0) {
        @memcpy(dst[0..copy_words], src[0..copy_words]);
        if ((count & (bits_per_long - 1)) != 0) {
            dst[copy_words - 1] &= lastWordMask(count);
        }
    }

    @memset(dst[copy_words..bitsToWords(size)], 0);
}

pub fn bitmap_copy_and_extend(dst: []Word, src: []const Word, count: usize, size: usize) void {
    copyAndExtend(dst, src, count, size);
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

    if (nbits == 0) {
        return 0;
    }

    var written: usize = 0;
    var first = true;
    var range_bottom = find_bit.findFirstBit(bitmap, nbits);

    if (range_bottom == nbits) {
        return 0;
    }

    while (range_bottom < nbits) {
        const next_zero = find_bit.findNextZeroBit(bitmap, nbits, range_bottom + 1);
        const range_top = if (next_zero == nbits) nbits - 1 else next_zero - 1;

        if (!first) {
            appendSlice(buffer, &written, ",");
        }
        first = false;

        appendUnsigned(buffer, &written, range_bottom);
        if (range_bottom < range_top) {
            appendSlice(buffer, &written, "-");
            appendUnsigned(buffer, &written, range_top);
        }

        if (next_zero == nbits) {
            break;
        }

        range_bottom = find_bit.findNextBit(bitmap, nbits, next_zero + 1);
    }

    if (buffer.len != 0 and written < buffer.len) {
        buffer[written] = 0;
    }

    return written;
}

pub fn bitmap_scnprintf(bitmap_words: []const Word, nbits: usize, buffer: []u8) usize {
    return scnprintf(bitmap_words, nbits, buffer);
}

test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap" {
    var map = [_]Word{0};
    var buffer = [_]u8{ 0xaa, 0xbb, 0xcc };

    const len = scnprintf(&map, 32, &buffer);
    try std.testing.expectEqual(@as(usize, 0), len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xbb, 0xcc }, &buffer);
}

test "bitmap allocator helpers size zero and free their buffers" {
    const allocator = std.testing.allocator;
    const nbits = bits_per_long + 5;

    var allocated = try alloc(allocator, nbits);
    defer free(allocator, &allocated);
    try std.testing.expect(allocated != null);
    try std.testing.expectEqual(bitsToWords(nbits), allocated.?.len);

    var zero_allocated = try zalloc(allocator, nbits);
    defer free(allocator, &zero_allocated);
    try std.testing.expect(zero_allocated != null);
    try std.testing.expectEqual(bitsToWords(nbits), zero_allocated.?.len);
    for (zero_allocated.?) |word| {
        try std.testing.expectEqual(@as(Word, 0), word);
    }

    free(allocator, &zero_allocated);
    try std.testing.expect(zero_allocated == null);

    const empty_alloc = try alloc(allocator, 0);
    try std.testing.expect(empty_alloc == null);
    const empty_zalloc = try zalloc(allocator, 0);
    try std.testing.expect(empty_zalloc == null);
}

test "bitmap size aliases round bit counts to full words in bytes" {
    try std.testing.expectEqual(@as(usize, 0), sizeBytes(0));
    try std.testing.expectEqual(@sizeOf(Word), sizeBytes(1));
    try std.testing.expectEqual(@sizeOf(Word), bitmap_size(bits_per_long));
    try std.testing.expectEqual(2 * @sizeOf(Word), sizeBytes(bits_per_long + 1));
    try std.testing.expectEqual(sizeBytes(bits_per_long + 5), bitmap_size(bits_per_long + 5));
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

test "bitmap range helpers honor exact first-word boundaries" {
    const start = bits_per_long - 3;
    var map = [_]Word{ 0, ~@as(Word, 0) };

    setRange(&map, start, 3);
    try std.testing.expectEqual(firstWordMask(start), map[0]);
    try std.testing.expectEqual(~@as(Word, 0), map[1]);

    clearRange(&map, start, 3);
    try std.testing.expectEqual(@as(Word, 0), map[0]);
    try std.testing.expectEqual(~@as(Word, 0), map[1]);
}

test "bitmap range helpers clamp the final partial word" {
    const start = bits_per_long + 2;
    const len = 3;

    var set_map = [_]Word{ 0, 0 };
    setRange(&set_map, start, len);
    try std.testing.expectEqual(@as(Word, 0), set_map[0]);
    try std.testing.expectEqual(@as(Word, 0b1_1100), set_map[1]);

    var clear_map = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    clearRange(&clear_map, start, len);
    try std.testing.expectEqual(~@as(Word, 0), clear_map[0]);
    try std.testing.expectEqual(~@as(Word, 0b1_1100), clear_map[1]);
}

test "bitmap fill clamps tail bits in partial words" {
    const nbits = bits_per_long + 5;
    var map = [_]Word{ 0, 0 };

    fill(&map, nbits);
    try std.testing.expectEqual(@as(Word, ~@as(Word, 0)), map[0]);
    try std.testing.expectEqual(lastWordMask(nbits), map[1]);

    map[1] = ~@as(Word, 0);
    try std.testing.expect(full(&map, nbits));
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

test "bitmap and andnot clamp tail bits in partial words" {
    const nbits = bits_per_long + 5;
    const in_range_and_tail = [_]Word{ 0, (@as(Word, 1) << 2) | (@as(Word, 1) << 9) };
    const shared_in_range_and_tail = [_]Word{ 0, (@as(Word, 1) << 2) | (@as(Word, 1) << 9) };
    const clear_in_range_only = [_]Word{ 0, @as(Word, 1) << 2 };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };

    try std.testing.expect(andBits(&dst, &in_range_and_tail, &shared_in_range_and_tail, nbits));
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, @as(Word, 1) << 2 }, &dst);

    try std.testing.expect(!andNotBits(&dst, &in_range_and_tail, &clear_in_range_only, nbits));
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, 0 }, &dst);
}

test "bitmap complement clamps tail bits and alias mirrors the primary helper" {
    const nbits = bits_per_long + 5;
    const src = [_]Word{ ~@as(Word, 0), (@as(Word, 1) << 2) | (@as(Word, 1) << 9) };
    var primary_dst = [_]Word{ 0, 0 };
    var alias_dst = [_]Word{ 0, 0 };

    complement(&primary_dst, &src, nbits);
    bitmap_complement(&alias_dst, &src, nbits);

    try std.testing.expectEqualSlices(Word, &primary_dst, &alias_dst);
    try std.testing.expectEqual(@as(Word, 0), primary_dst[0]);
    try std.testing.expectEqual(@as(Word, 0b1_1011), primary_dst[1]);
}

test "bitmap predicates ignore out-of-range tail bits" {
    const nbits = bits_per_long + 5;
    const in_range_only = [_]Word{ 0, @as(Word, 1) << 2 };
    const with_tail_bits = [_]Word{ 0, (@as(Word, 1) << 2) | (@as(Word, 1) << 9) };
    const tail_only = [_]Word{ 0, @as(Word, 1) << 9 };

    try std.testing.expect(equal(&in_range_only, &with_tail_bits, nbits));
    try std.testing.expect(!intersects(&in_range_only, &tail_only, nbits));
    try std.testing.expect(subset(&in_range_only, &with_tail_bits, nbits));
    try std.testing.expect(subset(&with_tail_bits, &in_range_only, nbits));
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

test "bitmap scnprintf collapses contiguous ranges across word boundaries" {
    const start = bits_per_long - 1;
    const len_bits = bits_per_long + 3;
    const later_bit = bits_per_long * 2 + 5;
    const nbits = later_bit + 1;
    var map = [_]Word{ 0, 0, 0 };
    setRange(&map, start, len_bits);
    setRange(&map, later_bit, 1);

    var buffer: [64]u8 = undefined;
    const written = scnprintf(&map, nbits, &buffer);

    var expected_buffer: [64]u8 = undefined;
    const expected = try std.fmt.bufPrint(&expected_buffer, "{d}-{d},{d}", .{ start, start + len_bits - 1, later_bit });
    try std.testing.expectEqualStrings(expected, buffer[0..written]);
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

test "bitmap scnprintf handles terminator-only and zero-length caller views" {
    var map = [_]Word{0};
    setRange(&map, 9, 1);

    var terminator_only = [_]u8{0xaa};
    const terminator_only_len = scnprintf(&map, 32, &terminator_only);
    try std.testing.expectEqual(@as(usize, 0), terminator_only_len);
    try std.testing.expectEqual(@as(u8, 0), terminator_only[0]);

    var zero_length_backing = [_]u8{0xaa};
    const zero_length_len = scnprintf(&map, 32, zero_length_backing[0..0]);
    try std.testing.expectEqual(@as(usize, 0), zero_length_len);
    try std.testing.expectEqual(@as(u8, 0xaa), zero_length_backing[0]);
}

test "bitmap copy alias preserves raw source words without tail clearing" {
    const count = bits_per_long + 5;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };

    var copied = [_]Word{ 0, 0 };
    copy(&copied, &src, count);
    try std.testing.expectEqual(@as(Word, ~@as(Word, 0)), copied[0]);
    try std.testing.expectEqual(@as(Word, ~@as(Word, 0)), copied[1]);

    var alias_copied = [_]Word{ 0, 0 };
    bitmap_copy(&alias_copied, &src, count);
    try std.testing.expectEqualSlices(Word, &copied, &alias_copied);

    var cleared = [_]Word{ 0, 0 };
    bitmap_copy_clear_tail(&cleared, &src, count);
    try std.testing.expectEqual(lastWordMask(count), cleared[1]);
}

test "bitmap copy aliases preserve tail clearing and extension semantics" {
    const count = bits_per_long + 5;
    const size = bits_per_long * 3;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };

    var cleared = [_]Word{ 0, 0, 0 };
    bitmap_copy_clear_tail(&cleared, &src, count);
    try std.testing.expectEqual(@as(Word, ~@as(Word, 0)), cleared[0]);
    try std.testing.expectEqual(lastWordMask(count), cleared[1]);

    var extended = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    bitmap_copy_and_extend(&extended, &src, count, size);
    try std.testing.expectEqual(@as(Word, ~@as(Word, 0)), extended[0]);
    try std.testing.expectEqual(lastWordMask(count), extended[1]);
    try std.testing.expectEqual(@as(Word, 0), extended[2]);
}

test "bitmap copy and extend handles zero and aligned counts" {
    const aligned_count = bits_per_long;
    const size = bits_per_long * 3;
    const src = [_]Word{ 0x0123_4567_89ab_cdef, ~@as(Word, 0), ~@as(Word, 0) };

    var zero_extended = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    copyAndExtend(&zero_extended, &[_]Word{}, 0, size);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, 0, 0 }, &zero_extended);

    var alias_zero_extended = [_]Word{ 1, 2, 3 };
    bitmap_copy_and_extend(&alias_zero_extended, &[_]Word{}, 0, size);
    try std.testing.expectEqualSlices(Word, &zero_extended, &alias_zero_extended);

    var aligned_cleared = [_]Word{0};
    copyClearTail(&aligned_cleared, src[0..1], aligned_count);
    try std.testing.expectEqual(src[0], aligned_cleared[0]);

    var alias_aligned_cleared = [_]Word{0};
    bitmap_copy_clear_tail(&alias_aligned_cleared, src[0..1], aligned_count);
    try std.testing.expectEqualSlices(Word, &aligned_cleared, &alias_aligned_cleared);

    var aligned_extended = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    copyAndExtend(&aligned_extended, src[0..1], aligned_count, size);
    try std.testing.expectEqualSlices(Word, &[_]Word{ src[0], 0, 0 }, &aligned_extended);

    var alias_aligned_extended = [_]Word{ 0, 1, 2 };
    bitmap_copy_and_extend(&alias_aligned_extended, src[0..1], aligned_count, size);
    try std.testing.expectEqualSlices(Word, &aligned_extended, &alias_aligned_extended);
}

test "bitmap copy helpers keep zero-sized destination views untouched" {
    const copy_src = [_]Word{0x0123_4567_89ab_cdef};

    var cleared_backing = [_]Word{0x55aa_55aa_55aa_55aa};
    copyClearTail(cleared_backing[0..0], copy_src[0..0], 0);
    try std.testing.expectEqual(@as(Word, 0x55aa_55aa_55aa_55aa), cleared_backing[0]);

    var alias_cleared_backing = [_]Word{0x1122_3344_5566_7788};
    bitmap_copy_clear_tail(alias_cleared_backing[0..0], copy_src[0..0], 0);
    try std.testing.expectEqual(@as(Word, 0x1122_3344_5566_7788), alias_cleared_backing[0]);

    var extended_backing = [_]Word{0xf0f0_f0f0_f0f0_f0f0};
    copyAndExtend(extended_backing[0..0], &[_]Word{}, 0, 0);
    try std.testing.expectEqual(@as(Word, 0xf0f0_f0f0_f0f0_f0f0), extended_backing[0]);

    var alias_extended_backing = [_]Word{0x0f0f_0f0f_0f0f_0f0f};
    bitmap_copy_and_extend(alias_extended_backing[0..0], &[_]Word{}, 0, 0);
    try std.testing.expectEqual(@as(Word, 0x0f0f_0f0f_0f0f_0f0f), alias_extended_backing[0]);
}

test "bitmap copy and extend leaves words past the requested size untouched" {
    const count = bits_per_long + 5;
    const size = bits_per_long * 3;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), 0x0123_4567_89ab_cdef };
    const sentinel = @as(Word, 0x55aa_55aa_55aa_55aa);

    var extended_backing = [_]Word{ 0, 0, 0, sentinel };
    copyAndExtend(extended_backing[0..], src[0..2], count, size);
    try std.testing.expectEqual(@as(Word, ~@as(Word, 0)), extended_backing[0]);
    try std.testing.expectEqual(lastWordMask(count), extended_backing[1]);
    try std.testing.expectEqual(@as(Word, 0), extended_backing[2]);
    try std.testing.expectEqual(sentinel, extended_backing[3]);

    var alias_extended_backing = [_]Word{ 1, 2, 3, sentinel };
    bitmap_copy_and_extend(alias_extended_backing[0..], src[0..2], count, size);
    try std.testing.expectEqualSlices(Word, extended_backing[0..3], alias_extended_backing[0..3]);
    try std.testing.expectEqual(sentinel, alias_extended_backing[3]);
}

test "bitmap zero-bit helpers stay explicit no-ops" {
    var dst = [_]Word{0x55aa55aa55aa55aa};
    const src1 = [_]Word{0xffff0000ffff0000};
    const src2 = [_]Word{0x0000ffff0000ffff};
    const copy_src = [_]Word{0x0123456789abcdef};
    const before = dst[0];

    zero(dst[0..0], 0);
    try std.testing.expectEqual(before, dst[0]);

    orBits(dst[0..0], src1[0..0], src2[0..0], 0);
    try std.testing.expectEqual(before, dst[0]);

    xorBits(dst[0..0], src1[0..0], src2[0..0], 0);
    try std.testing.expectEqual(before, dst[0]);

    copy(dst[0..0], copy_src[0..0], 0);
    try std.testing.expectEqual(before, dst[0]);

    try std.testing.expect(empty(&[_]Word{}, 0));
    try std.testing.expect(full(&[_]Word{}, 0));
    try std.testing.expectEqual(@as(usize, 0), weight(&[_]Word{}, 0));

    var buffer = [_]u8{0xaa};
    const rendered = scnprintf(&[_]Word{}, 0, &buffer);
    try std.testing.expectEqual(@as(usize, 0), rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), buffer[0]);
}

test "bitmap zero-bit binary helpers stay explicit identity operations" {
    const lhs = [_]Word{0xffff_0000_ffff_0000};
    const rhs = [_]Word{0x0000_ffff_0000_ffff};
    const mask = [_]Word{~@as(Word, 0)};

    var primary_dst = [_]Word{0x55aa_55aa_55aa_55aa};
    var alias_dst = [_]Word{0x55aa_55aa_55aa_55aa};
    const before = primary_dst[0];

    try std.testing.expectEqual(andBits(primary_dst[0..0], lhs[0..0], rhs[0..0], 0), bitmap_and(alias_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(@as(bool, false), andBits(primary_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(before, primary_dst[0]);
    try std.testing.expectEqual(before, alias_dst[0]);

    try std.testing.expectEqual(andNotBits(primary_dst[0..0], lhs[0..0], rhs[0..0], 0), bitmap_andnot(alias_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(@as(bool, false), andNotBits(primary_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(before, primary_dst[0]);
    try std.testing.expectEqual(before, alias_dst[0]);

    complement(primary_dst[0..0], lhs[0..0], 0);
    bitmap_complement(alias_dst[0..0], lhs[0..0], 0);
    try std.testing.expectEqual(before, primary_dst[0]);
    try std.testing.expectEqual(before, alias_dst[0]);

    replace(primary_dst[0..0], lhs[0..0], rhs[0..0], mask[0..0], 0);
    bitmap_replace(alias_dst[0..0], lhs[0..0], rhs[0..0], mask[0..0], 0);
    try std.testing.expectEqual(before, primary_dst[0]);
    try std.testing.expectEqual(before, alias_dst[0]);

    try std.testing.expect(equal(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(bitmap_equal(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(!intersects(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(!bitmap_intersects(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(subset(lhs[0..0], rhs[0..0], 0));
    try std.testing.expect(bitmap_subset(lhs[0..0], rhs[0..0], 0));
}

test "bitmap Linux-style aliases keep zero-bit windows explicit no-ops" {
    const allocator = std.testing.allocator;
    const lhs = [_]Word{0xffff_0000_ffff_0000};
    const rhs = [_]Word{0x0000_ffff_0000_ffff};
    const copy_src = [_]Word{0x0123_4567_89ab_cdef};

    var empty_alloc = try bitmap_alloc(allocator, 0);
    try std.testing.expect(empty_alloc == null);
    bitmap_free(allocator, &empty_alloc);
    try std.testing.expect(empty_alloc == null);

    var empty_zalloc = try bitmap_zalloc(allocator, 0);
    try std.testing.expect(empty_zalloc == null);
    bitmap_free(allocator, &empty_zalloc);
    try std.testing.expect(empty_zalloc == null);

    var zero_dst = [_]Word{0x55aa_55aa_55aa_55aa};
    const before = zero_dst[0];

    bitmap_zero(zero_dst[0..0], 0);
    try std.testing.expectEqual(before, zero_dst[0]);

    bitmap_or(zero_dst[0..0], lhs[0..0], rhs[0..0], 0);
    try std.testing.expectEqual(before, zero_dst[0]);

    bitmap_xor(zero_dst[0..0], lhs[0..0], rhs[0..0], 0);
    try std.testing.expectEqual(before, zero_dst[0]);

    try std.testing.expectEqual(@as(usize, 0), weightedOr(zero_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(before, zero_dst[0]);
    try std.testing.expectEqual(@as(usize, 0), bitmap_weighted_or(zero_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(before, zero_dst[0]);

    try std.testing.expectEqual(@as(usize, 0), weightedXor(zero_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(before, zero_dst[0]);
    try std.testing.expectEqual(@as(usize, 0), bitmap_weighted_xor(zero_dst[0..0], lhs[0..0], rhs[0..0], 0));
    try std.testing.expectEqual(before, zero_dst[0]);

    bitmap_copy(zero_dst[0..0], copy_src[0..0], 0);
    try std.testing.expectEqual(before, zero_dst[0]);

    var buffer = [_]u8{0xaa};
    const rendered = bitmap_scnprintf(&[_]Word{}, 0, &buffer);
    try std.testing.expectEqual(@as(usize, 0), rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), buffer[0]);
}

test "bitmap Linux-style aliases mirror the primary helper surface" {
    const allocator = std.testing.allocator;
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ ~@as(Word, 0), (@as(Word, 1) << 2) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0x0f, (@as(Word, 1) << 2) };
    const replace_old = [_]Word{ ~@as(Word, 0), (@as(Word, 1) << 1) | (@as(Word, 1) << 9) };
    const replace_new = [_]Word{ 0x0f, (@as(Word, 1) << 2) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const replace_mask = [_]Word{ 0xff, (@as(Word, 1) << 2) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };

    var allocated = try bitmap_alloc(allocator, nbits);
    defer bitmap_free(allocator, &allocated);
    try std.testing.expectEqual(try alloc(allocator, 0) == null, try bitmap_alloc(allocator, 0) == null);
    try std.testing.expect(allocated != null);

    var zero_allocated = try bitmap_zalloc(allocator, nbits);
    defer bitmap_free(allocator, &zero_allocated);
    try std.testing.expect(zero_allocated != null);
    for (zero_allocated.?) |word| {
        try std.testing.expectEqual(@as(Word, 0), word);
    }

    var primary_map = [_]Word{ 0, 0 };
    var alias_map = [_]Word{ 0, 0 };
    setRange(&primary_map, 1, 3);
    bitmap_set(&alias_map, 1, 3);
    setRange(&primary_map, bits_per_long + 2, 2);
    bitmap_set(&alias_map, bits_per_long + 2, 2);
    try std.testing.expectEqualSlices(Word, &primary_map, &alias_map);
    clearRange(&primary_map, 1, 3);
    bitmap_clear(&alias_map, 1, 3);
    clearRange(&primary_map, bits_per_long + 2, 2);
    bitmap_clear(&alias_map, bits_per_long + 2, 2);
    try std.testing.expectEqualSlices(Word, &primary_map, &alias_map);

    fill(&primary_map, nbits);
    bitmap_fill(&alias_map, nbits);
    try std.testing.expectEqualSlices(Word, &primary_map, &alias_map);
    zero(&primary_map, nbits);
    bitmap_zero(&alias_map, nbits);
    try std.testing.expectEqualSlices(Word, &primary_map, &alias_map);

    try std.testing.expectEqual(weight(&lhs, nbits), bitmap_weight(&lhs, nbits));
    try std.testing.expectEqual(empty(&[_]Word{ 0, 0 }, nbits), bitmap_empty(&[_]Word{ 0, 0 }, nbits));
    try std.testing.expectEqual(full(&[_]Word{ ~@as(Word, 0), lastWordMask(nbits) }, nbits), bitmap_full(&[_]Word{ ~@as(Word, 0), lastWordMask(nbits) }, nbits));

    var primary_dst = [_]Word{ 0, 0 };
    var alias_dst = [_]Word{ 0, 0 };
    orBits(&primary_dst, &lhs, &rhs, nbits);
    bitmap_or(&alias_dst, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &primary_dst, &alias_dst);

    const primary_or_weight = weightedOr(&primary_dst, &lhs, &rhs, nbits);
    const alias_or_weight = bitmap_weighted_or(&alias_dst, &lhs, &rhs, nbits);
    try std.testing.expectEqual(primary_or_weight, alias_or_weight);
    try std.testing.expectEqual(weight(&primary_dst, nbits), primary_or_weight);
    try std.testing.expectEqualSlices(Word, &primary_dst, &alias_dst);

    xorBits(&primary_dst, &lhs, &rhs, nbits);
    bitmap_xor(&alias_dst, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &primary_dst, &alias_dst);

    const primary_xor_weight = weightedXor(&primary_dst, &lhs, &rhs, nbits);
    const alias_xor_weight = bitmap_weighted_xor(&alias_dst, &lhs, &rhs, nbits);
    try std.testing.expectEqual(primary_xor_weight, alias_xor_weight);
    try std.testing.expectEqual(weight(&primary_dst, nbits), primary_xor_weight);
    try std.testing.expectEqualSlices(Word, &primary_dst, &alias_dst);

    try std.testing.expectEqual(andBits(&primary_dst, &lhs, &rhs, nbits), bitmap_and(&alias_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &primary_dst, &alias_dst);

    try std.testing.expectEqual(andNotBits(&primary_dst, &lhs, &rhs, nbits), bitmap_andnot(alias_dst[0..], lhs[0..], rhs[0..], nbits));
    try std.testing.expectEqualSlices(Word, &primary_dst, &alias_dst);

    complement(&primary_dst, &lhs, nbits);
    bitmap_complement(&alias_dst, &lhs, nbits);
    try std.testing.expectEqualSlices(Word, &primary_dst, &alias_dst);

    replace(&primary_dst, &replace_old, &replace_new, &replace_mask, nbits);
    bitmap_replace(&alias_dst, &replace_old, &replace_new, &replace_mask, nbits);
    try std.testing.expectEqualSlices(Word, &primary_dst, &alias_dst);
    try std.testing.expectEqual(@as(Word, 0x0f), primary_dst[0]);
    try std.testing.expectEqual(@as(Word, 0b1_0110), primary_dst[1]);

    try std.testing.expectEqual(equal(&lhs, &rhs, nbits), bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expectEqual(intersects(&lhs, &rhs, nbits), bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expectEqual(subset(&rhs, &lhs, nbits), bitmap_subset(&rhs, &lhs, nbits));

    var primary_buffer: [32]u8 = undefined;
    var alias_buffer: [32]u8 = undefined;
    const primary_len = scnprintf(&lhs, nbits, &primary_buffer);
    const alias_len = bitmap_scnprintf(&lhs, nbits, &alias_buffer);
    try std.testing.expectEqual(primary_len, alias_len);
    try std.testing.expectEqualStrings(primary_buffer[0..primary_len], alias_buffer[0..alias_len]);
}
