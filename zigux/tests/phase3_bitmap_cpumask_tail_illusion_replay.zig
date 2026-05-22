const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "tail-only bits do not fake discovery in a sparse final partial word" {
    const capacity = (bitmap_view.word_bits * 2) + 5;
    const words = [_]usize{
        0,
        0,
        bit(1) | bit(4) | bit(8) | bit(17),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 2), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, (bitmap_view.word_bits * 2) + 1), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu((bitmap_view.word_bits * 2) + 4));
    try testing.expect(!cpumask.hasCpu((bitmap_view.word_bits * 2) + 2));
}

test "tail-only bits do not fake subset or overlap inside the final partial word" {
    const capacity = (bitmap_view.word_bits * 2) + 5;
    const base_words = [_]usize{
        bit(2),
        bit(5),
        bit(1) | bit(4) | bit(14),
    };
    const tail_only_words = [_]usize{
        0,
        0,
        bit(7) | bit(10) | bit(19),
    };
    const missing_valid_words = [_]usize{
        bit(2),
        bit(5),
        bit(1) | bit(9),
    };
    const valid_overlap_words = [_]usize{
        0,
        bit(5),
        bit(4) | bit(8),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const tail_only = cpumask_view.CpuMaskView.init(tail_only_words[0..], capacity);
    const missing_valid = cpumask_view.CpuMaskView.init(missing_valid_words[0..], capacity);
    const valid_overlap = cpumask_view.CpuMaskView.init(valid_overlap_words[0..], capacity);
    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_words[0..], capacity);

    try testing.expectEqual(@as(usize, 0), tail_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), tail_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), tail_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), tail_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_only.firstMissingCpu());
    try testing.expect(tail_only.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(missing_valid));
    try testing.expect(missing_valid.isSubsetOf(base));
    try testing.expect(!base.intersects(tail_only));
    try testing.expect(!tail_only.intersects(base));
    try testing.expect(base.intersects(valid_overlap));
    try testing.expect(valid_overlap.intersects(base));
}
