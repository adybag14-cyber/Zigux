const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

test "minimal-window replay keeps zero-capacity bitmap and cpumask views trivial even with noisy storage" {
    const quiet_words = [_]usize{0};
    const noisy_words = [_]usize{std.math.maxInt(usize)};

    const quiet_bitmap = bitmap_view.BitmapView.init(quiet_words[0..], 0);
    const noisy_bitmap = bitmap_view.BitmapView.init(noisy_words[0..], 0);
    const quiet_cpumask = cpumask_view.CpuMaskView.init(quiet_words[0..], 0);
    const noisy_cpumask = cpumask_view.CpuMaskView.init(noisy_words[0..], 0);

    try testing.expectEqual(@as(usize, 0), quiet_bitmap.countSetBits());
    try testing.expectEqual(quiet_bitmap.countSetBits(), noisy_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), noisy_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, null), noisy_bitmap.firstClearBit());
    try testing.expectEqual(@as(usize, 0), noisy_cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), noisy_cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, null), noisy_cpumask.firstMissingCpu());
    try testing.expect(quiet_cpumask.isSubsetOf(noisy_cpumask));
    try testing.expect(noisy_cpumask.isSubsetOf(quiet_cpumask));
    try testing.expect(!quiet_cpumask.intersects(noisy_cpumask));
}

test "minimal-window replay keeps a single clear active bit aligned while ignoring out-of-range noise" {
    const words = [_]usize{@as(usize, 1) << 1};
    const bit_len = 1;

    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try testing.expectEqual(@as(usize, 0), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(!cpumask.hasCpu(0));
}

test "minimal-window replay keeps one live cpu aligned and rejects overlap from invalid tail bits" {
    const bit_len = 1;
    const base_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 5)};
    const mirror_words = [_]usize{@as(usize, 1) << 0};
    const noisy_disjoint_words = [_]usize{@as(usize, 1) << 5};

    const bitmap = bitmap_view.BitmapView.init(base_words[0..], bit_len);
    const base = cpumask_view.CpuMaskView.init(base_words[0..], bit_len);
    const mirror = cpumask_view.CpuMaskView.init(mirror_words[0..], bit_len);
    const noisy_disjoint = cpumask_view.CpuMaskView.init(noisy_disjoint_words[0..], bit_len);

    try testing.expect(bitmap.isSet(0));
    try testing.expect(base.hasCpu(0));
    try testing.expectEqual(@as(usize, 1), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), base.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), base.firstCpu());
    try testing.expectEqual(@as(?usize, null), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), base.firstMissingCpu());
    try testing.expect(base.isSubsetOf(mirror));
    try testing.expect(mirror.isSubsetOf(base));
    try testing.expect(base.intersects(mirror));
    try testing.expect(!base.intersects(noisy_disjoint));
}
