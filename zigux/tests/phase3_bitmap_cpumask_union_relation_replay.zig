const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const word_count = 3;
const capacity = word_bits * 2 + 11;

fn bitMask(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn setBit(words: *[word_count]Word, bit_index: usize) void {
    words[bit_index / word_bits] |= bitMask(bit_index);
}

fn clearBit(words: *[word_count]Word, bit_index: usize) void {
    words[bit_index / word_bits] &= ~bitMask(bit_index);
}

fn tailNoise() Word {
    return ~((@as(Word, 1) << 11) - 1);
}

fn unionWords(left: [word_count]Word, right: [word_count]Word) [word_count]Word {
    var result: [word_count]Word = undefined;
    for (0..word_count) |index| {
        result[index] = left[index] | right[index];
    }
    return result;
}

fn expectMirroredView(words: []const Word, expected_count: usize, first_set: ?usize, first_clear: ?usize) !void {
    const bitmap = bitmap_view.BitmapView.init(words, capacity);
    const mask = cpumask_view.CpuMaskView.init(words, capacity);

    try testing.expectEqual(expected_count, bitmap.countSetBits());
    try testing.expectEqual(expected_count, mask.countPresentCpus());
    try testing.expectEqual(first_set, bitmap.firstSetBit());
    try testing.expectEqual(first_set, mask.firstCpu());
    try testing.expectEqual(first_clear, bitmap.firstClearBit());
    try testing.expectEqual(first_clear, mask.firstMissingCpu());
}

test "bitmap and cpumask agree across union-derived active masks" {
    var online = [_]Word{ 0, 0, tailNoise() };
    var isolated = [_]Word{ 0, 0, tailNoise() };

    for ([_]usize{ 1, 4, word_bits - 1, word_bits + 3, word_bits * 2 + 2, word_bits * 2 + 10 }) |bit| {
        setBit(&online, bit);
    }
    for ([_]usize{ 0, 4, word_bits, word_bits + 9, word_bits * 2 + 8 }) |bit| {
        setBit(&isolated, bit);
    }

    const combined_words = unionWords(online, isolated);
    const online_bitmap = bitmap_view.BitmapView.init(online[0..], capacity);
    const isolated_bitmap = bitmap_view.BitmapView.init(isolated[0..], capacity);
    const combined_bitmap = bitmap_view.BitmapView.init(combined_words[0..], capacity);
    const combined_mask = cpumask_view.CpuMaskView.init(combined_words[0..], capacity);

    try expectMirroredView(combined_words[0..], 10, 0, 2);
    try testing.expect(online_bitmap.isSubsetOf(combined_bitmap));
    try testing.expect(isolated_bitmap.isSubsetOf(combined_bitmap));
    try testing.expect(combined_bitmap.intersects(online_bitmap));
    try testing.expect(combined_bitmap.intersects(isolated_bitmap));
    try testing.expectEqual(@as(?usize, word_bits - 1), combined_bitmap.nextSetBit(5));
    try testing.expectEqual(@as(?usize, word_bits - 1), combined_mask.nextCpu(5));
    try testing.expectEqual(@as(?usize, word_bits + 1), combined_bitmap.nextClearBit(word_bits + 1));
    try testing.expectEqual(@as(?usize, word_bits + 1), combined_mask.nextMissingCpu(word_bits + 1));
    try testing.expect(combined_bitmap.isSet(word_bits * 2 + 10));
    try testing.expect(combined_mask.hasCpu(word_bits * 2 + 10));
}

test "union mirrors recompute after overlap and removal mutations" {
    var primary = [_]Word{ 0, 0, tailNoise() };
    var secondary = [_]Word{ 0, 0, tailNoise() };

    for ([_]usize{ 2, 7, word_bits + 1, word_bits + 6, word_bits * 2 + 1, word_bits * 2 + 9 }) |bit| {
        setBit(&primary, bit);
    }
    for ([_]usize{ 5, word_bits + 6, word_bits + 8, word_bits * 2 + 3 }) |bit| {
        setBit(&secondary, bit);
    }

    var combined_words = unionWords(primary, secondary);
    try expectMirroredView(combined_words[0..], 9, 2, 0);

    setBit(&secondary, 7);
    combined_words = unionWords(primary, secondary);
    const combined_after_overlap = bitmap_view.BitmapView.init(combined_words[0..], capacity);
    const secondary_after_overlap = cpumask_view.CpuMaskView.init(secondary[0..], capacity);

    try expectMirroredView(combined_words[0..], 9, 2, 0);
    try testing.expect(secondary_after_overlap.isSubsetOf(cpumask_view.CpuMaskView.init(combined_words[0..], capacity)));
    try testing.expect(combined_after_overlap.intersects(secondary_after_overlap.bitmap));
    try testing.expectEqual(@as(?usize, 7), secondary_after_overlap.nextCpu(6));

    clearBit(&primary, word_bits + 6);
    combined_words = unionWords(primary, secondary);
    const combined_after_primary_clear = cpumask_view.CpuMaskView.init(combined_words[0..], capacity);

    try expectMirroredView(combined_words[0..], 9, 2, 0);
    try testing.expect(combined_after_primary_clear.hasCpu(word_bits + 6));
    try testing.expectEqual(@as(?usize, word_bits + 6), combined_after_primary_clear.nextCpu(word_bits + 2));

    clearBit(&secondary, word_bits + 6);
    combined_words = unionWords(primary, secondary);
    const combined_after_both_clear = bitmap_view.BitmapView.init(combined_words[0..], capacity);

    try expectMirroredView(combined_words[0..], 8, 2, 0);
    try testing.expect(!combined_after_both_clear.isSet(word_bits + 6));
    try testing.expectEqual(@as(?usize, word_bits + 6), combined_after_both_clear.nextClearBit(word_bits + 6));
}
