const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(offset: usize) Word {
    return @as(Word, 1) << @intCast(offset);
}

fn lowMask(count: usize) Word {
    if (count == 0) return 0;
    if (count == word_bits) return std.math.maxInt(Word);
    return (@as(Word, 1) << @intCast(count)) - 1;
}

fn expectMirrors(
    words: []const Word,
    capacity: usize,
    expected_count: usize,
    expected_first_present: ?usize,
    expected_first_missing: ?usize,
) !void {
    const bitmap = BitmapView.init(words, capacity);
    const cpumask = CpuMaskView.init(words, capacity);

    try std.testing.expectEqual(expected_count, bitmap.countSetBits());
    try std.testing.expectEqual(expected_count, cpumask.countPresentCpus());
    try std.testing.expectEqual(expected_first_present, bitmap.firstSetBit());
    try std.testing.expectEqual(expected_first_present, cpumask.firstCpu());
    try std.testing.expectEqual(expected_first_missing, bitmap.firstClearBit());
    try std.testing.expectEqual(expected_first_missing, cpumask.firstMissingCpu());
}

fn expectCursorMirror(words: []const Word, capacity: usize, start: usize, present: ?usize, missing: ?usize) !void {
    const bitmap = BitmapView.init(words, capacity);
    const cpumask = CpuMaskView.init(words, capacity);

    try std.testing.expectEqual(present, bitmap.nextSetBit(start));
    try std.testing.expectEqual(present, cpumask.nextCpu(start));
    try std.testing.expectEqual(missing, bitmap.nextClearBit(start));
    try std.testing.expectEqual(missing, cpumask.nextMissingCpu(start));
}

test "phase3 bitmap cpumask sawtooth gaps mirror across banks" {
    const capacity = word_bits * 3 + 19;
    const sawtooth_words = [_]Word{
        bit(0) | bit(2) | bit(5) | bit(9) | bit(14) | bit(20) | bit(27) | bit(35) | bit(44) | bit(54),
        bit(1) | bit(4) | bit(8) | bit(13) | bit(19) | bit(26) | bit(34) | bit(43) | bit(53),
        bit(0) | bit(3) | bit(7) | bit(12) | bit(18) | bit(25) | bit(33) | bit(42) | bit(52),
        bit(2) | bit(6) | bit(11) | bit(17) | bit(41),
    };
    const dense_tail_words = [_]Word{
        std.math.maxInt(Word),
        std.math.maxInt(Word),
        std.math.maxInt(Word),
        lowMask(19) | bit(41),
    };
    const odd_anchor_words = [_]Word{
        bit(9) | bit(35),
        bit(13) | bit(43),
        bit(7) | bit(52),
        bit(17) | bit(41),
    };

    try expectMirrors(sawtooth_words[0..], capacity, 32, 0, 1);
    try expectCursorMirror(sawtooth_words[0..], capacity, 1, 2, 1);
    try expectCursorMirror(sawtooth_words[0..], capacity, 10, 14, 10);
    try expectCursorMirror(sawtooth_words[0..], capacity, word_bits + 2, word_bits + 4, word_bits + 2);
    try expectCursorMirror(sawtooth_words[0..], capacity, word_bits * 2 + 8, word_bits * 2 + 12, word_bits * 2 + 8);
    try expectCursorMirror(sawtooth_words[0..], capacity, word_bits * 3 + 18, null, word_bits * 3 + 18);

    const sawtooth_bitmap = BitmapView.init(sawtooth_words[0..], capacity);
    const dense_tail_bitmap = BitmapView.init(dense_tail_words[0..], capacity);
    const odd_anchor_bitmap = BitmapView.init(odd_anchor_words[0..], capacity);
    const sawtooth_cpumask = CpuMaskView.init(sawtooth_words[0..], capacity);
    const dense_tail_cpumask = CpuMaskView.init(dense_tail_words[0..], capacity);
    const odd_anchor_cpumask = CpuMaskView.init(odd_anchor_words[0..], capacity);

    try std.testing.expect(sawtooth_bitmap.isSubsetOf(dense_tail_bitmap));
    try std.testing.expect(sawtooth_cpumask.isSubsetOf(dense_tail_cpumask));
    try std.testing.expect(odd_anchor_bitmap.isSubsetOf(sawtooth_bitmap));
    try std.testing.expect(odd_anchor_cpumask.isSubsetOf(sawtooth_cpumask));
    try std.testing.expect(!dense_tail_bitmap.isSubsetOf(sawtooth_bitmap));
    try std.testing.expect(!dense_tail_cpumask.isSubsetOf(sawtooth_cpumask));
    try std.testing.expect(sawtooth_bitmap.intersects(odd_anchor_bitmap));
    try std.testing.expect(sawtooth_cpumask.intersects(odd_anchor_cpumask));
    try std.testing.expect(sawtooth_cpumask.hasCpu(word_bits * 3 + 17));
    try std.testing.expect(!sawtooth_cpumask.hasCpu(word_bits * 3 + 18));
}

