const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "offset weave keeps counts and discovery aligned across staggered words" {
    const capacity = (bitmap_view.word_bits * 2) + 13;
    const words = [_]usize{
        bit(1) | bit(7) | bit(11),
        bit(2) | bit(9) | bit(17),
        bit(0) | bit(4) | bit(11) | bit(15),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expect(bitmap.isSet(1));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 17));
    try testing.expect(bitmap.isSet((bitmap_view.word_bits * 2) + 11));
    try testing.expect(!bitmap.isSet(0));
    try testing.expect(!bitmap.isSet(bitmap_view.word_bits + 3));
    try testing.expectEqual(@as(usize, 9), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu((bitmap_view.word_bits * 2) + 11));
    try testing.expect(!cpumask.hasCpu((bitmap_view.word_bits * 2) + 12));
}

test "offset weave keeps subset and overlap checks bounded under tail noise" {
    const capacity = (bitmap_view.word_bits * 2) + 13;
    const base_words = [_]usize{
        bit(1) | bit(7) | bit(11),
        bit(2) | bit(9) | bit(17),
        bit(0) | bit(4) | bit(11) | bit(15),
    };
    const subset_words = [_]usize{
        bit(7) | bit(11),
        bit(2) | bit(17),
        bit(4) | bit(18),
    };
    const overlap_words = [_]usize{
        bit(0) | bit(7),
        bit(5) | bit(17),
        bit(11) | bit(14),
    };
    const disjoint_words = [_]usize{
        bit(3) | bit(8),
        bit(6) | bit(10),
        bit(1) | bit(12),
    };
    const tail_only_words = [_]usize{
        0,
        0,
        bit(13) | bit(17),
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
    try testing.expect(!base.intersects(disjoint));
    try testing.expect(!disjoint.intersects(base));
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
