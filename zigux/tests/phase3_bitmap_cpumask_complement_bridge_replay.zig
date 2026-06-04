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

test "phase3 bitmap cpumask complement bridge keeps active gaps exhaustive" {
    const capacity = 2 * word_bits + 9;
    const primary_words = [_]Word{
        bit(0) | bit(2) | bit(word_bits - 1),
        bit(word_bits + 3) | bit(word_bits + 17),
        bit(2 * word_bits + 1) | bit(2 * word_bits + 8) | ~tailMask(capacity),
    };
    const complement_words = [_]Word{
        ~primary_words[0],
        ~primary_words[1],
        (~primary_words[2] & tailMask(capacity)) | ~tailMask(capacity),
    };

    const primary_bitmap = BitmapView.init(primary_words[0..], capacity);
    const complement_bitmap = BitmapView.init(complement_words[0..], capacity);
    const primary_mask = CpuMaskView.init(primary_words[0..], capacity);
    const complement_mask = CpuMaskView.init(complement_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 7), primary_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 7), primary_mask.countPresentCpus());
    try std.testing.expectEqual(capacity - 7, complement_bitmap.countSetBits());
    try std.testing.expectEqual(capacity - 7, complement_mask.countPresentCpus());

    try std.testing.expect(!primary_bitmap.intersects(complement_bitmap));
    try std.testing.expect(!primary_mask.intersects(complement_mask));
    try std.testing.expectEqual(capacity, primary_bitmap.countSetBits() + complement_bitmap.countSetBits());

    try std.testing.expectEqual(@as(?usize, 0), primary_bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 1), primary_bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits - 1), primary_bitmap.nextSetBit(word_bits - 2));
    try std.testing.expectEqual(@as(?usize, word_bits), primary_bitmap.nextClearBit(word_bits));
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 8), primary_bitmap.nextSetBit(2 * word_bits + 2));
    try std.testing.expectEqual(@as(?usize, null), primary_bitmap.nextSetBit(capacity));

    try std.testing.expect(primary_mask.hasCpu(word_bits + 17));
    try std.testing.expect(!primary_mask.hasCpu(word_bits + 18));
    try std.testing.expectEqual(@as(?usize, word_bits + 3), primary_mask.nextCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits + 4), primary_mask.nextMissingCpu(word_bits + 4));
    try std.testing.expectEqual(@as(?usize, null), primary_mask.nextCpu(capacity));
}

test "phase3 bitmap cpumask complement bridge ignores padding-only peer noise" {
    const capacity = 2 * word_bits + 9;
    const all_active_words = [_]Word{
        std.math.maxInt(Word),
        std.math.maxInt(Word),
        tailMask(capacity) | ~tailMask(capacity),
    };
    const sparse_words = [_]Word{
        bit(7) | bit(word_bits - 3),
        bit(word_bits + 1) | bit(word_bits + 31),
        bit(2 * word_bits + 4) | ~tailMask(capacity),
    };
    const padding_only_words = [_]Word{
        0,
        0,
        ~tailMask(capacity),
    };

    const all_bitmap = BitmapView.init(all_active_words[0..], capacity);
    const sparse_bitmap = BitmapView.init(sparse_words[0..], capacity);
    const padding_bitmap = BitmapView.init(padding_only_words[0..], capacity);
    const all_mask = CpuMaskView.init(all_active_words[0..], capacity);
    const sparse_mask = CpuMaskView.init(sparse_words[0..], capacity);
    const padding_mask = CpuMaskView.init(padding_only_words[0..], capacity);

    try std.testing.expect(sparse_bitmap.isSubsetOf(all_bitmap));
    try std.testing.expect(sparse_mask.isSubsetOf(all_mask));
    try std.testing.expect(!all_bitmap.isSubsetOf(sparse_bitmap));
    try std.testing.expect(!all_mask.isSubsetOf(sparse_mask));

    try std.testing.expectEqual(@as(usize, 0), padding_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 0), padding_mask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, null), padding_bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, null), padding_mask.firstCpu());
    try std.testing.expect(!padding_bitmap.intersects(sparse_bitmap));
    try std.testing.expect(!padding_mask.intersects(sparse_mask));
}
