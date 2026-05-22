const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "exact whole-word capacity ignores a fully extra trailing word" {
    const capacity = bitmap_view.word_bits * 2;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(7) | bit(19),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(capacity, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, null), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(capacity - 1));
    try testing.expect(cpumask.hasCpu(capacity - 1));
}

test "exact whole-word capacity keeps subset and overlap checks off the ignored trailing word" {
    const capacity = bitmap_view.word_bits * 2;
    const base_words = [_]usize{
        bit(1) | bit(6) | bit(11),
        bit(0) | bit(4) | bit(8),
        bit(2) | bit(9),
    };
    const superset_words = [_]usize{
        bit(1) | bit(3) | bit(6) | bit(11),
        bit(0) | bit(4) | bit(7) | bit(8),
        0,
    };
    const overlapping_words = [_]usize{
        bit(6),
        bit(4) | bit(12),
        bit(2),
    };
    const tail_only_words = [_]usize{
        0,
        0,
        bit(0) | bit(5) | bit(17),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const overlapping = cpumask_view.CpuMaskView.init(overlapping_words[0..], capacity);
    const tail_only = cpumask_view.CpuMaskView.init(tail_only_words[0..], capacity);
    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_words[0..], capacity);

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(base.intersects(overlapping));
    try testing.expect(overlapping.intersects(base));
    try testing.expect(!base.intersects(tail_only));
    try testing.expect(!tail_only.intersects(base));
    try testing.expect(tail_only.isSubsetOf(base));
    try testing.expectEqual(@as(usize, 0), tail_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), tail_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), tail_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), tail_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_only.firstMissingCpu());
}
