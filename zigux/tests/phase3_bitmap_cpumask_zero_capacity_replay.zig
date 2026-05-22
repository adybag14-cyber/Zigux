const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

test "zero capacity keeps bitmap and cpumask summaries empty despite noisy words" {
    const words = [_]usize{
        std.math.maxInt(usize),
        0x5a5a5a5a5a5a5a5a,
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], 0);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], 0);

    try testing.expectEqual(@as(usize, 0), bitmap.activeWordLen());
    try testing.expectEqual(@as(usize, 0), bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, null), bitmap.firstClearBit());

    try testing.expectEqual(@as(usize, 0), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, null), cpumask.firstMissingCpu());
}

test "zero capacity keeps subset checks vacuously true and overlaps empty" {
    const noisy_a = [_]usize{
        std.math.maxInt(usize),
        0,
    };
    const noisy_b = [_]usize{
        0,
        std.math.maxInt(usize),
    };

    const empty_a = cpumask_view.CpuMaskView.init(noisy_a[0..], 0);
    const empty_b = cpumask_view.CpuMaskView.init(noisy_b[0..], 0);

    try testing.expect(empty_a.isSubsetOf(empty_b));
    try testing.expect(empty_b.isSubsetOf(empty_a));
    try testing.expect(!empty_a.intersects(empty_b));
    try testing.expect(!empty_b.intersects(empty_a));
}
