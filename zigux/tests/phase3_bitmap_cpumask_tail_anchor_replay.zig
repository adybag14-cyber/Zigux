const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn inactiveTailNoise(bit_len: usize) usize {
    const remainder = bit_len % bitmap_view.word_bits;
    if (remainder == 0) return 0;
    return ~((@as(usize, 1) << @intCast(remainder)) - 1);
}

test "tail anchor keeps the last valid bit visible under noisy storage" {
    const capacity = bitmap_view.word_bits + 5;
    const last_valid_bit = capacity - 1;
    const words = [_]usize{
        0,
        (@as(usize, 1) << @intCast(last_valid_bit - bitmap_view.word_bits)) | inactiveTailNoise(capacity),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 1), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, last_valid_bit), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(last_valid_bit));
    try testing.expect(cpumask.hasCpu(last_valid_bit));
    try testing.expect(!bitmap.isSet(last_valid_bit - 1));
    try testing.expect(!cpumask.hasCpu(last_valid_bit - 1));
}

test "tail anchor stays disjoint from a noisy empty peer" {
    const capacity = bitmap_view.word_bits + 5;
    const last_valid_bit = capacity - 1;
    const anchor_words = [_]usize{
        (@as(usize, 1) << 2),
        (@as(usize, 1) << @intCast(last_valid_bit - bitmap_view.word_bits)) | inactiveTailNoise(capacity),
    };
    const empty_noise_words = [_]usize{ 0, inactiveTailNoise(capacity) };

    const anchor = cpumask_view.CpuMaskView.init(anchor_words[0..], capacity);
    const empty_noise = cpumask_view.CpuMaskView.init(empty_noise_words[0..], capacity);

    try testing.expectEqual(@as(usize, 2), anchor.countPresentCpus());
    try testing.expectEqual(@as(usize, 0), empty_noise.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), empty_noise.firstCpu());
    try testing.expectEqual(@as(?usize, 0), empty_noise.firstMissingCpu());
    try testing.expect(!anchor.intersects(empty_noise));
    try testing.expect(!empty_noise.intersects(anchor));
    try testing.expect(empty_noise.isSubsetOf(anchor));
    try testing.expect(!anchor.isSubsetOf(empty_noise));
}

test "tail anchor remains subset-bounded inside a full valid union" {
    const capacity = bitmap_view.word_bits + 5;
    const last_valid_bit = capacity - 1;
    const anchor_words = [_]usize{
        (@as(usize, 1) << 2),
        (@as(usize, 1) << @intCast(last_valid_bit - bitmap_view.word_bits)) | inactiveTailNoise(capacity),
    };
    const full_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
    };

    const anchor = cpumask_view.CpuMaskView.init(anchor_words[0..], capacity);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], capacity);

    try testing.expect(anchor.isSubsetOf(full));
    try testing.expect(full.intersects(anchor));
    try testing.expectEqual(@as(usize, capacity), full.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), full.firstMissingCpu());
    try testing.expectEqual(@as(?usize, 0), full.firstCpu());
}
