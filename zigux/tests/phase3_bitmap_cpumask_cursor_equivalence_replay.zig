const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(global_bit: usize) usize {
    return @as(usize, 1) << @intCast(global_bit % bitmap_view.word_bits);
}

test "bitmap and cpumask present cursors agree across patterned words" {
    const capacity = bitmap_view.word_bits * 2 + 13;
    const words = [_]usize{
        bit(0) | bit(3) | bit(31),
        bit(bitmap_view.word_bits + 2) | bit(bitmap_view.word_bits * 2 - 1),
        bit(bitmap_view.word_bits * 2) |
            bit(bitmap_view.word_bits * 2 + 5) |
            bit(bitmap_view.word_bits * 2 + 12) |
            (~@as(usize, 0) << 13),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(usize, 8), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());

    const starts = [_]usize{
        0,
        1,
        4,
        bitmap_view.word_bits,
        bitmap_view.word_bits + 3,
        bitmap_view.word_bits * 2 + 6,
        capacity,
    };
    const expected = [_]?usize{
        0,
        3,
        31,
        bitmap_view.word_bits + 2,
        bitmap_view.word_bits * 2 - 1,
        bitmap_view.word_bits * 2 + 12,
        null,
    };

    for (starts, expected) |start, next| {
        try testing.expectEqual(next, bitmap.nextSetBit(start));
        try testing.expectEqual(next, cpumask.nextCpu(start));
    }
}

test "bitmap and cpumask missing cursors agree at capacity boundaries" {
    const capacity = bitmap_view.word_bits * 2 + 13;
    const words = [_]usize{
        bit(0) | bit(3) | bit(31),
        bit(bitmap_view.word_bits + 2) | bit(bitmap_view.word_bits * 2 - 1),
        bit(bitmap_view.word_bits * 2) |
            bit(bitmap_view.word_bits * 2 + 5) |
            bit(bitmap_view.word_bits * 2 + 12) |
            (~@as(usize, 0) << 13),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expectEqual(@as(?usize, 1), cpumask.firstMissingCpu());

    const starts = [_]usize{
        0,
        3,
        bitmap_view.word_bits + 2,
        bitmap_view.word_bits * 2,
        bitmap_view.word_bits * 2 + 5,
        bitmap_view.word_bits * 2 + 12,
        capacity,
    };
    const expected = [_]?usize{
        1,
        4,
        bitmap_view.word_bits + 3,
        bitmap_view.word_bits * 2 + 1,
        bitmap_view.word_bits * 2 + 6,
        null,
        null,
    };

    for (starts, expected) |start, next| {
        try testing.expectEqual(next, bitmap.nextClearBit(start));
        try testing.expectEqual(next, cpumask.nextMissingCpu(start));
    }
}
