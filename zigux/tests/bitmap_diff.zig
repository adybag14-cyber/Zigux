const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;
const bitmap_nbits: usize = 1024;
const word_count: usize = bitmap.bitsToWords(bitmap_nbits);

fn expectSet(map: []const Word, bit: usize) !void {
    try std.testing.expect(((map[bit / bits_per_long] >> @intCast(bit % bits_per_long)) & 1) == 1);
}

fn expectClear(map: []const Word, bit: usize) !void {
    try std.testing.expect(((map[bit / bits_per_long] >> @intCast(bit % bits_per_long)) & 1) == 0);
}

fn roundedPrefixLen(prefix_bits: usize) usize {
    return bitmap.bitsToWords(prefix_bits) * bits_per_long;
}

fn fillPrefix(map: []Word, prefix_bits: usize) void {
    bitmap.zero(map, bitmap_nbits);
    bitmap.fill(map[0..bitmap.bitsToWords(prefix_bits)], prefix_bits);
}

fn zeroPrefix(map: []Word, prefix_bits: usize) void {
    bitmap.zero(map[0..bitmap.bitsToWords(prefix_bits)], prefix_bits);
}

fn copyFrom(dst: []Word, src: []const Word, nbits: usize) void {
    bitmap.copy(dst, src, nbits);
}

fn firstSet(map: []const Word, nbits: usize) usize {
    return find_bit.findFirstBit(map, nbits);
}

fn firstZero(map: []const Word, nbits: usize) usize {
    return find_bit.findFirstZeroBit(map, nbits);
}

fn weight(map: []const Word, nbits: usize) usize {
    return bitmap.weight(map, nbits);
}

fn findNthSet(map: []const Word, nbits: usize, nth: usize) usize {
    var bit = firstSet(map, nbits);
    var seen: usize = 0;
    while (bit < nbits) : (bit = find_bit.findNextBit(map, nbits, bit + 1)) {
        if (seen == nth) {
            return bit;
        }
        seen += 1;
    }
    return nbits;
}

