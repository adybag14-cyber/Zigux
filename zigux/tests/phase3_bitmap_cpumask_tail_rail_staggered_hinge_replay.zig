const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "tail rail staggered hinge keeps the earliest tail gap aligned under a bounded union" {
    const capacity = bitmap_view.word_bits + 12;
    const tail_base = bitmap_view.word_bits;

    const union_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(2) | bit(3) | bit(6) | bit(8) | bit(9) | bit(11),
    };
    const left_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(2) | bit(3) | bit(8),
    };
    const right_words = [_]usize{
        0,
        bit(3) | bit(6) | bit(9) | bit(11),
    };
    const noise_words = [_]usize{
        0,
        bit(12) | bit(14) | bit(17),
    };

    const union_bitmap = bitmap_view.BitmapView.init(union_words[0..], capacity);
    const union_cpumask = cpumask_view.CpuMaskView.init(union_words[0..], capacity);
    const left = cpumask_view.CpuMaskView.init(left_words[0..], capacity);
    const right = cpumask_view.CpuMaskView.init(right_words[0..], capacity);
    const noise_bitmap = bitmap_view.BitmapView.init(noise_words[0..], capacity);
    const noise = cpumask_view.CpuMaskView.init(noise_words[0..], capacity);

    try testing.expectEqual(@as(usize, capacity - 5), union_bitmap.countSetBits());
    try testing.expectEqual(union_bitmap.countSetBits(), union_cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), union_bitmap.firstSetBit());
    try testing.expectEqual(union_bitmap.firstSetBit(), union_cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, tail_base + 1), union_bitmap.firstClearBit());
    try testing.expectEqual(union_bitmap.firstClearBit(), union_cpumask.firstMissingCpu());
    try testing.expect(union_cpumask.hasCpu(tail_base));
    try testing.expect(!union_cpumask.hasCpu(tail_base + 1));
    try testing.expect(union_cpumask.hasCpu(tail_base + 3));
    try testing.expect(!union_cpumask.hasCpu(tail_base + 4));
    try testing.expect(union_cpumask.hasCpu(tail_base + 8));
    try testing.expect(!union_cpumask.hasCpu(tail_base + 10));
    try testing.expect(union_cpumask.hasCpu(capacity - 1));

    try testing.expect(left.isSubsetOf(union_cpumask));
    try testing.expect(right.isSubsetOf(union_cpumask));
    try testing.expect(!union_cpumask.isSubsetOf(left));
    try testing.expect(!union_cpumask.isSubsetOf(right));
    try testing.expect(left.intersects(right));
    try testing.expect(right.intersects(left));
    try testing.expect(union_cpumask.intersects(left));
    try testing.expect(union_cpumask.intersects(right));

    try testing.expectEqual(@as(usize, 0), noise_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), noise_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), noise_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), noise.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), noise.firstCpu());
    try testing.expectEqual(@as(?usize, 0), noise.firstMissingCpu());
    try testing.expect(noise.isSubsetOf(union_cpumask));
    try testing.expect(!noise.intersects(union_cpumask));
    try testing.expect(!union_cpumask.intersects(noise));
}

test "tail rail staggered hinge keeps a two-gap probe outside the bounded union" {
    const capacity = bitmap_view.word_bits + 12;
    const tail_base = bitmap_view.word_bits;

    const anchor_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(2) | bit(3) | bit(6) | bit(8) | bit(9) | bit(11),
    };
    const gap_probe_words = [_]usize{
        0,
        bit(1) | bit(10) | bit(13) | bit(16),
    };

    const anchor = cpumask_view.CpuMaskView.init(anchor_words[0..], capacity);
    const gap_probe = cpumask_view.CpuMaskView.init(gap_probe_words[0..], capacity);
    const gap_probe_bitmap = bitmap_view.BitmapView.init(gap_probe_words[0..], capacity);

    try testing.expectEqual(@as(usize, 2), gap_probe_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, tail_base + 1), gap_probe_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), gap_probe_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 2), gap_probe.countPresentCpus());
    try testing.expectEqual(@as(?usize, tail_base + 1), gap_probe.firstCpu());
    try testing.expectEqual(@as(?usize, 0), gap_probe.firstMissingCpu());
    try testing.expect(gap_probe.hasCpu(tail_base + 1));
    try testing.expect(!gap_probe.hasCpu(tail_base + 3));
    try testing.expect(gap_probe.hasCpu(tail_base + 10));
    try testing.expect(!gap_probe.hasCpu(capacity - 1));
    try testing.expect(!gap_probe.isSubsetOf(anchor));
    try testing.expect(!anchor.intersects(gap_probe));
    try testing.expect(!gap_probe.intersects(anchor));
}
