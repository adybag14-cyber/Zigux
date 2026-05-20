const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

test "tail-window replay keeps the final valid bit aligned while padding bits stay ignored" {
    const words = [_]usize{
        0,
        std.math.maxInt(usize),
    };
    const bit_len = bitmap_view.word_bits + 1;

    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try testing.expect(bitmap.isSet(bitmap_view.word_bits));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits));
    try testing.expectEqual(@as(usize, 1), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}

test "tail-window replay treats invalid-only extra words as empty shared state" {
    const noisy_words = [_]usize{
        0,
        std.math.maxInt(usize),
    };
    const quiet_words = [_]usize{
        0,
        0,
    };
    const bit_len = bitmap_view.word_bits;

    const noisy_bitmap = bitmap_view.BitmapView.init(noisy_words[0..], bit_len);
    const noisy_cpumask = cpumask_view.CpuMaskView.init(noisy_words[0..], bit_len);
    const quiet_cpumask = cpumask_view.CpuMaskView.init(quiet_words[0..], bit_len);

    try testing.expectEqual(@as(usize, 0), noisy_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), noisy_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), noisy_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), noisy_cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), noisy_cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), noisy_cpumask.firstMissingCpu());
    try testing.expect(noisy_cpumask.isSubsetOf(quiet_cpumask));
    try testing.expect(quiet_cpumask.isSubsetOf(noisy_cpumask));
    try testing.expect(!noisy_cpumask.intersects(quiet_cpumask));
}

test "tail-window replay keeps the first clear bit aligned inside a partial last word" {
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize) & ~(@as(usize, 1) << 1),
    };
    const bit_len = bitmap_view.word_bits + 3;

    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try testing.expect(bitmap.isSet(bitmap_view.word_bits));
    try testing.expect(!bitmap.isSet(bitmap_view.word_bits + 1));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 2));
    try testing.expectEqual(@as(usize, bitmap_view.word_bits + 2), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}
