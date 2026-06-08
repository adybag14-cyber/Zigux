const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const word_bits = bitmap_view.word_bits;
const Word = bitmap_view.Word;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn expectBitmapCpuMaskMirror(bitmap: bitmap_view.BitmapView, cpumask: cpumask_view.CpuMaskView, expected_count: usize, first_gap: ?usize) !void {
    try std.testing.expectEqual(expected_count, bitmap.countSetBits());
    try std.testing.expectEqual(expected_count, cpumask.countPresentCpus());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try std.testing.expectEqual(first_gap, bitmap.firstClearBit());
    try std.testing.expectEqual(first_gap, cpumask.firstMissingCpu());
}

test "bitmap cpumask foldback delta replay keeps bridge and rollback views aligned" {
    const capacity = word_bits * 2 + 11;
    const tail_noise = bit(word_bits * 2 + 12) | bit(word_bits * 2 + 33);

    const base_words = [_]Word{
        bit(2) | bit(9) | bit(21),
        bit(word_bits + 4) | bit(word_bits + 19) | bit(word_bits + 31),
        bit(word_bits * 2 + 3) | tail_noise,
    };
    const bridge_words = [_]Word{
        bit(9),
        bit(word_bits + 4) | bit(word_bits + 31),
        tail_noise,
    };
    const delta_words = [_]Word{
        bit(2) | bit(21),
        bit(word_bits + 19),
        bit(word_bits * 2 + 3) | tail_noise,
    };
    const folded_words = [_]Word{
        bit(2) | bit(9) | bit(21),
        bit(word_bits + 4) | bit(word_bits + 19) | bit(word_bits + 31),
        bit(word_bits * 2 + 3) | tail_noise,
    };
    const outside_words = [_]Word{
        bit(1) | bit(8),
        bit(word_bits + 18),
        bit(word_bits * 2 + 9) | tail_noise,
    };

    const base = bitmap_view.BitmapView.init(base_words[0..], capacity);
    const bridge = bitmap_view.BitmapView.init(bridge_words[0..], capacity);
    const delta = bitmap_view.BitmapView.init(delta_words[0..], capacity);
    const folded = bitmap_view.BitmapView.init(folded_words[0..], capacity);
    const outside = bitmap_view.BitmapView.init(outside_words[0..], capacity);

    const base_mask = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const bridge_mask = cpumask_view.CpuMaskView.init(bridge_words[0..], capacity);
    const delta_mask = cpumask_view.CpuMaskView.init(delta_words[0..], capacity);
    const folded_mask = cpumask_view.CpuMaskView.init(folded_words[0..], capacity);
    const outside_mask = cpumask_view.CpuMaskView.init(outside_words[0..], capacity);

    try expectBitmapCpuMaskMirror(base, base_mask, 7, 0);
    try expectBitmapCpuMaskMirror(bridge, bridge_mask, 3, 0);
    try expectBitmapCpuMaskMirror(delta, delta_mask, 4, 0);
    try expectBitmapCpuMaskMirror(folded, folded_mask, 7, 0);

    try std.testing.expect(bridge.isSubsetOf(base));
    try std.testing.expect(delta.isSubsetOf(base));
    try std.testing.expect(bridge_mask.isSubsetOf(base_mask));
    try std.testing.expect(delta_mask.isSubsetOf(base_mask));

    try std.testing.expect(!bridge.intersects(delta));
    try std.testing.expect(!bridge_mask.intersects(delta_mask));
    try std.testing.expect(!base.intersects(outside));
    try std.testing.expect(!base_mask.intersects(outside_mask));

    try std.testing.expect(base.isSubsetOf(folded));
    try std.testing.expect(folded.isSubsetOf(base));
    try std.testing.expect(base_mask.isSubsetOf(folded_mask));
    try std.testing.expect(folded_mask.isSubsetOf(base_mask));

    try std.testing.expect(base_mask.hasCpu(9));
    try std.testing.expect(bridge_mask.hasCpu(word_bits + 31));
    try std.testing.expect(delta_mask.hasCpu(word_bits * 2 + 3));
    try std.testing.expect(!folded_mask.hasCpu(word_bits * 2 + 10));

    try std.testing.expectEqual(@as(?usize, 2), base.nextSetBit(0));
    try std.testing.expectEqual(@as(?usize, 9), bridge.nextSetBit(3));
    try std.testing.expectEqual(@as(?usize, word_bits + 19), delta.nextSetBit(22));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 3), folded.nextSetBit(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, null), folded.nextSetBit(capacity));
}

test "bitmap cpumask foldback delta clips declared tail noise before counting" {
    const capacity = word_bits + 7;
    const active_tail_bit = word_bits + 6;
    const hidden_tail_noise = bit(word_bits + 7) | bit(word_bits + 13) | bit(word_bits + 27);

    const active_words = [_]Word{
        bit(0) | bit(15),
        bit(active_tail_bit) | hidden_tail_noise,
    };
    const active = bitmap_view.BitmapView.init(active_words[0..], capacity);
    const active_mask = cpumask_view.CpuMaskView.init(active_words[0..], capacity);

    try expectBitmapCpuMaskMirror(active, active_mask, 3, 1);
    try std.testing.expect(active_mask.hasCpu(active_tail_bit));
    try std.testing.expect(!active_mask.hasCpu(word_bits + 5));
    try std.testing.expectEqual(@as(?usize, active_tail_bit), active.nextSetBit(word_bits));
    try std.testing.expectEqual(@as(?usize, null), active.nextSetBit(active_tail_bit + 1));
    try std.testing.expectEqual(@as(?usize, word_bits), active_mask.nextMissingCpu(word_bits));
}
