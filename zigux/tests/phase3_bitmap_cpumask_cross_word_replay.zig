const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

test "cross-word replay keeps bitmap and cpumask scans aligned inside the bounded window" {
    const words = [_]usize{
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        (@as(usize, 1) << 2) |
            (@as(usize, 1) << 5),
    };
    const bit_len = bitmap_view.word_bits + 4;

    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try testing.expect(bitmap.isSet(0));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits - 1));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 2));
    try testing.expect(cpumask.hasCpu(0));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits - 1));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 2));

    try testing.expectEqual(@as(usize, 3), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}

test "cross-word replay keeps a saturated bounded window identical for bitmap and cpumask views" {
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
    };
    const bit_len = bitmap_view.word_bits + 3;

    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try testing.expectEqual(bit_len, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, null), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(bit_len - 1));
}

test "cross-word replay keeps subset and overlap checks blind to out-of-range tail bits" {
    const bit_len = bitmap_view.word_bits + 2;
    const base_words = [_]usize{
        (@as(usize, 1) << (bitmap_view.word_bits - 2)),
        (@as(usize, 1) << 1),
    };
    const superset_words = [_]usize{
        (@as(usize, 1) << (bitmap_view.word_bits - 2)),
        std.math.maxInt(usize),
    };
    const disjoint_words = [_]usize{
        0,
        (@as(usize, 1) << 3),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], bit_len);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], bit_len);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], bit_len);

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(base.intersects(superset));
    try testing.expect(!base.intersects(disjoint));
    try testing.expectEqual(@as(usize, 0), disjoint.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), disjoint.firstCpu());
    try testing.expectEqual(@as(?usize, 0), disjoint.firstMissingCpu());
}
