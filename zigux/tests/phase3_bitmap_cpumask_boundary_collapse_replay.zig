const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn mask(bit: usize) Word {
    return @as(Word, 1) << @intCast(bit % word_bits);
}

fn setBit(words: []Word, bit: usize) void {
    words[bit / word_bits] |= mask(bit);
}

fn clearBit(words: []Word, bit: usize) void {
    words[bit / word_bits] &= ~mask(bit);
}

fn makeWords(comptime bits: []const usize) [3]Word {
    var words = [_]Word{ 0, 0, 0 };
    inline for (bits) |bit| {
        setBit(words[0..], bit);
    }
    return words;
}

fn expectBitmapAndCpuMaskMatch(bitmap: BitmapView, cpumask: CpuMaskView, expected_count: usize) !void {
    try std.testing.expectEqual(expected_count, bitmap.countSetBits());
    try std.testing.expectEqual(expected_count, cpumask.countPresentCpus());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try std.testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    const starts = [_]usize{
        0,
        word_bits - 2,
        word_bits - 1,
        word_bits,
        word_bits + 1,
        (2 * word_bits) + 3,
        (2 * word_bits) + 8,
    };

    for (starts) |start| {
        try std.testing.expectEqual(bitmap.nextSetBit(start), cpumask.nextCpu(start));
        try std.testing.expectEqual(bitmap.nextClearBit(start), cpumask.nextMissingCpu(start));
    }
}

test "bitmap and cpumask agree while a boundary superset collapses to baseline" {
    const bit_len = (2 * word_bits) + 9;
    const baseline_bits = &[_]usize{
        0,
        word_bits - 2,
        word_bits,
        word_bits + 5,
        (2 * word_bits) + 3,
        (2 * word_bits) + 8,
    };
    const extras = &[_]usize{
        word_bits - 1,
        word_bits + 1,
        (2 * word_bits) + 6,
    };

    var baseline_words = makeWords(baseline_bits);
    var superset_words = baseline_words;
    inline for (extras) |bit| {
        setBit(superset_words[0..], bit);
    }
    setBit(superset_words[0..], bit_len + 2);

    const baseline_bitmap = BitmapView.init(baseline_words[0..], bit_len);
    var superset_bitmap = BitmapView.init(superset_words[0..], bit_len);
    var superset_cpumask = CpuMaskView.init(superset_words[0..], bit_len);

    try expectBitmapAndCpuMaskMatch(superset_bitmap, superset_cpumask, baseline_bits.len + extras.len);
    try std.testing.expect(baseline_bitmap.isSubsetOf(superset_bitmap));
    try std.testing.expect(superset_cpumask.isSubsetOf(CpuMaskView.init(superset_words[0..], bit_len)));
    try std.testing.expect(superset_cpumask.intersects(CpuMaskView.init(baseline_words[0..], bit_len)));
    try std.testing.expectEqual(@as(?usize, word_bits + 2), superset_bitmap.nextClearBit(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits + 2), superset_cpumask.nextMissingCpu(word_bits));

    inline for (extras) |bit| {
        clearBit(superset_words[0..], bit);
    }

    superset_bitmap = BitmapView.init(superset_words[0..], bit_len);
    superset_cpumask = CpuMaskView.init(superset_words[0..], bit_len);

    try expectBitmapAndCpuMaskMatch(superset_bitmap, superset_cpumask, baseline_bits.len);
    try std.testing.expect(superset_bitmap.isSubsetOf(baseline_bitmap));
    try std.testing.expect(baseline_bitmap.isSubsetOf(superset_bitmap));
    try std.testing.expect(superset_cpumask.isSubsetOf(CpuMaskView.init(baseline_words[0..], bit_len)));
    try std.testing.expectEqual(@as(?usize, word_bits - 1), superset_bitmap.nextClearBit(word_bits - 2));
    try std.testing.expectEqual(@as(?usize, word_bits - 1), superset_cpumask.nextMissingCpu(word_bits - 2));
    try std.testing.expect(!superset_cpumask.hasCpu((2 * word_bits) + 6));
}

test "bitmap and cpumask preserve cursor mirrors across tail-capacity collapse" {
    const bit_len = (2 * word_bits) + 5;
    var words = [_]Word{
        std.math.maxInt(Word),
        std.math.maxInt(Word),
        mask((2 * word_bits) + 0) |
            mask((2 * word_bits) + 2) |
            mask((2 * word_bits) + 4),
    };
    setBit(words[0..], bit_len + 1);

    var bitmap = BitmapView.init(words[0..], bit_len);
    var cpumask = CpuMaskView.init(words[0..], bit_len);

    try expectBitmapAndCpuMaskMatch(bitmap, cpumask, (2 * word_bits) + 3);
    try std.testing.expectEqual(@as(?usize, (2 * word_bits) + 1), bitmap.nextClearBit(2 * word_bits));
    try std.testing.expectEqual(@as(?usize, (2 * word_bits) + 1), cpumask.nextMissingCpu(2 * word_bits));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextCpu(bit_len));

    clearBit(words[0..], word_bits - 1);
    clearBit(words[0..], word_bits);
    clearBit(words[0..], (2 * word_bits) + 4);

    bitmap = BitmapView.init(words[0..], bit_len);
    cpumask = CpuMaskView.init(words[0..], bit_len);

    try expectBitmapAndCpuMaskMatch(bitmap, cpumask, (2 * word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits - 1), bitmap.nextClearBit(word_bits - 2));
    try std.testing.expectEqual(@as(?usize, word_bits - 1), cpumask.nextMissingCpu(word_bits - 2));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), bitmap.nextSetBit(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), cpumask.nextCpu(word_bits));
}
