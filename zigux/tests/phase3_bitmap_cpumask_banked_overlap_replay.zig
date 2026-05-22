const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "banked overlap keeps counts and discovery aligned across separated active banks" {
    const capacity = (bitmap_view.word_bits * 2) + 7;
    const words = [_]usize{
        bit(2) | bit(5) | bit(9),
        bit(0) | bit(1) | bit(6) | bit(12),
        bit(1) | bit(5) | bit(10) | bit(19),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expect(bitmap.isSet(2));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits));
    try testing.expect(bitmap.isSet((bitmap_view.word_bits * 2) + 5));
    try testing.expect(!bitmap.isSet(0));
    try testing.expect(!bitmap.isSet(bitmap_view.word_bits + 2));
    try testing.expectEqual(@as(usize, 9), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 2), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}

test "banked overlap keeps subset and overlap checks bounded under noisy tail storage" {
    const capacity = (bitmap_view.word_bits * 2) + 7;
    const base_words = [_]usize{
        bit(2) | bit(5) | bit(9),
        bit(0) | bit(1) | bit(6) | bit(12),
        bit(1) | bit(5) | bit(10) | bit(19),
    };
    const overlapping_words = [_]usize{
        bit(5),
        bit(1) | bit(6) | bit(8),
        bit(5) | bit(6) | bit(17),
    };
    const subset_words = [_]usize{
        bit(2) | bit(9),
        bit(1) | bit(6),
        bit(1) | bit(13) | bit(29),
    };
    const tail_only_words = [_]usize{
        0,
        0,
        bit(7) | bit(8) | bit(22),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const overlapping = cpumask_view.CpuMaskView.init(overlapping_words[0..], capacity);
    const subset = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const tail_only = cpumask_view.CpuMaskView.init(tail_only_words[0..], capacity);

    try testing.expect(base.intersects(overlapping));
    try testing.expect(overlapping.intersects(base));
    try testing.expect(!base.isSubsetOf(overlapping));
    try testing.expect(!overlapping.isSubsetOf(base));
    try testing.expect(subset.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(subset));
    try testing.expect(subset.intersects(base));
    try testing.expect(!base.intersects(tail_only));
    try testing.expect(!tail_only.intersects(base));
}
