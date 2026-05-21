const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn inactiveTailNoise(bit_len: usize) usize {
    const remainder = bit_len % bitmap_view.word_bits;
    if (remainder == 0) return 0;
    return ~((@as(usize, 1) << @intCast(remainder)) - 1);
}

test "center hole keeps the interior clear bit aligned under noisy tail storage" {
    const capacity = bitmap_view.word_bits + 6;
    const hole_bit = bitmap_view.word_bits + 2;
    const words = [_]usize{
        std.math.maxInt(usize),
        ((@as(usize, 1) << 6) - 1) & ~(@as(usize, 1) << 2) | inactiveTailNoise(capacity),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(capacity - 1, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, hole_bit), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(!bitmap.isSet(hole_bit));
    try testing.expect(!cpumask.hasCpu(hole_bit));
    try testing.expect(bitmap.isSet(hole_bit - 1));
    try testing.expect(cpumask.hasCpu(hole_bit - 1));
    try testing.expect(bitmap.isSet(hole_bit + 1));
    try testing.expect(cpumask.hasCpu(hole_bit + 1));
}

test "center hole stays disjoint from a peer that only fills the hole" {
    const capacity = bitmap_view.word_bits + 6;
    const hole_bit = bitmap_view.word_bits + 2;
    const center_hole_words = [_]usize{
        std.math.maxInt(usize),
        ((@as(usize, 1) << 6) - 1) & ~(@as(usize, 1) << 2) | inactiveTailNoise(capacity),
    };
    const hole_only_words = [_]usize{
        0,
        (@as(usize, 1) << 2) | inactiveTailNoise(capacity),
    };

    const center_hole = cpumask_view.CpuMaskView.init(center_hole_words[0..], capacity);
    const hole_only = cpumask_view.CpuMaskView.init(hole_only_words[0..], capacity);

    try testing.expectEqual(@as(usize, capacity - 1), center_hole.countPresentCpus());
    try testing.expectEqual(@as(usize, 1), hole_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, hole_bit), hole_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), hole_only.firstMissingCpu());
    try testing.expect(!center_hole.intersects(hole_only));
    try testing.expect(!hole_only.intersects(center_hole));
    try testing.expect(!center_hole.isSubsetOf(hole_only));
    try testing.expect(!hole_only.isSubsetOf(center_hole));
}

test "center hole and hole-only peer rebuild the full bounded union" {
    const capacity = bitmap_view.word_bits + 6;
    const center_hole_words = [_]usize{
        std.math.maxInt(usize),
        ((@as(usize, 1) << 6) - 1) & ~(@as(usize, 1) << 2) | inactiveTailNoise(capacity),
    };
    const hole_only_words = [_]usize{
        0,
        (@as(usize, 1) << 2) | inactiveTailNoise(capacity),
    };
    const full_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
    };

    const center_hole = cpumask_view.CpuMaskView.init(center_hole_words[0..], capacity);
    const hole_only = cpumask_view.CpuMaskView.init(hole_only_words[0..], capacity);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], capacity);

    try testing.expect(center_hole.isSubsetOf(full));
    try testing.expect(hole_only.isSubsetOf(full));
    try testing.expect(full.intersects(center_hole));
    try testing.expect(full.intersects(hole_only));
    try testing.expectEqual(@as(usize, capacity), full.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), full.firstCpu());
    try testing.expectEqual(@as(?usize, null), full.firstMissingCpu());
}
