const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "dual window masked peer keeps bounded counts and missing slots explicit" {
    const capacity = bitmap_view.word_bits + 12;
    const words = [_]usize{
        bit(0) | bit(1) | bit(2) | bit(5) | bit(6),
        bit(1) | bit(2) | bit(6) | bit(7) | bit(10) | bit(11),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 11), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 3), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(6));
    try testing.expect(!cpumask.hasCpu(7));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 7));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits + 8));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 11));
}

test "dual window masked peer ignores out-of-range tail bits while preserving subset and overlap checks" {
    const capacity = bitmap_view.word_bits + 12;
    const base_words = [_]usize{
        bit(0) | bit(1) | bit(2) | bit(5) | bit(6),
        bit(1) | bit(2) | bit(6) | bit(7) | bit(10) | bit(11),
    };
    const masked_subset_words = [_]usize{
        bit(1) | bit(6),
        bit(2) | bit(7) | bit(13) | bit(15),
    };
    const masked_overlap_words = [_]usize{
        bit(5),
        bit(8) | bit(14),
    };
    const gap_probe_words = [_]usize{
        bit(3),
        bit(8) | bit(12) | bit(14),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const masked_subset = cpumask_view.CpuMaskView.init(masked_subset_words[0..], capacity);
    const masked_overlap = cpumask_view.CpuMaskView.init(masked_overlap_words[0..], capacity);
    const gap_probe = cpumask_view.CpuMaskView.init(gap_probe_words[0..], capacity);
    const masked_subset_bitmap = bitmap_view.BitmapView.init(masked_subset_words[0..], capacity);
    const gap_probe_bitmap = bitmap_view.BitmapView.init(gap_probe_words[0..], capacity);

    try testing.expect(masked_subset.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(masked_subset));
    try testing.expect(base.intersects(masked_overlap));
    try testing.expect(masked_overlap.intersects(base));
    try testing.expect(!base.intersects(gap_probe));
    try testing.expect(!gap_probe.intersects(base));
    try testing.expect(!gap_probe.isSubsetOf(base));

    try testing.expectEqual(@as(usize, 4), masked_subset_bitmap.countSetBits());
    try testing.expectEqual(masked_subset_bitmap.countSetBits(), masked_subset.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), masked_subset_bitmap.firstSetBit());
    try testing.expectEqual(masked_subset_bitmap.firstSetBit(), masked_subset.firstCpu());
    try testing.expectEqual(@as(?usize, 0), masked_subset_bitmap.firstClearBit());
    try testing.expectEqual(masked_subset_bitmap.firstClearBit(), masked_subset.firstMissingCpu());
    try testing.expect(masked_subset.hasCpu(bitmap_view.word_bits + 7));
    try testing.expect(!masked_subset.hasCpu(bitmap_view.word_bits + 8));

    try testing.expectEqual(@as(usize, 2), gap_probe_bitmap.countSetBits());
    try testing.expectEqual(gap_probe_bitmap.countSetBits(), gap_probe.countPresentCpus());
    try testing.expectEqual(@as(?usize, 3), gap_probe_bitmap.firstSetBit());
    try testing.expectEqual(gap_probe_bitmap.firstSetBit(), gap_probe.firstCpu());
    try testing.expectEqual(@as(?usize, 0), gap_probe_bitmap.firstClearBit());
    try testing.expectEqual(gap_probe_bitmap.firstClearBit(), gap_probe.firstMissingCpu());
    try testing.expect(gap_probe.hasCpu(3));
    try testing.expect(gap_probe.hasCpu(bitmap_view.word_bits + 8));
    try testing.expect(!gap_probe.hasCpu(bitmap_view.word_bits + 9));
}
