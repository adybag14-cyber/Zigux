const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "tail rail terminal hinge keeps the last valid shared rail aligned under a bounded union" {
    const capacity = bitmap_view.word_bits + 7;
    const tail_base = bitmap_view.word_bits;

    const union_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(3) | bit(6),
    };
    const left_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(6),
    };
    const right_words = [_]usize{
        0,
        bit(3) | bit(6),
    };
    const noise_words = [_]usize{
        0,
        bit(7) | bit(10) | bit(14),
    };

    const union_bitmap = bitmap_view.BitmapView.init(union_words[0..], capacity);
    const union_cpumask = cpumask_view.CpuMaskView.init(union_words[0..], capacity);
    const left = cpumask_view.CpuMaskView.init(left_words[0..], capacity);
    const right = cpumask_view.CpuMaskView.init(right_words[0..], capacity);
    const noise_bitmap = bitmap_view.BitmapView.init(noise_words[0..], capacity);
    const noise = cpumask_view.CpuMaskView.init(noise_words[0..], capacity);

    try testing.expectEqual(@as(usize, capacity - 3), union_bitmap.countSetBits());
    try testing.expectEqual(union_bitmap.countSetBits(), union_cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), union_bitmap.firstSetBit());
    try testing.expectEqual(union_bitmap.firstSetBit(), union_cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, tail_base + 2), union_bitmap.firstClearBit());
    try testing.expectEqual(union_bitmap.firstClearBit(), union_cpumask.firstMissingCpu());
    try testing.expect(union_cpumask.hasCpu(tail_base));
    try testing.expect(union_cpumask.hasCpu(tail_base + 1));
    try testing.expect(!union_cpumask.hasCpu(tail_base + 2));
    try testing.expect(union_cpumask.hasCpu(tail_base + 3));
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

test "tail rail terminal hinge keeps a last-rail-only peer visible without admitting tail noise" {
    const capacity = bitmap_view.word_bits + 7;
    const tail_base = bitmap_view.word_bits;

    const anchor_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(3) | bit(6),
    };
    const hinge_only_words = [_]usize{
        0,
        bit(6) | bit(8) | bit(13),
    };

    const anchor = cpumask_view.CpuMaskView.init(anchor_words[0..], capacity);
    const hinge_only = cpumask_view.CpuMaskView.init(hinge_only_words[0..], capacity);
    const hinge_bitmap = bitmap_view.BitmapView.init(hinge_only_words[0..], capacity);

    try testing.expectEqual(@as(usize, 1), hinge_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, tail_base + 6), hinge_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), hinge_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 1), hinge_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, tail_base + 6), hinge_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), hinge_only.firstMissingCpu());
    try testing.expect(hinge_only.hasCpu(tail_base + 6));
    try testing.expect(!hinge_only.hasCpu(tail_base + 5));
    try testing.expect(!hinge_only.hasCpu(tail_base + 4));
    try testing.expect(hinge_only.isSubsetOf(anchor));
    try testing.expect(anchor.intersects(hinge_only));
    try testing.expect(hinge_only.intersects(anchor));
}
