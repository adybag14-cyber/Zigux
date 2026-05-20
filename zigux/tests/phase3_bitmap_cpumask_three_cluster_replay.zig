const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

test "bitmap three-cluster replay ignores out-of-range tail noise" {
    const words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 2) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 7) |
            (@as(usize, 1) << 8) |
            (@as(usize, 1) << 9) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        std.math.maxInt(usize),
    };
    const capacity = bitmap_view.word_bits + 9;
    const view = bitmap_view.BitmapView.init(words[0..], capacity);

    try testing.expect(view.isSet(1));
    try testing.expect(view.isSet(2));
    try testing.expect(view.isSet(bitmap_view.word_bits - 1));
    try testing.expect(view.isSet(bitmap_view.word_bits));
    try testing.expect(view.isSet(bitmap_view.word_bits + 7));
    try testing.expect(view.isSet(bitmap_view.word_bits + 8));
    try testing.expectEqual(@as(usize, 6), view.countSetBits());
    try testing.expectEqual(@as(?usize, 1), view.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), view.firstClearBit());
}

test "cpumask three-cluster replay keeps subset and overlap checks bounded" {
    const base_words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 2) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 7) |
            (@as(usize, 1) << 8) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        std.math.maxInt(usize),
    };
    const superset_words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 2) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 4) |
            (@as(usize, 1) << 7) |
            (@as(usize, 1) << 8) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        0,
    };
    const disjoint_words = [_]usize{
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 5),
        (@as(usize, 1) << 3) |
            (@as(usize, 1) << 6) |
            (@as(usize, 1) << (bitmap_view.word_bits - 2)),
        std.math.maxInt(usize),
    };
    const capacity = bitmap_view.word_bits + 9;

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);

    try testing.expectEqual(@as(usize, 6), base.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), base.firstCpu());
    try testing.expectEqual(@as(?usize, 0), base.firstMissingCpu());
    try testing.expect(base.hasCpu(bitmap_view.word_bits + 8));
    try testing.expect(!base.hasCpu(bitmap_view.word_bits + 4));
    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(base.intersects(superset));
    try testing.expect(!base.intersects(disjoint));
}
