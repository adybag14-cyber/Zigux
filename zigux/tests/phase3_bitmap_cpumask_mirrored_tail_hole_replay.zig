const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const word_bits = bitmap_view.word_bits;

fn bit(offset: usize) usize {
    return @as(usize, 1) << @intCast(offset);
}

fn invalidTailNoise(valid_tail_bits: usize) usize {
    return std.math.maxInt(usize) & ~((@as(usize, 1) << @intCast(valid_tail_bits)) - 1);
}

test "mirrored tail hole replay keeps bitmap and cpumask aligned across mirrored lanes" {
    const capacity = word_bits * 2 + 7;
    const base_words = [_]usize{
        bit(1) | bit(word_bits - 2),
        bit(2) | bit(word_bits - 3),
        bit(0) | bit(6) | invalidTailNoise(7),
    };
    const superset_words = [_]usize{
        bit(1) | bit(word_bits - 2),
        bit(2) | bit(5) | bit(word_bits - 3),
        bit(0) | bit(3) | bit(6) | invalidTailNoise(7),
    };
    const disjoint_words = [_]usize{
        bit(0) | bit(word_bits - 1),
        bit(4) | bit(word_bits - 5),
        bit(2) | invalidTailNoise(7),
    };

    const bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);

    try testing.expect(bitmap.isSet(1));
    try testing.expect(bitmap.isSet(word_bits - 2));
    try testing.expect(bitmap.isSet(word_bits + 2));
    try testing.expect(bitmap.isSet(word_bits * 2 + 6));
    try testing.expectEqual(@as(usize, 6), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(base.intersects(superset));
    try testing.expect(!base.intersects(disjoint));
}

test "mirrored tail hole replay keeps the first valid tail hole discoverable" {
    const capacity = word_bits + 6;
    const words = [_]usize{
        std.math.maxInt(usize),
        bit(0) | bit(2) | bit(3) | bit(5) | invalidTailNoise(6),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(capacity - 2, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, word_bits + 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}

test "mirrored tail hole replay ignores overlap that exists only in invalid tail storage" {
    const capacity = word_bits * 2 + 3;
    const left_words = [_]usize{
        0,
        bit(1),
        bit(0) | invalidTailNoise(3),
    };
    const noise_only_words = [_]usize{
        0,
        0,
        invalidTailNoise(3),
    };

    const left_bitmap = bitmap_view.BitmapView.init(left_words[0..], capacity);
    const noise_only_bitmap = bitmap_view.BitmapView.init(noise_only_words[0..], capacity);
    const left = cpumask_view.CpuMaskView.init(left_words[0..], capacity);
    const noise_only = cpumask_view.CpuMaskView.init(noise_only_words[0..], capacity);

    try testing.expectEqual(@as(usize, 2), left_bitmap.countSetBits());
    try testing.expectEqual(@as(usize, 0), noise_only_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, word_bits + 1), left_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, null), noise_only_bitmap.firstSetBit());

    try testing.expect(!left.intersects(noise_only));
    try testing.expect(noise_only.isSubsetOf(left));
}
