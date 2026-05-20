const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

test "exact-word replay keeps a whole-word leading gap aligned for bitmap and cpumask views" {
    const words = [_]usize{
        0,
        (@as(usize, 1) << 1) | (@as(usize, 1) << 4),
    };
    const bit_len = bitmap_view.word_bits * 2;

    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try testing.expectEqual(@as(usize, 2), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 1), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 4));
}

test "exact-word replay keeps a full first word and sparse second word aligned without tail masking" {
    const words = [_]usize{
        std.math.maxInt(usize),
        (@as(usize, 1) << 0) | (@as(usize, 1) << 3),
    };
    const bit_len = bitmap_view.word_bits * 2;

    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try testing.expectEqual(@as(usize, bitmap_view.word_bits + 2), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 3));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits + 1));
}

test "exact-word replay ignores noisy storage beyond the declared two-word window" {
    const quiet_words = [_]usize{ 0, 0, 0 };
    const noisy_words = [_]usize{ 0, 0, std.math.maxInt(usize) };
    const bit_len = bitmap_view.word_bits * 2;

    const quiet_bitmap = bitmap_view.BitmapView.init(quiet_words[0..], bit_len);
    const noisy_bitmap = bitmap_view.BitmapView.init(noisy_words[0..], bit_len);
    const quiet_cpumask = cpumask_view.CpuMaskView.init(quiet_words[0..], bit_len);
    const noisy_cpumask = cpumask_view.CpuMaskView.init(noisy_words[0..], bit_len);

    try testing.expectEqual(@as(usize, 0), quiet_bitmap.countSetBits());
    try testing.expectEqual(quiet_bitmap.countSetBits(), noisy_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), noisy_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), noisy_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), noisy_cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), noisy_cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), noisy_cpumask.firstMissingCpu());
    try testing.expect(quiet_cpumask.isSubsetOf(noisy_cpumask));
    try testing.expect(noisy_cpumask.isSubsetOf(quiet_cpumask));
    try testing.expect(!quiet_cpumask.intersects(noisy_cpumask));
}