test "bitmap diff gate replays bounded lib/test_bitmap.c range expectations" {
    var map = [_]Word{0} ** word_count;

    // test_fill_set bitmap_fill rounds 35 bits to one full word
    try std.testing.expectEqual(bits_per_long, roundedPrefixLen(35));
    fillPrefix(&map, 35);
    try std.testing.expectEqual(@as(usize, 35), weight(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstSet(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 35), firstZero(&map, bitmap_nbits));
    try expectSet(&map, 34);
    try expectClear(&map, 35);
    try expectClear(&map, bits_per_long);

    bitmap.zero(&map, bitmap_nbits);
    bitmap.setRange(&map, 1, 3);
    bitmap.setRange(&map, 7, 1);
    bitmap.setRange(&map, 10, 2);
    var buffer: [64]u8 = undefined;
    const len = bitmap.scnprintf(&map, 32, &buffer);
    try std.testing.expectEqualStrings("1-3,7,10-11", buffer[0..len]);

    var trunc_buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const trunc_len = bitmap.scnprintf(&map, 8, &trunc_buffer);
    try std.testing.expectEqual(@as(usize, 3), trunc_len);
    try std.testing.expectEqualStrings("1-3", trunc_buffer[0..trunc_len]);
    try std.testing.expectEqual(@as(u8, 0), trunc_buffer[trunc_len]);

    bitmap.fill(&map, bitmap_nbits);
    // test_zero_clear bitmap_zero rounds 115 bits to two full words
    try std.testing.expectEqual(bits_per_long * 2, roundedPrefixLen(115));
    zeroPrefix(&map, 115);
    try std.testing.expectEqual(@as(usize, 0), firstZero(&map, bitmap_nbits));
    try std.testing.expectEqual(bitmap_nbits - roundedPrefixLen(115), weight(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2), firstSet(&map, bitmap_nbits));
    try expectClear(&map, 114);
    try expectSet(&map, bits_per_long * 2);
}

test "bitmap diff gate records exact full-width fill and zero endpoints" {
    var map = [_]Word{0} ** word_count;

    bitmap.fill(&map, bitmap_nbits);
    try std.testing.expectEqual(@as(usize, bitmap_nbits), weight(&map, bitmap_nbits));
    try std.testing.expectEqual(bitmap_nbits, firstZero(&map, bitmap_nbits));
    try expectSet(&map, 0);
    try expectSet(&map, bitmap_nbits - 1);

    bitmap.zero(&map, bitmap_nbits);
    try std.testing.expectEqual(@as(usize, 0), weight(&map, bitmap_nbits));
    try std.testing.expectEqual(bitmap_nbits, firstSet(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstZero(&map, bitmap_nbits));
    try expectClear(&map, 0);
    try expectClear(&map, bitmap_nbits - 1);
}

test "bitmap diff gate records exact bounded copy checks" {
    var small_src = [_]Word{ 0, 0 };
    var small_dst = [_]Word{ 0, 0 };
    var src = [_]Word{ 0, 0, 0 };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };

    bitmap.zero(&small_src, bits_per_long * small_src.len);
    bitmap.zero(&small_dst, bits_per_long * small_dst.len);
    bitmap.setRange(&small_src, 0, 19);
    // test_copy single-word copy keeps only the source bits inside a 23-bit window
    copyFrom(&small_dst, &small_src, 23);
    try std.testing.expectEqual(@as(usize, 19), weight(&small_dst, 23));
    try std.testing.expectEqual(@as(usize, 19), firstZero(&small_dst, 23));
    try expectSet(&small_dst, 18);
    try expectClear(&small_dst, 19);
    try expectClear(&small_dst, 22);

    bitmap.zero(&small_dst, bits_per_long * small_dst.len);
    bitmap.setRange(&small_dst, 0, 23);
    // test_copy single-word copy clears the stale tail bits inside the copied window
    copyFrom(&small_dst, &small_src, 23);
    try std.testing.expectEqual(@as(usize, 19), weight(&small_dst, 23));
    try expectSet(&small_dst, 18);
    try expectClear(&small_dst, 19);
    try expectClear(&small_dst, 22);

    bitmap.setRange(&src, 0, 109);
    copyFrom(&dst, &src, bits_per_long * 3);
    try std.testing.expectEqual(@as(usize, 109), weight(&dst, bits_per_long * 3));
    try std.testing.expectEqual(@as(usize, 109), firstZero(&dst, bits_per_long * 3));
    try std.testing.expectEqual(bitmap.lastWordMask(109), dst[1]);
    try std.testing.expectEqual(@as(Word, 0), dst[2]);

    bitmap.fill(&dst, bits_per_long * 3);
    // test_copy full-width copy also clears a pre-filled destination back to the source shape
    copyFrom(&dst, &src, bits_per_long * 3);
    try std.testing.expectEqual(@as(usize, 109), weight(&dst, bits_per_long * 3));
    try std.testing.expectEqual(@as(usize, 109), firstZero(&dst, bits_per_long * 3));
    try std.testing.expectEqual(bitmap.lastWordMask(109), dst[1]);
    try std.testing.expectEqual(@as(Word, 0), dst[2]);

    bitmap.fill(&dst, bits_per_long * 3);
    // test_copy partial-word tail clearing at 109 bits
    copyFrom(&dst, &src, 109);
    try std.testing.expectEqual(@as(usize, 109), weight(dst[0..bitmap.bitsToWords(109)], 109));
    try std.testing.expectEqual(bitmap.lastWordMask(109), dst[1]);
    try std.testing.expectEqual(~@as(Word, 0), dst[2]);

    bitmap.fill(&dst, bits_per_long * 3);
    // test_copy aligned-on-word-length at 97 bits keeps the stale tail word visible
    copyFrom(&dst, &src, 97);
    try std.testing.expectEqual(@as(usize, 109 + bits_per_long), weight(&dst, bits_per_long * 3));
    try expectSet(&dst, 108);
    try expectClear(&dst, 109);
    try expectClear(&dst, bits_per_long * 2 - 1);
    try expectSet(&dst, bits_per_long * 2);

    bitmap.fill(&dst, bits_per_long * 3);
    bitmap.copyClearTail(&dst, &src, 109);
    try std.testing.expectEqual(@as(usize, 109), weight(dst[0..bitmap.bitsToWords(109)], 109));
    try std.testing.expectEqual(bitmap.lastWordMask(109), dst[1]);
    try std.testing.expectEqual(~@as(Word, 0), dst[2]);
}

test "bitmap diff gate records exact bounded find_nth_bit checks" {
    const nth_nbits = bits_per_long * 3;
    var map = [_]Word{ 0, 0, 0 };

    // test_find_nth_bit starter population
    bitmap.setRange(&map, 10, 1);
    bitmap.setRange(&map, 20, 1);
    bitmap.setRange(&map, 30, 1);
    bitmap.setRange(&map, 40, 1);
    bitmap.setRange(&map, 50, 1);
    bitmap.setRange(&map, 60, 1);
    bitmap.setRange(&map, 80, 1);
    bitmap.setRange(&map, 123, 1);

    try std.testing.expectEqual(@as(usize, 10), findNthSet(&map, nth_nbits, 0));
    try std.testing.expectEqual(@as(usize, 20), findNthSet(&map, nth_nbits, 1));
    try std.testing.expectEqual(@as(usize, 30), findNthSet(&map, nth_nbits, 2));
    try std.testing.expectEqual(@as(usize, 40), findNthSet(&map, nth_nbits, 3));
    try std.testing.expectEqual(@as(usize, 50), findNthSet(&map, nth_nbits, 4));
    try std.testing.expectEqual(@as(usize, 60), findNthSet(&map, nth_nbits, 5));
    try std.testing.expectEqual(@as(usize, 80), findNthSet(&map, nth_nbits, 6));
    // test_find_nth_bit full-width nth 7
    try std.testing.expectEqual(@as(usize, 123), findNthSet(&map, nth_nbits, 7));
    // test_find_nth_bit truncated-width nth 8 returns nbits
    try std.testing.expectEqual(nth_nbits, findNthSet(&map, nth_nbits, 8));

    var truncated = map;
    truncated[1] &= ~(@as(Word, 1) << 16);
    try std.testing.expectEqual(@as(usize, 123), findNthSet(&truncated, nth_nbits - 1, 6));
    try std.testing.expectEqual(nth_nbits - 1, findNthSet(&truncated, nth_nbits - 1, 7));
}
