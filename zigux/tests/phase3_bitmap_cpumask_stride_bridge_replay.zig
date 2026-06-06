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

test "bitmap and cpumask align across stride bridge promotion" {
    const cpu_capacity = word_bits + 17;
    const bridge_cpu = word_bits;
    const trailing_cpu = word_bits + 16;

    const even_stride_words = [_]Word{
        bit(2) | bit(6) | bit(10) | bit(14),
        bit(word_bits + 4) | bit(word_bits + 8) | bit(trailing_cpu) | ~@as(Word, 0) << 17,
    };
    const odd_stride_words = [_]Word{
        bit(3) | bit(7) | bit(11) | bit(15),
        bit(word_bits + 5) | bit(word_bits + 9) | ~@as(Word, 0) << 17,
    };
    const bridge_words = [_]Word{
        even_stride_words[0] | odd_stride_words[0],
        bit(bridge_cpu) | bit(word_bits + 4) | bit(word_bits + 5) | bit(word_bits + 8) | bit(word_bits + 9) | bit(trailing_cpu) | ~@as(Word, 0) << 17,
    };
    const bridge_without_tail_words = [_]Word{
        bridge_words[0],
        bridge_words[1] & ~bit(trailing_cpu),
    };

    const even_bitmap = bitmap_view.BitmapView.init(even_stride_words[0..], cpu_capacity);
    const odd_bitmap = bitmap_view.BitmapView.init(odd_stride_words[0..], cpu_capacity);
    const bridge_bitmap = bitmap_view.BitmapView.init(bridge_words[0..], cpu_capacity);
    const no_tail_bitmap = bitmap_view.BitmapView.init(bridge_without_tail_words[0..], cpu_capacity);

    const even_mask = cpumask_view.CpuMaskView.init(even_stride_words[0..], cpu_capacity);
    const odd_mask = cpumask_view.CpuMaskView.init(odd_stride_words[0..], cpu_capacity);
    const bridge_mask = cpumask_view.CpuMaskView.init(bridge_words[0..], cpu_capacity);
    const no_tail_mask = cpumask_view.CpuMaskView.init(bridge_without_tail_words[0..], cpu_capacity);

    try std.testing.expectEqual(@as(usize, 7), even_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 7), even_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 6), odd_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 6), odd_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 14), bridge_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 14), bridge_mask.countPresentCpus());

    try std.testing.expect(!even_bitmap.intersects(odd_bitmap));
    try std.testing.expect(!even_mask.intersects(odd_mask));
    try std.testing.expect(even_bitmap.isSubsetOf(bridge_bitmap));
    try std.testing.expect(even_mask.isSubsetOf(bridge_mask));
    try std.testing.expect(odd_bitmap.isSubsetOf(bridge_bitmap));
    try std.testing.expect(odd_mask.isSubsetOf(bridge_mask));
    try std.testing.expect(!bridge_bitmap.isSubsetOf(even_bitmap));
    try std.testing.expect(!bridge_mask.isSubsetOf(even_mask));

    try expectCursorPair(bridge_bitmap, bridge_mask, 0, 2);
    try expectCursorPair(bridge_bitmap, bridge_mask, 3, 3);
    try expectCursorPair(bridge_bitmap, bridge_mask, 12, 14);
    try expectCursorPair(bridge_bitmap, bridge_mask, word_bits - 1, bridge_cpu);
    try expectCursorPair(bridge_bitmap, bridge_mask, word_bits + 1, word_bits + 4);
    try expectCursorPair(bridge_bitmap, bridge_mask, trailing_cpu, trailing_cpu);
    try expectCursorPair(bridge_bitmap, bridge_mask, trailing_cpu + 1, null);

    try expectMissingPair(bridge_bitmap, bridge_mask, 0, 0);
    try expectMissingPair(bridge_bitmap, bridge_mask, 2, 4);
    try expectMissingPair(bridge_bitmap, bridge_mask, word_bits, word_bits + 1);
    try expectMissingPair(bridge_bitmap, bridge_mask, trailing_cpu, null);

    try std.testing.expect(no_tail_bitmap.isSubsetOf(bridge_bitmap));
    try std.testing.expect(no_tail_mask.isSubsetOf(bridge_mask));
    try std.testing.expect(!bridge_bitmap.isSubsetOf(no_tail_bitmap));
    try std.testing.expect(!bridge_mask.isSubsetOf(no_tail_mask));
    try expectCursorPair(no_tail_bitmap, no_tail_mask, word_bits + 10, null);
    try expectMissingPair(no_tail_bitmap, no_tail_mask, trailing_cpu, trailing_cpu);
}

test "bitmap and cpumask keep stride bridge cursors aligned after a lower-bank handoff" {
    const cpu_capacity = word_bits + 9;
    const bridge_cpu = word_bits;

    const lower_stride_words = [_]Word{
        bit(1) | bit(5) | bit(9) | bit(13),
        bit(word_bits + 8) | ~@as(Word, 0) << 9,
    };
    const handed_off_words = [_]Word{
        bit(5) | bit(9) | bit(13),
        bit(bridge_cpu) | bit(word_bits + 4) | bit(word_bits + 8) | ~@as(Word, 0) << 9,
    };

    const lower_bitmap = bitmap_view.BitmapView.init(lower_stride_words[0..], cpu_capacity);
    const handoff_bitmap = bitmap_view.BitmapView.init(handed_off_words[0..], cpu_capacity);
    const lower_mask = cpumask_view.CpuMaskView.init(lower_stride_words[0..], cpu_capacity);
    const handoff_mask = cpumask_view.CpuMaskView.init(handed_off_words[0..], cpu_capacity);

    try std.testing.expect(lower_bitmap.intersects(handoff_bitmap));
    try std.testing.expect(lower_mask.intersects(handoff_mask));
    try std.testing.expect(!lower_bitmap.isSubsetOf(handoff_bitmap));
    try std.testing.expect(!lower_mask.isSubsetOf(handoff_mask));
    try std.testing.expect(!handoff_bitmap.isSubsetOf(lower_bitmap));
    try std.testing.expect(!handoff_mask.isSubsetOf(lower_mask));

    try expectCursorPair(handoff_bitmap, handoff_mask, 0, 5);
    try expectCursorPair(handoff_bitmap, handoff_mask, word_bits - 2, bridge_cpu);
    try expectCursorPair(handoff_bitmap, handoff_mask, bridge_cpu + 1, word_bits + 4);
    try expectCursorPair(handoff_bitmap, handoff_mask, word_bits + 8, word_bits + 8);
    try expectCursorPair(handoff_bitmap, handoff_mask, word_bits + 9, null);

    try expectMissingPair(handoff_bitmap, handoff_mask, 0, 0);
    try expectMissingPair(handoff_bitmap, handoff_mask, 5, 6);
    try expectMissingPair(handoff_bitmap, handoff_mask, bridge_cpu, word_bits + 1);
    try expectMissingPair(handoff_bitmap, handoff_mask, word_bits + 8, null);
}
