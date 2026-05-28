const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

test "bitmap starter packet keeps set-bit counting bounded to the declared range" {
    const all_bits = std.math.maxInt(usize);
    const words = [_]usize{ all_bits, all_bits };
    const capacity = bitmap_view.word_bits + 3;
    const view = bitmap_view.BitmapView.init(words[0..], capacity);

    try testing.expectEqual(capacity, view.countSetBits());
    try testing.expectEqual(@as(?usize, 0), view.firstSetBit());
    try testing.expectEqual(@as(?usize, null), view.firstClearBit());
}

test "bitmap starter packet keeps a sparse shared bitmap reviewable" {
    const words = [_]usize{
        (@as(usize, 1) << 2) |
            (@as(usize, 1) << 9),
    };
    const view = bitmap_view.BitmapView.init(words[0..], 16);

    try testing.expect(view.isSet(2));
    try testing.expect(!view.isSet(3));
    try testing.expectEqual(@as(usize, 2), view.countSetBits());
    try testing.expectEqual(@as(?usize, 2), view.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), view.firstClearBit());
}

test "bitmap starter packet keeps subset and overlap checks reusable across helper families" {
    const bit_len = bitmap_view.word_bits + 2;
    const base_words = [_]usize{
        (@as(usize, 1) << 1),
        (@as(usize, 1) << 2),
    };
    const superset_words = [_]usize{
        (@as(usize, 1) << 1),
        (@as(usize, 1) << 0),
    };
    const disjoint_words = [_]usize{
        (@as(usize, 1) << 3),
        (@as(usize, 1) << 2),
    };

    const base = bitmap_view.BitmapView.init(base_words[0..], bit_len);
    const superset = bitmap_view.BitmapView.init(superset_words[0..], bit_len);
    const disjoint = bitmap_view.BitmapView.init(disjoint_words[0..], bit_len);

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(!base.intersects(disjoint));
}

test "bitmap starter packet ignores cross-word tail padding while walking bounded clear bits" {
    const words = [_]usize{
        std.math.maxInt(usize),
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 4) |
            (~@as(usize, 0) << 5),
    };
    const capacity = bitmap_view.word_bits + 5;
    const view = bitmap_view.BitmapView.init(words[0..], capacity);

    try testing.expectEqual(capacity - 3, view.countSetBits());
    try testing.expectEqual(@as(?usize, 0), view.firstSetBit());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 1), view.firstClearBit());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 4), view.nextSetBit(bitmap_view.word_bits + 1));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 2), view.nextClearBit(bitmap_view.word_bits + 2));
}

test "bitmap starter packet can walk set and clear bits from a bounded start point" {
    const words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 4) |
            (@as(usize, 1) << 7),
        std.math.maxInt(usize),
    };
    const view = bitmap_view.BitmapView.init(words[0..], 8);

    try testing.expectEqual(@as(?usize, 1), view.nextSetBit(0));
    try testing.expectEqual(@as(?usize, 4), view.nextSetBit(2));
    try testing.expectEqual(@as(?usize, 7), view.nextSetBit(7));
    try testing.expectEqual(@as(?usize, null), view.nextSetBit(8));

    try testing.expectEqual(@as(?usize, 0), view.nextClearBit(0));
    try testing.expectEqual(@as(?usize, 2), view.nextClearBit(2));
    try testing.expectEqual(@as(?usize, 5), view.nextClearBit(5));
    try testing.expectEqual(@as(?usize, null), view.nextClearBit(8));
}

test "cpumask starter packet keeps cpu membership and missing-cpu discovery explicit" {
    const words = [_]usize{
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 2) |
            (@as(usize, 1) << 7),
    };
    const mask = cpumask_view.CpuMaskView.init(words[0..], 8);

    try testing.expect(mask.hasCpu(0));
    try testing.expect(mask.hasCpu(7));
    try testing.expect(!mask.hasCpu(1));
    try testing.expectEqual(@as(usize, 3), mask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), mask.firstCpu());
    try testing.expectEqual(@as(?usize, 1), mask.firstMissingCpu());
}

test "cpumask starter packet keeps subset and overlap semantics inside the bounded mask" {
    const base_words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 4),
        std.math.maxInt(usize),
    };
    const superset_words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 3) |
            (@as(usize, 1) << 4),
        0,
    };
    const disjoint_words = [_]usize{
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 2),
        0,
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], 8);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], 8);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], 8);

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(base.intersects(superset));
    try testing.expect(!base.intersects(disjoint));
}

test "cpumask starter packet ignores cross-word tail padding while walking missing cpus" {
    const words = [_]usize{
        std.math.maxInt(usize),
        (@as(usize, 1) << 0) |
            (~@as(usize, 0) << 3),
    };
    const capacity = bitmap_view.word_bits + 3;
    const mask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(capacity - 2, mask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), mask.firstCpu());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 1), mask.firstMissingCpu());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits), mask.nextCpu(bitmap_view.word_bits));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 2), mask.nextMissingCpu(bitmap_view.word_bits + 2));
}

test "cpumask starter packet can walk the next routable cpu inside the declared mask" {
    const words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 4) |
            (@as(usize, 1) << 7),
        std.math.maxInt(usize),
    };
    const mask = cpumask_view.CpuMaskView.init(words[0..], 8);

    try testing.expectEqual(@as(?usize, 1), mask.nextCpu(0));
    try testing.expectEqual(@as(?usize, 4), mask.nextCpu(2));
    try testing.expectEqual(@as(?usize, 7), mask.nextCpu(7));
    try testing.expectEqual(@as(?usize, null), mask.nextCpu(8));

    try testing.expectEqual(@as(?usize, 0), mask.nextMissingCpu(0));
    try testing.expectEqual(@as(?usize, 2), mask.nextMissingCpu(2));
    try testing.expectEqual(@as(?usize, 5), mask.nextMissingCpu(5));
    try testing.expectEqual(@as(?usize, null), mask.nextMissingCpu(8));
}
