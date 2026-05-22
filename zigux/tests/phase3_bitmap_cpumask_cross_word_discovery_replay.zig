const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "first set bit can live in a later word after a fully clear prefix" {
    const capacity = bitmap_view.word_bits + 5;
    const base_words = [_]usize{
        0,
        bit(1) | bit(4) | bit(11),
    };
    const superset_words = [_]usize{
        bit(3),
        bit(1) | bit(2) | bit(4),
    };
    const prefix_only_words = [_]usize{
        std.math.maxInt(usize),
        0,
    };

    const bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const prefix_only = cpumask_view.CpuMaskView.init(prefix_only_words[0..], capacity);

    try testing.expect(!bitmap.isSet(0));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 1));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 4));
    try testing.expectEqual(@as(usize, 2), bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 1), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());

    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(cpumask));
    try testing.expect(!cpumask.intersects(prefix_only));
}

test "first missing cpu can live in a later word after a fully saturated prefix" {
    const capacity = bitmap_view.word_bits + 5;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(2) | bit(4) | bit(9),
    };
    const superset_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(4),
    };
    const ignored_tail_only_words = [_]usize{
        0,
        bit(9),
    };

    const bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const ignored_tail_only = cpumask_view.CpuMaskView.init(ignored_tail_only_words[0..], capacity);

    try testing.expect(bitmap.isSet(0));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits));
    try testing.expect(!bitmap.isSet(bitmap_view.word_bits + 1));
    try testing.expectEqual(capacity - 2, bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 1), bitmap.firstClearBit());

    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(cpumask));
    try testing.expect(!cpumask.intersects(ignored_tail_only));
}
