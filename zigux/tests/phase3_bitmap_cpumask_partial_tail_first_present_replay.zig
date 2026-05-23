const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "partial tail first-present discovery skips empty leading words and ignores tail noise" {
    const capacity = (bitmap_view.word_bits * 2) + 7;
    const words = [_]usize{
        0,
        0,
        bit(3) | bit(5) | bit(11) | bit(17),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);
    const expected_first = (bitmap_view.word_bits * 2) + 3;

    try testing.expectEqual(@as(usize, 2), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, expected_first), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(expected_first));
    try testing.expect(bitmap.isSet((bitmap_view.word_bits * 2) + 5));
    try testing.expect(!bitmap.isSet((bitmap_view.word_bits * 2) + 6));
    try testing.expect(cpumask.hasCpu(expected_first));
    try testing.expect(cpumask.hasCpu((bitmap_view.word_bits * 2) + 5));
    try testing.expect(!cpumask.hasCpu((bitmap_view.word_bits * 2) + 6));
}

test "partial tail first-present subset and overlap checks stay blind to tail-only noise" {
    const capacity = (bitmap_view.word_bits * 2) + 7;
    const base_words = [_]usize{
        0,
        0,
        bit(1) | bit(3) | bit(5),
    };
    const subset_words = [_]usize{
        0,
        0,
        bit(1) | bit(5) | bit(10),
    };
    const overlap_words = [_]usize{
        0,
        0,
        bit(3) | bit(9),
    };
    const disjoint_words = [_]usize{
        0,
        0,
        bit(0) | bit(2) | bit(6),
    };
    const tail_only_words = [_]usize{
        0,
        0,
        bit(9) | bit(14) | bit(20),
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
