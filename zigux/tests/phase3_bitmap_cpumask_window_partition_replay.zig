const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "window partition keeps a full valid range saturated despite noisy trailing storage" {
    const capacity = (bitmap_view.word_bits * 2) + 5;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(3) | bit(4) | bit(12) | bit(27),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(capacity, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, null), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet((bitmap_view.word_bits * 2) + 4));
    try testing.expect(cpumask.hasCpu((bitmap_view.word_bits * 2) + 4));
}

test "window partition keeps disjoint peers subset-bounded under a full valid union" {
    const capacity = (bitmap_view.word_bits * 2) + 6;
    const left_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2),
    };
    const right_words = [_]usize{
        0,
        0,
        bit(3) | bit(4) | bit(5) | bit(11) | bit(23),
    };
    const union_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(3) | bit(4) | bit(5) | bit(9) | bit(19),
    };

    const left_bitmap = bitmap_view.BitmapView.init(left_words[0..], capacity);
    const right_bitmap = bitmap_view.BitmapView.init(right_words[0..], capacity);
    const union_bitmap = bitmap_view.BitmapView.init(union_words[0..], capacity);

    const left = cpumask_view.CpuMaskView.init(left_words[0..], capacity);
    const right = cpumask_view.CpuMaskView.init(right_words[0..], capacity);
    const full_mask = cpumask_view.CpuMaskView.init(union_words[0..], capacity);

    try testing.expectEqual(@as(usize, (bitmap_view.word_bits * 2) + 3), left_bitmap.countSetBits());
    try testing.expectEqual(@as(usize, 3), right_bitmap.countSetBits());
    try testing.expectEqual(capacity, union_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), union_bitmap.firstClearBit());
    try testing.expectEqual(union_bitmap.firstClearBit(), full_mask.firstMissingCpu());

    try testing.expect(left.isSubsetOf(full_mask));
    try testing.expect(right.isSubsetOf(full_mask));
    try testing.expect(!left.isSubsetOf(right));
    try testing.expect(!right.isSubsetOf(left));
    try testing.expect(!left.intersects(right));
    try testing.expect(!right.intersects(left));
    try testing.expect(full_mask.intersects(left));
    try testing.expect(full_mask.intersects(right));
}
