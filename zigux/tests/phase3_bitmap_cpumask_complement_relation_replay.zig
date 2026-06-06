const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(global_bit: usize) usize {
    return @as(usize, 1) << @intCast(global_bit % bitmap_view.word_bits);
}

fn wordMask(capacity: usize, index: usize) usize {
    const active_words = if (capacity == 0) 0 else (capacity + bitmap_view.word_bits - 1) / bitmap_view.word_bits;
    if (index >= active_words) return 0;

    const tail_bits = capacity % bitmap_view.word_bits;
    if (index + 1 < active_words or tail_bits == 0) return std.math.maxInt(usize);
    return (@as(usize, 1) << @intCast(tail_bits)) - 1;
}

fn complementWords(base: []const usize, out: []usize, capacity: usize) void {
    for (base, 0..) |word, index| {
        out[index] = ~word & wordMask(capacity, index);
    }
}

fn expectBitmapCpuMaskMirror(words: []const usize, capacity: usize) !void {
    const bitmap = bitmap_view.BitmapView.init(words, capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words, capacity);

    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    const starts = [_]usize{
        0,
        1,
        bitmap_view.word_bits - 1,
        bitmap_view.word_bits,
        bitmap_view.word_bits + 6,
        bitmap_view.word_bits * 2 + 1,
        capacity - 1,
        capacity,
    };

    for (starts) |start| {
        try testing.expectEqual(bitmap.nextSetBit(start), cpumask.nextCpu(start));
        try testing.expectEqual(bitmap.nextClearBit(start), cpumask.nextMissingCpu(start));
    }
}

fn expectComplementRelation(base_words: []const usize, complement_words: []const usize, capacity: usize) !void {
    const base_bitmap = bitmap_view.BitmapView.init(base_words, capacity);
    const complement_bitmap = bitmap_view.BitmapView.init(complement_words, capacity);
    const base_cpumask = cpumask_view.CpuMaskView.init(base_words, capacity);
    const complement_cpumask = cpumask_view.CpuMaskView.init(complement_words, capacity);

    try testing.expectEqual(base_bitmap.countSetBits(), base_cpumask.countPresentCpus());
    try testing.expectEqual(complement_bitmap.countSetBits(), complement_cpumask.countPresentCpus());
    try testing.expectEqual(capacity, base_bitmap.countSetBits() + complement_bitmap.countSetBits());
    try testing.expectEqual(capacity, base_cpumask.countPresentCpus() + complement_cpumask.countPresentCpus());

    try testing.expect(!base_bitmap.intersects(complement_bitmap));
    try testing.expect(!base_cpumask.intersects(complement_cpumask));
    try testing.expect(!base_bitmap.isSubsetOf(complement_bitmap));
    try testing.expect(!base_cpumask.isSubsetOf(complement_cpumask));

    const starts = [_]usize{
        0,
        2,
        bitmap_view.word_bits - 2,
        bitmap_view.word_bits,
        bitmap_view.word_bits + 9,
        bitmap_view.word_bits * 2,
        capacity - 1,
        capacity,
    };

    for (starts) |start| {
        try testing.expectEqual(base_bitmap.nextSetBit(start), complement_cpumask.nextMissingCpu(start));
        try testing.expectEqual(base_cpumask.nextCpu(start), complement_bitmap.nextClearBit(start));
        try testing.expectEqual(base_bitmap.nextClearBit(start), complement_cpumask.nextCpu(start));
        try testing.expectEqual(base_cpumask.nextMissingCpu(start), complement_bitmap.nextSetBit(start));
    }
}

test "bitmap and cpumask preserve complement cursor mirrors" {
    const capacity = bitmap_view.word_bits * 2 + 13;
    const base_words = [_]usize{
        bit(0) | bit(3) | bit(bitmap_view.word_bits - 1),
        bit(bitmap_view.word_bits + 2) |
            bit(bitmap_view.word_bits + 8) |
            bit(bitmap_view.word_bits + 31),
        bit(bitmap_view.word_bits * 2 + 0) |
            bit(bitmap_view.word_bits * 2 + 7) |
            bit(bitmap_view.word_bits * 2 + 12) |
            (~@as(usize, 0) << 13),
    };
    var complement_words: [base_words.len]usize = undefined;
    complementWords(base_words[0..], complement_words[0..], capacity);

    try expectBitmapCpuMaskMirror(base_words[0..], capacity);
    try expectBitmapCpuMaskMirror(complement_words[0..], capacity);
    try expectComplementRelation(base_words[0..], complement_words[0..], capacity);

    const base_bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);
    const complement_cpumask = cpumask_view.CpuMaskView.init(complement_words[0..], capacity);
    try testing.expectEqual(@as(usize, 9), base_bitmap.countSetBits());
    try testing.expectEqual(capacity - 9, complement_cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), base_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 1), complement_cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 2), base_bitmap.nextSetBit(bitmap_view.word_bits));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 3), complement_cpumask.nextCpu(bitmap_view.word_bits + 3));
}

test "bitmap and cpumask keep complement relations tail-bounded after mutation" {
    const capacity = bitmap_view.word_bits + 10;
    var base_words = [_]usize{
        bit(2) | bit(5) | bit(bitmap_view.word_bits - 3),
        bit(bitmap_view.word_bits + 1) |
            bit(bitmap_view.word_bits + 4) |
            bit(bitmap_view.word_bits + 9) |
            (~@as(usize, 0) << 10),
    };
    var complement_words: [base_words.len]usize = undefined;

    complementWords(base_words[0..], complement_words[0..], capacity);
    try expectComplementRelation(base_words[0..], complement_words[0..], capacity);

    base_words[0] |= bit(0);
    base_words[0] &= ~bit(5);
    base_words[1] |= bit(bitmap_view.word_bits + 7);
    base_words[1] &= ~bit(bitmap_view.word_bits + 1);
    base_words[1] |= bit(capacity + 4);
    complementWords(base_words[0..], complement_words[0..], capacity);

    try expectBitmapCpuMaskMirror(base_words[0..], capacity);
    try expectBitmapCpuMaskMirror(complement_words[0..], capacity);
    try expectComplementRelation(base_words[0..], complement_words[0..], capacity);

    const base_cpumask = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const complement_bitmap = bitmap_view.BitmapView.init(complement_words[0..], capacity);
    try testing.expectEqual(@as(usize, 6), base_cpumask.countPresentCpus());
    try testing.expectEqual(capacity - 6, complement_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, 0), base_cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 1), complement_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, null), base_cpumask.nextCpu(capacity));
    try testing.expectEqual(@as(?usize, null), complement_bitmap.nextSetBit(capacity));
}
