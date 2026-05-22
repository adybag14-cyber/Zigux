const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn partialTailNoise(valid_bits_in_tail: usize) Word {
    return ~((@as(Word, 1) << @intCast(valid_bits_in_tail)) - 1);
}

test "phase3 bitmap and cpumask keep keystone ladder discovery aligned across stepped words" {
    const capacity = (2 * word_bits) + 6;
    const words = [_]Word{
        (@as(Word, 1) << 1) |
            (@as(Word, 1) << 5),
        (@as(Word, 1) << 0) |
            (@as(Word, 1) << 6),
        (@as(Word, 1) << 1) |
            (@as(Word, 1) << 5) |
            partialTailNoise(6),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 6), bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 6), cpumask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 1), cpumask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), cpumask.firstMissingCpu());
    try std.testing.expect(bitmap.isSet((2 * word_bits) + 5));
    try std.testing.expect(cpumask.hasCpu((2 * word_bits) + 5));
    try std.testing.expect(!bitmap.isSet((2 * word_bits) + 4));
    try std.testing.expect(!cpumask.hasCpu((2 * word_bits) + 4));
}

test "phase3 bitmap and cpumask keep shared keystone overlap without subset collapse" {
    const capacity = (2 * word_bits) + 6;
    const noise = partialTailNoise(6);

    const left_words = [_]Word{
        (@as(Word, 1) << 1) |
            (@as(Word, 1) << 5),
        (@as(Word, 1) << 2) |
            (@as(Word, 1) << 6),
        (@as(Word, 1) << 1) |
            noise,
    };
    const right_words = [_]Word{
        (@as(Word, 1) << 5),
        (@as(Word, 1) << 6) |
            (@as(Word, 1) << 9),
        (@as(Word, 1) << 4) |
            noise,
    };
    const union_words = [_]Word{
        (@as(Word, 1) << 1) |
            (@as(Word, 1) << 5),
        (@as(Word, 1) << 2) |
            (@as(Word, 1) << 6) |
            (@as(Word, 1) << 9),
        (@as(Word, 1) << 1) |
            (@as(Word, 1) << 4) |
            noise,
    };

    const left_bitmap = bitmap_view.BitmapView.init(left_words[0..], capacity);
    const right_bitmap = bitmap_view.BitmapView.init(right_words[0..], capacity);
    const union_bitmap = bitmap_view.BitmapView.init(union_words[0..], capacity);

    const left_mask = cpumask_view.CpuMaskView.init(left_words[0..], capacity);
    const right_mask = cpumask_view.CpuMaskView.init(right_words[0..], capacity);
    const union_mask = cpumask_view.CpuMaskView.init(union_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 5), left_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 4), right_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 7), union_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 5), left_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 4), right_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 7), union_mask.countPresentCpus());

    try std.testing.expect(left_mask.intersects(right_mask));
    try std.testing.expect(right_mask.intersects(left_mask));
    try std.testing.expect(left_mask.intersects(union_mask));
    try std.testing.expect(right_mask.intersects(union_mask));
    try std.testing.expect(left_mask.isSubsetOf(union_mask));
    try std.testing.expect(right_mask.isSubsetOf(union_mask));
    try std.testing.expect(!left_mask.isSubsetOf(right_mask));
    try std.testing.expect(!right_mask.isSubsetOf(left_mask));
}

test "phase3 bitmap and cpumask keep tail-only noise from inventing ladder peers" {
    const capacity = (2 * word_bits) + 6;
    const noise = partialTailNoise(6);

    const tail_only_words = [_]Word{
        0,
        0,
        noise,
    };
    const inner_words = [_]Word{
        0,
        (@as(Word, 1) << 6),
        (@as(Word, 1) << 4) |
            noise,
    };

    const tail_only_bitmap = bitmap_view.BitmapView.init(tail_only_words[0..], capacity);
    const tail_only_mask = cpumask_view.CpuMaskView.init(tail_only_words[0..], capacity);
    const inner_mask = cpumask_view.CpuMaskView.init(inner_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 0), tail_only_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 0), tail_only_mask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, null), tail_only_bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, null), tail_only_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 0), tail_only_bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), tail_only_mask.firstMissingCpu());

    try std.testing.expect(!tail_only_mask.intersects(inner_mask));
    try std.testing.expect(!inner_mask.intersects(tail_only_mask));
    try std.testing.expect(tail_only_mask.isSubsetOf(inner_mask));
    try std.testing.expect(!inner_mask.isSubsetOf(tail_only_mask));
}
