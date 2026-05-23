const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "mixed tail validity keeps sparse tail discovery aligned despite ignored trailing noise" {
    const capacity = (bitmap_view.word_bits * 2) + 10;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(4) | bit(8) | bit(15) | bit(29),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual((bitmap_view.word_bits * 2) + 3, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, (bitmap_view.word_bits * 2) + 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet((bitmap_view.word_bits * 2) + 8));
    try testing.expect(!bitmap.isSet((bitmap_view.word_bits * 2) + 1));
    try testing.expect(cpumask.hasCpu((bitmap_view.word_bits * 2) + 8));
    try testing.expect(!cpumask.hasCpu((bitmap_view.word_bits * 2) + 9));
}

test "mixed tail validity keeps valid subset and overlap semantics ahead of ignored tail extras" {
    const capacity = (bitmap_view.word_bits * 2) + 10;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(4) | bit(8) | bit(14),
    };
    const subset_words = [_]usize{
        0,
        0,
        bit(0) | bit(8) | bit(12),
    };
    const superset_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(0) | bit(3) | bit(4) | bit(8) | bit(16),
    };
    const overlap_words = [_]usize{
        0,
        bit(31),
        bit(4) | bit(13),
    };
    const mismatch_words = [_]usize{
        0,
        0,
        bit(2) | bit(12),
    };
    const tail_noise_words = [_]usize{
        0,
        0,
        bit(10) | bit(11) | bit(21),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const subset = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const overlap = cpumask_view.CpuMaskView.init(overlap_words[0..], capacity);
    const mismatch = cpumask_view.CpuMaskView.init(mismatch_words[0..], capacity);
    const tail_noise = cpumask_view.CpuMaskView.init(tail_noise_words[0..], capacity);
    const tail_noise_bitmap = bitmap_view.BitmapView.init(tail_noise_words[0..], capacity);

    try testing.expect(subset.isSubsetOf(base));
    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(!mismatch.isSubsetOf(base));
    try testing.expect(base.intersects(overlap));
    try testing.expect(overlap.intersects(base));
    try testing.expect(!base.intersects(mismatch));
    try testing.expect(!mismatch.intersects(base));
    try testing.expect(!base.intersects(tail_noise));
    try testing.expect(!tail_noise.intersects(base));
    try testing.expect(tail_noise.isSubsetOf(base));
    try testing.expectEqual(@as(usize, 0), tail_noise_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), tail_noise_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_noise_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), tail_noise.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), tail_noise.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_noise.firstMissingCpu());
}