test "phase3 bitmap cpumask sawtooth refill keeps subset and tail noise bounded" {
    const capacity = word_bits * 3 + 19;
    const sawtooth_words = [_]Word{
        bit(0) | bit(2) | bit(5) | bit(9) | bit(14) | bit(20) | bit(27) | bit(35) | bit(44) | bit(54),
        bit(1) | bit(4) | bit(8) | bit(13) | bit(19) | bit(26) | bit(34) | bit(43) | bit(53),
        bit(0) | bit(3) | bit(7) | bit(12) | bit(18) | bit(25) | bit(33) | bit(42) | bit(52),
        bit(2) | bit(6) | bit(11) | bit(17) | bit(41),
    };
    const refill_words = [_]Word{
        sawtooth_words[0] | bit(1) | bit(3) | bit(10) | bit(21) | bit(36),
        sawtooth_words[1] | bit(0) | bit(2) | bit(14) | bit(35) | bit(44),
        sawtooth_words[2] | bit(1) | bit(4) | bit(13) | bit(26) | bit(43),
        sawtooth_words[3] | bit(0) | bit(3) | bit(7) | bit(18) | bit(52),
    };
    const refill_witness_words = [_]Word{
        bit(1) | bit(10) | bit(36),
        bit(0) | bit(14) | bit(44),
        bit(1) | bit(26) | bit(43),
        bit(0) | bit(18) | bit(52),
    };

    try expectMirrors(refill_words[0..], capacity, 51, 0, 4);
    try expectMirrors(refill_witness_words[0..], capacity, 11, 1, 0);
    try expectCursorMirror(refill_words[0..], capacity, 0, 0, 4);
    try expectCursorMirror(refill_words[0..], capacity, 4, 5, 4);
    try expectCursorMirror(refill_words[0..], capacity, word_bits + 14, word_bits + 14, word_bits + 15);
    try expectCursorMirror(refill_words[0..], capacity, word_bits * 2 + 43, word_bits * 2 + 43, word_bits * 2 + 44);
    try expectCursorMirror(refill_words[0..], capacity, capacity, null, null);

    const sawtooth_bitmap = BitmapView.init(sawtooth_words[0..], capacity);
    const refill_bitmap = BitmapView.init(refill_words[0..], capacity);
    const witness_bitmap = BitmapView.init(refill_witness_words[0..], capacity);
    const sawtooth_cpumask = CpuMaskView.init(sawtooth_words[0..], capacity);
    const refill_cpumask = CpuMaskView.init(refill_words[0..], capacity);
    const witness_cpumask = CpuMaskView.init(refill_witness_words[0..], capacity);

    try std.testing.expect(sawtooth_bitmap.isSubsetOf(refill_bitmap));
    try std.testing.expect(sawtooth_cpumask.isSubsetOf(refill_cpumask));
    try std.testing.expect(witness_bitmap.isSubsetOf(refill_bitmap));
    try std.testing.expect(witness_cpumask.isSubsetOf(refill_cpumask));
    try std.testing.expect(!refill_bitmap.isSubsetOf(sawtooth_bitmap));
    try std.testing.expect(!refill_cpumask.isSubsetOf(sawtooth_cpumask));
    try std.testing.expect(!witness_bitmap.intersects(sawtooth_bitmap));
    try std.testing.expect(!witness_cpumask.intersects(sawtooth_cpumask));
    try std.testing.expect(refill_bitmap.intersects(witness_bitmap));
    try std.testing.expect(refill_cpumask.intersects(witness_cpumask));
}
