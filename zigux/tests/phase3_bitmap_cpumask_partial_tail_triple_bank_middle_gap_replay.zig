const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "triple-bank partial tail middle-gap keeps the real tail gap visible" {
    const capacity = (bitmap_view.word_bits * 3) + 5;
    const tail_base = bitmap_view.word_bits * 3;
    const gap_cpu = tail_base + 2;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(3) | bit(4) | bit(8) | bit(12),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual((bitmap_view.word_bits * 3) + 4, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, gap_cpu), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(tail_base));
    try testing.expect(bitmap.isSet(tail_base + 1));
    try testing.expect(!bitmap.isSet(gap_cpu));
    try testing.expect(bitmap.isSet(tail_base + 3));
    try testing.expect(bitmap.isSet(tail_base + 4));
    try testing.expect(cpumask.hasCpu(tail_base));
    try testing.expect(cpumask.hasCpu(tail_base + 1));
    try testing.expect(!cpumask.hasCpu(gap_cpu));
    try testing.expect(cpumask.hasCpu(tail_base + 3));
    try testing.expect(cpumask.hasCpu(tail_base + 4));
}

test "triple-bank partial tail middle-gap peers ignore invalid tail extras the same way" {
    const capacity = (bitmap_view.word_bits * 3) + 5;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(3) | bit(4),
    };
    const noisy_equivalent_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(3) | bit(4) | bit(8) | bit(12),
    };
    const middle_gap_only_words = [_]usize{
        0,
        0,
        0,
        bit(0) | bit(1) | bit(3) | bit(4),
    };
    const invalid_only_words = [_]usize{
        0,
        0,
        0,
        bit(6) | bit(10),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const noisy_equivalent = cpumask_view.CpuMaskView.init(noisy_equivalent_words[0..], capacity);
    const middle_gap_only = cpumask_view.CpuMaskView.init(middle_gap_only_words[0..], capacity);
    const invalid_only = cpumask_view.CpuMaskView.init(invalid_only_words[0..], capacity);
    const invalid_only_bitmap = bitmap_view.BitmapView.init(invalid_only_words[0..], capacity);

    try testing.expect(base.isSubsetOf(noisy_equivalent));
    try testing.expect(noisy_equivalent.isSubsetOf(base));
    try testing.expect(base.intersects(noisy_equivalent));
    try testing.expect(noisy_equivalent.intersects(base));
    try testing.expect(base.intersects(middle_gap_only));
    try testing.expect(middle_gap_only.intersects(base));
    try testing.expect(!base.intersects(invalid_only));
    try testing.expect(!invalid_only.intersects(base));
    try testing.expect(invalid_only.isSubsetOf(base));
    try testing.expectEqual(@as(usize, 0), invalid_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), invalid_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), invalid_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), invalid_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), invalid_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), invalid_only.firstMissingCpu());
}
