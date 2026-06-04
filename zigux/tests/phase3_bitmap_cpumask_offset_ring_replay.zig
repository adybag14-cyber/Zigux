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

test "phase3 bitmap cpumask offset ring replay keeps shifted rings aligned" {
    const capacity = 4 * word_bits + 19;
    const ring_words = [_]Word{
        bit(2) | bit(7) | bit(19) | bit(word_bits - 3),
        bit(word_bits + 3) | bit(word_bits + 8) | bit(word_bits + 20) | bit(2 * word_bits - 2),
        bit(2 * word_bits + 4) | bit(2 * word_bits + 9) | bit(2 * word_bits + 21) | bit(3 * word_bits - 1),
        bit(3 * word_bits + 5) | bit(3 * word_bits + 10) | bit(3 * word_bits + 22) | bit(4 * word_bits - 4),
        bit(4 * word_bits + 6) | bit(4 * word_bits + 11) | bit(4 * word_bits + 18) | ~tailMask(capacity),
    };

    const bitmap = BitmapView.init(ring_words[0..], capacity);
    const cpumask = CpuMaskView.init(ring_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 19), bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 19), cpumask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 2), bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 2), cpumask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), cpumask.firstMissingCpu());

    const present = [_]usize{
        2,
        7,
        19,
        word_bits - 3,
        word_bits + 3,
        word_bits + 8,
        word_bits + 20,
        2 * word_bits - 2,
        2 * word_bits + 4,
        2 * word_bits + 9,
        2 * word_bits + 21,
        3 * word_bits - 1,
        3 * word_bits + 5,
        3 * word_bits + 10,
        3 * word_bits + 22,
        4 * word_bits - 4,
        4 * word_bits + 6,
        4 * word_bits + 11,
        4 * word_bits + 18,
    };
    inline for (present) |cpu| {
        try std.testing.expect(bitmap.isSet(cpu));
        try std.testing.expect(cpumask.hasCpu(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), bitmap.nextSetBit(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), cpumask.nextCpu(cpu));
    }

    try std.testing.expectEqual(@as(?usize, word_bits + 3), bitmap.nextSetBit(word_bits));
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 4), cpumask.nextCpu(2 * word_bits));
    try std.testing.expectEqual(@as(?usize, 3 * word_bits + 5), bitmap.nextSetBit(3 * word_bits));
    try std.testing.expectEqual(@as(?usize, 4 * word_bits + 6), cpumask.nextCpu(4 * word_bits));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextCpu(capacity));
}

test "phase3 bitmap cpumask offset ring replay masks padding-only ring peers" {
    const capacity = 4 * word_bits + 19;
    const base_words = [_]Word{
        bit(1) | bit(9) | bit(17),
        bit(word_bits + 2) | bit(word_bits + 10) | bit(word_bits + 18),
        bit(2 * word_bits + 3) | bit(2 * word_bits + 11) | bit(2 * word_bits + 19),
        bit(3 * word_bits + 4) | bit(3 * word_bits + 12) | bit(3 * word_bits + 20),
        bit(4 * word_bits + 5) | bit(4 * word_bits + 13) | ~tailMask(capacity),
    };
    const superset_words = [_]Word{
        bit(1) | bit(9) | bit(17) | bit(31),
        bit(word_bits + 2) | bit(word_bits + 10) | bit(word_bits + 18) | bit(word_bits + 31),
        bit(2 * word_bits + 3) | bit(2 * word_bits + 11) | bit(2 * word_bits + 19) | bit(2 * word_bits + 31),
        bit(3 * word_bits + 4) | bit(3 * word_bits + 12) | bit(3 * word_bits + 20) | bit(3 * word_bits + 31),
        bit(4 * word_bits + 5) | bit(4 * word_bits + 13) | bit(4 * word_bits + 18) | ~tailMask(capacity),
    };
    const padding_peer_words = [_]Word{
        0,
        0,
        0,
        0,
        ~tailMask(capacity),
    };
    const disjoint_ring_words = [_]Word{
        bit(0) | bit(8) | bit(16),
        bit(word_bits + 1) | bit(word_bits + 9) | bit(word_bits + 17),
        bit(2 * word_bits + 2) | bit(2 * word_bits + 10) | bit(2 * word_bits + 18),
        bit(3 * word_bits + 3) | bit(3 * word_bits + 11) | bit(3 * word_bits + 19),
        bit(4 * word_bits + 4) | bit(4 * word_bits + 12) | ~tailMask(capacity),
    };

    const base_bitmap = BitmapView.init(base_words[0..], capacity);
    const base_mask = CpuMaskView.init(base_words[0..], capacity);
    const superset_bitmap = BitmapView.init(superset_words[0..], capacity);
    const superset_mask = CpuMaskView.init(superset_words[0..], capacity);
    const padding_bitmap = BitmapView.init(padding_peer_words[0..], capacity);
    const padding_mask = CpuMaskView.init(padding_peer_words[0..], capacity);
    const disjoint_bitmap = BitmapView.init(disjoint_ring_words[0..], capacity);
    const disjoint_mask = CpuMaskView.init(disjoint_ring_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 14), base_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 14), base_mask.countPresentCpus());
    try std.testing.expect(base_bitmap.isSubsetOf(superset_bitmap));
    try std.testing.expect(base_mask.isSubsetOf(superset_mask));
    try std.testing.expect(!superset_bitmap.isSubsetOf(base_bitmap));
    try std.testing.expect(!superset_mask.isSubsetOf(base_mask));
    try std.testing.expect(base_bitmap.intersects(superset_bitmap));
    try std.testing.expect(base_mask.intersects(superset_mask));

    try std.testing.expectEqual(@as(usize, 0), padding_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 0), padding_mask.countPresentCpus());
    try std.testing.expect(!padding_bitmap.intersects(base_bitmap));
    try std.testing.expect(!padding_mask.intersects(base_mask));
    try std.testing.expect(!disjoint_bitmap.intersects(base_bitmap));
    try std.testing.expect(!disjoint_mask.intersects(base_mask));
    try std.testing.expectEqual(@as(?usize, 0), disjoint_bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 0), disjoint_mask.firstCpu());
}
