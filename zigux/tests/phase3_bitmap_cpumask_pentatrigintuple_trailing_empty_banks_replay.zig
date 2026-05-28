const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const empty_bank_count = 35;
const active_word_count = empty_bank_count + 2;
const tail_word_index = active_word_count - 1;
const tail_capacity = 5;
const total_capacity = bitmap_view.word_bits * tail_word_index + tail_capacity;
const tail_base = bitmap_view.word_bits * tail_word_index;

fn makeBaseWords() [active_word_count]usize {
    var words = [_]usize{0} ** active_word_count;
    words[0] = (@as(usize, 1) << 0) | (@as(usize, 1) << 5);
    words[tail_word_index] =
        (@as(usize, 1) << 1) |
        (@as(usize, 1) << 4) |
        (~@as(usize, 0) << 5);
    return words;
}

test "bitmap replay keeps pentatrigintuple trailing empty banks aligned with a masked tail" {
    const words = makeBaseWords();
    const view = bitmap_view.BitmapView.init(words[0..], total_capacity);

    try testing.expectEqual(@as(usize, 4), view.countSetBits());
    try testing.expectEqual(@as(?usize, 0), view.firstSetBit());
    try testing.expectEqual(@as(?usize, 1), view.firstClearBit());
    try testing.expectEqual(@as(?usize, tail_base + 1), view.nextSetBit(bitmap_view.word_bits));
    try testing.expectEqual(@as(?usize, tail_base + 4), view.nextSetBit(tail_base + 2));
    try testing.expectEqual(@as(?usize, tail_base), view.nextClearBit(tail_base));
    try testing.expectEqual(@as(?usize, tail_base + 2), view.nextClearBit(tail_base + 2));
    try testing.expectEqual(@as(?usize, null), view.nextSetBit(total_capacity));
}

test "bitmap replay keeps subset and overlap checks blind to invalid tail-only noise" {
    const base_words = makeBaseWords();
    var superset_words = makeBaseWords();
    var disjoint_words = [_]usize{0} ** active_word_count;

    superset_words[tail_word_index] |= @as(usize, 1) << 3;
    disjoint_words[0] = @as(usize, 1) << 2;
    disjoint_words[tail_word_index] = ~@as(usize, 0) << 5;

    const base = bitmap_view.BitmapView.init(base_words[0..], total_capacity);
    const superset = bitmap_view.BitmapView.init(superset_words[0..], total_capacity);
    const disjoint = bitmap_view.BitmapView.init(disjoint_words[0..], total_capacity);

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(!base.intersects(disjoint));
}

test "cpumask replay mirrors the same pentatrigintuple tail behavior" {
    const base_words = makeBaseWords();
    var superset_words = makeBaseWords();
    var disjoint_words = [_]usize{0} ** active_word_count;

    superset_words[tail_word_index] |= @as(usize, 1) << 3;
    disjoint_words[0] = @as(usize, 1) << 2;
    disjoint_words[tail_word_index] = ~@as(usize, 0) << 5;

    const base = cpumask_view.CpuMaskView.init(base_words[0..], total_capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], total_capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], total_capacity);

    try testing.expect(base.hasCpu(0));
    try testing.expect(base.hasCpu(5));
    try testing.expect(base.hasCpu(tail_base + 1));
    try testing.expect(!base.hasCpu(tail_base));
    try testing.expectEqual(@as(usize, 4), base.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), base.firstCpu());
    try testing.expectEqual(@as(?usize, 1), base.firstMissingCpu());
    try testing.expectEqual(@as(?usize, tail_base + 1), base.nextCpu(bitmap_view.word_bits));
    try testing.expectEqual(@as(?usize, tail_base), base.nextMissingCpu(tail_base));
    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(!base.intersects(disjoint));
}
