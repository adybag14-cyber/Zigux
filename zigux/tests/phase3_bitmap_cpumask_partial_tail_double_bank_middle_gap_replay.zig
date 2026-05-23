const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "double-bank partial tail middle-gap keeps interior clear-bit discovery aligned" {
    const capacity = (bitmap_view.word_bits * 2) + 5;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(3) | bit(4) | bit(9) | bit(17),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);
    const expected_missing = (bitmap_view.word_bits * 2) + 2;

    try testing.expectEqual(capacity - 1, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, expected_missing), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits * 2));
    try testing.expect(cpumask.hasCpu((bitmap_view.word_bits * 2) + 1));
    try testing.expect(!cpumask.hasCpu(expected_missing));
    try testing.expect(cpumask.hasCpu(capacity - 1));
}

test "double-bank partial tail middle-gap keeps subset and overlap blind to tail-only noise" {
    const capacity = (bitmap_view.word_bits * 2) + 5;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(3) | bit(4) | bit(7) | bit(13),
    };
    const subset_words = [_]usize{
        bit(5) | bit(11),
        bit(0) | bit(31),
        bit(0) | bit(4) | bit(18),
    };
    const overlap_words = [_]usize{
        0,
        0,
        bit(3) | bit(9),
    };
    const gap_only_words = [_]usize{
        0,
        0,
        bit(2) | bit(14),
    };
    const tail_only_noise_words = [_]usize{
        0,
        0,
        bit(6) | bit(10) | bit(16),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const subset = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const overlap = cpumask_view.CpuMaskView.init(overlap_words[0..], capacity);
    const gap_only = cpumask_view.CpuMaskView.init(gap_only_words[0..], capacity);
    const tail_only_noise = cpumask_view.CpuMaskView.init(tail_only_noise_words[0..], capacity);
    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_noise_words[0..], capacity);

    try testing.expect(subset.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(subset));
    try testing.expect(base.intersects(overlap));
    try testing.expect(overlap.intersects(base));
    try testing.expect(!base.intersects(gap_only));
    try testing.expect(!gap_only.intersects(base));
    try testing.expect(!gap_only.isSubsetOf(base));
    try testing.expect(!base.intersects(tail_only_noise));
    try testing.expect(!tail_only_noise.intersects(base));
    try testing.expect(tail_only_noise.isSubsetOf(base));
    try testing.expectEqual(@as(usize, 0), tail_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), tail_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), tail_only_noise.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), tail_only_noise.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_only_noise.firstMissingCpu());
}
