const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "partial tail full-valid range reports no missing cpu and ignores tail noise" {
    const capacity = (bitmap_view.word_bits * 2) + 5;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(3) | bit(4) | bit(8) | bit(14),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);
    const last_valid = capacity - 1;

    try testing.expectEqual(capacity, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, null), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(last_valid));
    try testing.expect(cpumask.hasCpu(last_valid));
}

test "partial tail full-valid masks stay equivalent despite invalid extra bits" {
    const capacity = (bitmap_view.word_bits * 2) + 5;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(3) | bit(4),
    };
    const noisy_equivalent_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(3) | bit(4) | bit(9) | bit(18),
    };
    const valid_overlap_words = [_]usize{
        0,
        bit(11),
        bit(2) | bit(8),
    };
    const invalid_only_words = [_]usize{
        0,
        0,
        bit(6) | bit(12) | bit(17),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const noisy_equivalent = cpumask_view.CpuMaskView.init(noisy_equivalent_words[0..], capacity);
    const valid_overlap = cpumask_view.CpuMaskView.init(valid_overlap_words[0..], capacity);
    const invalid_only = cpumask_view.CpuMaskView.init(invalid_only_words[0..], capacity);
    const invalid_only_bitmap = bitmap_view.BitmapView.init(invalid_only_words[0..], capacity);

    try testing.expect(base.isSubsetOf(noisy_equivalent));
    try testing.expect(noisy_equivalent.isSubsetOf(base));
    try testing.expect(base.intersects(noisy_equivalent));
    try testing.expect(noisy_equivalent.intersects(base));
    try testing.expect(base.intersects(valid_overlap));
    try testing.expect(valid_overlap.intersects(base));
    try testing.expect(!base.intersects(invalid_only));
    try testing.expect(!invalid_only.intersects(base));
    try testing.expect(invalid_only.isSubsetOf(base));
    try testing.expectEqual(@as(usize, 0), invalid_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), invalid_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), invalid_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), invalid_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), invalid_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), invalid_only.firstMissingCpu());
}
