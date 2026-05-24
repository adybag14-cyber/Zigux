const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "triple-bank partition keeps discovery aligned across disjoint peers" {
    const capacity = (bitmap_view.word_bits * 3) + 5;
    const tail_base = bitmap_view.word_bits * 3;
    const union_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(2) | bit(4) | bit(11) | bit(19),
    };
    const left_words = [_]usize{
        std.math.maxInt(usize),
        0,
        std.math.maxInt(usize),
        bit(0) | bit(4) | bit(8),
    };
    const right_words = [_]usize{
        0,
        std.math.maxInt(usize),
        0,
        bit(2) | bit(9) | bit(17),
    };
    const gap_words = [_]usize{
        0,
        0,
        0,
        bit(1) | bit(3) | bit(12),
    };

    const union_bitmap = bitmap_view.BitmapView.init(union_words[0..], capacity);
    const union_cpumask = cpumask_view.CpuMaskView.init(union_words[0..], capacity);
    const left = cpumask_view.CpuMaskView.init(left_words[0..], capacity);
    const right = cpumask_view.CpuMaskView.init(right_words[0..], capacity);
    const gaps = cpumask_view.CpuMaskView.init(gap_words[0..], capacity);

    try testing.expectEqual(capacity - 2, union_bitmap.countSetBits());
    try testing.expectEqual(union_bitmap.countSetBits(), union_cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), union_bitmap.firstSetBit());
    try testing.expectEqual(union_bitmap.firstSetBit(), union_cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, tail_base + 1), union_bitmap.firstClearBit());
    try testing.expectEqual(union_bitmap.firstClearBit(), union_cpumask.firstMissingCpu());
    try testing.expect(union_cpumask.hasCpu(tail_base));
    try testing.expect(!union_cpumask.hasCpu(tail_base + 1));
    try testing.expect(union_cpumask.hasCpu(tail_base + 2));
    try testing.expect(!union_cpumask.hasCpu(tail_base + 3));
    try testing.expect(union_cpumask.hasCpu(capacity - 1));

    try testing.expect(left.isSubsetOf(union_cpumask));
    try testing.expect(right.isSubsetOf(union_cpumask));
    try testing.expect(!union_cpumask.isSubsetOf(left));
    try testing.expect(!union_cpumask.isSubsetOf(right));
    try testing.expect(!left.intersects(right));
    try testing.expect(!right.intersects(left));
    try testing.expect(union_cpumask.intersects(left));
    try testing.expect(union_cpumask.intersects(right));
    try testing.expect(!gaps.isSubsetOf(union_cpumask));
    try testing.expect(!union_cpumask.intersects(gaps));
}

test "triple-bank partition keeps tail-only noise invisible to empty peers" {
    const capacity = (bitmap_view.word_bits * 3) + 5;
    const union_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(2) | bit(4) | bit(10) | bit(18),
    };
    const tail_only_noise_words = [_]usize{
        0,
        0,
        0,
        bit(8) | bit(9) | bit(17),
    };

    const union_cpumask = cpumask_view.CpuMaskView.init(union_words[0..], capacity);
    const tail_only_noise = cpumask_view.CpuMaskView.init(tail_only_noise_words[0..], capacity);
    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_noise_words[0..], capacity);

    try testing.expectEqual(@as(usize, 0), tail_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), tail_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), tail_only_noise.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), tail_only_noise.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_only_noise.firstMissingCpu());
    try testing.expect(tail_only_noise.isSubsetOf(union_cpumask));
    try testing.expect(!union_cpumask.intersects(tail_only_noise));
    try testing.expect(!tail_only_noise.intersects(union_cpumask));
}
