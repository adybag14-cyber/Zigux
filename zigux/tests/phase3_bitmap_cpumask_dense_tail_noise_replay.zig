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

test "phase3 bitmap cpumask dense tail noise replay keeps dense walks aligned" {
    const capacity = 2 * word_bits + 17;
    const missing = [_]usize{
        0,
        2,
        word_bits - 1,
        word_bits + 5,
        word_bits + 6,
        2 * word_bits - 3,
        2 * word_bits,
        2 * word_bits + 16,
    };
    const words = [_]Word{
        std.math.maxInt(Word) ^ bit(missing[0]) ^ bit(missing[1]) ^ bit(missing[2]),
        std.math.maxInt(Word) ^ bit(missing[3]) ^ bit(missing[4]) ^ bit(missing[5]),
        (tailMask(capacity) ^ bit(missing[6]) ^ bit(missing[7])) | ~tailMask(capacity),
    };

    const bitmap = BitmapView.init(words[0..], capacity);
    const cpumask = CpuMaskView.init(words[0..], capacity);

    try std.testing.expectEqual(capacity - missing.len, bitmap.countSetBits());
    try std.testing.expectEqual(capacity - missing.len, cpumask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 1), cpumask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), cpumask.firstMissingCpu());

    inline for (missing) |gap| {
        try std.testing.expect(!bitmap.isSet(gap));
        try std.testing.expect(!cpumask.hasCpu(gap));
        try std.testing.expectEqual(@as(?usize, gap), bitmap.nextClearBit(gap));
        try std.testing.expectEqual(@as(?usize, gap), cpumask.nextMissingCpu(gap));
    }

    try std.testing.expectEqual(@as(?usize, 3), bitmap.nextSetBit(2));
    try std.testing.expectEqual(@as(?usize, word_bits + 7), cpumask.nextCpu(word_bits + 6));
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 1), bitmap.nextSetBit(2 * word_bits));
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextCpu(capacity - 1));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextClearBit(capacity));
}

test "phase3 bitmap cpumask dense tail noise replay masks padding-only peers" {
    const capacity = 2 * word_bits + 17;
    const active_words = [_]Word{
        std.math.maxInt(Word) ^ bit(7),
        std.math.maxInt(Word) ^ bit(word_bits + 11),
        bit(2 * word_bits + 1) | bit(2 * word_bits + 8) | bit(2 * word_bits + 15) | ~tailMask(capacity),
    };
    const superset_words = [_]Word{
        std.math.maxInt(Word),
        std.math.maxInt(Word),
        tailMask(capacity) | ~tailMask(capacity),
    };
    const padding_noise_words = [_]Word{
        0,
        0,
        ~tailMask(capacity),
    };

    const active_bitmap = BitmapView.init(active_words[0..], capacity);
    const active_mask = CpuMaskView.init(active_words[0..], capacity);
    const superset_bitmap = BitmapView.init(superset_words[0..], capacity);
    const superset_mask = CpuMaskView.init(superset_words[0..], capacity);
    const padding_bitmap = BitmapView.init(padding_noise_words[0..], capacity);
    const padding_mask = CpuMaskView.init(padding_noise_words[0..], capacity);

    try std.testing.expect(active_bitmap.isSubsetOf(superset_bitmap));
    try std.testing.expect(active_mask.isSubsetOf(superset_mask));
    try std.testing.expect(!superset_bitmap.isSubsetOf(active_bitmap));
    try std.testing.expect(!superset_mask.isSubsetOf(active_mask));
    try std.testing.expect(active_bitmap.intersects(superset_bitmap));
    try std.testing.expect(active_mask.intersects(superset_mask));

    try std.testing.expectEqual(@as(usize, 0), padding_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 0), padding_mask.countPresentCpus());
    try std.testing.expect(!padding_bitmap.intersects(active_bitmap));
    try std.testing.expect(!padding_mask.intersects(active_mask));
    try std.testing.expect(padding_bitmap.isSubsetOf(superset_bitmap));
    try std.testing.expect(padding_mask.isSubsetOf(superset_mask));
    try std.testing.expectEqual(@as(?usize, null), padding_bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, null), padding_mask.firstCpu());
}
