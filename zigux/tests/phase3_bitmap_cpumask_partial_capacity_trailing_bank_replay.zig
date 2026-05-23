const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "partial capacity ignores fully extra trailing banks during discovery" {
    const capacity = bitmap_view.word_bits + 6;
    const expected_missing = bitmap_view.word_bits + 4;
    const words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(3) | bit(5) | bit(11),
        std.math.maxInt(usize),
        bit(7) | bit(19),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(capacity - 1, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, expected_missing), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(capacity - 1));
    try testing.expect(!bitmap.isSet(expected_missing));
    try testing.expect(cpumask.hasCpu(capacity - 1));
    try testing.expect(!cpumask.hasCpu(expected_missing));
}

test "partial capacity ignores fully extra trailing banks during subset and overlap" {
    const capacity = bitmap_view.word_bits + 6;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(3) | bit(5) | bit(11),
        std.math.maxInt(usize),
        bit(7),
    };
    const subset_words = [_]usize{
        bit(1) | bit(17),
        bit(0) | bit(3) | bit(9),
        std.math.maxInt(usize),
        bit(1),
    };
    const valid_overlap_words = [_]usize{
        0,
        bit(3) | bit(12),
        bit(0),
        0,
    };
    const trailing_only_words = [_]usize{
        0,
        0,
        std.math.maxInt(usize),
        bit(2),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const subset = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const valid_overlap = cpumask_view.CpuMaskView.init(valid_overlap_words[0..], capacity);
    const trailing_only = cpumask_view.CpuMaskView.init(trailing_only_words[0..], capacity);
    const trailing_only_bitmap = bitmap_view.BitmapView.init(trailing_only_words[0..], capacity);

    try testing.expect(subset.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(subset));
    try testing.expect(base.intersects(valid_overlap));
    try testing.expect(valid_overlap.intersects(base));
    try testing.expect(!base.intersects(trailing_only));
    try testing.expect(!trailing_only.intersects(base));
    try testing.expect(trailing_only.isSubsetOf(base));
    try testing.expectEqual(@as(usize, 0), trailing_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), trailing_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), trailing_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), trailing_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), trailing_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), trailing_only.firstMissingCpu());
}
