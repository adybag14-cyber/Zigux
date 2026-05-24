const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "tail rail bookend gap keeps first and last valid tail gaps explicit" {
    const capacity = bitmap_view.word_bits + 9;
    const tail_base = bitmap_view.word_bits;

    const union_words = [_]usize{
        std.math.maxInt(usize),
        bit(1) | bit(2) | bit(3) | bit(4) | bit(5) | bit(6) | bit(7),
    };
    const left_words = [_]usize{
        std.math.maxInt(usize),
        bit(1) | bit(2) | bit(3) | bit(4),
    };
    const right_words = [_]usize{
        0,
        bit(4) | bit(5) | bit(6) | bit(7),
    };
    const noise_words = [_]usize{
        0,
        bit(9) | bit(13) | bit(17),
    };

    const union_bitmap = bitmap_view.BitmapView.init(union_words[0..], capacity);
    const union_cpumask = cpumask_view.CpuMaskView.init(union_words[0..], capacity);
    const left = cpumask_view.CpuMaskView.init(left_words[0..], capacity);
    const right = cpumask_view.CpuMaskView.init(right_words[0..], capacity);
    const noise_bitmap = bitmap_view.BitmapView.init(noise_words[0..], capacity);
    const noise = cpumask_view.CpuMaskView.init(noise_words[0..], capacity);

    try testing.expectEqual(@as(usize, capacity - 2), union_bitmap.countSetBits());
    try testing.expectEqual(union_bitmap.countSetBits(), union_cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), union_bitmap.firstSetBit());
    try testing.expectEqual(union_bitmap.firstSetBit(), union_cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, tail_base), union_bitmap.firstClearBit());
    try testing.expectEqual(union_bitmap.firstClearBit(), union_cpumask.firstMissingCpu());
    try testing.expect(!union_cpumask.hasCpu(tail_base));
    try testing.expect(union_cpumask.hasCpu(tail_base + 1));
    try testing.expect(union_cpumask.hasCpu(tail_base + 7));
    try testing.expect(!union_cpumask.hasCpu(capacity - 1));

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

test "tail rail bookend gap keeps an interior-only peer bounded to valid tail bits" {
    const capacity = bitmap_view.word_bits + 9;
    const tail_base = bitmap_view.word_bits;

    const anchor_words = [_]usize{
        std.math.maxInt(usize),
        bit(1) | bit(2) | bit(3) | bit(4) | bit(5) | bit(6) | bit(7),
    };
    const interior_words = [_]usize{
        0,
        bit(2) | bit(3) | bit(6) | bit(10) | bit(14),
    };

    const anchor = cpumask_view.CpuMaskView.init(anchor_words[0..], capacity);
    const interior = cpumask_view.CpuMaskView.init(interior_words[0..], capacity);
    const interior_bitmap = bitmap_view.BitmapView.init(interior_words[0..], capacity);

    try testing.expectEqual(@as(usize, 3), interior_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, tail_base + 2), interior_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), interior_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 3), interior.countPresentCpus());
    try testing.expectEqual(@as(?usize, tail_base + 2), interior.firstCpu());
    try testing.expectEqual(@as(?usize, 0), interior.firstMissingCpu());
    try testing.expect(!interior.hasCpu(tail_base));
    try testing.expect(interior.hasCpu(tail_base + 2));
    try testing.expect(interior.hasCpu(tail_base + 6));
    try testing.expect(!interior.hasCpu(capacity - 1));
    try testing.expect(interior.isSubsetOf(anchor));
    try testing.expect(anchor.intersects(interior));
    try testing.expect(interior.intersects(anchor));
}
