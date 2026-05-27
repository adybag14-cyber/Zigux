const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(local_index: usize) usize {
    return @as(usize, 1) << @intCast(local_index);
}

fn noiseAbove(valid_bits: usize) usize {
    if (valid_bits >= bitmap_view.word_bits) return 0;
    return (~@as(usize, 0)) << @as(std.math.Log2Int(usize), @intCast(valid_bits));
}

test "tail-anchor bridge replay keeps bitmap and cpumask discovery aligned" {
    const capacity = (bitmap_view.word_bits * 2) + 5;
    const words = [_]usize{
        bit(2) | bit(9),
        bit(0) | bit(5) | bit(bitmap_view.word_bits - 1),
        bit(1) | bit(4) | noiseAbove(5),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 7), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());

    try testing.expectEqual(@as(?usize, 2), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    try testing.expectEqual(@as(?usize, 9), bitmap.nextSetBit(3));
    try testing.expectEqual(bitmap.nextSetBit(3), cpumask.nextCpu(3));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits), bitmap.nextSetBit(10));
    try testing.expectEqual(bitmap.nextSetBit(10), cpumask.nextCpu(10));
    try testing.expectEqual(@as(?usize, (bitmap_view.word_bits * 2) + 1), bitmap.nextSetBit(bitmap_view.word_bits * 2));
    try testing.expectEqual(bitmap.nextSetBit(bitmap_view.word_bits * 2), cpumask.nextCpu(bitmap_view.word_bits * 2));

    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 1), bitmap.nextClearBit(bitmap_view.word_bits));
    try testing.expectEqual(bitmap.nextClearBit(bitmap_view.word_bits), cpumask.nextMissingCpu(bitmap_view.word_bits));
    try testing.expectEqual(@as(?usize, (bitmap_view.word_bits * 2) + 2), bitmap.nextClearBit((bitmap_view.word_bits * 2) + 2));
    try testing.expectEqual(bitmap.nextClearBit((bitmap_view.word_bits * 2) + 2), cpumask.nextMissingCpu((bitmap_view.word_bits * 2) + 2));
}

test "tail-anchor bridge replay keeps missing-tail discovery inside valid capacity" {
    const capacity = (bitmap_view.word_bits * 2) + 5;
    const words = [_]usize{
        bit(0) | bit(4),
        bit(3) | bit(bitmap_view.word_bits - 1),
        bit(1) | bit(4) | noiseAbove(5),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(?usize, 1), bitmap.nextClearBit(0));
    try testing.expectEqual(bitmap.nextClearBit(0), cpumask.nextMissingCpu(0));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits), bitmap.nextClearBit(bitmap_view.word_bits));
    try testing.expectEqual(bitmap.nextClearBit(bitmap_view.word_bits), cpumask.nextMissingCpu(bitmap_view.word_bits));
    try testing.expectEqual(@as(?usize, (bitmap_view.word_bits * 2) + 2), bitmap.nextClearBit((bitmap_view.word_bits * 2) + 1));
    try testing.expectEqual(bitmap.nextClearBit((bitmap_view.word_bits * 2) + 1), cpumask.nextMissingCpu((bitmap_view.word_bits * 2) + 1));
    try testing.expectEqual(@as(?usize, 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}

test "tail-anchor bridge replay ignores tail-only noise for subset and overlap checks" {
    const capacity = bitmap_view.word_bits + 5;
    const base_words = [_]usize{
        bit(3) | bit(bitmap_view.word_bits - 1),
        bit(1) | noiseAbove(5),
    };
    const superset_words = [_]usize{
        bit(3) | bit(7) | bit(bitmap_view.word_bits - 1),
        bit(1) | bit(4) | noiseAbove(5),
    };
    const disjoint_words = [_]usize{
        bit(0) | bit(5),
        noiseAbove(5),
    };
    const tail_noise_only_words = [_]usize{
        0,
        noiseAbove(5),
    };

    const base_bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], capacity);
    const disjoint_bitmap = bitmap_view.BitmapView.init(disjoint_words[0..], capacity);
    const tail_noise_bitmap = bitmap_view.BitmapView.init(tail_noise_only_words[0..], capacity);

    const base_cpumask = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset_cpumask = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const disjoint_cpumask = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);
    const tail_noise_cpumask = cpumask_view.CpuMaskView.init(tail_noise_only_words[0..], capacity);

    try testing.expect(base_bitmap.isSubsetOf(superset_bitmap));
    try testing.expect(base_cpumask.isSubsetOf(superset_cpumask));
    try testing.expect(!superset_bitmap.isSubsetOf(base_bitmap));
    try testing.expect(!superset_cpumask.isSubsetOf(base_cpumask));

    try testing.expect(!base_bitmap.intersects(disjoint_bitmap));
    try testing.expect(!base_cpumask.intersects(disjoint_cpumask));
    try testing.expect(!base_bitmap.intersects(tail_noise_bitmap));
    try testing.expect(!base_cpumask.intersects(tail_noise_cpumask));
}
