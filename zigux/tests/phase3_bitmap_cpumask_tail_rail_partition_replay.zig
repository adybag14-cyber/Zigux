const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "tail rail partition keeps disjoint peers aligned under a shared union" {
    const capacity = bitmap_view.word_bits + 9;
    const tail_base = bitmap_view.word_bits;

    const union_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(4) | bit(6) | bit(8),
    };
    const left_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(4) | bit(8),
    };
    const right_words = [_]usize{
        0,
        bit(1) | bit(6),
    };
    const overlap_noise_words = [_]usize{
        0,
        bit(9) | bit(12) | bit(15),
    };

    const union_bitmap = bitmap_view.BitmapView.init(union_words[0..], capacity);
    const union_cpumask = cpumask_view.CpuMaskView.init(union_words[0..], capacity);
    const left = cpumask_view.CpuMaskView.init(left_words[0..], capacity);
    const right = cpumask_view.CpuMaskView.init(right_words[0..], capacity);
    const overlap_noise = cpumask_view.CpuMaskView.init(overlap_noise_words[0..], capacity);
    const overlap_noise_bitmap = bitmap_view.BitmapView.init(overlap_noise_words[0..], capacity);

    try testing.expectEqual(@as(usize, capacity - 4), union_bitmap.countSetBits());
    try testing.expectEqual(union_bitmap.countSetBits(), union_cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), union_bitmap.firstSetBit());
    try testing.expectEqual(union_bitmap.firstSetBit(), union_cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, tail_base + 2), union_bitmap.firstClearBit());
    try testing.expectEqual(union_bitmap.firstClearBit(), union_cpumask.firstMissingCpu());

    try testing.expect(left.isSubsetOf(union_cpumask));
    try testing.expect(right.isSubsetOf(union_cpumask));
    try testing.expect(!union_cpumask.isSubsetOf(left));
    try testing.expect(!union_cpumask.isSubsetOf(right));
    try testing.expect(!left.intersects(right));
    try testing.expect(!right.intersects(left));
    try testing.expect(union_cpumask.intersects(left));
    try testing.expect(union_cpumask.intersects(right));

    try testing.expectEqual(@as(usize, 0), overlap_noise_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), overlap_noise_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), overlap_noise_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), overlap_noise.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), overlap_noise.firstCpu());
    try testing.expectEqual(@as(?usize, 0), overlap_noise.firstMissingCpu());
    try testing.expect(overlap_noise.isSubsetOf(union_cpumask));
    try testing.expect(!overlap_noise.intersects(union_cpumask));
    try testing.expect(!union_cpumask.intersects(overlap_noise));
}

test "tail rail partition keeps a valid tail gap visible across both views" {
    const capacity = bitmap_view.word_bits + 9;
    const tail_base = bitmap_view.word_bits;

    const words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(4) | bit(5) | bit(7) | bit(8),
    };
    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(?usize, tail_base + 3), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(tail_base));
    try testing.expect(!cpumask.hasCpu(tail_base + 3));
    try testing.expect(cpumask.hasCpu(tail_base + 8));
}
