const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

test "bitmap and cpumask stay aligned across bookend pairs and a wide interior gap" {
    const bit_len = word_bits + 9;
    const words = [_]Word{
        bit(0) | bit(1) | bit(word_bits - 2) | bit(word_bits - 1),
        bit(word_bits) | bit(word_bits + 8) | bit(word_bits + 16),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try std.testing.expectEqual(@as(usize, 6), bitmap.countSetBits());
    try std.testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 2), bitmap.firstClearBit());
    try std.testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try std.testing.expect(bitmap.isSet(word_bits - 1));
    try std.testing.expect(bitmap.isSet(word_bits + 8));
    try std.testing.expect(cpumask.hasCpu(word_bits - 1));
    try std.testing.expect(cpumask.hasCpu(word_bits + 8));
    try std.testing.expect(!bitmap.isSet(3));
    try std.testing.expect(!cpumask.hasCpu(3));
}

test "bookend peers stay bounded while the interior gap remains disjoint" {
    const bit_len = word_bits + 9;
    const base_words = [_]Word{
        bit(0) | bit(1) | bit(word_bits - 2) | bit(word_bits - 1),
        bit(word_bits) | bit(word_bits + 8),
    };
    const left_bookend_words = [_]Word{
        bit(0) | bit(1),
        bit(word_bits),
    };
    const right_bookend_words = [_]Word{
        bit(word_bits - 2) | bit(word_bits - 1),
        bit(word_bits + 8),
    };
    const gap_words = [_]Word{
        bit(2) | bit(word_bits - 3),
        bit(word_bits + 4) | bit(word_bits + 15),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], bit_len);
    const left_bookend = cpumask_view.CpuMaskView.init(left_bookend_words[0..], bit_len);
    const right_bookend = cpumask_view.CpuMaskView.init(right_bookend_words[0..], bit_len);
    const gap = cpumask_view.CpuMaskView.init(gap_words[0..], bit_len);

    try std.testing.expect(left_bookend.isSubsetOf(base));
    try std.testing.expect(right_bookend.isSubsetOf(base));
    try std.testing.expect(base.intersects(left_bookend));
    try std.testing.expect(base.intersects(right_bookend));
    try std.testing.expect(!left_bookend.intersects(right_bookend));
    try std.testing.expect(!base.intersects(gap));
    try std.testing.expect(!gap.isSubsetOf(base));
}

test "full-window bitmap and cpumask keep bookend peers inside the bounded union" {
    const bit_len = word_bits + 9;
    const full_words = [_]Word{
        std.math.maxInt(Word),
        std.math.maxInt(Word),
    };
    const left_bookend_words = [_]Word{
        bit(0) | bit(1),
        bit(word_bits),
    };
    const right_bookend_words = [_]Word{
        bit(word_bits - 2) | bit(word_bits - 1),
        bit(word_bits + 8) | bit(word_bits + 18),
    };

    const bitmap = bitmap_view.BitmapView.init(full_words[0..], bit_len);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], bit_len);
    const left_bookend = cpumask_view.CpuMaskView.init(left_bookend_words[0..], bit_len);
    const right_bookend = cpumask_view.CpuMaskView.init(right_bookend_words[0..], bit_len);

    try std.testing.expectEqual(bit_len, bitmap.countSetBits());
    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, null), bitmap.firstClearBit());
    try std.testing.expectEqual(bit_len, full.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 0), full.firstCpu());
    try std.testing.expectEqual(@as(?usize, null), full.firstMissingCpu());
    try std.testing.expect(left_bookend.isSubsetOf(full));
    try std.testing.expect(right_bookend.isSubsetOf(full));
}
