const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "partial tail empty-valid range keeps discovery aligned" {
    const capacity = bitmap_view.word_bits + 5;
    const words = [_]usize{
        0,
        bit(5) | bit(9) | bit(17),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 0), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(!cpumask.hasCpu(0));
    try testing.expect(!cpumask.hasCpu(capacity - 1));
}

test "partial tail empty-valid range keeps subset and overlap blind to tail noise" {
    const capacity = bitmap_view.word_bits + 5;
    const empty_valid_words = [_]usize{
        0,
        bit(5) | bit(11) | bit(20),
    };
    const full_valid_words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(1) | bit(2) | bit(3) | bit(4) | bit(9) | bit(17),
    };
    const valid_overlap_words = [_]usize{
        bit(7),
        0,
    };
    const tail_only_noise_words = [_]usize{
        0,
        bit(6) | bit(8) | bit(18),
    };

    const empty_valid = cpumask_view.CpuMaskView.init(empty_valid_words[0..], capacity);
    const full_valid = cpumask_view.CpuMaskView.init(full_valid_words[0..], capacity);
    const valid_overlap = cpumask_view.CpuMaskView.init(valid_overlap_words[0..], capacity);
    const tail_only_noise = cpumask_view.CpuMaskView.init(tail_only_noise_words[0..], capacity);

    try testing.expect(empty_valid.isSubsetOf(full_valid));
    try testing.expect(tail_only_noise.isSubsetOf(full_valid));
    try testing.expect(!full_valid.isSubsetOf(empty_valid));
    try testing.expect(!empty_valid.intersects(full_valid));
    try testing.expect(!full_valid.intersects(empty_valid));
    try testing.expect(full_valid.intersects(valid_overlap));
    try testing.expect(valid_overlap.intersects(full_valid));
    try testing.expect(!empty_valid.intersects(tail_only_noise));
    try testing.expect(!tail_only_noise.intersects(empty_valid));
}
