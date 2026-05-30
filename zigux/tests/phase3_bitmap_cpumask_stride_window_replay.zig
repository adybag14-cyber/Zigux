const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const tail_word_index = 3;
const tail_valid_bits = 23;
const stride_capacity = tail_word_index * bitmap_view.word_bits + tail_valid_bits;

fn bit(offset: usize) usize {
    return @as(usize, 1) << @as(std.math.Log2Int(usize), @intCast(offset));
}

fn paddingNoise() usize {
    return ~@as(usize, 0) << @as(std.math.Log2Int(usize), @intCast(tail_valid_bits));
}

fn strideWords() [tail_word_index + 1]usize {
    var words = [_]usize{0} ** (tail_word_index + 1);
    words[0] = bit(0) | bit(13) | bit(bitmap_view.word_bits - 2);
    words[1] = bit(7) | bit(31);
    words[2] = bit(3) | bit(29) | bit(bitmap_view.word_bits - 1);
    words[tail_word_index] = bit(1) | bit(11) | bit(22) | paddingNoise();
    return words;
}

test "lane27 stride-window replay walks spaced bitmap bits across active words" {
    const words = strideWords();
    const view = bitmap_view.BitmapView.init(words[0..], stride_capacity);
    const tail_base = tail_word_index * bitmap_view.word_bits;

    try testing.expectEqual(@as(usize, 11), view.countSetBits());
    try testing.expectEqual(@as(?usize, 0), view.firstSetBit());
    try testing.expectEqual(@as(?usize, 1), view.firstClearBit());
    try testing.expectEqual(@as(?usize, 13), view.nextSetBit(1));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits - 2), view.nextSetBit(14));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 7), view.nextSetBit(bitmap_view.word_bits));
    try testing.expectEqual(@as(?usize, 2 * bitmap_view.word_bits + 3), view.nextSetBit(bitmap_view.word_bits + 32));
    try testing.expectEqual(@as(?usize, 3 * bitmap_view.word_bits - 1), view.nextSetBit(2 * bitmap_view.word_bits + 30));
    try testing.expectEqual(@as(?usize, tail_base + 1), view.nextSetBit(tail_base));
    try testing.expectEqual(@as(?usize, tail_base + 11), view.nextSetBit(tail_base + 2));
    try testing.expectEqual(@as(?usize, tail_base + 22), view.nextSetBit(tail_base + 12));
    try testing.expectEqual(@as(?usize, null), view.nextSetBit(tail_base + tail_valid_bits));
    try testing.expectEqual(@as(?usize, tail_base + 21), view.nextClearBit(tail_base + 21));
    try testing.expectEqual(@as(?usize, null), view.nextClearBit(tail_base + 22));
}

test "lane27 stride-window replay keeps cpumask reads in lockstep with bitmap reads" {
    const words = strideWords();
    const bitmap = bitmap_view.BitmapView.init(words[0..], stride_capacity);
    const mask = cpumask_view.CpuMaskView.init(words[0..], stride_capacity);
    const tail_base = tail_word_index * bitmap_view.word_bits;

    try testing.expectEqual(bitmap.countSetBits(), mask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), mask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), mask.firstMissingCpu());
    try testing.expect(mask.hasCpu(0));
    try testing.expect(mask.hasCpu(bitmap_view.word_bits + 31));
    try testing.expect(mask.hasCpu(3 * bitmap_view.word_bits - 1));
    try testing.expect(mask.hasCpu(tail_base + 22));
    try testing.expect(!mask.hasCpu(tail_base + 21));
    try testing.expectEqual(bitmap.nextSetBit(bitmap_view.word_bits + 8), mask.nextCpu(bitmap_view.word_bits + 8));
    try testing.expectEqual(bitmap.nextSetBit(2 * bitmap_view.word_bits + 4), mask.nextCpu(2 * bitmap_view.word_bits + 4));
    try testing.expectEqual(bitmap.nextClearBit(tail_base + 21), mask.nextMissingCpu(tail_base + 21));
}

test "lane27 stride-window replay keeps subset and overlap bounded despite padding noise" {
    const base_words = strideWords();
    var superset_words = strideWords();
    var straddle_words = [_]usize{0} ** (tail_word_index + 1);
    var padding_only_words = [_]usize{0} ** (tail_word_index + 1);
    const tail_base = tail_word_index * bitmap_view.word_bits;

    superset_words[0] |= bit(2);
    superset_words[tail_word_index] |= bit(5);
    straddle_words[0] = bit(1) | bit(bitmap_view.word_bits - 1);
    straddle_words[1] = bit(0) | bit(30);
    straddle_words[tail_word_index] = bit(21);
    padding_only_words[tail_word_index] = paddingNoise();

    const base_bitmap = bitmap_view.BitmapView.init(base_words[0..], stride_capacity);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], stride_capacity);
    const straddle_bitmap = bitmap_view.BitmapView.init(straddle_words[0..], stride_capacity);
    const padding_bitmap = bitmap_view.BitmapView.init(padding_only_words[0..], stride_capacity);

    const base_mask = cpumask_view.CpuMaskView.init(base_words[0..], stride_capacity);
    const superset_mask = cpumask_view.CpuMaskView.init(superset_words[0..], stride_capacity);
    const straddle_mask = cpumask_view.CpuMaskView.init(straddle_words[0..], stride_capacity);
    const padding_mask = cpumask_view.CpuMaskView.init(padding_only_words[0..], stride_capacity);

    try testing.expect(base_bitmap.isSubsetOf(superset_bitmap));
    try testing.expect(!superset_bitmap.isSubsetOf(base_bitmap));
    try testing.expect(!base_bitmap.intersects(straddle_bitmap));
    try testing.expect(!base_bitmap.intersects(padding_bitmap));
    try testing.expectEqual(@as(?usize, null), padding_bitmap.firstSetBit());

    try testing.expect(base_mask.isSubsetOf(superset_mask));
    try testing.expect(!superset_mask.isSubsetOf(base_mask));
    try testing.expect(!base_mask.intersects(straddle_mask));
    try testing.expect(!base_mask.intersects(padding_mask));
    try testing.expectEqual(@as(?usize, 1), straddle_mask.firstCpu());
    try testing.expectEqual(@as(?usize, tail_base + 21), straddle_mask.nextCpu(tail_base));
    try testing.expectEqual(@as(?usize, null), padding_mask.firstCpu());
}
