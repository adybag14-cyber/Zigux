const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "sexquadragintuple trailing empty banks preserve first and next cpu walks across the sparse gulf" {
    const capacity = (48 * bitmap_view.word_bits) + 13;
    const empty46: [46]usize = @splat(0);
    const words = [_]usize{
        bit(2) | bit(5) | bit(11),
        bit(1) | bit(9) | bit(14) | bit(17),
    } ++ empty46 ++ [_]usize{
        bit(0) | bit(3) | bit(6) | bit(9) | bit(12),
        std.math.maxInt(usize),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 12), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 2), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expectEqual(@as(?usize, 5), bitmap.nextSetBit(3));
    try testing.expectEqual(bitmap.nextSetBit(3), cpumask.nextCpu(3));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 1), cpumask.nextCpu(12));
    try testing.expectEqual(@as(?usize, (48 * bitmap_view.word_bits) + 0), cpumask.nextCpu(2 * bitmap_view.word_bits));
    try testing.expectEqual(@as(?usize, (48 * bitmap_view.word_bits) + 12), bitmap.nextSetBit((48 * bitmap_view.word_bits) + 10));
    try testing.expectEqual(@as(?usize, null), cpumask.nextCpu((48 * bitmap_view.word_bits) + 13));
    try testing.expectEqual(@as(?usize, (48 * bitmap_view.word_bits) + 1), cpumask.nextMissingCpu(48 * bitmap_view.word_bits));
    try testing.expect(!bitmap.isSet((47 * bitmap_view.word_bits) + 31));
    try testing.expect(cpumask.hasCpu((48 * bitmap_view.word_bits) + 12));
}

test "sexquadragintuple trailing empty banks keep subset and overlap decisions independent of ignored tail noise" {
    const capacity = (48 * bitmap_view.word_bits) + 13;
    const empty46: [46]usize = @splat(0);
    const empty48: [48]usize = @splat(0);
    const base_words = [_]usize{
        bit(2) | bit(5) | bit(11),
        bit(1) | bit(9) | bit(14) | bit(17),
    } ++ empty46 ++ [_]usize{
        bit(0) | bit(3) | bit(6) | bit(9) | bit(12),
        std.math.maxInt(usize),
    };
    const subset_words = [_]usize{
        bit(2) | bit(11),
        bit(14),
    } ++ empty46 ++ [_]usize{
        bit(3) | bit(12),
        std.math.maxInt(usize),
    };
    const overlap_words = [_]usize{
        bit(5),
        bit(9) | bit(17),
    } ++ empty46 ++ [_]usize{
        bit(0) | bit(6),
        std.math.maxInt(usize),
    };
    const disjoint_words = [_]usize{
        bit(0) | bit(7),
        bit(3) | bit(12),
    } ++ empty46 ++ [_]usize{
        bit(1) | bit(10),
        std.math.maxInt(usize),
    };
    const ignored_tail_words = empty48 ++ [_]usize{
        bit(14) | bit(21) | bit(30),
        std.math.maxInt(usize),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const subset = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const overlap = cpumask_view.CpuMaskView.init(overlap_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);
    const ignored_tail = cpumask_view.CpuMaskView.init(ignored_tail_words[0..], capacity);
    const ignored_tail_bitmap = bitmap_view.BitmapView.init(ignored_tail_words[0..], capacity);

    try testing.expect(subset.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(subset));
    try testing.expect(base.intersects(overlap));
    try testing.expect(overlap.intersects(base));
    try testing.expect(!disjoint.isSubsetOf(base));
    try testing.expect(!base.intersects(disjoint));
    try testing.expect(!disjoint.intersects(base));
    try testing.expect(ignored_tail.isSubsetOf(base));
    try testing.expect(!base.intersects(ignored_tail));
    try testing.expect(!ignored_tail.intersects(base));
    try testing.expectEqual(@as(usize, 0), ignored_tail_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), ignored_tail_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), ignored_tail_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), ignored_tail.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), ignored_tail.firstCpu());
    try testing.expectEqual(@as(?usize, 0), ignored_tail.firstMissingCpu());
}
