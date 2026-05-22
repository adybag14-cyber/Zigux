const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "declared capacity ignores trailing words beyond the active range" {
    const capacity = 8;
    const base_words = [_]usize{
        bit(1) | bit(4) | bit(7),
        std.math.maxInt(usize),
    };
    const superset_words = [_]usize{
        bit(1) | bit(4) | bit(7),
        0,
    };
    const trailing_only_words = [_]usize{
        0,
        std.math.maxInt(usize),
    };

    const bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const trailing_only = cpumask_view.CpuMaskView.init(trailing_only_words[0..], capacity);

    try testing.expect(bitmap.isSet(1));
    try testing.expect(bitmap.isSet(4));
    try testing.expect(bitmap.isSet(7));
    try testing.expect(!bitmap.isSet(0));
    try testing.expectEqual(@as(usize, 3), bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());

    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(trailing_only));
    try testing.expect(!cpumask.intersects(trailing_only));
}

test "zero-capacity bitmap and cpumask views stay trivial even with noisy backing words" {
    const noisy_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
    };

    const bitmap = bitmap_view.BitmapView.init(noisy_words[0..], 0);
    const cpumask = cpumask_view.CpuMaskView.init(noisy_words[0..], 0);
    const peer = cpumask_view.CpuMaskView.init(noisy_words[0..], 0);

    try testing.expectEqual(@as(usize, 0), bitmap.activeWordLen());
    try testing.expectEqual(@as(usize, 0), bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, null), bitmap.firstClearBit());

    try testing.expectEqual(@as(usize, 0), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, null), cpumask.firstMissingCpu());
    try testing.expect(cpumask.isSubsetOf(peer));
    try testing.expect(!cpumask.intersects(peer));
}
