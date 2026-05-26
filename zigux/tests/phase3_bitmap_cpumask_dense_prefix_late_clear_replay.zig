const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "dense-prefix late-clear replay keeps the first missing cpu aligned under masked tail noise" {
    const capacity = (3 * bitmap_view.word_bits) + 7;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize) ^ bit(13),
        bit(0) | bit(1) | bit(5) | bit(8),
        std.math.maxInt(usize),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expect(bitmap.isSet(0));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits - 1));
    try testing.expect(!bitmap.isSet(bitmap_view.word_bits + 13));
    try testing.expect(bitmap.isSet((2 * bitmap_view.word_bits) + 5));
    try testing.expect(!bitmap.isSet((2 * bitmap_view.word_bits) + 2));
    try testing.expect(bitmap.isSet((3 * bitmap_view.word_bits) + 6));
    try testing.expectEqual(@as(usize, (2 * bitmap_view.word_bits) + 10), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 13), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu((2 * bitmap_view.word_bits) + 8));
    try testing.expect(!cpumask.hasCpu((2 * bitmap_view.word_bits) + 2));
    try testing.expect(cpumask.hasCpu((3 * bitmap_view.word_bits) + 6));
}

test "dense-prefix late-clear replay keeps subset and overlap checks bounded to valid bits" {
    const capacity = (3 * bitmap_view.word_bits) + 7;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize) ^ bit(13),
        bit(0) | bit(1) | bit(5) | bit(8),
        std.math.maxInt(usize),
    };
    const subset_words = [_]usize{
        bit(0) | bit(31),
        bit(5),
        bit(1) | bit(8),
        std.math.maxInt(usize),
    };
    const overlap_words = [_]usize{
        0,
        0,
        bit(5),
        0,
    };
    const disjoint_words = [_]usize{
        0,
        bit(13),
        bit(2) | bit(4),
        0,
    };
    const tail_only_noise_words = [_]usize{
        0,
        0,
        0,
        bit(10) | bit(20) | bit(31),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const subset = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const overlap = cpumask_view.CpuMaskView.init(overlap_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);
    const tail_only_noise = cpumask_view.CpuMaskView.init(tail_only_noise_words[0..], capacity);
    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_noise_words[0..], capacity);

    try testing.expect(subset.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(subset));
    try testing.expect(base.intersects(overlap));
    try testing.expect(overlap.intersects(base));
    try testing.expect(!disjoint.isSubsetOf(base));
    try testing.expect(!base.intersects(disjoint));
    try testing.expect(!disjoint.intersects(base));
    try testing.expect(tail_only_noise.isSubsetOf(base));
    try testing.expect(!base.intersects(tail_only_noise));
    try testing.expect(!tail_only_noise.intersects(base));
    try testing.expectEqual(@as(usize, 0), tail_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), tail_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), tail_only_noise.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), tail_only_noise.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_only_noise.firstMissingCpu());
}
