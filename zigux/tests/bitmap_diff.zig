const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;
const bitmap_nbits: usize = 1024;
const word_count: usize = bitmap.bitsToWords(bitmap_nbits);
const exp1 = [_]Word{
    0x1,
    0x2,
    0x0000ffff,
    0xffff0000,
    0x55555555,
    0xaaaaaaaa,
    0x11111111,
    0x22222222,
    0xffffffff,
    0xfffffffe,
    0x3333333311111111,
    0xffffffff77777777,
    0x0,
    0x00008000,
    0x80000000,
};

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

fn expectPrintedList(map: []const Word, nbits: usize, expected: []const u8) !void {
    var buffer: [128]u8 = undefined;
    const len = bitmap.scnprintf(map, nbits, &buffer);
    try std.testing.expectEqualStrings(expected, buffer[0..len]);
}

fn expectCurrentFillPrefix(
    map: []Word,
    prefix_bits: usize,
    expected_weight: usize,
    expected_list: []const u8,
) !void {
    bitmap.zero(map, bitmap_nbits);
    fillPrefix(map, prefix_bits);
    try std.testing.expectEqual(expected_weight, weight(map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstSet(map, bitmap_nbits));
    try std.testing.expectEqual(expected_weight, firstZero(map, bitmap_nbits));
    try expectPrintedList(map, bitmap_nbits, expected_list);
    try expectSet(map, expected_weight - 1);
    try expectClear(map, expected_weight);
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

const ThresholdReplaySummary = struct {
    iterations: usize,
    checksum: u64,
    final_weight: usize,
    final_first_set: usize,
    final_first_zero: usize,
    final_nth_seven: usize,
    final_render_len: usize,
};

fn mixThresholdChecksum(checksum: *u64, value: usize) void {
    checksum.* = checksum.* *% 0x9e3779b185ebca87 +% @as(u64, @intCast(value));
}

// Keep one deterministic batch available so a future bitmap threshold lane can
// benchmark the exact current rollback gate instead of a looser synthetic loop.
pub fn runThresholdReplay(iterations: usize) ThresholdReplaySummary {
    var map = [_]Word{0} ** word_count;
    var src = [_]Word{0} ** word_count;
    var dst = [_]Word{0} ** word_count;
    var buffer: [64]u8 = undefined;
    var checksum: u64 = 0;
    var render_len: usize = 0;

    var iteration: usize = 0;
    while (iteration < iterations) : (iteration += 1) {
        bitmap.zero(&map, bitmap_nbits);
        bitmap.setRange(&map, 0, 9);
        mixThresholdChecksum(&checksum, weight(&map, bitmap_nbits));
        mixThresholdChecksum(&checksum, firstZero(&map, bitmap_nbits));

        bitmap.fill(&map, bitmap_nbits);
        zeroPrefix(&map, 115);
        mixThresholdChecksum(&checksum, weight(&map, bitmap_nbits));
        mixThresholdChecksum(&checksum, firstSet(&map, bitmap_nbits));

        bitmap.zero(&src, bitmap_nbits);
        bitmap.setRange(&src, 0, 109);
        bitmap.fill(&dst, bitmap_nbits);
        copyFrom(&dst, &src, 97);
        mixThresholdChecksum(&checksum, weight(&dst, bitmap_nbits));
        mixThresholdChecksum(&checksum, firstZero(&dst, bitmap_nbits));

        bitmap.zero(&map, bitmap_nbits);
        bitmap.setRange(&map, 1, 3);
        bitmap.setRange(&map, 7, 1);
        bitmap.setRange(&map, 10, 2);
        render_len = bitmap.scnprintf(&map, 32, &buffer);
        mixThresholdChecksum(&checksum, render_len);
        mixThresholdChecksum(&checksum, @as(usize, buffer[0]));

        bitmap.zero(&map, bits_per_long * 3);
        bitmap.setRange(&map, 10, 1);
        bitmap.setRange(&map, 20, 1);
        bitmap.setRange(&map, 30, 1);
        bitmap.setRange(&map, 40, 1);
        bitmap.setRange(&map, 50, 1);
        bitmap.setRange(&map, 60, 1);
        bitmap.setRange(&map, 80, 1);
        bitmap.setRange(&map, 123, 1);
        mixThresholdChecksum(&checksum, findNthSet(&map, bits_per_long * 3, 7));
        mixThresholdChecksum(&checksum, findNthSet(&map, bits_per_long * 3, 8));
    }

    return .{
        .iterations = iterations,
        .checksum = checksum,
        .final_weight = weight(&map, bits_per_long * 3),
        .final_first_set = firstSet(&map, bits_per_long * 3),
        .final_first_zero = firstZero(&map, bits_per_long * 3),
        .final_nth_seven = findNthSet(&map, bits_per_long * 3, 7),
        .final_render_len = render_len,
    };
}

test "bitmap diff gate records exact starting printlist anchors" {
    var map = [_]Word{0} ** word_count;

    bitmap.fill(&map, bitmap_nbits);
    // test_zero_clear starts from a known all-bits-set state in both truncated and full-width views
    try expectPrintedList(&map, 23, "0-22");
    try expectPrintedList(&map, bitmap_nbits, "0-1023");

    bitmap.zero(&map, bitmap_nbits);
    // test_fill_set starts from a known empty state in both truncated and full-width views
    try expectPrintedList(&map, 23, "");
    try expectPrintedList(&map, bitmap_nbits, "");
}

fn expectNthMatchesSequentialWalk(map: []const Word, nbits: usize) !void {
    var nth: usize = 0;
    var bit = firstSet(map, nbits);
    while (bit < nbits) : (bit = find_bit.findNextBit(map, nbits, bit + 1)) {
        try std.testing.expectEqual(bit, findNthSet(map, nbits, nth));
        nth += 1;
    }
    try std.testing.expectEqual(nbits, findNthSet(map, nbits, nth));
}

test "bitmap diff gate replays bounded lib/test_bitmap.c range expectations" {
    var map = [_]Word{0} ** word_count;

    bitmap.zero(&map, bitmap_nbits);
    // test_fill_set single-word bitmap_set keeps the exact 0..8 prefix
    bitmap.setRange(&map, 0, 9);
    try std.testing.expectEqual(@as(usize, 9), weight(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstSet(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 9), firstZero(&map, bitmap_nbits));
    try expectPrintedList(&map, bitmap_nbits, "0-8");
    try expectSet(&map, 8);
    try expectClear(&map, 9);

    bitmap.fill(&map, bitmap_nbits);
    // test_zero_clear single-word bitmap_clear keeps the exact 9..1023 suffix
    bitmap.clearRange(&map, 0, 9);
    try std.testing.expectEqual(bitmap_nbits - 9, weight(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 9), firstSet(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstZero(&map, bitmap_nbits));
    try expectPrintedList(&map, bitmap_nbits, "9-1023");
    try expectClear(&map, 8);
    try expectSet(&map, 9);

    // The shipped Zig helper still keeps bitmap_fill(35) at the requested whole-word-rounded prefix boundary.
    // bitmap_fill() matches the Linux rounded whole-word contract at the 35-bit edge.
    try std.testing.expectEqual(bits_per_long, roundedPrefixLen(35));
    try expectCurrentFillPrefix(&map, 35, roundedPrefixLen(35), "0-63");
    try expectSet(&map, 35);
    try expectSet(&map, bits_per_long - 1);
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
    // test_zero_clear bitmap_zero rounds 35 bits to one full word without disturbing the next word
    try std.testing.expectEqual(bits_per_long, roundedPrefixLen(35));
    zeroPrefix(&map, 35);
    try std.testing.expectEqual(@as(usize, 0), firstZero(&map, bitmap_nbits));
    try std.testing.expectEqual(bitmap_nbits - bits_per_long, weight(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long), firstSet(&map, bitmap_nbits));
    try expectPrintedList(&map, bitmap_nbits, "64-1023");
    try expectClear(&map, 35);
    try expectClear(&map, bits_per_long - 1);
    try expectSet(&map, bits_per_long);

    bitmap.fill(&map, bitmap_nbits);
    // test_zero_clear bitmap_zero rounds 115 bits to two full words
    try std.testing.expectEqual(bits_per_long * 2, roundedPrefixLen(115));
    zeroPrefix(&map, 115);
    try std.testing.expectEqual(@as(usize, 0), firstZero(&map, bitmap_nbits));
    try std.testing.expectEqual(bitmap_nbits - roundedPrefixLen(115), weight(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2), firstSet(&map, bitmap_nbits));
    try expectPrintedList(&map, bitmap_nbits, "128-1023");
    try expectClear(&map, 114);
    try expectSet(&map, bits_per_long * 2);
}

test "bitmap diff survey keeps the current rounded fill drifts explicit against lib/test_bitmap.c and records the resolved 115-bit fill parity" {
    var map = [_]Word{0} ** word_count;

    // No longer true that the current Zig helper stops at bit 114; the 115-bit fill now rounds to the Linux two-word anchor.
    // The Linux anchor rounds fill(115) to two whole words and the Zig helper now matches it.
    try std.testing.expectEqual(bits_per_long * 2, roundedPrefixLen(115));
    try expectCurrentFillPrefix(&map, 115, roundedPrefixLen(115), "0-127");
    try expectSet(&map, 114);
    try expectSet(&map, 115);
    try expectSet(&map, bits_per_long * 2 - 1);
}

test "bitmap diff gate records exact cross-boundary set and clear checks" {
    var map = [_]Word{0} ** word_count;

    bitmap.setRange(&map, 0, 64);
    // test_fill_set bitmap_set crosses the 79..97 window without disturbing the gap
    bitmap.setRange(&map, 79, 19);
    try expectPrintedList(&map, bitmap_nbits, "0-63,79-97");
    try std.testing.expectEqual(@as(usize, 83), weight(&map, bitmap_nbits));
    try expectSet(&map, 63);
    try expectClear(&map, 64);
    try expectSet(&map, 79);
    try expectSet(&map, 97);
    try expectClear(&map, 98);

    bitmap.fill(&map, 115);
    // test_fill_set carried-forward bitmap_fill(115) from the exact 0-63,79-97 anchor state closes back over the gap to 0-127
    try std.testing.expectEqual(@as(usize, roundedPrefixLen(115)), weight(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstSet(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, roundedPrefixLen(115)), firstZero(&map, bitmap_nbits));
    try expectPrintedList(&map, bitmap_nbits, "0-127");
    try expectSet(&map, 114);
    try expectSet(&map, 115);
    try expectSet(&map, bits_per_long * 2 - 1);
    try expectClear(&map, bits_per_long * 2);

    bitmap.fill(&map, bitmap_nbits);
    zeroPrefix(&map, 35);
    // test_zero_clear bitmap_clear crosses the 79..97 window from the exact 64..1023 anchor state
    try expectPrintedList(&map, bitmap_nbits, "64-1023");
    bitmap.clearRange(&map, 79, 19);
    try expectPrintedList(&map, bitmap_nbits, "64-78,98-1023");
    try std.testing.expectEqual(bitmap_nbits - bits_per_long - 19, weight(&map, bitmap_nbits));
    try expectClear(&map, 63);
    try expectSet(&map, 64);
    try expectSet(&map, 78);
    try expectClear(&map, 79);
    try expectClear(&map, 97);
    try expectSet(&map, 98);
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

test "bitmap diff gate keeps zero-nbits bitmap helpers as explicit no-ops" {
    var map = [_]Word{ 0xaaaa, 0xbbbb };
    const src = [_]Word{ 0x5555, 0xcccc };
    const lhs = [_]Word{ 0x1357, 0x2468 };
    const rhs = [_]Word{ 0xf0f0, 0x0f0f };
    var buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };

    bitmap.setRange(&map, 0, 0);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0xaaaa, 0xbbbb }, &map);

    bitmap.clearRange(&map, 0, 0);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0xaaaa, 0xbbbb }, &map);

    bitmap.zero(&map, 0);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0xaaaa, 0xbbbb }, &map);

    bitmap.fill(&map, 0);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0xaaaa, 0xbbbb }, &map);

    copyFrom(&map, &src, 0);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0xaaaa, 0xbbbb }, &map);

    bitmap.copyClearTail(&map, &src, 0);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0xaaaa, 0xbbbb }, &map);

    bitmap.orBits(&map, &lhs, &rhs, 0);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0xaaaa, 0xbbbb }, &map);

    bitmap.xorBits(&map, &lhs, &rhs, 0);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0xaaaa, 0xbbbb }, &map);

    try std.testing.expect(!bitmap.andBits(&map, &lhs, &rhs, 0));
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0xaaaa, 0xbbbb }, &map);

    try std.testing.expect(!bitmap.andNotBits(&map, &lhs, &rhs, 0));
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0xaaaa, 0xbbbb }, &map);

    try std.testing.expectEqual(@as(usize, 0), firstSet(&[_]Word{}, 0));
    try std.testing.expectEqual(@as(usize, 0), firstZero(&[_]Word{}, 0));
    try std.testing.expectEqual(@as(usize, 0), weight(&[_]Word{}, 0));
    try expectPrintedList(&[_]Word{}, 0, "");
    try std.testing.expectEqual(@as(usize, 0), bitmap.scnprintf(&[_]Word{}, 0, &buffer));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa, 0xaa }, &buffer);
}

