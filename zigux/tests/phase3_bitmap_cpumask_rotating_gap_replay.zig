const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn tailMask(bit_len: usize) Word {
    const remainder = bit_len % word_bits;
    if (remainder == 0) return std.math.maxInt(Word);
    return (@as(Word, 1) << @intCast(remainder)) - 1;
}

test "phase3 bitmap cpumask rotating gap replay keeps walks aligned" {
    const capacity = 3 * word_bits + 11;
    const missing = [_]usize{
        0,
        7,
        31,
        word_bits + 2,
        word_bits + 33,
        2 * word_bits + 5,
        2 * word_bits + 61,
        3 * word_bits + 3,
        3 * word_bits + 10,
    };
    const words = [_]Word{
        std.math.maxInt(Word) ^ bit(missing[0]) ^ bit(missing[1]) ^ bit(missing[2]),
        std.math.maxInt(Word) ^ bit(missing[3]) ^ bit(missing[4]),
        std.math.maxInt(Word) ^ bit(missing[5]) ^ bit(missing[6]),
        (tailMask(capacity) ^ bit(missing[7]) ^ bit(missing[8])) | ~tailMask(capacity),
    };

    const bitmap = BitmapView.init(words[0..], capacity);
    const cpumask = CpuMaskView.init(words[0..], capacity);

    try std.testing.expectEqual(capacity - missing.len, bitmap.countSetBits());
    try std.testing.expectEqual(capacity - missing.len, cpumask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 1), cpumask.firstCpu());
    try std.testing.expectEqual(@as(?usize, missing[0]), bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, missing[0]), cpumask.firstMissingCpu());

    inline for (missing) |gap| {
        try std.testing.expect(!bitmap.isSet(gap));
        try std.testing.expect(!cpumask.hasCpu(gap));
        try std.testing.expectEqual(@as(?usize, gap), bitmap.nextClearBit(gap));
        try std.testing.expectEqual(@as(?usize, gap), cpumask.nextMissingCpu(gap));
    }

    try std.testing.expectEqual(@as(?usize, 8), bitmap.nextSetBit(7));
    try std.testing.expectEqual(@as(?usize, word_bits + 34), cpumask.nextCpu(word_bits + 33));
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 62), bitmap.nextSetBit(2 * word_bits + 61));
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextCpu(capacity));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextClearBit(capacity));
}

test "phase3 bitmap cpumask rotating gap replay ignores rotated padding noise" {
    const capacity = 3 * word_bits + 11;
    const full_words = [_]Word{
        std.math.maxInt(Word),
        std.math.maxInt(Word),
        std.math.maxInt(Word),
        tailMask(capacity) | ~tailMask(capacity),
    };
    const rotated_words = [_]Word{
        bit(3) | bit(19) | bit(word_bits - 2),
        bit(word_bits + 4) | bit(word_bits + 41),
        bit(2 * word_bits + 8) | bit(2 * word_bits + 29) | bit(2 * word_bits + 47),
        bit(3 * word_bits + 1) | bit(3 * word_bits + 9) | ~tailMask(capacity),
    };
    const padding_noise_words = [_]Word{
        0,
        0,
        0,
        ~tailMask(capacity),
    };

    const full_bitmap = BitmapView.init(full_words[0..], capacity);
    const full_mask = CpuMaskView.init(full_words[0..], capacity);
    const rotated_bitmap = BitmapView.init(rotated_words[0..], capacity);
    const rotated_mask = CpuMaskView.init(rotated_words[0..], capacity);
    const padding_bitmap = BitmapView.init(padding_noise_words[0..], capacity);
    const padding_mask = CpuMaskView.init(padding_noise_words[0..], capacity);

    try std.testing.expect(rotated_bitmap.isSubsetOf(full_bitmap));
    try std.testing.expect(rotated_mask.isSubsetOf(full_mask));
    try std.testing.expect(!full_bitmap.isSubsetOf(rotated_bitmap));
    try std.testing.expect(!full_mask.isSubsetOf(rotated_mask));
    try std.testing.expect(full_bitmap.intersects(rotated_bitmap));
    try std.testing.expect(full_mask.intersects(rotated_mask));

    try std.testing.expectEqual(@as(usize, 0), padding_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 0), padding_mask.countPresentCpus());
    try std.testing.expect(!padding_bitmap.intersects(rotated_bitmap));
    try std.testing.expect(!padding_mask.intersects(rotated_mask));
    try std.testing.expectEqual(@as(?usize, null), padding_bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, null), padding_mask.firstCpu());
}
