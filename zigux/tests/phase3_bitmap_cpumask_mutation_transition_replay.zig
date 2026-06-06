const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(global_bit: usize) usize {
    return @as(usize, 1) << @intCast(global_bit % bitmap_view.word_bits);
}

fn clearBit(words: []usize, global_bit: usize) void {
    words[global_bit / bitmap_view.word_bits] &= ~bit(global_bit);
}

fn setBit(words: []usize, global_bit: usize) void {
    words[global_bit / bitmap_view.word_bits] |= bit(global_bit);
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
        bitmap_view.word_bits + 11,
        bitmap_view.word_bits * 2 + 1,
        capacity - 1,
        capacity,
    };

    for (starts) |start| {
        try testing.expectEqual(bitmap.nextSetBit(start), cpumask.nextCpu(start));
        try testing.expectEqual(bitmap.nextClearBit(start), cpumask.nextMissingCpu(start));
    }
}

test "bitmap and cpumask mirror shared backing clear and set transitions" {
    const capacity = bitmap_view.word_bits * 2 + 9;
    var words = [_]usize{
        bit(0) | bit(2) | bit(bitmap_view.word_bits - 1),
        bit(bitmap_view.word_bits) |
            bit(bitmap_view.word_bits + 7) |
            bit(bitmap_view.word_bits + 12),
        bit(bitmap_view.word_bits * 2 + 1) |
            bit(bitmap_view.word_bits * 2 + 8) |
            (~@as(usize, 0) << 9),
    };

    try expectBitmapCpuMaskMirror(words[0..], capacity);

    const initial_bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const initial_cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);
    try testing.expectEqual(@as(usize, 8), initial_cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), initial_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 1), initial_cpumask.firstMissingCpu());
    try testing.expect(initial_cpumask.hasCpu(bitmap_view.word_bits + 7));

    clearBit(words[0..], 0);
    clearBit(words[0..], bitmap_view.word_bits + 7);
    setBit(words[0..], 1);
    setBit(words[0..], bitmap_view.word_bits + 11);
    setBit(words[0..], capacity + 3);

    try expectBitmapCpuMaskMirror(words[0..], capacity);

    const mutated_bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const mutated_cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);
    try testing.expectEqual(@as(usize, 8), mutated_cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), mutated_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), mutated_cpumask.firstMissingCpu());
    try testing.expect(!mutated_cpumask.hasCpu(bitmap_view.word_bits + 7));
    try testing.expect(mutated_cpumask.hasCpu(bitmap_view.word_bits + 11));
    try testing.expectEqual(@as(?usize, null), mutated_bitmap.nextSetBit(capacity));
    try testing.expectEqual(@as(?usize, null), mutated_cpumask.nextCpu(capacity));

    clearBit(words[0..], bitmap_view.word_bits * 2 + 8);
    setBit(words[0..], bitmap_view.word_bits * 2 + 2);

    try expectBitmapCpuMaskMirror(words[0..], capacity);

    const final_bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const final_cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);
    try testing.expectEqual(@as(usize, 8), final_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits * 2 + 2), final_cpumask.nextCpu(bitmap_view.word_bits * 2 + 2));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits * 2 + 3), final_bitmap.nextClearBit(bitmap_view.word_bits * 2 + 3));
}

test "bitmap and cpumask mutation transitions keep relation checks tail-bounded" {
    const capacity = bitmap_view.word_bits + 6;
    var base_words = [_]usize{
        bit(1) | bit(5),
        bit(bitmap_view.word_bits + 1) |
            bit(bitmap_view.word_bits + 5) |
            (~@as(usize, 0) << 6),
    };
    var superset_words = base_words;
    var disjoint_words = [_]usize{
        bit(0) | bit(2),
        bit(bitmap_view.word_bits + 2) |
            bit(bitmap_view.word_bits + 4) |
            (~@as(usize, 0) << 6),
    };

    var base_bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);
    var base_cpumask = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    var superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], capacity);
    var superset_cpumask = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    var disjoint_bitmap = bitmap_view.BitmapView.init(disjoint_words[0..], capacity);
    var disjoint_cpumask = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);

    try testing.expect(base_bitmap.isSubsetOf(superset_bitmap));
    try testing.expect(base_cpumask.isSubsetOf(superset_cpumask));
    try testing.expect(!base_bitmap.intersects(disjoint_bitmap));
    try testing.expect(!base_cpumask.intersects(disjoint_cpumask));

    setBit(superset_words[0..], 0);
    setBit(superset_words[0..], bitmap_view.word_bits + 4);
    clearBit(disjoint_words[0..], bitmap_view.word_bits + 2);
    setBit(disjoint_words[0..], bitmap_view.word_bits + 1);
    setBit(disjoint_words[0..], capacity + 4);

    base_bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);
    base_cpumask = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], capacity);
    superset_cpumask = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    disjoint_bitmap = bitmap_view.BitmapView.init(disjoint_words[0..], capacity);
    disjoint_cpumask = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);

    try testing.expect(base_bitmap.isSubsetOf(superset_bitmap));
    try testing.expect(base_cpumask.isSubsetOf(superset_cpumask));
    try testing.expect(base_bitmap.intersects(disjoint_bitmap));
    try testing.expect(base_cpumask.intersects(disjoint_cpumask));
    try testing.expectEqual(base_bitmap.countSetBits(), base_cpumask.countPresentCpus());
    try testing.expectEqual(disjoint_bitmap.countSetBits(), disjoint_cpumask.countPresentCpus());
    try testing.expectEqual(@as(usize, 4), base_cpumask.countPresentCpus());
    try testing.expectEqual(@as(usize, 4), disjoint_cpumask.countPresentCpus());
}
