const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const bit = bitMask;

fn bitMask(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

test "bitmap cpumask ring gate keeps rotating bands aligned" {
    const capacity = word_bits * 3 + 11;
    const low_gate = word_bits - 3;
    const mid_gate = word_bits + 9;
    const high_gate = word_bits * 2 + 5;
    const tail_gate = word_bits * 3 + 4;
    const tail_noise = ~@as(Word, 0) << @as(std.math.Log2Int(Word), @intCast(11));

    const ring_words = [_]Word{
        bit(2) | bit(11) | bit(low_gate),
        bit(mid_gate) | bit(word_bits + 37),
        bit(high_gate) | bit(word_bits * 2 + 31),
        bit(tail_gate) | tail_noise,
    };
    const gate_words = [_]Word{
        bit(low_gate),
        bit(mid_gate) | bit(word_bits + 37),
        bit(high_gate),
        bit(tail_gate) | tail_noise,
    };
    const closed_words = [_]Word{
        bit(2) | bit(11),
        0,
        bit(word_bits * 2 + 31),
        tail_noise,
    };

    const ring_bitmap = bitmap_view.BitmapView.init(ring_words[0..], capacity);
    const ring_mask = cpumask_view.CpuMaskView.init(ring_words[0..], capacity);
    const gate_bitmap = bitmap_view.BitmapView.init(gate_words[0..], capacity);
    const gate_mask = cpumask_view.CpuMaskView.init(gate_words[0..], capacity);
    const closed_bitmap = bitmap_view.BitmapView.init(closed_words[0..], capacity);
    const closed_mask = cpumask_view.CpuMaskView.init(closed_words[0..], capacity);

    try testing.expectEqual(ring_bitmap.countSetBits(), ring_mask.countPresentCpus());
    try testing.expectEqual(@as(usize, 8), ring_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, 2), ring_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 2), ring_mask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), ring_bitmap.firstClearBit());
    try testing.expectEqual(@as(?usize, 0), ring_mask.firstMissingCpu());

    try testing.expect(ring_bitmap.isSet(low_gate));
    try testing.expect(ring_mask.hasCpu(mid_gate));
    try testing.expect(ring_mask.hasCpu(high_gate));
    try testing.expect(ring_mask.hasCpu(tail_gate));
    try testing.expect(!ring_mask.hasCpu(capacity - 1));
    try testing.expectEqual(@as(?usize, word_bits + 37), ring_mask.nextCpu(word_bits + 10));
    try testing.expectEqual(@as(?usize, word_bits * 2 + 31), ring_bitmap.nextSetBit(high_gate + 1));
    try testing.expectEqual(@as(?usize, high_gate + 1), ring_mask.nextMissingCpu(high_gate + 1));

    try testing.expect(gate_bitmap.isSubsetOf(ring_bitmap));
    try testing.expect(gate_mask.isSubsetOf(ring_mask));
    try testing.expect(!ring_bitmap.isSubsetOf(gate_bitmap));
    try testing.expect(!closed_bitmap.intersects(gate_bitmap));
    try testing.expect(!closed_mask.intersects(gate_mask));
    try testing.expect(closed_bitmap.intersects(ring_bitmap));
    try testing.expect(closed_mask.intersects(ring_mask));
    try testing.expectEqual(@as(usize, 5), gate_mask.countPresentCpus());
    try testing.expectEqual(@as(usize, 3), closed_mask.countPresentCpus());
}

test "bitmap cpumask ring gate reopens through a shared bridge cpu" {
    const capacity = word_bits * 2 + 19;
    const bridge = word_bits + 17;
    const low_anchor = 7;
    const mid_anchor = word_bits + 3;
    const tail_anchor = word_bits * 2 + 5;
    const tail_noise = ~@as(Word, 0) << @as(std.math.Log2Int(Word), @intCast(19));

    const before_words = [_]Word{
        bit(low_anchor) | bit(21),
        bit(mid_anchor),
        bit(tail_anchor) | tail_noise,
    };
    const bridge_words = [_]Word{
        bit(low_anchor),
        bit(bridge),
        bit(tail_anchor) | tail_noise,
    };
    const after_words = [_]Word{
        bit(low_anchor) | bit(21),
        bit(mid_anchor) | bit(bridge),
        bit(tail_anchor) | tail_noise,
    };

    const before_bitmap = bitmap_view.BitmapView.init(before_words[0..], capacity);
    const bridge_bitmap = bitmap_view.BitmapView.init(bridge_words[0..], capacity);
    const after_bitmap = bitmap_view.BitmapView.init(after_words[0..], capacity);
    const before_mask = cpumask_view.CpuMaskView.init(before_words[0..], capacity);
    const bridge_mask = cpumask_view.CpuMaskView.init(bridge_words[0..], capacity);
    const after_mask = cpumask_view.CpuMaskView.init(after_words[0..], capacity);

    try testing.expect(before_bitmap.intersects(bridge_bitmap));
    try testing.expect(before_mask.intersects(bridge_mask));
    try testing.expect(!bridge_bitmap.isSubsetOf(before_bitmap));
    try testing.expect(!bridge_mask.isSubsetOf(before_mask));
    try testing.expect(bridge_bitmap.isSubsetOf(after_bitmap));
    try testing.expect(bridge_mask.isSubsetOf(after_mask));
    try testing.expect(before_bitmap.isSubsetOf(after_bitmap));
    try testing.expect(before_mask.isSubsetOf(after_mask));

    try testing.expectEqual(@as(usize, 4), before_bitmap.countSetBits());
    try testing.expectEqual(@as(usize, 3), bridge_mask.countPresentCpus());
    try testing.expectEqual(@as(usize, 5), after_mask.countPresentCpus());
    try testing.expectEqual(@as(?usize, bridge), bridge_bitmap.nextSetBit(word_bits));
    try testing.expectEqual(@as(?usize, bridge), bridge_mask.nextCpu(word_bits));
    try testing.expectEqual(@as(?usize, mid_anchor + 1), after_bitmap.nextClearBit(mid_anchor + 1));
    try testing.expectEqual(@as(?usize, mid_anchor + 1), after_mask.nextMissingCpu(mid_anchor + 1));
    try testing.expect(!after_mask.hasCpu(capacity - 1));
}
