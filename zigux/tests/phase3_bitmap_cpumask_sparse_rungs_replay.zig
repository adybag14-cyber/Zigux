const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "sparse rungs keep bitmap and cpumask counts aligned across alternating words" {
    const capacity = bitmap_view.word_bits * 3 - 5;
    const valid_tail_bits = bitmap_view.word_bits - 5;
    const invalid_tail_noise = ~((@as(usize, 1) << @intCast(valid_tail_bits)) - 1);
    const words = [_]usize{
        bit(1) | bit(5) | bit(9),
        bit(2) | bit(7),
        bit(0) | bit(4) | bit(10) | invalid_tail_noise,
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 8), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 7));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 7));
}

test "sparse rungs ignore tail-only overlap and subset noise beyond the declared capacity" {
    const capacity = bitmap_view.word_bits * 2 + 9;
    const base_words = [_]usize{
        bit(0) | bit(4) | bit(11),
        bit(1) | bit(6),
        bit(3),
    };
    const superset_words = [_]usize{
        bit(0) | bit(4) | bit(7) | bit(11),
        bit(1) | bit(5) | bit(6),
        bit(3) | bit(8),
    };
    const overlap_words = [_]usize{
        bit(11),
        bit(6),
        0,
    };
    const tail_only_words = [_]usize{
        0,
        0,
        bit(9) | bit(14) | bit(21),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const overlap = cpumask_view.CpuMaskView.init(overlap_words[0..], capacity);
    const tail_only = cpumask_view.CpuMaskView.init(tail_only_words[0..], capacity);
    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_words[0..], capacity);

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(base.intersects(overlap));
    try testing.expect(overlap.intersects(base));
    try testing.expect(!base.intersects(tail_only));
    try testing.expect(!tail_only.intersects(base));
    try testing.expect(tail_only.isSubsetOf(base));
    try testing.expectEqual(@as(usize, 0), tail_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), tail_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), tail_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), tail_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_only.firstMissingCpu());
}
