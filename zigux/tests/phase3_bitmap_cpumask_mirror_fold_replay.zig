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

test "phase3 bitmap cpumask mirror banks fold into the shared core" {
    const capacity = word_bits * 3 + 23;
    const left_words = [_]Word{
        bit(1) | bit(5) | bit(9) | bit(17) | bit(25) | bit(33) | bit(41) | bit(49) | bit(57),
        bit(2) | bit(10) | bit(18) | bit(26) | bit(34) | bit(42) | bit(50) | bit(58),
        bit(3) | bit(11) | bit(19) | bit(27) | bit(35) | bit(43) | bit(51) | bit(59),
        bit(4) | bit(10) | bit(16) | bit(22) | bit(55),
    };
    const right_words = [_]Word{
        bit(6) | bit(14) | bit(22) | bit(30) | bit(38) | bit(46) | bit(54) | bit(62),
        bit(5) | bit(13) | bit(21) | bit(29) | bit(37) | bit(45) | bit(53) | bit(61),
        bit(4) | bit(12) | bit(20) | bit(28) | bit(36) | bit(44) | bit(52) | bit(60),
        bit(2) | bit(8) | bit(14) | bit(20) | bit(60),
    };
    const core_words = [_]Word{
        bit(1) | bit(62),
        bit(2) | bit(61),
        bit(3) | bit(60),
        bit(4) | bit(20) | bit(55),
    };
    const folded_words = [_]Word{
        left_words[0] | right_words[0],
        left_words[1] | right_words[1],
        left_words[2] | right_words[2],
        left_words[3] | right_words[3],
    };

    try expectMirrors(left_words[0..], capacity, 29, 1, 0);
    try expectMirrors(right_words[0..], capacity, 28, 6, 0);
    try expectMirrors(core_words[0..], capacity, 8, 1, 0);
    try expectMirrors(folded_words[0..], capacity, 57, 1, 0);

    try expectCursorMirror(left_words[0..], capacity, word_bits + 51, word_bits + 58, word_bits + 51);
    try expectCursorMirror(right_words[0..], capacity, word_bits * 2 + 53, word_bits * 2 + 60, word_bits * 2 + 53);
    try expectCursorMirror(core_words[0..], capacity, word_bits * 3 + 5, word_bits * 3 + 20, word_bits * 3 + 5);
    try expectCursorMirror(folded_words[0..], capacity, word_bits * 3 + 21, word_bits * 3 + 22, word_bits * 3 + 21);
    try expectCursorMirror(folded_words[0..], capacity, capacity, null, null);

    const left_bitmap = BitmapView.init(left_words[0..], capacity);
    const right_bitmap = BitmapView.init(right_words[0..], capacity);
    const core_bitmap = BitmapView.init(core_words[0..], capacity);
    const folded_bitmap = BitmapView.init(folded_words[0..], capacity);
    const left_cpumask = CpuMaskView.init(left_words[0..], capacity);
    const right_cpumask = CpuMaskView.init(right_words[0..], capacity);
    const core_cpumask = CpuMaskView.init(core_words[0..], capacity);
    const folded_cpumask = CpuMaskView.init(folded_words[0..], capacity);

    try std.testing.expect(left_bitmap.isSubsetOf(folded_bitmap));
    try std.testing.expect(left_cpumask.isSubsetOf(folded_cpumask));
    try std.testing.expect(right_bitmap.isSubsetOf(folded_bitmap));
    try std.testing.expect(right_cpumask.isSubsetOf(folded_cpumask));
    try std.testing.expect(core_bitmap.isSubsetOf(folded_bitmap));
    try std.testing.expect(core_cpumask.isSubsetOf(folded_cpumask));
    try std.testing.expect(!left_bitmap.intersects(right_bitmap));
    try std.testing.expect(!left_cpumask.intersects(right_cpumask));
    try std.testing.expect(core_bitmap.intersects(left_bitmap));
    try std.testing.expect(core_cpumask.intersects(left_cpumask));
    try std.testing.expect(core_bitmap.intersects(right_bitmap));
    try std.testing.expect(core_cpumask.intersects(right_cpumask));
    try std.testing.expect(folded_cpumask.hasCpu(word_bits * 3 + 22));
    try std.testing.expect(!folded_cpumask.hasCpu(word_bits * 3 + 23 - 2));
}

test "phase3 bitmap cpumask mirror fold expands without leaking tail noise" {
    const capacity = word_bits * 3 + 23;
    const core_words = [_]Word{
        bit(1) | bit(62),
        bit(2) | bit(61),
        bit(3) | bit(60),
        bit(4) | bit(20) | bit(55),
    };
    const expanded_words = [_]Word{
        core_words[0] | bit(5) | bit(9) | bit(14) | bit(22) | bit(57),
        core_words[1] | bit(10) | bit(18) | bit(29) | bit(42) | bit(53),
        core_words[2] | bit(11) | bit(20) | bit(35) | bit(44) | bit(52),
        core_words[3] | bit(0) | bit(2) | bit(8) | bit(14) | bit(22) | bit(49) | bit(63),
    };
    const refolded_words = [_]Word{
        bit(1) | bit(5) | bit(9) | bit(57) | bit(62),
        bit(2) | bit(10) | bit(53) | bit(61),
        bit(3) | bit(11) | bit(52) | bit(60),
        bit(4) | bit(14) | bit(20) | bit(22) | bit(63),
    };

    try expectMirrors(core_words[0..], capacity, 8, 1, 0);
    try expectMirrors(expanded_words[0..], capacity, 28, 1, 0);
    try expectMirrors(refolded_words[0..], capacity, 17, 1, 0);

    try expectCursorMirror(expanded_words[0..], capacity, 6, 9, 6);
    try expectCursorMirror(expanded_words[0..], capacity, word_bits + 54, word_bits + 61, word_bits + 54);
    try expectCursorMirror(refolded_words[0..], capacity, word_bits * 3 + 21, word_bits * 3 + 22, word_bits * 3 + 21);
    try expectCursorMirror(refolded_words[0..], capacity, capacity, null, null);

    const core_bitmap = BitmapView.init(core_words[0..], capacity);
    const expanded_bitmap = BitmapView.init(expanded_words[0..], capacity);
    const refolded_bitmap = BitmapView.init(refolded_words[0..], capacity);
    const core_cpumask = CpuMaskView.init(core_words[0..], capacity);
    const expanded_cpumask = CpuMaskView.init(expanded_words[0..], capacity);
    const refolded_cpumask = CpuMaskView.init(refolded_words[0..], capacity);

    try std.testing.expect(core_bitmap.isSubsetOf(expanded_bitmap));
    try std.testing.expect(core_cpumask.isSubsetOf(expanded_cpumask));
    try std.testing.expect(refolded_bitmap.isSubsetOf(expanded_bitmap));
    try std.testing.expect(refolded_cpumask.isSubsetOf(expanded_cpumask));
    try std.testing.expect(!expanded_bitmap.isSubsetOf(refolded_bitmap));
    try std.testing.expect(!expanded_cpumask.isSubsetOf(refolded_cpumask));
    try std.testing.expect(core_bitmap.intersects(refolded_bitmap));
    try std.testing.expect(core_cpumask.intersects(refolded_cpumask));
    try std.testing.expect(expanded_cpumask.hasCpu(word_bits * 3 + 22));
    try std.testing.expect(!expanded_cpumask.hasCpu(word_bits * 3 + 21));
}
