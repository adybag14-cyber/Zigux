const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn inactiveTailNoise(bit_len: usize) usize {
    const remainder = bit_len % bitmap_view.word_bits;
    if (remainder == 0) return 0;
    return ~((@as(usize, 1) << @intCast(remainder)) - 1);
}

test "all-clear bounded windows stay distinct from empty sentinels" {
    const capacity = bitmap_view.word_bits + 5;
    const clear_words = [_]usize{
        0,
        inactiveTailNoise(capacity),
    };

    const bitmap = bitmap_view.BitmapView.init(clear_words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(clear_words[0..], capacity);

    const empty_bitmap = bitmap_view.BitmapView.init(&.{}, 0);
    const empty_cpumask = cpumask_view.CpuMaskView.init(&.{}, 0);

    try testing.expectEqual(@as(usize, 0), bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, null), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());

    try testing.expectEqual(@as(usize, 0), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), cpumask.firstMissingCpu());

    try testing.expectEqual(@as(?usize, null), empty_bitmap.firstClearBit());
    try testing.expectEqual(@as(?usize, null), empty_cpumask.firstMissingCpu());
}

test "all-clear bounded windows ignore noisy trailing storage in both views" {
    const capacity = bitmap_view.word_bits + 5;
    const stray_tail = inactiveTailNoise(capacity);
    const clear_words = [_]usize{
        0,
        stray_tail,
    };

    const bitmap = bitmap_view.BitmapView.init(clear_words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(clear_words[0..], capacity);

    try testing.expectEqual(@as(usize, 0), bitmap.countSetBits());
    try testing.expectEqual(@as(usize, 0), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}

test "all-clear cpumasks stay subset-compatible without creating false overlap" {
    const capacity = bitmap_view.word_bits + 5;
    const clear_words = [_]usize{
        0,
        inactiveTailNoise(capacity),
    };
    const populated_words = [_]usize{
        0,
        (@as(usize, 1) << 2) | inactiveTailNoise(capacity),
    };

    const clear = cpumask_view.CpuMaskView.init(clear_words[0..], capacity);
    const populated = cpumask_view.CpuMaskView.init(populated_words[0..], capacity);

    try testing.expect(clear.isSubsetOf(populated));
    try testing.expect(!populated.isSubsetOf(clear));
    try testing.expect(!clear.intersects(populated));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 2), populated.firstCpu());
    try testing.expectEqual(@as(?usize, 0), clear.firstMissingCpu());
}
