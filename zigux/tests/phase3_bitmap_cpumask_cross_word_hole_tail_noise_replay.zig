const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "cross-word hole replay keeps the first missing cpu aligned under masked tail noise" {
    const capacity = (2 * bitmap_view.word_bits) + 6;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize) ^ bit(11),
        bit(0) | bit(5) | bit(12) | bit(31),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expect(bitmap.isSet(0));
    try testing.expect(cpumask.hasCpu(0));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits - 1));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits - 1));
    try testing.expect(!bitmap.isSet(bitmap_view.word_bits + 11));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits + 11));
    try testing.expect(bitmap.isSet((2 * bitmap_view.word_bits) + 5));
    try testing.expect(cpumask.hasCpu((2 * bitmap_view.word_bits) + 5));
    try testing.expectEqual(@as(usize, (2 * bitmap_view.word_bits) + 1), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 11), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}

test "cross-word hole replay ignores invalid tail-only subset and overlap noise" {
    const capacity = (2 * bitmap_view.word_bits) + 6;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize) ^ bit(11),
        bit(0) | bit(5) | bit(12) | bit(31),
    };
    const subset_words = [_]usize{
        bit(0) | bit(15) | bit(31),
        bit(3) | bit(60),
        bit(5) | bit(28),
    };
    const tail_only_noise_words = [_]usize{
        0,
        0,
        bit(12) | bit(31),
    };
    const disjoint_words = [_]usize{
        0,
        bit(11),
        bit(2),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const subset = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const tail_only_noise = cpumask_view.CpuMaskView.init(tail_only_noise_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);
    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_noise_words[0..], capacity);

    try testing.expect(subset.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(subset));
    try testing.expect(!base.intersects(tail_only_noise));
    try testing.expect(!tail_only_noise.intersects(base));
    try testing.expect(!disjoint.isSubsetOf(base));
    try testing.expect(!base.intersects(disjoint));
    try testing.expect(!disjoint.intersects(base));
    try testing.expectEqual(@as(usize, 0), tail_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), tail_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), tail_only_noise.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), tail_only_noise.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_only_noise.firstMissingCpu());
}
