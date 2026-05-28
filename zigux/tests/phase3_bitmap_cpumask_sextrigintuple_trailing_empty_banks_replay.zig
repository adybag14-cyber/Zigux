const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "sextrigintuple trailing empty banks keep early windows aligned and masked tail bits bounded" {
    const capacity = (38 * bitmap_view.word_bits) + 13;
    const words = [_]usize{
        bit(1) | bit(6) | bit(10) | bit(15),
        bit(0) | bit(4) | bit(8) | bit(13),
    } ++ [_]usize{0} ** 36 ++ [_]usize{
        bit(2) | bit(7) | bit(9) | bit(12),
        std.math.maxInt(usize),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expect(!bitmap.isSet(0));
    try testing.expect(bitmap.isSet(1));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 13));
    try testing.expect(!bitmap.isSet((2 * bitmap_view.word_bits) + 5));
    try testing.expect(bitmap.isSet((38 * bitmap_view.word_bits) + 2));
    try testing.expect(bitmap.isSet((38 * bitmap_view.word_bits) + 12));
    try testing.expect(!bitmap.isSet((38 * bitmap_view.word_bits) + 11));
    try testing.expectEqual(@as(usize, 12), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 4));
    try testing.expect(!cpumask.hasCpu((37 * bitmap_view.word_bits) + 14));
    try testing.expect(cpumask.hasCpu((38 * bitmap_view.word_bits) + 7));
}

test "sextrigintuple trailing empty banks keep subset and overlap checks bounded under masked late noise" {
    const capacity = (38 * bitmap_view.word_bits) + 13;
    const base_words = [_]usize{
        bit(1) | bit(6) | bit(10) | bit(15),
        bit(0) | bit(4) | bit(8) | bit(13),
    } ++ [_]usize{0} ** 36 ++ [_]usize{
        bit(2) | bit(7) | bit(9) | bit(12),
        std.math.maxInt(usize),
    };
    const subset_words = [_]usize{
        bit(6) | bit(15),
        bit(4) | bit(8),
    } ++ [_]usize{0} ** 36 ++ [_]usize{
        bit(7) | bit(12),
        std.math.maxInt(usize),
    };
    const overlap_words = [_]usize{
        bit(1),
        bit(13),
    } ++ [_]usize{0} ** 36 ++ [_]usize{
        bit(9),
        std.math.maxInt(usize),
    };
    const disjoint_words = [_]usize{
        bit(3) | bit(12),
        bit(2) | bit(11),
    } ++ [_]usize{0} ** 36 ++ [_]usize{
        bit(5),
        std.math.maxInt(usize),
    };
    const tail_only_words = [_]usize{0} ** 38 ++ [_]usize{
        bit(13) | bit(14) | bit(15),
        std.math.maxInt(usize),
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
