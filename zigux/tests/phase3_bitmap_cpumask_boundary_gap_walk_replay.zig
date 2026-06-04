const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn expectSetWalk(view: bitmap_view.BitmapView, expected: []const usize) !void {
    var start: usize = 0;
    for (expected) |expected_bit| {
        try std.testing.expectEqual(@as(?usize, expected_bit), view.nextSetBit(start));
        start = expected_bit + 1;
    }
    try std.testing.expectEqual(@as(?usize, null), view.nextSetBit(start));
}

test "bitmap and cpumask walk alternating boundary gaps with noisy padding" {
    const bit_len = word_bits * 3 + 9;
    const words = [_]Word{
        bit(0) | bit(word_bits - 1),
        bit(word_bits) | bit(word_bits + 2) | bit((word_bits * 2) - 1),
        0,
        bit(word_bits * 3) | bit(word_bits * 3 + 8) | (~@as(Word, 0) << 9),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    const expected_set = [_]usize{
        0,
        word_bits - 1,
        word_bits,
        word_bits + 2,
        word_bits * 2 - 1,
        word_bits * 3,
        word_bits * 3 + 8,
    };
    try std.testing.expectEqual(expected_set.len, bitmap.countSetBits());
    try std.testing.expectEqual(expected_set.len, cpumask.countPresentCpus());
    try expectSetWalk(bitmap, expected_set[0..]);

    for (expected_set) |cpu| {
        try std.testing.expect(cpumask.hasCpu(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), cpumask.nextCpu(cpu));
    }
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextCpu(bit_len));

    try std.testing.expectEqual(@as(?usize, 1), bitmap.nextClearBit(0));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), bitmap.nextClearBit(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits * 2), bitmap.nextClearBit(word_bits * 2 - 1));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 1), bitmap.nextClearBit(word_bits * 3));

    try std.testing.expect(!cpumask.hasCpu(1));
    try std.testing.expect(!cpumask.hasCpu(word_bits + 1));
    try std.testing.expect(!cpumask.hasCpu(word_bits * 2));
    try std.testing.expect(!cpumask.hasCpu(word_bits * 3 + 1));
    try std.testing.expectEqual(@as(?usize, 1), cpumask.nextMissingCpu(0));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), cpumask.nextMissingCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits * 2), cpumask.nextMissingCpu(word_bits * 2 - 1));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 1), cpumask.nextMissingCpu(word_bits * 3));
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextMissingCpu(bit_len));
}

test "boundary gap masks keep subset and overlap decisions inside the active range" {
    const bit_len = word_bits * 2 + 5;
    const base_words = [_]Word{
        bit(1) | bit(word_bits - 1),
        bit(word_bits) | bit(word_bits + 3),
        bit(word_bits * 2 + 4) | (~@as(Word, 0) << 5),
    };
    const superset_words = [_]Word{
        base_words[0] | bit(2),
        base_words[1],
        bit(word_bits * 2) | bit(word_bits * 2 + 4) | (~@as(Word, 0) << 5),
    };
    const padding_only_words = [_]Word{
        bit(4),
        bit(word_bits + 7),
        ~@as(Word, 0) << 5,
    };

    const base_bitmap = bitmap_view.BitmapView.init(base_words[0..], bit_len);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], bit_len);
    const padding_only_bitmap = bitmap_view.BitmapView.init(padding_only_words[0..], bit_len);

    const base_mask = cpumask_view.CpuMaskView.init(base_words[0..], bit_len);
    const superset_mask = cpumask_view.CpuMaskView.init(superset_words[0..], bit_len);
    const padding_only_mask = cpumask_view.CpuMaskView.init(padding_only_words[0..], bit_len);

    try std.testing.expect(base_bitmap.isSubsetOf(superset_bitmap));
    try std.testing.expect(base_mask.isSubsetOf(superset_mask));
    try std.testing.expect(!superset_bitmap.isSubsetOf(base_bitmap));
    try std.testing.expect(!superset_mask.isSubsetOf(base_mask));

    try std.testing.expect(!base_bitmap.intersects(padding_only_bitmap));
    try std.testing.expect(!base_mask.intersects(padding_only_mask));
    try std.testing.expectEqual(@as(?usize, 4), padding_only_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2), padding_only_mask.nextMissingCpu(word_bits * 2));
}
