const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "dual window parity keeps bounded counts and first-gap discovery aligned" {
    const capacity = bitmap_view.word_bits + 11;
    const words = [_]usize{
        bit(0) | bit(1) | bit(2) | bit(5) | bit(8),
        bit(1) | bit(2) | bit(5) | bit(6) | bit(9) | bit(13),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expect(bitmap.isSet(0));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 9));
    try testing.expect(!bitmap.isSet(bitmap_view.word_bits + 10));
    try testing.expectEqual(@as(usize, 10), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 3), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 6));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits + 10));
}

test "dual window parity keeps subset and overlap checks bounded under tail-only noise" {
    const capacity = bitmap_view.word_bits + 11;
    const base_words = [_]usize{
        bit(0) | bit(1) | bit(2) | bit(5) | bit(8),
        bit(1) | bit(2) | bit(5) | bit(6) | bit(9),
    };
    const subset_words = [_]usize{
        bit(1) | bit(5),
        bit(2) | bit(6) | bit(13),
    };
    const overlap_words = [_]usize{
        bit(8),
        bit(10),
    };
    const disjoint_words = [_]usize{
        bit(3) | bit(4),
        bit(0) | bit(4),
    };
    const tail_only_words = [_]usize{
        0,
        bit(11) | bit(13),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const subset = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const overlap = cpumask_view.CpuMaskView.init(overlap_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);
    const tail_only = cpumask_view.CpuMaskView.init(tail_only_words[0..], capacity);
    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_words[0..], capacity);

    try testing.expect(subset.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(subset));
    try testing.expect(base.intersects(overlap));
    try testing.expect(overlap.intersects(base));
    try testing.expect(!base.intersects(disjoint));
    try testing.expect(!disjoint.intersects(base));
    try testing.expect(!base.intersects(tail_only));
    try testing.expect(!tail_only.intersects(base));
    try testing.expect(tail_only.isSubsetOf(base));
    try testing.expectEqual(@as(usize, 0), tail_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), tail_only_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), tail_only_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), tail_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), tail_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_only.firstMissingCpu());
}
