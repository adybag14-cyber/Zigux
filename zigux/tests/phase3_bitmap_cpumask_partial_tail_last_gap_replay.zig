const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "partial tail last-gap keeps final valid clear-bit discovery aligned" {
    const capacity = (bitmap_view.word_bits * 2) + 7;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(3) | bit(4) | bit(5) | bit(11) | bit(19),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);
    const expected_missing = capacity - 1;

    try testing.expectEqual(capacity - 1, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, expected_missing), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(expected_missing - 1));
    try testing.expect(!bitmap.isSet(expected_missing));
    try testing.expect(cpumask.hasCpu(expected_missing - 1));
    try testing.expect(!cpumask.hasCpu(expected_missing));
}

test "partial tail last-gap keeps subset and overlap checks blind to tail-only noise" {
    const capacity = (bitmap_view.word_bits * 2) + 7;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(3) | bit(4) | bit(5) | bit(12),
    };
    const subset_words = [_]usize{
        bit(5) | bit(19),
        bit(11),
        bit(1) | bit(4) | bit(16),
    };
    const overlap_words = [_]usize{
        0,
        bit(9),
        bit(2) | bit(15),
    };
    const disjoint_words = [_]usize{
        0,
        0,
        bit(6) | bit(18) | bit(23),
    };
    const tail_noise_words = [_]usize{
        0,
        0,
        bit(8) | bit(14) | bit(21),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const subset = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const overlap = cpumask_view.CpuMaskView.init(overlap_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);
    const tail_noise = cpumask_view.CpuMaskView.init(tail_noise_words[0..], capacity);
    const tail_noise_bitmap = bitmap_view.BitmapView.init(tail_noise_words[0..], capacity);

    try testing.expect(subset.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(subset));
    try testing.expect(base.intersects(overlap));
    try testing.expect(overlap.intersects(base));
    try testing.expect(!base.intersects(disjoint));
    try testing.expect(!disjoint.intersects(base));
    try testing.expect(!base.intersects(tail_noise));
    try testing.expect(!tail_noise.intersects(base));
    try testing.expect(tail_noise.isSubsetOf(base));
    try testing.expectEqual(@as(usize, 0), tail_noise_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), tail_noise_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_noise_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), tail_noise.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), tail_noise.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_noise.firstMissingCpu());
}
