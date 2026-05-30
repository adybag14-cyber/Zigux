const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn poisonAbove(tail_bits: usize) Word {
    return ~((@as(Word, 1) << @intCast(tail_bits)) - 1);
}

fn expectNextClearParity(bitmap: bitmap_view.BitmapView, cpus: cpumask_view.CpuMaskView, starts: []const usize) !void {
    for (starts) |start| {
        try std.testing.expectEqual(bitmap.nextClearBit(start), cpus.nextMissingCpu(start));
    }
}

test "bitmap and cpumask clear traversal agree across a poisoned tail window" {
    const bit_len = word_bits * 2 + 11;
    const shared_words = [_]Word{
        std.math.maxInt(Word) & ~bit(0) & ~bit(word_bits - 2),
        std.math.maxInt(Word) & ~bit(word_bits) & ~bit(word_bits + 9),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 7) | poisonAbove(11),
    };

    const bitmap = bitmap_view.BitmapView.init(shared_words[0..], bit_len);
    const cpus = cpumask_view.CpuMaskView.init(shared_words[0..], bit_len);

    try std.testing.expectEqual(bitmap.firstClearBit(), cpus.firstMissingCpu());
    try expectNextClearParity(bitmap, cpus, &.{ 0, 1, word_bits - 3, word_bits - 2, word_bits - 1, word_bits, word_bits + 1, word_bits + 9, word_bits * 2, word_bits * 2 + 2, bit_len - 1, bit_len });

    try std.testing.expectEqual(@as(?usize, 0), cpus.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits - 2), cpus.nextMissingCpu(1));
    try std.testing.expectEqual(@as(?usize, word_bits), cpus.nextMissingCpu(word_bits - 1));
    try std.testing.expectEqual(@as(?usize, word_bits + 9), cpus.nextMissingCpu(word_bits + 1));
    try std.testing.expectEqual(@as(?usize, word_bits * 2), cpus.nextMissingCpu(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 2), cpus.nextMissingCpu(word_bits * 2 + 2));
    try std.testing.expectEqual(@as(?usize, bit_len - 1), cpus.nextMissingCpu(bit_len - 1));
    try std.testing.expectEqual(@as(?usize, null), cpus.nextMissingCpu(bit_len));
}

test "bitmap projection preserves cpumask subset and overlap on active words only" {
    const bit_len = word_bits * 2 + 5;
    const base_words = [_]Word{
        bit(1) | bit(word_bits - 1),
        bit(word_bits + 3) | bit(word_bits + 17),
        bit(word_bits * 2 + 4) | poisonAbove(6),
    };
    const superset_words = [_]Word{
        base_words[0] | bit(5),
        base_words[1] | bit(word_bits + 31),
        base_words[2] | bit(word_bits * 2 + 2),
    };
    const disjoint_words = [_]Word{
        bit(2) | bit(6),
        bit(word_bits + 1),
        bit(word_bits * 2 + 3) | poisonAbove(5),
    };

    const base_bitmap = bitmap_view.BitmapView.init(base_words[0..], bit_len);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], bit_len);
    const disjoint_bitmap = bitmap_view.BitmapView.init(disjoint_words[0..], bit_len);

    const base_cpus = cpumask_view.CpuMaskView.init(base_words[0..], bit_len);
    const superset_cpus = cpumask_view.CpuMaskView.init(superset_words[0..], bit_len);
    const disjoint_cpus = cpumask_view.CpuMaskView.init(disjoint_words[0..], bit_len);

    try std.testing.expectEqual(base_bitmap.isSubsetOf(superset_bitmap), base_cpus.isSubsetOf(superset_cpus));
    try std.testing.expectEqual(superset_bitmap.isSubsetOf(base_bitmap), superset_cpus.isSubsetOf(base_cpus));
    try std.testing.expectEqual(base_bitmap.intersects(superset_bitmap), base_cpus.intersects(superset_cpus));
    try std.testing.expectEqual(base_bitmap.intersects(disjoint_bitmap), base_cpus.intersects(disjoint_cpus));

    try std.testing.expect(base_cpus.isSubsetOf(superset_cpus));
    try std.testing.expect(!superset_cpus.isSubsetOf(base_cpus));
    try std.testing.expect(base_cpus.intersects(superset_cpus));
    try std.testing.expect(!base_cpus.intersects(disjoint_cpus));
}

test "empty bitmap projection keeps cpumask missing traversal bounded" {
    const words = [_]Word{ std.math.maxInt(Word), std.math.maxInt(Word) };
    const bitmap = bitmap_view.BitmapView.init(words[0..], 0);
    const cpus = cpumask_view.CpuMaskView.init(words[0..], 0);

    try std.testing.expectEqual(bitmap.firstClearBit(), cpus.firstMissingCpu());
    try std.testing.expectEqual(bitmap.nextClearBit(0), cpus.nextMissingCpu(0));
    try std.testing.expectEqual(@as(?usize, null), cpus.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), cpus.nextMissingCpu(0));
}
