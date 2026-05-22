const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "exact full-word capacity keeps bitmap and cpumask summaries aligned" {
    const capacity = bitmap_view.word_bits * 2;
    const words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(bitmap_view.word_bits - 1),
        std.math.maxInt(usize),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expect(bitmap.isSet(0));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits - 1));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits));
    try testing.expect(bitmap.isSet(capacity - 1));
    try testing.expect(!bitmap.isSet(bitmap_view.word_bits + 1));
    try testing.expectEqual(@as(usize, bitmap_view.word_bits + 2), bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 1), bitmap.firstClearBit());

    try testing.expect(cpumask.hasCpu(0));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits));
    try testing.expect(cpumask.hasCpu(capacity - 1));
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}

test "exact full-word capacity ignores storage beyond the active words for subset and overlap" {
    const capacity = bitmap_view.word_bits * 2;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(bitmap_view.word_bits - 1),
        std.math.maxInt(usize),
    };
    const superset_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(3) | bit(bitmap_view.word_bits - 1),
        0,
    };
    const peer_words = [_]usize{
        0,
        bit(bitmap_view.word_bits - 1),
        std.math.maxInt(usize),
    };
    const outside_only_words = [_]usize{
        0,
        0,
        std.math.maxInt(usize),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const peer = cpumask_view.CpuMaskView.init(peer_words[0..], capacity);
    const outside_only = cpumask_view.CpuMaskView.init(outside_only_words[0..], capacity);

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(base.intersects(peer));
    try testing.expect(!base.intersects(outside_only));
}
