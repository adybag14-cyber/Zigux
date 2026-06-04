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

test "phase3 bitmap cpumask stride mirror replay keeps mirrored walks aligned" {
    const capacity = 3 * word_bits + 23;
    const stride_words = [_]Word{
        bit(1) | bit(5) | bit(13) | bit(word_bits - 2),
        bit(word_bits + 0) | bit(word_bits + 8) | bit(word_bits + 21) | bit(2 * word_bits - 1),
        bit(2 * word_bits + 3) | bit(2 * word_bits + 16) | bit(3 * word_bits - 4),
        bit(3 * word_bits + 2) | bit(3 * word_bits + 11) | bit(3 * word_bits + 22) | ~tailMask(capacity),
    };

    const bitmap = BitmapView.init(stride_words[0..], capacity);
    const cpumask = CpuMaskView.init(stride_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 14), bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 14), cpumask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 1), cpumask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), cpumask.firstMissingCpu());

    const present = [_]usize{
        1,
        5,
        13,
        word_bits - 2,
        word_bits,
        word_bits + 8,
        word_bits + 21,
        2 * word_bits - 1,
        2 * word_bits + 3,
        2 * word_bits + 16,
        3 * word_bits - 4,
        3 * word_bits + 2,
        3 * word_bits + 11,
        3 * word_bits + 22,
    };
    inline for (present) |cpu| {
        try std.testing.expect(bitmap.isSet(cpu));
        try std.testing.expect(cpumask.hasCpu(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), bitmap.nextSetBit(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), cpumask.nextCpu(cpu));
    }

    try std.testing.expectEqual(@as(?usize, 5), bitmap.nextSetBit(2));
    try std.testing.expectEqual(@as(?usize, word_bits), cpumask.nextCpu(word_bits - 1));
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 3), bitmap.nextSetBit(2 * word_bits));
    try std.testing.expectEqual(@as(?usize, 3 * word_bits + 22), cpumask.nextCpu(3 * word_bits + 12));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextCpu(capacity));
}

test "phase3 bitmap cpumask stride mirror replay bounds peers to active capacity" {
    const capacity = 3 * word_bits + 23;
    const active_words = [_]Word{
        bit(3) | bit(9) | bit(word_bits - 1),
        bit(word_bits + 3) | bit(word_bits + 9) | bit(2 * word_bits - 1),
        bit(2 * word_bits + 3) | bit(2 * word_bits + 9) | bit(3 * word_bits - 1),
        bit(3 * word_bits + 3) | bit(3 * word_bits + 9) | ~tailMask(capacity),
    };
    const mirror_words = [_]Word{
        bit(0) | bit(3) | bit(9) | bit(word_bits - 1),
        bit(word_bits + 1) | bit(word_bits + 3) | bit(word_bits + 9) | bit(2 * word_bits - 1),
        bit(2 * word_bits + 2) | bit(2 * word_bits + 3) | bit(2 * word_bits + 9) | bit(3 * word_bits - 1),
        bit(3 * word_bits + 3) | bit(3 * word_bits + 9) | bit(3 * word_bits + 18) | ~tailMask(capacity),
    };
    const padding_peer_words = [_]Word{
        0,
        0,
        0,
        ~tailMask(capacity),
    };
    const outside_peer_words = [_]Word{
        bit(4),
        bit(word_bits + 4),
        bit(2 * word_bits + 4),
        bit(3 * word_bits + 4) | ~tailMask(capacity),
    };

    const active_bitmap = BitmapView.init(active_words[0..], capacity);
    const active_mask = CpuMaskView.init(active_words[0..], capacity);
    const mirror_bitmap = BitmapView.init(mirror_words[0..], capacity);
    const mirror_mask = CpuMaskView.init(mirror_words[0..], capacity);
    const padding_bitmap = BitmapView.init(padding_peer_words[0..], capacity);
    const padding_mask = CpuMaskView.init(padding_peer_words[0..], capacity);
    const outside_bitmap = BitmapView.init(outside_peer_words[0..], capacity);
    const outside_mask = CpuMaskView.init(outside_peer_words[0..], capacity);

    try std.testing.expect(active_bitmap.isSubsetOf(mirror_bitmap));
    try std.testing.expect(active_mask.isSubsetOf(mirror_mask));
    try std.testing.expect(!mirror_bitmap.isSubsetOf(active_bitmap));
    try std.testing.expect(!mirror_mask.isSubsetOf(active_mask));
    try std.testing.expect(active_bitmap.intersects(mirror_bitmap));
    try std.testing.expect(active_mask.intersects(mirror_mask));

    try std.testing.expectEqual(@as(usize, 0), padding_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 0), padding_mask.countPresentCpus());
    try std.testing.expect(!padding_bitmap.intersects(active_bitmap));
    try std.testing.expect(!padding_mask.intersects(active_mask));
    try std.testing.expect(!outside_bitmap.intersects(active_bitmap));
    try std.testing.expect(!outside_mask.intersects(active_mask));
    try std.testing.expectEqual(@as(?usize, 4), outside_bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 4), outside_mask.firstCpu());
}
