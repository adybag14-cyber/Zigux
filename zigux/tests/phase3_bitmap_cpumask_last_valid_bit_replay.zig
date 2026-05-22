const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

test "last valid bit replay keeps a saturated tail bounded to the declared capacity" {
    const capacity = bitmap_view.word_bits + 1;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    try testing.expectEqual(capacity, bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, null), bitmap.firstClearBit());

    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);
    try testing.expectEqual(capacity, cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, null), cpumask.firstMissingCpu());
}

test "last valid bit replay ignores invalid overlap in the trailing word" {
    const capacity = bitmap_view.word_bits + 1;
    const tail_only_words = [_]usize{
        0,
        std.math.maxInt(usize),
    };
    const invalid_only_words = [_]usize{
        0,
        std.math.maxInt(usize) & ~@as(usize, 1),
    };
    const exact_tail_words = [_]usize{
        0,
        @as(usize, 1),
    };

    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_words[0..], capacity);
    try testing.expectEqual(@as(usize, 1), tail_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits), tail_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_only_bitmap.firstClearBit());

    const tail_only = cpumask_view.CpuMaskView.init(tail_only_words[0..], capacity);
    const invalid_only = cpumask_view.CpuMaskView.init(invalid_only_words[0..], capacity);
    const exact_tail = cpumask_view.CpuMaskView.init(exact_tail_words[0..], capacity);

    try testing.expectEqual(@as(usize, 1), tail_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits), tail_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_only.firstMissingCpu());

    try testing.expectEqual(@as(usize, 0), invalid_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), invalid_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), invalid_only.firstMissingCpu());

    try testing.expect(!tail_only.intersects(invalid_only));
    try testing.expect(!tail_only.isSubsetOf(invalid_only));
    try testing.expect(invalid_only.isSubsetOf(tail_only));

    try testing.expect(tail_only.intersects(exact_tail));
    try testing.expect(tail_only.isSubsetOf(exact_tail));
    try testing.expect(exact_tail.isSubsetOf(tail_only));
}
