const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const word_bits = bitmap_view.word_bits;
const Word = bitmap_view.Word;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

test "sparse bitmap walk ignores poisoned tail padding after nonzero starts" {
    const capacity = word_bits * 2 + 9;
    const words = [_]Word{
        bit(3) | bit(19),
        bit(word_bits + 11) | bit(word_bits + 47),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 8) | (~@as(Word, 0) << 9),
    };
    const view = bitmap_view.BitmapView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 6), view.countSetBits());
    try testing.expectEqual(@as(?usize, 3), view.firstSetBit());
    try testing.expectEqual(@as(?usize, 19), view.nextSetBit(4));
    try testing.expectEqual(@as(?usize, word_bits + 11), view.nextSetBit(20));
    try testing.expectEqual(@as(?usize, word_bits * 2 + 1), view.nextSetBit(word_bits + 48));
    try testing.expectEqual(@as(?usize, word_bits * 2 + 8), view.nextSetBit(word_bits * 2 + 2));
    try testing.expectEqual(@as(?usize, null), view.nextSetBit(word_bits * 2 + 9));

    try testing.expectEqual(@as(?usize, 4), view.nextClearBit(4));
    try testing.expectEqual(@as(?usize, word_bits + 48), view.nextClearBit(word_bits + 48));
    try testing.expectEqual(@as(?usize, word_bits * 2 + 2), view.nextClearBit(word_bits * 2 + 2));
    try testing.expectEqual(@as(?usize, null), view.nextClearBit(capacity));
}

test "sparse cpumask mirrors bitmap walk while tail padding is poisoned" {
    const capacity = word_bits * 2 + 9;
    const words = [_]Word{
        bit(2) | bit(17),
        bit(word_bits + 5) | bit(word_bits + 31),
        bit(word_bits * 2) | bit(word_bits * 2 + 7) | (~@as(Word, 0) << 9),
    };
    const mask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 6), mask.countPresentCpus());
    try testing.expect(mask.hasCpu(word_bits * 2 + 7));
    try testing.expectEqual(@as(?usize, 2), mask.firstCpu());
    try testing.expectEqual(@as(?usize, 17), mask.nextCpu(3));
    try testing.expectEqual(@as(?usize, word_bits + 5), mask.nextCpu(18));
    try testing.expectEqual(@as(?usize, word_bits * 2), mask.nextCpu(word_bits + 32));
    try testing.expectEqual(@as(?usize, null), mask.nextCpu(capacity));

    try testing.expectEqual(@as(?usize, 3), mask.nextMissingCpu(3));
    try testing.expectEqual(@as(?usize, word_bits + 32), mask.nextMissingCpu(word_bits + 32));
    try testing.expectEqual(@as(?usize, word_bits * 2 + 8), mask.nextMissingCpu(word_bits * 2 + 8));
    try testing.expectEqual(@as(?usize, null), mask.nextMissingCpu(capacity));
}

test "sparse cpumask subset and overlap stay bounded to active tail bits" {
    const capacity = word_bits + 6;
    const base_words = [_]Word{
        bit(1) | bit(15),
        bit(word_bits + 1) | bit(word_bits + 5) | (~@as(Word, 0) << 6),
    };
    const superset_words = [_]Word{
        bit(1) | bit(9) | bit(15),
        bit(word_bits + 1) | bit(word_bits + 3) | bit(word_bits + 5),
    };
    const disjoint_words = [_]Word{
        bit(0) | bit(8),
        bit(word_bits + 2) | bit(word_bits + 4) | (~@as(Word, 0) << 6),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(base.intersects(superset));
    try testing.expect(!base.intersects(disjoint));
}
