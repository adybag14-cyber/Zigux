const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "triple-bank partial tail last-gap keeps the final valid hole visible" {
    const capacity = (bitmap_view.word_bits * 3) + 5;
    const tail_base = bitmap_view.word_bits * 3;
    const last_valid_cpu = tail_base + 4;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(3) | bit(8) | bit(13),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual((bitmap_view.word_bits * 3) + 4, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, last_valid_cpu), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(tail_base));
    try testing.expect(bitmap.isSet(tail_base + 1));
    try testing.expect(bitmap.isSet(tail_base + 2));
    try testing.expect(bitmap.isSet(tail_base + 3));
    try testing.expect(!bitmap.isSet(last_valid_cpu));
    try testing.expect(cpumask.hasCpu(tail_base));
    try testing.expect(cpumask.hasCpu(tail_base + 1));
    try testing.expect(cpumask.hasCpu(tail_base + 2));
    try testing.expect(cpumask.hasCpu(tail_base + 3));
    try testing.expect(!cpumask.hasCpu(last_valid_cpu));
}

test "triple-bank partial tail last-gap peers ignore invalid tail-only extras" {
    const capacity = (bitmap_view.word_bits * 3) + 5;
    const full_until_last_gap_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(3),
    };
    const noisy_equivalent_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(3) | bit(9) | bit(17),
    };
    const tail_only_words = [_]usize{
        0,
        0,
        0,
        bit(3),
    };
    const invalid_only_words = [_]usize{
        0,
        0,
        0,
        bit(6) | bit(10),
    };

    const full_until_last_gap = cpumask_view.CpuMaskView.init(full_until_last_gap_words[0..], capacity);
    const noisy_equivalent = cpumask_view.CpuMaskView.init(noisy_equivalent_words[0..], capacity);
    const tail_only = cpumask_view.CpuMaskView.init(tail_only_words[0..], capacity);
    const invalid_only = cpumask_view.CpuMaskView.init(invalid_only_words[0..], capacity);
    const invalid_only_bitmap = bitmap_view.BitmapView.init(invalid_only_words[0..], capacity);

    try testing.expect(full_until_last_gap.isSubsetOf(noisy_equivalent));
    try testing.expect(noisy_equivalent.isSubsetOf(full_until_last_gap));
    try testing.expect(full_until_last_gap.intersects(noisy_equivalent));
    try testing.expect(noisy_equivalent.intersects(full_until_last_gap));
    try testing.expect(full_until_last_gap.intersects(tail_only));
    try testing.expect(tail_only.intersects(full_until_last_gap));
    try testing.expect(!full_until_last_gap.intersects(invalid_only));
    try testing.expect(!invalid_only.intersects(full_until_last_gap));
    try testing.expect(invalid_only.isSubsetOf(full_until_last_gap));
    try testing.expectEqual(@as(usize, 0), invalid_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), invalid_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), invalid_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), invalid_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), invalid_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), invalid_only.firstMissingCpu());
}
