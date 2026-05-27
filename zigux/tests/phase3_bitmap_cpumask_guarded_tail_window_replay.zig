const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const word_bits = bitmap_view.word_bits;

fn bit(offset: usize) usize {
    return @as(usize, 1) << @intCast(offset);
}

fn invalidTailNoise(valid_tail_bits: usize) usize {
    return std.math.maxInt(usize) & ~((@as(usize, 1) << @intCast(valid_tail_bits)) - 1);
}

test "guarded tail window keeps counts and first-bit discovery bounded to valid capacity" {
    const capacity = (2 * word_bits) + 11;
    const words = [_]usize{
        bit(0) | bit(5) | bit(12),
        bit(1) | bit(7) | bit(15),
        bit(0) | bit(3) | bit(10) | invalidTailNoise(11),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 9), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    try testing.expect(bitmap.isSet(0));
    try testing.expect(bitmap.isSet(word_bits + 15));
    try testing.expect(bitmap.isSet((2 * word_bits) + 10));
    try testing.expect(!bitmap.isSet((2 * word_bits) + 9));
    try testing.expect(cpumask.hasCpu(word_bits + 1));
    try testing.expect(!cpumask.hasCpu(word_bits + 2));
    try testing.expect(cpumask.hasCpu((2 * word_bits) + 3));
}

test "guarded tail window keeps subset and overlap checks blind to tail-only noise" {
    const capacity = (2 * word_bits) + 11;
    const base_words = [_]usize{
        bit(0) | bit(5) | bit(12),
        bit(1) | bit(7) | bit(15),
        bit(0) | bit(3) | bit(10) | invalidTailNoise(11),
    };
    const guarded_words = [_]usize{
        0,
        bit(7) | bit(15),
        bit(3) | bit(10) | invalidTailNoise(11),
    };
    const overlap_words = [_]usize{
        bit(12),
        bit(1),
        bit(10) | invalidTailNoise(11),
    };
    const disjoint_words = [_]usize{
        bit(2) | bit(9),
        bit(4) | bit(6),
        bit(1) | bit(8) | invalidTailNoise(11),
    };
    const tail_only_words = [_]usize{
        0,
        0,
        invalidTailNoise(11),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const guarded = cpumask_view.CpuMaskView.init(guarded_words[0..], capacity);
    const overlap = cpumask_view.CpuMaskView.init(overlap_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);
    const tail_only = cpumask_view.CpuMaskView.init(tail_only_words[0..], capacity);
    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_words[0..], capacity);

    try testing.expect(guarded.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(guarded));
    try testing.expect(base.intersects(overlap));
    try testing.expect(overlap.intersects(base));
    try testing.expect(!disjoint.isSubsetOf(base));
    try testing.expect(!base.intersects(disjoint));
    try testing.expect(!disjoint.intersects(base));
    try testing.expect(tail_only.isSubsetOf(base));
    try testing.expect(!base.intersects(tail_only));
    try testing.expect(!tail_only.intersects(base));
    try testing.expectEqual(@as(usize, 0), tail_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), tail_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), tail_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), tail_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_only.firstMissingCpu());
}
