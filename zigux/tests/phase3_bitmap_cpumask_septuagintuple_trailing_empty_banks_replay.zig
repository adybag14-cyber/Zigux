const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "septuagintuple trailing empty banks keep bitmap and cpumask walks aligned across a wide silent span" {
    const capacity = (72 * bitmap_view.word_bits) + 19;
    const empty70: [70]usize = @splat(0);
    const words = [_]usize{
        bit(1) | bit(6) | bit(13) | bit(21),
        bit(2) | bit(8) | bit(15),
    } ++ empty70 ++ [_]usize{
        bit(0) | bit(4) | bit(9) | bit(18),
        std.math.maxInt(usize),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 11), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expectEqual(@as(?usize, 6), bitmap.nextSetBit(2));
    try testing.expectEqual(bitmap.nextSetBit(2), cpumask.nextCpu(2));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 2), cpumask.nextCpu(22));
    try testing.expectEqual(@as(?usize, (72 * bitmap_view.word_bits) + 0), cpumask.nextCpu(2 * bitmap_view.word_bits));
    try testing.expectEqual(@as(?usize, (72 * bitmap_view.word_bits) + 18), bitmap.nextSetBit((72 * bitmap_view.word_bits) + 10));
    try testing.expectEqual(@as(?usize, null), cpumask.nextCpu((72 * bitmap_view.word_bits) + 19));
    try testing.expectEqual(@as(?usize, (72 * bitmap_view.word_bits) + 1), cpumask.nextMissingCpu(72 * bitmap_view.word_bits));
    try testing.expect(!bitmap.isSet((71 * bitmap_view.word_bits) + 37));
    try testing.expect(cpumask.hasCpu((72 * bitmap_view.word_bits) + 18));
}

test "septuagintuple trailing empty banks keep subset overlap and ignored tail noise bounded" {
    const capacity = (72 * bitmap_view.word_bits) + 19;
    const empty70: [70]usize = @splat(0);
    const empty72: [72]usize = @splat(0);
    const base_words = [_]usize{
        bit(1) | bit(6) | bit(13) | bit(21),
        bit(2) | bit(8) | bit(15),
    } ++ empty70 ++ [_]usize{
        bit(0) | bit(4) | bit(9) | bit(18),
        std.math.maxInt(usize),
    };
    const subset_words = [_]usize{
        bit(1) | bit(21),
        bit(8),
    } ++ empty70 ++ [_]usize{
        bit(4) | bit(18),
        std.math.maxInt(usize),
    };
    const overlap_words = [_]usize{
        bit(6),
        bit(2) | bit(15),
    } ++ empty70 ++ [_]usize{
        bit(0) | bit(9),
        std.math.maxInt(usize),
    };
    const disjoint_words = [_]usize{
        bit(0) | bit(5),
        bit(1) | bit(7) | bit(14),
    } ++ empty70 ++ [_]usize{
        bit(2) | bit(10) | bit(17),
        std.math.maxInt(usize),
    };
    const ignored_tail_words = empty72 ++ [_]usize{
        bit(19) | bit(27) | bit(41),
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
