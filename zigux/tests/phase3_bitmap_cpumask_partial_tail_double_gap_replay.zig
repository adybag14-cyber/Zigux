const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "partial tail double-gap keeps first missing cpu discovery aligned" {
    const capacity = bitmap_view.word_bits + 7;
    const words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(2) | bit(3) | bit(5) | bit(6) | bit(9) | bit(12),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);
    const first_missing = bitmap_view.word_bits + 1;
    const second_missing = bitmap_view.word_bits + 4;

    try testing.expectEqual(capacity - 2, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, first_missing), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits));
    try testing.expect(!cpumask.hasCpu(first_missing));
    try testing.expect(!cpumask.hasCpu(second_missing));
    try testing.expect(cpumask.hasCpu(capacity - 1));
}

test "partial tail double-gap keeps subset and overlap blind to invalid tail noise" {
    const capacity = bitmap_view.word_bits + 7;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(2) | bit(3) | bit(5) | bit(6) | bit(8) | bit(15),
    };
    const subset_words = [_]usize{
        bit(7),
        bit(0) | bit(5) | bit(11),
    };
    const valid_overlap_words = [_]usize{
        0,
        bit(3) | bit(10),
    };
    const double_gap_words = [_]usize{
        0,
        bit(1) | bit(4) | bit(9),
    };
    const tail_only_noise_words = [_]usize{
        0,
        bit(7) | bit(12) | bit(18),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const subset = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const valid_overlap = cpumask_view.CpuMaskView.init(valid_overlap_words[0..], capacity);
    const double_gap = cpumask_view.CpuMaskView.init(double_gap_words[0..], capacity);
    const tail_only_noise = cpumask_view.CpuMaskView.init(tail_only_noise_words[0..], capacity);
    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_noise_words[0..], capacity);

    try testing.expect(subset.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(subset));
    try testing.expect(base.intersects(valid_overlap));
    try testing.expect(valid_overlap.intersects(base));
    try testing.expect(!base.intersects(double_gap));
    try testing.expect(!double_gap.intersects(base));
    try testing.expect(!double_gap.isSubsetOf(base));
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
