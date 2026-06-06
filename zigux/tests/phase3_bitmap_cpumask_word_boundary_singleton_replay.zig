const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn tailNoise(valid_tail_bits: usize) Word {
    std.debug.assert(valid_tail_bits > 0 and valid_tail_bits < word_bits);
    const valid_mask = (@as(Word, 1) << @intCast(valid_tail_bits)) - 1;
    return ~valid_mask;
}

fn expectBitmapCpuMirror(words: []const Word, bit_len: usize) !void {
    const bitmap = bitmap_view.BitmapView.init(words, bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words, bit_len);

    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    for (0..bit_len + 2) |start| {
        try testing.expectEqual(bitmap.nextSetBit(start), cpumask.nextCpu(start));
        try testing.expectEqual(bitmap.nextClearBit(start), cpumask.nextMissingCpu(start));
    }
}

test "word-boundary singleton bits mirror across bitmap and cpumask cursors" {
    const bit_len = word_bits + 5;
    const words = [_]Word{
        bit(word_bits - 1),
        bit(word_bits) | bit(word_bits + 4) | tailNoise(5),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try expectBitmapCpuMirror(words[0..], bit_len);
    try testing.expectEqual(@as(usize, 3), bitmap.countSetBits());
    try testing.expectEqual(@as(usize, 3), cpumask.countPresentCpus());

    try testing.expect(bitmap.isSet(word_bits - 1));
    try testing.expect(cpumask.hasCpu(word_bits - 1));
    try testing.expect(bitmap.isSet(word_bits));
    try testing.expect(cpumask.hasCpu(word_bits));
    try testing.expect(bitmap.isSet(word_bits + 4));
    try testing.expect(cpumask.hasCpu(word_bits + 4));

    try testing.expectEqual(@as(?usize, word_bits - 1), bitmap.nextSetBit(word_bits - 2));
    try testing.expectEqual(@as(?usize, word_bits), bitmap.nextSetBit(word_bits));
    try testing.expectEqual(@as(?usize, word_bits + 4), bitmap.nextSetBit(word_bits + 1));
    try testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(bit_len));

    try testing.expectEqual(@as(?usize, word_bits + 1), bitmap.nextClearBit(word_bits - 1));
    try testing.expectEqual(@as(?usize, word_bits + 1), cpumask.nextMissingCpu(word_bits - 1));
    try testing.expectEqual(@as(?usize, null), bitmap.nextClearBit(bit_len));
    try testing.expectEqual(@as(?usize, null), cpumask.nextMissingCpu(bit_len));
}

test "word-boundary relation checks ignore noisy padding beyond capacity" {
    const bit_len = word_bits + 5;
    const base_words = [_]Word{
        bit(word_bits - 1),
        bit(word_bits) | bit(word_bits + 4) | tailNoise(5),
    };
    const superset_words = [_]Word{
        bit(2) | bit(word_bits - 1),
        bit(word_bits) | bit(word_bits + 4),
    };
    const disjoint_words = [_]Word{
        bit(1),
        tailNoise(5),
    };

    const base_bitmap = bitmap_view.BitmapView.init(base_words[0..], bit_len);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], bit_len);
    const disjoint_bitmap = bitmap_view.BitmapView.init(disjoint_words[0..], bit_len);
    const base_cpu = cpumask_view.CpuMaskView.init(base_words[0..], bit_len);
    const superset_cpu = cpumask_view.CpuMaskView.init(superset_words[0..], bit_len);
    const disjoint_cpu = cpumask_view.CpuMaskView.init(disjoint_words[0..], bit_len);

    try testing.expect(base_bitmap.isSubsetOf(superset_bitmap));
    try testing.expect(base_cpu.isSubsetOf(superset_cpu));
    try testing.expect(!superset_bitmap.isSubsetOf(base_bitmap));
    try testing.expect(!superset_cpu.isSubsetOf(base_cpu));

    try testing.expect(base_bitmap.intersects(superset_bitmap));
    try testing.expect(base_cpu.intersects(superset_cpu));
    try testing.expect(!base_bitmap.intersects(disjoint_bitmap));
    try testing.expect(!base_cpu.intersects(disjoint_cpu));

    try testing.expectEqual(@as(usize, 1), disjoint_bitmap.countSetBits());
    try testing.expectEqual(@as(usize, 1), disjoint_cpu.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), disjoint_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 1), disjoint_cpu.firstCpu());
}
