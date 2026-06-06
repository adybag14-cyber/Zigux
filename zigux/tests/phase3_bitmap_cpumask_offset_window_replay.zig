const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(offset: usize) usize {
    return @as(usize, 1) << @intCast(offset);
}

test "bitmap and cpumask offset windows keep independent declared tails" {
    const word_bits = bitmap_view.word_bits;
    const capacity = word_bits + 6;
    const backing = [_]usize{
        bit(1) | bit(5) | bit(word_bits - 1),
        bit(0) | bit(3) | bit(5),
        bit(2) | (~@as(usize, 0) << 6),
    };

    const leading_bitmap = bitmap_view.BitmapView.init(backing[0..2], capacity);
    const leading_cpumask = cpumask_view.CpuMaskView.init(backing[0..2], capacity);
    const shifted_bitmap = bitmap_view.BitmapView.init(backing[1..3], capacity);
    const shifted_cpumask = cpumask_view.CpuMaskView.init(backing[1..3], capacity);

    try testing.expectEqual(@as(usize, 6), leading_bitmap.countSetBits());
    try testing.expectEqual(leading_bitmap.countSetBits(), leading_cpumask.countPresentCpus());
    try testing.expectEqual(@as(usize, 4), shifted_bitmap.countSetBits());
    try testing.expectEqual(shifted_bitmap.countSetBits(), shifted_cpumask.countPresentCpus());

    try testing.expectEqual(@as(?usize, 1), leading_bitmap.firstSetBit());
    try testing.expectEqual(leading_bitmap.firstSetBit(), leading_cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), shifted_bitmap.firstSetBit());
    try testing.expectEqual(shifted_bitmap.firstSetBit(), shifted_cpumask.firstCpu());

    try testing.expectEqual(@as(?usize, 0), leading_bitmap.firstClearBit());
    try testing.expectEqual(leading_bitmap.firstClearBit(), leading_cpumask.firstMissingCpu());
    try testing.expectEqual(@as(?usize, 1), shifted_bitmap.firstClearBit());
    try testing.expectEqual(shifted_bitmap.firstClearBit(), shifted_cpumask.firstMissingCpu());

    try testing.expectEqual(@as(?usize, word_bits + 3), leading_bitmap.nextSetBit(word_bits + 1));
    try testing.expectEqual(leading_bitmap.nextSetBit(word_bits + 1), leading_cpumask.nextCpu(word_bits + 1));
    try testing.expectEqual(@as(?usize, word_bits + 2), shifted_bitmap.nextSetBit(word_bits));
    try testing.expectEqual(shifted_bitmap.nextSetBit(word_bits), shifted_cpumask.nextCpu(word_bits));
    try testing.expectEqual(@as(?usize, null), shifted_bitmap.nextSetBit(word_bits + 3));
    try testing.expectEqual(shifted_bitmap.nextSetBit(word_bits + 3), shifted_cpumask.nextCpu(word_bits + 3));
}

test "bitmap and cpumask offset windows compare against matching windows only" {
    const word_bits = bitmap_view.word_bits;
    const capacity = word_bits + 4;
    const backing = [_]usize{
        bit(2) | bit(9),
        bit(1) | bit(word_bits - 1) | bit(0),
        bit(0) | bit(3) | (~@as(usize, 0) << 4),
    };
    const leading_subset_words = [_]usize{
        backing[0] | bit(12),
        backing[1] | bit(2),
    };
    const shifted_subset_words = [_]usize{
        backing[1] | bit(7),
        backing[2] | bit(2),
    };
    const leading_disjoint_words = [_]usize{ bit(0), bit(2) };
    const shifted_disjoint_words = [_]usize{ bit(6), bit(1) };

    const leading_bitmap = bitmap_view.BitmapView.init(backing[0..2], capacity);
    const leading_cpumask = cpumask_view.CpuMaskView.init(backing[0..2], capacity);
    const shifted_bitmap = bitmap_view.BitmapView.init(backing[1..3], capacity);
    const shifted_cpumask = cpumask_view.CpuMaskView.init(backing[1..3], capacity);

    const leading_superset_bitmap = bitmap_view.BitmapView.init(leading_subset_words[0..], capacity);
    const leading_superset_cpumask = cpumask_view.CpuMaskView.init(leading_subset_words[0..], capacity);
    const shifted_superset_bitmap = bitmap_view.BitmapView.init(shifted_subset_words[0..], capacity);
    const shifted_superset_cpumask = cpumask_view.CpuMaskView.init(shifted_subset_words[0..], capacity);
    const leading_disjoint_bitmap = bitmap_view.BitmapView.init(leading_disjoint_words[0..], capacity);
    const leading_disjoint_cpumask = cpumask_view.CpuMaskView.init(leading_disjoint_words[0..], capacity);
    const shifted_disjoint_bitmap = bitmap_view.BitmapView.init(shifted_disjoint_words[0..], capacity);
    const shifted_disjoint_cpumask = cpumask_view.CpuMaskView.init(shifted_disjoint_words[0..], capacity);

    try testing.expect(leading_bitmap.isSubsetOf(leading_superset_bitmap));
    try testing.expect(leading_cpumask.isSubsetOf(leading_superset_cpumask));
    try testing.expect(!leading_superset_bitmap.isSubsetOf(leading_bitmap));
    try testing.expect(!leading_superset_cpumask.isSubsetOf(leading_cpumask));
    try testing.expect(!leading_bitmap.intersects(leading_disjoint_bitmap));
    try testing.expect(!leading_cpumask.intersects(leading_disjoint_cpumask));

    try testing.expect(shifted_bitmap.isSubsetOf(shifted_superset_bitmap));
    try testing.expect(shifted_cpumask.isSubsetOf(shifted_superset_cpumask));
    try testing.expect(!shifted_superset_bitmap.isSubsetOf(shifted_bitmap));
    try testing.expect(!shifted_superset_cpumask.isSubsetOf(shifted_cpumask));
    try testing.expect(!shifted_bitmap.intersects(shifted_disjoint_bitmap));
    try testing.expect(!shifted_cpumask.intersects(shifted_disjoint_cpumask));
}
