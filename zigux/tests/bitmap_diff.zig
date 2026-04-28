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

// Preserve the Phase 1 artifact anchor while this file carries the newer
// bounded replay checks for the Phase 4 bitmap lane.
// bitmap.scnprintf
fn roundedPrefixLen(nbits: usize) usize {
    return bitmap.bitsToWords(nbits) * bits_per_long;
}

fn fillPrefix(map: []Word, nbits: usize) void {
    bitmap.fill(map[0..bitmap.bitsToWords(nbits)], nbits);
}

fn zeroPrefix(map: []Word, nbits: usize) void {
    bitmap.zero(map[0..bitmap.bitsToWords(nbits)], nbits);
}

fn copyFrom(dst: []Word, src: []const Word, nbits: usize) void {
    bitmap.copyClearTail(dst, src, nbits);
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
    var current = firstSet(map, nbits);
    var index: usize = 0;
    while (current < nbits) {
        if (index == nth) return current;
        index += 1;
        current = find_bit.findNextBit(map, nbits, current + 1);
    }
    return nbits;
}

test "bitmap diff gate replays bounded lib/test_bitmap.c range expectations" {
    var map = [_]Word{0} ** word_count;

    try std.testing.expectEqual(bits_per_long, roundedPrefixLen(35));
    fillPrefix(&map, 35);
    try std.testing.expectEqual(@as(usize, 35), weight(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstSet(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 35), firstZero(&map, bitmap_nbits));
    try expectSet(&map, 34);
    try expectClear(&map, 35);
    // test_fill_set bitmap_fill rounds 35 bits to one full word
    try expectClear(&map, bits_per_long);

    bitmap.fill(&map, bitmap_nbits);
    try std.testing.expectEqual(bits_per_long * 2, roundedPrefixLen(115));
    zeroPrefix(&map, 115);
    try std.testing.expectEqual(@as(usize, bits_per_long * 2), firstSet(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstZero(&map, bitmap_nbits));
    try expectClear(&map, 115);
    // test_zero_clear bitmap_zero rounds 115 bits to two full words
    try expectSet(&map, bits_per_long * 2);
}

test "bitmap diff gate records exact bounded copy checks" {
    const nbits = 109;
    var src = [_]Word{0} ** word_count;
    var dst = [_]Word{0} ** word_count;

    fillPrefix(&src, nbits);
    copyFrom(&dst, &src, nbits);

    try std.testing.expectEqual(@as(usize, nbits), weight(&dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstSet(&dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, nbits), firstZero(&dst, bitmap_nbits));
    try expectSet(&dst, 108);
    // test_copy partial-word tail clearing at 109 bits
    try expectClear(&dst, 109);
    try expectClear(&dst, bitmap_nbits - 1);
}

test "bitmap diff gate records exact bounded find_nth_bit checks" {
    var map = [_]Word{0} ** word_count;
    const starter_population = [_]usize{ 10, 20, 30, 40, 50, 60, 80, 123 };

    for (starter_population) |bit| {
        bitmap.setRange(&map, bit, 1);
    }

    // test_find_nth_bit starter population
    try std.testing.expectEqual(@as(usize, 10), firstSet(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstZero(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, starter_population.len), weight(&map, bitmap_nbits));
    // test_find_nth_bit full-width nth 7
    try std.testing.expectEqual(@as(usize, 123), findNthSet(&map, bitmap_nbits, 7));
    // test_find_nth_bit truncated-width nth 8 returns nbits
    try std.testing.expectEqual(@as(usize, 81), findNthSet(&map, 81, 8));
}
