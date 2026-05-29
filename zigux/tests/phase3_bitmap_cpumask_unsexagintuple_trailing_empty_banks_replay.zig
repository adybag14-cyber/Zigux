const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const empty_bank_count = 61;
const tail_word_index = empty_bank_count + 1;
const tail_offset = 10;
const tail_capacity = tail_word_index * bitmap_view.word_bits + tail_offset + 1;

fn replayWords() [tail_word_index + 1]usize {
    var words = [_]usize{0} ** (tail_word_index + 1);
    words[0] = (@as(usize, 1) << 3) | (@as(usize, 1) << 17);
    words[tail_word_index] = (@as(usize, 1) << 0) |
        (@as(usize, 1) << tail_offset) |
        (~@as(usize, 0) << @as(std.math.Log2Int(usize), tail_offset + 1));
    return words;
}

test "lane27 unsexagintuple replay keeps bitmap discovery stable across 61 empty banks" {
    const words = replayWords();
    const view = bitmap_view.BitmapView.init(words[0..], tail_capacity);
    const tail_base = tail_word_index * bitmap_view.word_bits;

    try testing.expectEqual(@as(usize, 4), view.countSetBits());
    try testing.expectEqual(@as(?usize, 3), view.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), view.firstClearBit());
    try testing.expectEqual(@as(?usize, 17), view.nextSetBit(4));
    try testing.expectEqual(@as(?usize, tail_base), view.nextSetBit(18));
    try testing.expectEqual(@as(?usize, tail_base + tail_offset), view.nextSetBit(tail_base + 1));
    try testing.expectEqual(@as(?usize, null), view.nextSetBit(tail_base + tail_offset + 1));
    try testing.expectEqual(@as(?usize, 4), view.nextClearBit(4));
    try testing.expectEqual(@as(?usize, 18), view.nextClearBit(18));
    try testing.expectEqual(@as(?usize, tail_base + 1), view.nextClearBit(tail_base + 1));
}

test "lane27 unsexagintuple replay keeps cpumask traversal aligned with bitmap traversal" {
    const words = replayWords();
    const bitmap = bitmap_view.BitmapView.init(words[0..], tail_capacity);
    const mask = cpumask_view.CpuMaskView.init(words[0..], tail_capacity);
    const tail_base = tail_word_index * bitmap_view.word_bits;

    try testing.expectEqual(bitmap.countSetBits(), mask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), mask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), mask.firstMissingCpu());
    try testing.expect(mask.hasCpu(3));
    try testing.expect(mask.hasCpu(tail_base));
    try testing.expect(mask.hasCpu(tail_base + tail_offset));
    try testing.expect(!mask.hasCpu(4));
    try testing.expectEqual(bitmap.nextSetBit(18), mask.nextCpu(18));
    try testing.expectEqual(bitmap.nextSetBit(tail_base + 1), mask.nextCpu(tail_base + 1));
    try testing.expectEqual(bitmap.nextClearBit(bitmap_view.word_bits), mask.nextMissingCpu(bitmap_view.word_bits));
    try testing.expectEqual(bitmap.nextClearBit(tail_base + 1), mask.nextMissingCpu(tail_base + 1));
}

test "lane27 unsexagintuple replay ignores tail-only noise in subset and overlap checks" {
    const base_words = replayWords();
    var superset_words = replayWords();
    var tail_noise_only_words = [_]usize{0} ** (tail_word_index + 1);
    superset_words[0] |= (@as(usize, 1) << 29);
    tail_noise_only_words[tail_word_index] = ~@as(usize, 0) << @as(std.math.Log2Int(usize), tail_offset + 1);

    const base_bitmap = bitmap_view.BitmapView.init(base_words[0..], tail_capacity);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], tail_capacity);
    const noise_bitmap = bitmap_view.BitmapView.init(tail_noise_only_words[0..], tail_capacity);

    const base_mask = cpumask_view.CpuMaskView.init(base_words[0..], tail_capacity);
    const superset_mask = cpumask_view.CpuMaskView.init(superset_words[0..], tail_capacity);
    const noise_mask = cpumask_view.CpuMaskView.init(tail_noise_only_words[0..], tail_capacity);

    try testing.expect(base_bitmap.isSubsetOf(superset_bitmap));
    try testing.expect(!superset_bitmap.isSubsetOf(base_bitmap));
    try testing.expect(!base_bitmap.intersects(noise_bitmap));
    try testing.expectEqual(@as(?usize, null), noise_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), noise_bitmap.firstClearBit());

    try testing.expect(base_mask.isSubsetOf(superset_mask));
    try testing.expect(!superset_mask.isSubsetOf(base_mask));
    try testing.expect(!base_mask.intersects(noise_mask));
    try testing.expectEqual(@as(?usize, null), noise_mask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), noise_mask.firstMissingCpu());
}
