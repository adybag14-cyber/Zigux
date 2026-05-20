const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn inactiveTailNoise(bit_len: usize) usize {
    const remainder = bit_len % bitmap_view.word_bits;
    if (remainder == 0) return 0;
    return ~((@as(usize, 1) << @intCast(remainder)) - 1);
}

test "outer-edge replay keeps the first and last valid bits aligned across both views" {
    const bit_len = bitmap_view.word_bits + 6;
    const last_valid_bit = bit_len - 1;
    const words = [_]usize{
        (@as(usize, 1) << 0),
        (@as(usize, 1) << @intCast(last_valid_bit - bitmap_view.word_bits)) | inactiveTailNoise(bit_len),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try testing.expect(bitmap.isSet(0));
    try testing.expect(bitmap.isSet(last_valid_bit));
    try testing.expect(cpumask.hasCpu(0));
    try testing.expect(cpumask.hasCpu(last_valid_bit));

    try testing.expectEqual(@as(usize, 2), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}

test "outer-edge replay keeps a last-bit-only window distinct from an empty bounded range" {
    const bit_len = bitmap_view.word_bits + 6;
    const last_valid_bit = bit_len - 1;
    const words = [_]usize{
        0,
        (@as(usize, 1) << @intCast(last_valid_bit - bitmap_view.word_bits)) | inactiveTailNoise(bit_len),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try testing.expectEqual(@as(usize, 1), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, last_valid_bit), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}

test "outer-edge replay keeps subset and overlap checks blind to tail-only noise" {
    const bit_len = bitmap_view.word_bits + 6;
    const edge_words = [_]usize{
        (@as(usize, 1) << 0),
        (@as(usize, 1) << 5) | inactiveTailNoise(bit_len),
    };
    const superset_words = [_]usize{
        (@as(usize, 1) << 0) | (@as(usize, 1) << 3),
        (@as(usize, 1) << 1) | (@as(usize, 1) << 5) | inactiveTailNoise(bit_len),
    };
    const noise_only_words = [_]usize{
        0,
        inactiveTailNoise(bit_len),
    };

    const edge = cpumask_view.CpuMaskView.init(edge_words[0..], bit_len);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], bit_len);
    const noise_only = cpumask_view.CpuMaskView.init(noise_only_words[0..], bit_len);

    try testing.expect(edge.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(edge));
    try testing.expect(edge.intersects(superset));
    try testing.expect(!edge.intersects(noise_only));
    try testing.expectEqual(@as(usize, 0), noise_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), noise_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), noise_only.firstMissingCpu());
}
