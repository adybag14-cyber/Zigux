const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn partialTailNoise(valid_bits_in_tail: usize) Word {
    return ~((@as(Word, 1) << @intCast(valid_bits_in_tail)) - 1);
}

test "phase3 bitmap and cpumask keep the first missing cpu inside a noisy partial tail" {
    const capacity = word_bits + 5;
    const words = [_]Word{
        std.math.maxInt(Word),
        (@as(Word, 1) << 0) |
            (@as(Word, 1) << 2) |
            (@as(Word, 1) << 4) |
            partialTailNoise(5),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try std.testing.expectEqual(word_bits + 3, bitmap.countSetBits());
    try std.testing.expectEqual(word_bits + 3, cpumask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 0), cpumask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 1), bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits + 1), cpumask.firstMissingCpu());
    try std.testing.expect(bitmap.isSet(word_bits + 4));
    try std.testing.expect(cpumask.hasCpu(word_bits + 4));
    try std.testing.expect(!bitmap.isSet(word_bits + 3));
    try std.testing.expect(!cpumask.hasCpu(word_bits + 3));
}

test "phase3 bitmap and cpumask ignore invalid tail noise for partial-tail partitions" {
    const capacity = word_bits + 5;
    const noise = partialTailNoise(5);

    const left_words = [_]Word{
        0,
        (@as(Word, 1) << 0) |
            (@as(Word, 1) << 4) |
            noise,
    };
    const right_words = [_]Word{
        0,
        (@as(Word, 1) << 1) |
            (@as(Word, 1) << 3) |
            noise,
    };
    const union_words = [_]Word{
        0,
        ((@as(Word, 1) << 5) - 1) |
            noise,
    };

    const left_bitmap = bitmap_view.BitmapView.init(left_words[0..], capacity);
    const right_bitmap = bitmap_view.BitmapView.init(right_words[0..], capacity);
    const union_bitmap = bitmap_view.BitmapView.init(union_words[0..], capacity);

    const left_mask = cpumask_view.CpuMaskView.init(left_words[0..], capacity);
    const right_mask = cpumask_view.CpuMaskView.init(right_words[0..], capacity);
    const union_mask = cpumask_view.CpuMaskView.init(union_words[0..], capacity);

    try std.testing.expectEqual(@as(?usize, word_bits), left_bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits), left_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 1), right_bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits + 1), right_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 0), left_bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), left_mask.firstMissingCpu());

    try std.testing.expectEqual(@as(usize, 2), left_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 2), right_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 5), union_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 2), left_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 2), right_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 5), union_mask.countPresentCpus());

    try std.testing.expect(!left_mask.intersects(right_mask));
    try std.testing.expect(!right_mask.intersects(left_mask));
    try std.testing.expect(left_mask.intersects(union_mask));
    try std.testing.expect(right_mask.intersects(union_mask));
    try std.testing.expect(left_mask.isSubsetOf(union_mask));
    try std.testing.expect(right_mask.isSubsetOf(union_mask));
    try std.testing.expect(!union_mask.isSubsetOf(left_mask));
    try std.testing.expect(!union_mask.isSubsetOf(right_mask));
}
