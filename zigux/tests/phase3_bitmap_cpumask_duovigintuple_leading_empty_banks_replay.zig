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

test "duovigintuple leading empty banks keep late windows aligned and masked tail bits bounded" {
    const capacity = (25 * word_bits) + 9;
    const words = [_]usize{0} ** 22 ++ [_]usize{
        bit(1) | bit(4) | bit(9) | bit(13),
        bit(0) | bit(6) | bit(10) | bit(15),
        bit(2) | bit(5) | bit(11),
        bit(0) | bit(4) | bit(8) | invalidTailNoise(9),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 14), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 22 * word_bits + 1), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    try testing.expect(!bitmap.isSet(22 * word_bits + 0));
    try testing.expect(bitmap.isSet(22 * word_bits + 1));
    try testing.expect(bitmap.isSet(23 * word_bits + 15));
    try testing.expect(bitmap.isSet(24 * word_bits + 11));
    try testing.expect(!bitmap.isSet(25 * word_bits + 7));
    try testing.expect(bitmap.isSet(25 * word_bits + 8));
    try testing.expect(cpumask.hasCpu(22 * word_bits + 13));
    try testing.expect(!cpumask.hasCpu(23 * word_bits + 11));
    try testing.expect(cpumask.hasCpu(25 * word_bits + 4));
}

test "duovigintuple leading empty banks keep subset and overlap checks blind to invalid tail noise" {
    const capacity = (25 * word_bits) + 9;
    const base_words = [_]usize{0} ** 22 ++ [_]usize{
        bit(1) | bit(4) | bit(9) | bit(13),
        bit(0) | bit(6) | bit(10) | bit(15),
        bit(2) | bit(5) | bit(11),
        bit(0) | bit(4) | bit(8) | invalidTailNoise(9),
    };
    const subset_words = [_]usize{0} ** 22 ++ [_]usize{
        bit(4) | bit(13),
        bit(6) | bit(15),
        bit(5) | bit(11),
        bit(4) | bit(8) | invalidTailNoise(9),
    };
    const overlap_words = [_]usize{0} ** 22 ++ [_]usize{
        bit(0),
        bit(10),
        bit(5),
        bit(8) | invalidTailNoise(9),
    };
    const disjoint_words = [_]usize{0} ** 22 ++ [_]usize{
        bit(0) | bit(2),
        bit(1) | bit(5),
        bit(0) | bit(7),
        invalidTailNoise(9),
    };
    const tail_only_words = [_]usize{0} ** 25 ++ [_]usize{
        invalidTailNoise(9),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const subset = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const overlap = cpumask_view.CpuMaskView.init(overlap_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);
    const tail_only = cpumask_view.CpuMaskView.init(tail_only_words[0..], capacity);
    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_words[0..], capacity);

    try testing.expect(subset.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(subset));
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
