const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "partial tail noise does not affect bitmap and cpumask decisions" {
    const capacity = bitmap_view.word_bits + 3;
    const active_tail_cpu = bitmap_view.word_bits + 1;

    const base_words = [_]usize{
        bit(5),
        bit(1) | bit(6),
    };
    const superset_words = [_]usize{
        bit(5) | bit(9),
        bit(1),
    };
    const ignored_overlap_words = [_]usize{
        0,
        bit(6),
    };

    const bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const ignored_overlap = cpumask_view.CpuMaskView.init(ignored_overlap_words[0..], capacity);

    try testing.expect(bitmap.isSet(5));
    try testing.expect(bitmap.isSet(active_tail_cpu));
    try testing.expectEqual(@as(usize, 2), bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, 5), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());

    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(cpumask));
    try testing.expect(!cpumask.intersects(ignored_overlap));
}

test "filled declared tail stays full even when the last backing word is noisy" {
    const capacity = bitmap_view.word_bits + 3;
    const words = [_]usize{
        std.math.maxInt(usize),
        bit(0) |
            bit(1) |
            bit(2) |
            bit(7),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(capacity, bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, null), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}
