const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const bit = bitMask;

fn bitMask(index: usize) Word {
    return @as(Word, 1) << @as(std.math.Log2Int(Word), @intCast(index % word_bits));
}

test "bitmap cpumask perimeter notches stay bounded to declared cpus" {
    const capacity = word_bits * 3 + 13;
    const tail_noise = ~@as(Word, 0) << @as(std.math.Log2Int(Word), @intCast(13));

    const perimeter_words = [_]Word{
        bit(0) | bit(1) | bit(word_bits - 2) | bit(word_bits - 1),
        bit(word_bits) | bit(word_bits + 1) | bit(word_bits + 17),
        bit(word_bits * 2) | bit(word_bits * 2 + 12) | bit(word_bits * 2 + 31),
        bit(word_bits * 3 + 2) | bit(word_bits * 3 + 12) | tail_noise,
    };
    const notched_words = [_]Word{
        bit(0) | bit(word_bits - 1),
        bit(word_bits + 1),
        bit(word_bits * 2 + 12),
        bit(word_bits * 3 + 2) | tail_noise,
    };
    const notch_only_words = [_]Word{
        bit(1) | bit(word_bits - 2),
        bit(word_bits) | bit(word_bits + 17),
        bit(word_bits * 2) | bit(word_bits * 2 + 31),
        bit(word_bits * 3 + 12) | tail_noise,
    };

    const perimeter_bitmap = bitmap_view.BitmapView.init(perimeter_words[0..], capacity);
    const perimeter_mask = cpumask_view.CpuMaskView.init(perimeter_words[0..], capacity);
    const notched_bitmap = bitmap_view.BitmapView.init(notched_words[0..], capacity);
    const notched_mask = cpumask_view.CpuMaskView.init(notched_words[0..], capacity);
    const notch_only_bitmap = bitmap_view.BitmapView.init(notch_only_words[0..], capacity);
    const notch_only_mask = cpumask_view.CpuMaskView.init(notch_only_words[0..], capacity);

    try testing.expectEqual(perimeter_bitmap.countSetBits(), perimeter_mask.countPresentCpus());
    try testing.expectEqual(@as(usize, 12), perimeter_mask.countPresentCpus());
    try testing.expectEqual(@as(usize, 5), notched_mask.countPresentCpus());
    try testing.expectEqual(@as(usize, 7), notch_only_mask.countPresentCpus());

    try testing.expect(notched_bitmap.isSubsetOf(perimeter_bitmap));
    try testing.expect(notched_mask.isSubsetOf(perimeter_mask));
    try testing.expect(notch_only_bitmap.isSubsetOf(perimeter_bitmap));
    try testing.expect(notch_only_mask.isSubsetOf(perimeter_mask));
    try testing.expect(!notched_bitmap.intersects(notch_only_bitmap));
    try testing.expect(!notched_mask.intersects(notch_only_mask));
    try testing.expect(perimeter_bitmap.intersects(notch_only_bitmap));
    try testing.expect(perimeter_mask.intersects(notched_mask));

    try testing.expectEqual(@as(?usize, 0), perimeter_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), perimeter_mask.firstCpu());
    try testing.expectEqual(@as(?usize, 2), perimeter_bitmap.firstClearBit());
    try testing.expectEqual(@as(?usize, 2), perimeter_mask.firstMissingCpu());
    try testing.expectEqual(@as(?usize, word_bits - 1), notched_mask.nextCpu(2));
    try testing.expectEqual(@as(?usize, word_bits - 2), notch_only_bitmap.nextSetBit(2));
    try testing.expectEqual(@as(?usize, word_bits * 3 + 12), notch_only_mask.nextCpu(word_bits * 3));
    try testing.expect(!perimeter_mask.hasCpu(capacity - 2));
}

test "bitmap cpumask perimeter notch refill closes edge gaps symmetrically" {
    const capacity = word_bits * 2 + 9;
    const low_left = 3;
    const low_right = word_bits - 4;
    const mid_left = word_bits + 5;
    const mid_right = word_bits * 2 - 6;
    const tail_left = word_bits * 2 + 1;
    const tail_right = word_bits * 2 + 8;
    const bridge = word_bits + 19;
    const tail_noise = ~@as(Word, 0) << @as(std.math.Log2Int(Word), @intCast(9));

    const edge_words = [_]Word{
        bit(low_left) | bit(low_right),
        bit(mid_left) | bit(mid_right),
        bit(tail_left) | bit(tail_right) | tail_noise,
    };
    const refill_words = [_]Word{
        bit(low_left),
        bit(mid_left) | bit(bridge),
        bit(tail_left) | tail_noise,
    };
    const closed_words = [_]Word{
        bit(low_left) | bit(low_right),
        bit(mid_left) | bit(mid_right) | bit(bridge),
        bit(tail_left) | bit(tail_right) | tail_noise,
    };

    const edge_bitmap = bitmap_view.BitmapView.init(edge_words[0..], capacity);
    const edge_mask = cpumask_view.CpuMaskView.init(edge_words[0..], capacity);
    const refill_bitmap = bitmap_view.BitmapView.init(refill_words[0..], capacity);
    const refill_mask = cpumask_view.CpuMaskView.init(refill_words[0..], capacity);
    const closed_bitmap = bitmap_view.BitmapView.init(closed_words[0..], capacity);
    const closed_mask = cpumask_view.CpuMaskView.init(closed_words[0..], capacity);

    try testing.expectEqual(@as(usize, 6), edge_bitmap.countSetBits());
    try testing.expectEqual(edge_bitmap.countSetBits(), edge_mask.countPresentCpus());
    try testing.expectEqual(@as(usize, 4), refill_mask.countPresentCpus());
    try testing.expectEqual(@as(usize, 7), closed_mask.countPresentCpus());

    try testing.expect(edge_bitmap.isSubsetOf(closed_bitmap));
    try testing.expect(edge_mask.isSubsetOf(closed_mask));
    try testing.expect(refill_bitmap.isSubsetOf(closed_bitmap));
    try testing.expect(refill_mask.isSubsetOf(closed_mask));
    try testing.expect(edge_bitmap.intersects(refill_bitmap));
    try testing.expect(edge_mask.intersects(refill_mask));
    try testing.expect(!closed_bitmap.isSubsetOf(edge_bitmap));
    try testing.expect(!closed_mask.isSubsetOf(edge_mask));

    try testing.expectEqual(@as(?usize, low_left), refill_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, low_left), refill_mask.firstCpu());
    try testing.expectEqual(@as(?usize, bridge), refill_bitmap.nextSetBit(mid_left + 1));
    try testing.expectEqual(@as(?usize, bridge), refill_mask.nextCpu(mid_left + 1));
    try testing.expectEqual(@as(?usize, bridge + 1), closed_bitmap.nextClearBit(bridge + 1));
    try testing.expectEqual(@as(?usize, bridge + 1), closed_mask.nextMissingCpu(bridge + 1));
    try testing.expect(!closed_mask.hasCpu(capacity - 2));
}
