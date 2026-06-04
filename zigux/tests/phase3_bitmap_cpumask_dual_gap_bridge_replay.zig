const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn tailMask(bit_len: usize) Word {
    const remainder = bit_len % word_bits;
    if (remainder == 0) return std.math.maxInt(Word);
    return (@as(Word, 1) << @intCast(remainder)) - 1;
}

const capacity = word_bits * 6 + 19;

fn backingWords() [8]Word {
    return .{
        bit(2) | bit(9),
        0,
        bit(0) | bit(17),
        0,
        0,
        bit(5) | bit(31),
        bit(1) | bit(18) | ~tailMask(19),
        std.math.maxInt(Word),
    };
}

fn supersetWords() [8]Word {
    return .{
        bit(2) | bit(9),
        bit(6),
        bit(0) | bit(6) | bit(17),
        0,
        bit(12),
        bit(5) | bit(31),
        bit(1) | bit(7) | bit(18) | ~tailMask(19),
        std.math.maxInt(Word),
    };
}

fn disjointWords() [8]Word {
    return .{
        bit(1) | bit(3),
        bit(11),
        bit(3),
        bit(8),
        bit(12),
        bit(6) | bit(30),
        bit(0) | bit(17) | ~tailMask(19),
        std.math.maxInt(Word),
    };
}

test "bitmap and cpumask bridge two empty gaps before a noisy tail" {
    const words = backingWords();
    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    const expected = [_]usize{
        2,
        9,
        word_bits * 2,
        word_bits * 2 + 17,
        word_bits * 5 + 5,
        word_bits * 5 + 31,
        word_bits * 6 + 1,
        word_bits * 6 + 18,
    };

    try std.testing.expectEqual(expected.len, bitmap.countSetBits());
    try std.testing.expectEqual(expected.len, cpumask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, expected[0]), bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, expected[0]), cpumask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), cpumask.firstMissingCpu());

    for (expected) |set_bit| {
        try std.testing.expect(bitmap.isSet(set_bit));
        try std.testing.expect(cpumask.hasCpu(set_bit));
    }

    try std.testing.expectEqual(@as(?usize, expected[1]), bitmap.nextSetBit(3));
    try std.testing.expectEqual(@as(?usize, expected[1]), cpumask.nextCpu(3));
    try std.testing.expectEqual(@as(?usize, expected[2]), bitmap.nextSetBit(10));
    try std.testing.expectEqual(@as(?usize, expected[2]), cpumask.nextCpu(10));
    try std.testing.expectEqual(@as(?usize, expected[4]), bitmap.nextSetBit(word_bits * 2 + 18));
    try std.testing.expectEqual(@as(?usize, expected[4]), cpumask.nextCpu(word_bits * 2 + 18));
    try std.testing.expectEqual(@as(?usize, expected[6]), bitmap.nextSetBit(word_bits * 5 + 32));
    try std.testing.expectEqual(@as(?usize, expected[6]), cpumask.nextCpu(word_bits * 5 + 32));
    try std.testing.expectEqual(@as(?usize, expected[7]), bitmap.nextSetBit(word_bits * 6 + 2));
    try std.testing.expectEqual(@as(?usize, expected[7]), cpumask.nextCpu(word_bits * 6 + 2));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(word_bits * 6 + 19));
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextCpu(word_bits * 6 + 19));
}

test "bitmap and cpumask keep dual-gap subset and overlap checks aligned" {
    const base_words = backingWords();
    const superset_words = supersetWords();
    const disjoint_words = disjointWords();

    const bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);
    const bitmap_superset = bitmap_view.BitmapView.init(superset_words[0..], capacity);
    const bitmap_disjoint = bitmap_view.BitmapView.init(disjoint_words[0..], capacity);

    const cpumask = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const cpumask_superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const cpumask_disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);

    try std.testing.expect(bitmap.isSubsetOf(bitmap_superset));
    try std.testing.expect(cpumask.isSubsetOf(cpumask_superset));
    try std.testing.expect(!bitmap_superset.isSubsetOf(bitmap));
    try std.testing.expect(!cpumask_superset.isSubsetOf(cpumask));

    try std.testing.expect(bitmap.intersects(bitmap_superset));
    try std.testing.expect(cpumask.intersects(cpumask_superset));
    try std.testing.expect(!bitmap.intersects(bitmap_disjoint));
    try std.testing.expect(!cpumask.intersects(cpumask_disjoint));

    try std.testing.expectEqual(@as(?usize, word_bits), bitmap.nextClearBit(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits), cpumask.nextMissingCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits * 6 + 2), bitmap.nextClearBit(word_bits * 6 + 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 6 + 2), cpumask.nextMissingCpu(word_bits * 6 + 2));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextClearBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextMissingCpu(capacity));
}
