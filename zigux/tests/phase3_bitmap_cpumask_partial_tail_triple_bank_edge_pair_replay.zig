const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "triple-bank partial tail edge-pair keeps edge clear-bit discovery aligned" {
    const capacity = (bitmap_view.word_bits * 3) + 7;
    const tail_base = bitmap_view.word_bits * 3;
    const first_missing = tail_base;
    const last_missing = capacity - 1;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(1) | bit(2) | bit(3) | bit(4) | bit(5) | bit(8) | bit(12),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(capacity - 2, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, first_missing), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(!cpumask.hasCpu(first_missing));
    try testing.expect(cpumask.hasCpu(tail_base + 1));
    try testing.expect(cpumask.hasCpu(tail_base + 5));
    try testing.expect(!cpumask.hasCpu(last_missing));
}

test "triple-bank partial tail edge-pair keeps subset and overlap blind to invalid tail noise" {
    const capacity = (bitmap_view.word_bits * 3) + 7;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        bit(1) | bit(2) | bit(4) | bit(5) | bit(10) | bit(14),
    };
    const subset_words = [_]usize{
        bit(3) | bit(17),
        bit(0) | bit(29),
        bit(11) | bit(47),
        bit(1) | bit(4) | bit(12),
    };
    const valid_overlap_words = [_]usize{
        0,
        0,
        0,
        bit(2) | bit(9),
    };
    const edge_gap_words = [_]usize{
        0,
        0,
        0,
        bit(0) | bit(6) | bit(13),
    };
    const tail_only_noise_words = [_]usize{
        0,
        0,
        0,
        bit(7) | bit(11) | bit(18),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const subset = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const valid_overlap = cpumask_view.CpuMaskView.init(valid_overlap_words[0..], capacity);
    const edge_gap = cpumask_view.CpuMaskView.init(edge_gap_words[0..], capacity);
    const tail_only_noise = cpumask_view.CpuMaskView.init(tail_only_noise_words[0..], capacity);
    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_noise_words[0..], capacity);

    try testing.expect(subset.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(subset));
    try testing.expect(base.intersects(valid_overlap));
    try testing.expect(valid_overlap.intersects(base));
    try testing.expect(!base.intersects(edge_gap));
    try testing.expect(!edge_gap.intersects(base));
    try testing.expect(!edge_gap.isSubsetOf(base));
    try testing.expect(!base.intersects(tail_only_noise));
    try testing.expect(!tail_only_noise.intersects(base));
    try testing.expect(tail_only_noise.isSubsetOf(base));
    try testing.expectEqual(@as(usize, 0), tail_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), tail_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), tail_only_noise.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), tail_only_noise.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_only_noise.firstMissingCpu());
}
