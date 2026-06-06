const std = @import("std");

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn expectCursorPair(bitmap: bitmap_view.BitmapView, cpumask: cpumask_view.CpuMaskView, start: usize, expected: ?usize) !void {
    try std.testing.expectEqual(expected, bitmap.nextSetBit(start));
    try std.testing.expectEqual(expected, cpumask.nextCpu(start));
}

fn expectMissingPair(bitmap: bitmap_view.BitmapView, cpumask: cpumask_view.CpuMaskView, start: usize, expected: ?usize) !void {
    try std.testing.expectEqual(expected, bitmap.nextClearBit(start));
    try std.testing.expectEqual(expected, cpumask.nextMissingCpu(start));
}

test "bitmap and cpumask align across bank rotation carry" {
    const cpu_capacity = (2 * word_bits) + 13;
    const lower_tail = word_bits - 1;
    const bank_carry = word_bits;
    const tail_head = 2 * word_bits;
    const tail_edge = (2 * word_bits) + 12;

    const original_words = [_]Word{
        bit(1) | bit(5) | bit(lower_tail),
        bit(word_bits + 2) | bit(word_bits + 11),
        bit((2 * word_bits) + 4) | ~@as(Word, 0) << 13,
    };
    const rotated_words = [_]Word{
        bit(5) | bit(17),
        bit(bank_carry) | bit(word_bits + 2) | bit(word_bits + 11),
        bit(tail_head) | bit((2 * word_bits) + 4) | bit(tail_edge) | ~@as(Word, 0) << 13,
    };
    const bridge_words = [_]Word{
        original_words[0] | rotated_words[0],
        original_words[1] | rotated_words[1],
        original_words[2] | rotated_words[2],
    };

    const original_bitmap = bitmap_view.BitmapView.init(original_words[0..], cpu_capacity);
    const rotated_bitmap = bitmap_view.BitmapView.init(rotated_words[0..], cpu_capacity);
    const bridge_bitmap = bitmap_view.BitmapView.init(bridge_words[0..], cpu_capacity);

    const original_mask = cpumask_view.CpuMaskView.init(original_words[0..], cpu_capacity);
    const rotated_mask = cpumask_view.CpuMaskView.init(rotated_words[0..], cpu_capacity);
    const bridge_mask = cpumask_view.CpuMaskView.init(bridge_words[0..], cpu_capacity);

    try std.testing.expectEqual(@as(usize, 6), original_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 6), original_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 8), rotated_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 8), rotated_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 10), bridge_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 10), bridge_mask.countPresentCpus());

    try std.testing.expect(original_bitmap.intersects(rotated_bitmap));
    try std.testing.expect(original_mask.intersects(rotated_mask));
    try std.testing.expect(original_bitmap.isSubsetOf(bridge_bitmap));
    try std.testing.expect(original_mask.isSubsetOf(bridge_mask));
    try std.testing.expect(rotated_bitmap.isSubsetOf(bridge_bitmap));
    try std.testing.expect(rotated_mask.isSubsetOf(bridge_mask));
    try std.testing.expect(!rotated_bitmap.isSubsetOf(original_bitmap));
    try std.testing.expect(!rotated_mask.isSubsetOf(original_mask));

    try expectCursorPair(bridge_bitmap, bridge_mask, 0, 1);
    try expectCursorPair(bridge_bitmap, bridge_mask, 2, 5);
    try expectCursorPair(bridge_bitmap, bridge_mask, lower_tail, lower_tail);
    try expectCursorPair(bridge_bitmap, bridge_mask, bank_carry, bank_carry);
    try expectCursorPair(bridge_bitmap, bridge_mask, tail_head + 5, tail_edge);
    try expectCursorPair(bridge_bitmap, bridge_mask, tail_edge + 1, null);

    try expectMissingPair(bridge_bitmap, bridge_mask, 0, 0);
    try expectMissingPair(bridge_bitmap, bridge_mask, lower_tail, word_bits + 1);
    try expectMissingPair(bridge_bitmap, bridge_mask, tail_edge, null);
    try expectMissingPair(original_bitmap, original_mask, tail_head + 4, tail_head + 5);
    try expectCursorPair(original_bitmap, original_mask, tail_head + 5, null);
}

test "bitmap and cpumask keep cursors aligned after carry clear" {
    const cpu_capacity = (2 * word_bits) + 7;
    const lower_tail = word_bits - 1;
    const bank_carry = word_bits;
    const tail_head = 2 * word_bits;
    const tail_edge = (2 * word_bits) + 6;

    const before_words = [_]Word{
        bit(0) | bit(lower_tail),
        bit(word_bits + 3),
        bit(tail_edge) | ~@as(Word, 0) << 7,
    };
    const after_words = [_]Word{
        bit(0),
        bit(bank_carry) | bit(word_bits + 3),
        bit(tail_head + 1) | bit(tail_edge) | ~@as(Word, 0) << 7,
    };

    const before_bitmap = bitmap_view.BitmapView.init(before_words[0..], cpu_capacity);
    const after_bitmap = bitmap_view.BitmapView.init(after_words[0..], cpu_capacity);
    const before_mask = cpumask_view.CpuMaskView.init(before_words[0..], cpu_capacity);
    const after_mask = cpumask_view.CpuMaskView.init(after_words[0..], cpu_capacity);

    try std.testing.expectEqual(@as(usize, 4), before_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 4), before_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 5), after_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 5), after_mask.countPresentCpus());

    try std.testing.expect(before_bitmap.intersects(after_bitmap));
    try std.testing.expect(before_mask.intersects(after_mask));
    try std.testing.expect(!before_bitmap.isSubsetOf(after_bitmap));
    try std.testing.expect(!before_mask.isSubsetOf(after_mask));
    try std.testing.expect(!after_bitmap.isSubsetOf(before_bitmap));
    try std.testing.expect(!after_mask.isSubsetOf(before_mask));

    try expectCursorPair(after_bitmap, after_mask, 0, 0);
    try expectCursorPair(after_bitmap, after_mask, 1, bank_carry);
    try expectCursorPair(after_bitmap, after_mask, bank_carry + 1, word_bits + 3);
    try expectCursorPair(after_bitmap, after_mask, tail_head, tail_head + 1);
    try expectCursorPair(after_bitmap, after_mask, tail_edge, tail_edge);
    try expectCursorPair(after_bitmap, after_mask, tail_edge + 1, null);

    try expectMissingPair(after_bitmap, after_mask, 0, 1);
    try expectMissingPair(after_bitmap, after_mask, bank_carry, word_bits + 1);
    try expectMissingPair(after_bitmap, after_mask, tail_edge, null);
}
