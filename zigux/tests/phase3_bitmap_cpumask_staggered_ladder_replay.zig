const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

test "staggered ladder replay keeps bitmap and cpumask summaries aligned" {
    const capacity = bitmap_view.word_bits + 11;
    const words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 5) |
            (@as(usize, 1) << (bitmap_view.word_bits - 2)),
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 4) |
            (@as(usize, 1) << 10) |
            ~((@as(usize, 1) << 11) - 1),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 6), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(1));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits - 2));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 4));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits + 5));
}

test "staggered ladder replay keeps subset and overlap checks bounded" {
    const capacity = bitmap_view.word_bits + 11;
    const ladder_words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 5) |
            (@as(usize, 1) << (bitmap_view.word_bits - 2)),
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 4) |
            (@as(usize, 1) << 10) |
            ~((@as(usize, 1) << 11) - 1),
    };
    const superset_words = [_]usize{
        ladder_words[0] | (@as(usize, 1) << 9),
        ladder_words[1] | (@as(usize, 1) << 7),
    };
    const shifted_words = [_]usize{
        (@as(usize, 1) << 2) |
            (@as(usize, 1) << 6),
        (@as(usize, 1) << 3) |
            ~((@as(usize, 1) << 11) - 1),
    };

    const ladder = cpumask_view.CpuMaskView.init(ladder_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const shifted = cpumask_view.CpuMaskView.init(shifted_words[0..], capacity);

    try testing.expect(ladder.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(ladder));
    try testing.expect(ladder.intersects(superset));
    try testing.expect(!ladder.intersects(shifted));
}

test "staggered ladder replay ignores tail-only storage for empty masks" {
    const capacity = bitmap_view.word_bits + 11;
    const words = [_]usize{
        0,
        ~((@as(usize, 1) << 11) - 1),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 0), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}