test "bitmap diff gate keeps zero-length range edits from changing populated anchors" {
    var map = [_]Word{0} ** word_count;

    bitmap.zero(&map, bitmap_nbits);
    bitmap.setRange(&map, 5, 4);
    bitmap.setRange(&map, 70, 3);
    try std.testing.expectEqual(@as(usize, 7), weight(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 5), firstSet(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstZero(&map, bitmap_nbits));
    try expectPrintedList(&map, bitmap_nbits, "5-8,70-72");

    bitmap.setRange(&map, 0, 0);
    bitmap.setRange(&map, 6, 0);
    bitmap.clearRange(&map, 0, 0);
    bitmap.clearRange(&map, 71, 0);
    try std.testing.expectEqual(@as(usize, 7), weight(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 5), firstSet(&map, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstZero(&map, bitmap_nbits));
    try expectPrintedList(&map, bitmap_nbits, "5-8,70-72");
    try expectClear(&map, 4);
    try expectSet(&map, 5);
    try expectSet(&map, 8);
    try expectClear(&map, 9);
    try expectClear(&map, 69);
    try expectSet(&map, 70);
    try expectSet(&map, 72);
    try expectClear(&map, 73);
}

test "bitmap diff gate records exact bounded copy checks" {
    const copy_nbits = bits_per_long * 3;
    var small_src = [_]Word{ 0, 0 };
    var small_dst = [_]Word{ 0, 0 };
    var anchor_src = [_]Word{0} ** word_count;
    var anchor_dst = [_]Word{0} ** word_count;
    var wide_src = [_]Word{0} ** word_count;
    var wide_dst = [_]Word{0} ** word_count;
    var src = [_]Word{ 0, 0, 0 };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };

    bitmap.zero(&small_src, bits_per_long * small_src.len);
    bitmap.zero(&small_dst, bits_per_long * small_dst.len);
    bitmap.setRange(&small_src, 0, 19);
    // test_copy single-word copy keeps only the source bits inside a 23-bit window
    copyFrom(&small_dst, &small_src, 23);
    try std.testing.expectEqual(@as(usize, 19), weight(&small_dst, 23));
    try std.testing.expectEqual(@as(usize, 19), firstZero(&small_dst, 23));
    try expectPrintedList(&small_dst, 23, "0-18");
    try expectSet(&small_dst, 18);
    try expectClear(&small_dst, 19);
    try expectClear(&small_dst, 22);
    try std.testing.expectEqual(@as(Word, 0), small_dst[1]);

    bitmap.zero(&small_dst, bits_per_long * small_dst.len);
    small_dst[1] = ~@as(Word, 0);
    bitmap.setRange(&small_dst, 0, 23);
    // test_copy single-word copy clears the stale tail bits inside the copied window while leaving the next word untouched
    copyFrom(&small_dst, &small_src, 23);
    try std.testing.expectEqual(@as(usize, 19), weight(&small_dst, 23));
    try expectPrintedList(&small_dst, 23, "0-18");
    try expectSet(&small_dst, 18);
    try expectClear(&small_dst, 19);
    try expectClear(&small_dst, 22);
    try std.testing.expectEqual(~@as(Word, 0), small_dst[1]);

    bitmap.zero(&anchor_src, bitmap_nbits);
    bitmap.zero(&anchor_dst, bitmap_nbits);
    bitmap.setRange(&anchor_src, 0, 19);
    // test_copy exact 1024-bit anchor replay for the 23-bit single-word window from a cleared destination
    copyFrom(&anchor_dst, &anchor_src, 23);
    try std.testing.expectEqual(@as(usize, 19), weight(&anchor_dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstSet(&anchor_dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 19), firstZero(&anchor_dst, bitmap_nbits));
    try expectPrintedList(&anchor_dst, bitmap_nbits, "0-18");
    try expectSet(&anchor_dst, 18);
    try expectClear(&anchor_dst, 19);
    try expectClear(&anchor_dst, bitmap_nbits - 1);

    bitmap.zero(&anchor_dst, bitmap_nbits);
    bitmap.setRange(&anchor_dst, 0, 23);
    // test_copy exact 1024-bit anchor replay for the 23-bit single-word window from the partially populated destination in lib/test_bitmap.c
    copyFrom(&anchor_dst, &anchor_src, 23);
    try std.testing.expectEqual(@as(usize, 19), weight(&anchor_dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstSet(&anchor_dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 19), firstZero(&anchor_dst, bitmap_nbits));
    try expectPrintedList(&anchor_dst, bitmap_nbits, "0-18");
    try expectSet(&anchor_dst, 18);
    try expectClear(&anchor_dst, 19);
    try expectClear(&anchor_dst, bitmap_nbits - 1);

    bitmap.setRange(&anchor_src, 19, 90);
    // test_copy exact 1024-bit anchor replay for the first multi-word copy from the carried-forward partial destination in lib/test_bitmap.c
    copyFrom(&anchor_dst, &anchor_src, bitmap_nbits);
    try std.testing.expectEqual(@as(usize, 109), weight(&anchor_dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstSet(&anchor_dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 109), firstZero(&anchor_dst, bitmap_nbits));
    try expectPrintedList(&anchor_dst, bitmap_nbits, "0-108");
    try expectSet(&anchor_dst, 108);
    try expectClear(&anchor_dst, 109);
    try expectClear(&anchor_dst, bitmap_nbits - 1);

    bitmap.zero(&wide_src, bitmap_nbits);
    bitmap.zero(&wide_dst, bitmap_nbits);
    // test_copy full-width copy keeps an empty source empty from a cleared destination
    copyFrom(&wide_dst, &wide_src, bitmap_nbits);
    try std.testing.expectEqual(@as(usize, 0), weight(&wide_dst, bitmap_nbits));
    try std.testing.expectEqual(bitmap_nbits, firstSet(&wide_dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstZero(&wide_dst, bitmap_nbits));
    try expectPrintedList(&wide_dst, bitmap_nbits, "");
    try expectClear(&wide_dst, 0);
    try expectClear(&wide_dst, bitmap_nbits - 1);

    bitmap.fill(&wide_dst, bitmap_nbits);
    // test_copy full-width copy keeps an empty source empty from a filled destination
    copyFrom(&wide_dst, &wide_src, bitmap_nbits);
    try std.testing.expectEqual(@as(usize, 0), weight(&wide_dst, bitmap_nbits));
    try std.testing.expectEqual(bitmap_nbits, firstSet(&wide_dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstZero(&wide_dst, bitmap_nbits));
    try expectPrintedList(&wide_dst, bitmap_nbits, "");
    try expectClear(&wide_dst, 0);
    try expectClear(&wide_dst, bitmap_nbits - 1);

    bitmap.setRange(&wide_src, 0, 109);
    // test_copy full-width copy from a cleared destination replays the exact source window
    copyFrom(&wide_dst, &wide_src, bitmap_nbits);
    try std.testing.expectEqual(@as(usize, 109), weight(&wide_dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstSet(&wide_dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 109), firstZero(&wide_dst, bitmap_nbits));
    try expectPrintedList(&wide_dst, bitmap_nbits, "0-108");
    try expectSet(&wide_dst, 108);
    try expectClear(&wide_dst, 109);
    try expectClear(&wide_dst, bitmap_nbits - 1);

    bitmap.fill(&wide_dst, bitmap_nbits);
    // test_copy filled-destination copies also drop stale tail bits
    copyFrom(&wide_dst, &wide_src, bitmap_nbits);
    try std.testing.expectEqual(@as(usize, 109), weight(&wide_dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 0), firstSet(&wide_dst, bitmap_nbits));
    try std.testing.expectEqual(@as(usize, 109), firstZero(&wide_dst, bitmap_nbits));
    try expectPrintedList(&wide_dst, bitmap_nbits, "0-108");
    try expectSet(&wide_dst, 108);
    try expectClear(&wide_dst, 109);
    try expectClear(&wide_dst, bitmap_nbits - 1);

    bitmap.fill(&wide_dst, bitmap_nbits);
    // test_copy 109-bit partial-tail replay keeps the stale tail visible through bit 1023
    copyFrom(&wide_dst, &wide_src, 109);
    try std.testing.expectEqual(@as(usize, 109), weight(wide_dst[0..bitmap.bitsToWords(109)], 109));
    try std.testing.expectEqual(@as(usize, 109 + (bitmap_nbits - bits_per_long * 2)), weight(&wide_dst, bitmap_nbits));
    try expectPrintedList(&wide_dst, bitmap_nbits, "0-108,128-1023");
    try std.testing.expectEqual(bitmap.lastWordMask(109), wide_dst[1]);
    try std.testing.expectEqual(~@as(Word, 0), wide_dst[2]);
    try expectSet(&wide_dst, 108);
    try expectClear(&wide_dst, 109);
    try expectClear(&wide_dst, bits_per_long * 2 - 1);
    try expectSet(&wide_dst, bits_per_long * 2);
    try expectSet(&wide_dst, bitmap_nbits - 1);

    bitmap.fill(&wide_dst, bitmap_nbits);
    // test_copy 97-bit aligned-copy replay keeps the stale tail visible through bit 1023
    copyFrom(&wide_dst, &wide_src, 97);
    try std.testing.expectEqual(@as(usize, 109 + (bitmap_nbits - bits_per_long * 2)), weight(&wide_dst, bitmap_nbits));
    try expectPrintedList(&wide_dst, bitmap_nbits, "0-108,128-1023");
    try std.testing.expectEqual(bitmap.lastWordMask(109), wide_dst[1]);
    try std.testing.expectEqual(~@as(Word, 0), wide_dst[2]);
    try expectSet(&wide_dst, 108);
    try expectClear(&wide_dst, 109);
    try expectClear(&wide_dst, bits_per_long * 2 - 1);
    try expectSet(&wide_dst, bits_per_long * 2);
    try expectSet(&wide_dst, bitmap_nbits - 1);

    bitmap.fill(&wide_dst, bitmap_nbits);
    // test_copy_clear_tail `bitmap.copyClearTail()` keeps the 109-bit cleared-tail contract explicit through bit 1023
    bitmap.copyClearTail(&wide_dst, &wide_src, 109);
    try std.testing.expectEqual(@as(usize, 109), weight(wide_dst[0..bitmap.bitsToWords(109)], 109));
    try std.testing.expectEqual(@as(usize, 109 + (bitmap_nbits - bits_per_long * 2)), weight(&wide_dst, bitmap_nbits));
    try expectPrintedList(&wide_dst, bitmap_nbits, "0-108,128-1023");
    try std.testing.expectEqual(bitmap.lastWordMask(109), wide_dst[1]);
    try std.testing.expectEqual(~@as(Word, 0), wide_dst[2]);
    try expectSet(&wide_dst, 108);
    try expectClear(&wide_dst, 109);
    try expectClear(&wide_dst, bits_per_long * 2 - 1);
    try expectSet(&wide_dst, bits_per_long * 2);
    try expectSet(&wide_dst, bitmap_nbits - 1);

    bitmap.fill(&wide_dst, bitmap_nbits);
    // test_copy_clear_tail aligned-on-word-length at 97 bits clears the copied-word tail while leaving later untouched words visible
    bitmap.copyClearTail(&wide_dst, &wide_src, 97);
    try std.testing.expectEqual(@as(usize, 97), weight(wide_dst[0..bitmap.bitsToWords(97)], 97));
    try std.testing.expectEqual(@as(usize, 97 + (bitmap_nbits - bits_per_long * 2)), weight(&wide_dst, bitmap_nbits));
    try expectPrintedList(&wide_dst, bitmap_nbits, "0-96,128-1023");
    try std.testing.expectEqual(bitmap.lastWordMask(97), wide_dst[1]);
    try std.testing.expectEqual(~@as(Word, 0), wide_dst[2]);
    try expectSet(&wide_dst, 96);
    try expectClear(&wide_dst, 97);
    try expectClear(&wide_dst, bits_per_long * 2 - 1);
    try expectSet(&wide_dst, bits_per_long * 2);
    try expectSet(&wide_dst, bitmap_nbits - 1);

    bitmap.setRange(&src, 0, 109);
    copyFrom(&dst, &src, copy_nbits);
    try std.testing.expectEqual(@as(usize, 109), weight(&dst, copy_nbits));
    try std.testing.expectEqual(@as(usize, 109), firstZero(&dst, copy_nbits));
    try expectPrintedList(&dst, copy_nbits, "0-108");

    bitmap.fill(&dst, copy_nbits);
    // test_copy partial-word tail clearing at 109 bits
    copyFrom(&dst, &src, 109);
    try std.testing.expectEqual(@as(usize, 109), weight(dst[0..bitmap.bitsToWords(109)], 109));
    try expectPrintedList(&dst, copy_nbits, "0-108,128-191");
    try std.testing.expectEqual(bitmap.lastWordMask(109), dst[1]);
    try std.testing.expectEqual(~@as(Word, 0), dst[2]);
    try expectSet(&dst, 108);
    try expectClear(&dst, 109);
    try expectClear(&dst, bits_per_long * 2 - 1);
    try expectSet(&dst, bits_per_long * 2);

    bitmap.fill(&dst, copy_nbits);
    // test_copy aligned-on-word-length at 97 bits keeps the stale tail word visible
    copyFrom(&dst, &src, 97);
    try std.testing.expectEqual(@as(usize, 109 + bits_per_long), weight(&dst, copy_nbits));
    try expectPrintedList(&dst, copy_nbits, "0-108,128-191");
    try std.testing.expectEqual(bitmap.lastWordMask(109), dst[1]);
    try std.testing.expectEqual(~@as(Word, 0), dst[2]);
    try expectSet(&dst, 108);
    try expectClear(&dst, 109);
    try expectClear(&dst, bits_per_long * 2 - 1);
    try expectSet(&dst, bits_per_long * 2);

    bitmap.fill(&dst, copy_nbits);
    // test_copy_clear_tail keeps the 109-bit cleared-tail contract explicit
    bitmap.copyClearTail(&dst, &src, 109);
    try std.testing.expectEqual(@as(usize, 109), weight(dst[0..bitmap.bitsToWords(109)], 109));
    try expectPrintedList(&dst, copy_nbits, "0-108,128-191");
    try std.testing.expectEqual(bitmap.lastWordMask(109), dst[1]);
    try std.testing.expectEqual(~@as(Word, 0), dst[2]);
    try expectSet(&dst, 108);
    try expectClear(&dst, 109);
    try expectClear(&dst, bits_per_long * 2 - 1);
    try expectSet(&dst, bits_per_long * 2);
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
    // test_find_nth_bit full-width nth-7 and nth-8 outcomes
    try std.testing.expectEqual(@as(usize, 123), findNthSet(&map, nth_nbits, 7));
    // test_find_nth_bit truncated-width nth 8 returns nbits
    try std.testing.expectEqual(nth_nbits, findNthSet(&map, nth_nbits, 8));
    // test_find_nth_bit reduced-width replay still keeps bit 123 for nth 7
    try std.testing.expectEqual(@as(usize, 123), findNthSet(&map, nth_nbits - 1, 7));
    // test_find_nth_bit reduced-width replay returns the cutoff width for nth 8
    try std.testing.expectEqual(nth_nbits - 1, findNthSet(&map, nth_nbits - 1, 8));

    var truncated = map;
    truncated[1] &= ~(@as(Word, 1) << 16);
    try std.testing.expectEqual(@as(usize, 123), findNthSet(&truncated, nth_nbits - 1, 6));
    try std.testing.expectEqual(nth_nbits - 1, findNthSet(&truncated, nth_nbits - 1, 7));

    // test_find_nth_bit exp1 walk keeps nth lookups aligned with the dense
    // mixed-word set-bit scan used by the C anchor's sequential replay.
    try expectNthMatchesSequentialWalk(&exp1, exp1.len * bits_per_long);
}

test "bitmap diff gate keeps a deterministic threshold replay batch ready for future perf baselines" {
    const single = runThresholdReplay(1);
    const repeated = runThresholdReplay(4);

    try std.testing.expectEqual(@as(usize, 1), single.iterations);
    try std.testing.expectEqual(@as(usize, 4), repeated.iterations);
    try std.testing.expectEqual(@as(usize, 8), single.final_weight);
    try std.testing.expectEqual(@as(usize, 10), single.final_first_set);
    try std.testing.expectEqual(@as(usize, 0), single.final_first_zero);
    try std.testing.expectEqual(@as(usize, 123), single.final_nth_seven);
    try std.testing.expectEqual(@as(usize, 11), single.final_render_len);
    try std.testing.expect(single.checksum != 0);
    try std.testing.expect(repeated.checksum != 0);
    try std.testing.expect(repeated.checksum != single.checksum);
    try std.testing.expectEqualDeep(repeated, runThresholdReplay(4));
}
