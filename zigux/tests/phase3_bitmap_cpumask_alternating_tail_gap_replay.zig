const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const middle_word_index = 1;
const tail_word_index = 2;
const tail_valid_bits = 17;
const tail_capacity = tail_word_index * bitmap_view.word_bits + tail_valid_bits;

fn bit(offset: usize) usize {
    return @as(usize, 1) << @as(std.math.Log2Int(usize), @intCast(offset));
}

fn paddingNoise() usize {
    return ~@as(usize, 0) << @as(std.math.Log2Int(usize), @intCast(tail_valid_bits));
}

fn replayWords() [tail_word_index + 1]usize {
    var words = [_]usize{0} ** (tail_word_index + 1);
    words[0] = bit(4) | bit(bitmap_view.word_bits - 1);
    words[middle_word_index] = bit(9);
    words[tail_word_index] = bit(0) | bit(2) | bit(4) | bit(8) | bit(16) | paddingNoise();
    return words;
}

test "lane27 alternating tail-gap replay keeps bitmap traversal bounded to valid tail bits" {
    const words = replayWords();
    const view = bitmap_view.BitmapView.init(words[0..], tail_capacity);
    const tail_base = tail_word_index * bitmap_view.word_bits;

    try testing.expectEqual(@as(usize, 8), view.countSetBits());
    try testing.expectEqual(@as(?usize, 4), view.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), view.firstClearBit());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits - 1), view.nextSetBit(5));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 9), view.nextSetBit(bitmap_view.word_bits));
    try testing.expectEqual(@as(?usize, tail_base), view.nextSetBit(bitmap_view.word_bits + 10));
    try testing.expectEqual(@as(?usize, tail_base + 2), view.nextSetBit(tail_base + 1));
    try testing.expectEqual(@as(?usize, tail_base + 8), view.nextSetBit(tail_base + 5));
    try testing.expectEqual(@as(?usize, tail_base + 16), view.nextSetBit(tail_base + 9));
    try testing.expectEqual(@as(?usize, null), view.nextSetBit(tail_base + tail_valid_bits));
    try testing.expectEqual(@as(?usize, tail_base + 1), view.nextClearBit(tail_base));
    try testing.expectEqual(@as(?usize, tail_base + 15), view.nextClearBit(tail_base + 15));
    try testing.expectEqual(@as(?usize, null), view.nextClearBit(tail_base + 16));
}

test "lane27 alternating tail-gap replay keeps cpumask traversal aligned with bitmap traversal" {
    const words = replayWords();
    const bitmap = bitmap_view.BitmapView.init(words[0..], tail_capacity);
    const mask = cpumask_view.CpuMaskView.init(words[0..], tail_capacity);
    const tail_base = tail_word_index * bitmap_view.word_bits;

    try testing.expectEqual(bitmap.countSetBits(), mask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), mask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), mask.firstMissingCpu());
    try testing.expect(mask.hasCpu(4));
    try testing.expect(mask.hasCpu(bitmap_view.word_bits + 9));
    try testing.expect(mask.hasCpu(tail_base + 16));
    try testing.expect(!mask.hasCpu(tail_base + 15));
    try testing.expectEqual(bitmap.nextSetBit(bitmap_view.word_bits), mask.nextCpu(bitmap_view.word_bits));
    try testing.expectEqual(bitmap.nextSetBit(tail_base + 5), mask.nextCpu(tail_base + 5));
    try testing.expectEqual(bitmap.nextClearBit(tail_base), mask.nextMissingCpu(tail_base));
    try testing.expectEqual(bitmap.nextClearBit(tail_base + 15), mask.nextMissingCpu(tail_base + 15));
}

test "lane27 alternating tail-gap replay ignores padding noise for subset and overlap" {
    const base_words = replayWords();
    var superset_words = replayWords();
    var gap_words = [_]usize{0} ** (tail_word_index + 1);
    var padding_only_words = [_]usize{0} ** (tail_word_index + 1);
    const tail_base = tail_word_index * bitmap_view.word_bits;

    superset_words[tail_word_index] |= bit(10);
    gap_words[tail_word_index] = bit(1) | bit(3) | bit(5) | bit(15);
    padding_only_words[tail_word_index] = paddingNoise();

    const base_bitmap = bitmap_view.BitmapView.init(base_words[0..], tail_capacity);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], tail_capacity);
    const gap_bitmap = bitmap_view.BitmapView.init(gap_words[0..], tail_capacity);
    const padding_bitmap = bitmap_view.BitmapView.init(padding_only_words[0..], tail_capacity);

    const base_mask = cpumask_view.CpuMaskView.init(base_words[0..], tail_capacity);
    const superset_mask = cpumask_view.CpuMaskView.init(superset_words[0..], tail_capacity);
    const gap_mask = cpumask_view.CpuMaskView.init(gap_words[0..], tail_capacity);
    const padding_mask = cpumask_view.CpuMaskView.init(padding_only_words[0..], tail_capacity);

    try testing.expect(base_bitmap.isSubsetOf(superset_bitmap));
    try testing.expect(!superset_bitmap.isSubsetOf(base_bitmap));
    try testing.expect(!base_bitmap.intersects(gap_bitmap));
    try testing.expect(!base_bitmap.intersects(padding_bitmap));
    try testing.expectEqual(@as(?usize, null), padding_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), padding_bitmap.firstClearBit());

    try testing.expect(base_mask.isSubsetOf(superset_mask));
    try testing.expect(!superset_mask.isSubsetOf(base_mask));
    try testing.expect(!base_mask.intersects(gap_mask));
    try testing.expect(!base_mask.intersects(padding_mask));
    try testing.expectEqual(@as(?usize, tail_base + 1), gap_mask.firstCpu());
    try testing.expectEqual(@as(?usize, null), padding_mask.firstCpu());
}
