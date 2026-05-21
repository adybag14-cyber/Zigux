const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

test "boundary hinge replay keeps bitmap and cpumask summaries aligned" {
    const capacity = bitmap_view.word_bits + 9;
    const tail_valid_mask = (@as(usize, 1) << 9) - 1;
    const words = [_]usize{
        std.math.maxInt(usize) ^ (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        (tail_valid_mask ^ ((@as(usize, 1) << 0) | (@as(usize, 1) << 4))) | ~tail_valid_mask,
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(capacity - 3, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits - 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits - 2));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits - 1));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 1));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits + 4));
}

test "boundary hinge replay keeps subset and overlap checks bounded" {
    const capacity = bitmap_view.word_bits + 9;
    const tail_valid_mask = (@as(usize, 1) << 9) - 1;
    const hinge_words = [_]usize{
        std.math.maxInt(usize) ^ (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        (tail_valid_mask ^ ((@as(usize, 1) << 0) | (@as(usize, 1) << 4))) | ~tail_valid_mask,
    };
    const superset_words = [_]usize{
        std.math.maxInt(usize),
        tail_valid_mask | ~tail_valid_mask,
    };
    const hinge_gaps_only_words = [_]usize{
        @as(usize, 1) << (bitmap_view.word_bits - 1),
        ((@as(usize, 1) << 0) | (@as(usize, 1) << 4)) | ~tail_valid_mask,
    };

    const hinge = cpumask_view.CpuMaskView.init(hinge_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const hinge_gaps_only = cpumask_view.CpuMaskView.init(hinge_gaps_only_words[0..], capacity);

    try testing.expect(hinge.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(hinge));
    try testing.expect(hinge.intersects(superset));
    try testing.expect(!hinge.intersects(hinge_gaps_only));
}

test "boundary hinge replay ignores tail-only storage outside the bounded window" {
    const capacity = bitmap_view.word_bits + 9;
    const words = [_]usize{
        0,
        ~((@as(usize, 1) << 9) - 1),
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
