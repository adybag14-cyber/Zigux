const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "all empty banks keep discovery pinned to the first valid gap" {
    const capacity = (3 * bitmap_view.word_bits) + 9;
    const words = [_]usize{
        0,
        0,
        0,
        bit(9) | bit(12) | bit(17),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expect(!bitmap.isSet(0));
    try testing.expect(!bitmap.isSet((2 * bitmap_view.word_bits) + 17));
    try testing.expect(!bitmap.isSet((3 * bitmap_view.word_bits) + 8));
    try testing.expectEqual(@as(usize, 0), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(!cpumask.hasCpu(0));
    try testing.expect(!cpumask.hasCpu((3 * bitmap_view.word_bits) + 8));
}

test "all empty banks keep masked tail noise invisible to subset and overlap checks" {
    const capacity = (3 * bitmap_view.word_bits) + 9;
    const base_words = [_]usize{
        0,
        0,
        0,
        bit(9) | bit(12) | bit(17),
    };
    const masked_tail_only_words = [_]usize{
        0,
        0,
        0,
        bit(10) | bit(13) | bit(18),
    };
    const real_tail_words = [_]usize{
        0,
        0,
        0,
        bit(2),
    };
    const head_words = [_]usize{
        bit(4),
        0,
        0,
        bit(9) | bit(12) | bit(17),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const masked_tail_only = cpumask_view.CpuMaskView.init(masked_tail_only_words[0..], capacity);
    const real_tail = cpumask_view.CpuMaskView.init(real_tail_words[0..], capacity);
    const head = cpumask_view.CpuMaskView.init(head_words[0..], capacity);
    const masked_tail_bitmap = bitmap_view.BitmapView.init(masked_tail_only_words[0..], capacity);

    try testing.expect(masked_tail_only.isSubsetOf(base));
    try testing.expect(base.isSubsetOf(masked_tail_only));
    try testing.expect(!base.intersects(masked_tail_only));
    try testing.expect(!masked_tail_only.intersects(base));
    try testing.expect(!real_tail.isSubsetOf(base));
    try testing.expect(!base.intersects(real_tail));
    try testing.expect(!real_tail.intersects(base));
    try testing.expect(!head.isSubsetOf(base));
    try testing.expect(!base.intersects(head));
    try testing.expect(!head.intersects(base));
    try testing.expectEqual(@as(usize, 0), masked_tail_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), masked_tail_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), masked_tail_bitmap.firstClearBit());
}
