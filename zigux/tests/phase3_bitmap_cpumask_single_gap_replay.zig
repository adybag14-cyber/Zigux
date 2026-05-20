const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

test "single bounded gap stays aligned for bitmap and cpumask views" {
    const gap = bitmap_view.word_bits + 2;
    const capacity = bitmap_view.word_bits + 5;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize) & ~(@as(usize, 1) << @intCast(gap - bitmap_view.word_bits)),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(capacity - 1, bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, gap), bitmap.firstClearBit());

    try testing.expectEqual(capacity - 1, cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, gap), cpumask.firstMissingCpu());
    try testing.expect(!cpumask.hasCpu(gap));
    try testing.expect(cpumask.hasCpu(gap - 1));
    try testing.expect(cpumask.hasCpu(gap + 1));
}

test "single bounded gap keeps subset and overlap checks honest" {
    const gap = bitmap_view.word_bits + 1;
    const capacity = bitmap_view.word_bits + 4;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize) & ~(@as(usize, 1) << @intCast(gap - bitmap_view.word_bits)),
    };
    const full_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
    };
    const gap_only_words = [_]usize{
        0,
        (@as(usize, 1) << @intCast(gap - bitmap_view.word_bits)) | ~bitmapTailMask(capacity),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], capacity);
    const gap_only = cpumask_view.CpuMaskView.init(gap_only_words[0..], capacity);

    try testing.expect(base.isSubsetOf(full));
    try testing.expect(!full.isSubsetOf(base));
    try testing.expect(!base.intersects(gap_only));
    try testing.expect(!base.isSubsetOf(gap_only));
    try testing.expectEqual(@as(?usize, gap), gap_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), gap_only.firstMissingCpu());
    try testing.expectEqual(@as(usize, 1), gap_only.countPresentCpus());
}

fn bitmapTailMask(bit_len: usize) usize {
    const remainder = bit_len % bitmap_view.word_bits;
    if (remainder == 0) return std.math.maxInt(usize);
    return (@as(usize, 1) << @intCast(remainder)) - 1;
}
