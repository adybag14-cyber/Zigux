const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

test "guard-band flip replay keeps bitmap and cpumask summaries aligned across a partial tail" {
    const words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        (@as(usize, 1) << 2) |
            (@as(usize, 1) << 9),
    };
    const capacity = bitmap_view.word_bits + 5;
    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expect(bitmap.isSet(1));
    try testing.expect(cpumask.hasCpu(1));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits - 1));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits - 1));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 2));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 2));
    try testing.expectEqual(@as(usize, 3), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
}

test "guard-band flip replay ignores invalid tail-only noise in subset and overlap checks" {
    const capacity = bitmap_view.word_bits + 3;
    const base_words = [_]usize{
        (@as(usize, 1) << 2) |
            (@as(usize, 1) << 6),
        (@as(usize, 1) << 4) |
            (@as(usize, 1) << 10),
    };
    const superset_words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 2) |
            (@as(usize, 1) << 6),
        0,
    };
    const disjoint_words = [_]usize{
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 5),
        (@as(usize, 1) << 4) |
            (@as(usize, 1) << 10),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(base.intersects(superset));
    try testing.expect(!base.intersects(disjoint));
}

test "guard-band flip replay keeps the boundary gap visible without counting invalid tail ones" {
    const capacity = bitmap_view.word_bits + 4;
    const words = [_]usize{
        std.math.maxInt(usize) ^ (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        std.math.maxInt(usize),
    };
    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(capacity - 1, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits - 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}
