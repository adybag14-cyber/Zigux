const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "offset windows keep first-present discovery aligned" {
    const capacity = bitmap_view.word_bits + 10;
    const words = [_]usize{
        bit(4) | bit(5) | bit(9),
        bit(0) | bit(3) | bit(8),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expect(!bitmap.isSet(0));
    try testing.expect(bitmap.isSet(4));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 8));
    try testing.expect(!bitmap.isSet(bitmap_view.word_bits + 9));
    try testing.expectEqual(@as(usize, 6), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 4), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 3));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits + 9));
}

test "dense prefix keeps late gaps and tail-only masks bounded" {
    const capacity = bitmap_view.word_bits + 9;
    const dense_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(4) | bit(8) | bit(11),
    };
    const subset_words = [_]usize{
        bit(2) | bit(5) | bit(9),
        bit(1) | bit(8) | bit(11),
    };
    const late_overlap_words = [_]usize{
        0,
        bit(8),
    };
    const late_disjoint_words = [_]usize{
        0,
        bit(3) | bit(5),
    };
    const tail_only_words = [_]usize{
        0,
        bit(10) | bit(11),
    };

    const dense_bitmap = bitmap_view.BitmapView.init(dense_words[0..], capacity);
    const dense = cpumask_view.CpuMaskView.init(dense_words[0..], capacity);
    const subset = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const late_overlap = cpumask_view.CpuMaskView.init(late_overlap_words[0..], capacity);
    const late_disjoint = cpumask_view.CpuMaskView.init(late_disjoint_words[0..], capacity);
    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_words[0..], capacity);
    const tail_only = cpumask_view.CpuMaskView.init(tail_only_words[0..], capacity);

    try testing.expectEqual(capacity - 4, dense_bitmap.countSetBits());
    try testing.expectEqual(dense_bitmap.countSetBits(), dense.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), dense_bitmap.firstSetBit());
    try testing.expectEqual(dense_bitmap.firstSetBit(), dense.firstCpu());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 3), dense_bitmap.firstClearBit());
    try testing.expectEqual(dense_bitmap.firstClearBit(), dense.firstMissingCpu());
    try testing.expect(subset.isSubsetOf(dense));
    try testing.expect(!dense.isSubsetOf(subset));
    try testing.expect(dense.intersects(late_overlap));
    try testing.expect(late_overlap.intersects(dense));
    try testing.expect(!dense.intersects(late_disjoint));
    try testing.expect(!late_disjoint.intersects(dense));
    try testing.expect(!dense.intersects(tail_only));
    try testing.expect(!tail_only.intersects(dense));
    try testing.expect(tail_only.isSubsetOf(dense));
    try testing.expectEqual(@as(usize, 0), tail_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), tail_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), tail_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), tail_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_only.firstMissingCpu());
}
