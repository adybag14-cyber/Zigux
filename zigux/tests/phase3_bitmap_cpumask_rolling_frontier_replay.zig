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

test "phase3 bitmap cpumask rolling frontier grows through sparse banks" {
    const capacity = word_bits * 3 + 19;
    const frontier_words = [_]Word{
        lowMask(11),
        lowMask(4) | bit(10),
        bit(0) | bit(23),
        bit(18) | bit(40),
    };

    try expectMirrors(frontier_words[0..], capacity, 19, 0, 11);
    try expectCursorMirror(frontier_words[0..], capacity, 0, 0, 11);
    try expectCursorMirror(frontier_words[0..], capacity, 11, word_bits + 0, 11);
    try expectCursorMirror(frontier_words[0..], capacity, word_bits + 4, word_bits + 10, word_bits + 4);
    try expectCursorMirror(frontier_words[0..], capacity, word_bits * 2 + 1, word_bits * 2 + 23, word_bits * 2 + 1);
    try expectCursorMirror(frontier_words[0..], capacity, word_bits * 3, word_bits * 3 + 18, word_bits * 3);
    try expectCursorMirror(frontier_words[0..], capacity, capacity, null, null);

    const bitmap = BitmapView.init(frontier_words[0..], capacity);
    const cpumask = CpuMaskView.init(frontier_words[0..], capacity);

    try std.testing.expect(cpumask.hasCpu(word_bits * 3 + 18));
    try std.testing.expect(!cpumask.hasCpu(word_bits * 3 + 17));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(word_bits * 3 + 19));
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextCpu(word_bits * 3 + 19));
}

test "phase3 bitmap cpumask rolling frontier prunes while preserving relations" {
    const capacity = word_bits * 3 + 19;
    const narrow_words = [_]Word{
        bit(5) | bit(10),
        bit(10),
        bit(23),
        bit(18) | bit(41),
    };
    const frontier_words = [_]Word{
        lowMask(11),
        lowMask(4) | bit(10),
        bit(0) | bit(23),
        bit(18) | bit(40),
    };
    const expanded_words = [_]Word{
        frontier_words[0] | bit(18) | bit(31),
        frontier_words[1] | bit(17) | bit(word_bits - 1),
        frontier_words[2] | bit(12) | bit(35),
        frontier_words[3] | bit(3) | bit(11) | bit(57),
    };

    try expectMirrors(narrow_words[0..], capacity, 5, 5, 0);
    try expectMirrors(frontier_words[0..], capacity, 19, 0, 11);
    try expectMirrors(expanded_words[0..], capacity, 27, 0, 11);

    const narrow_bitmap = BitmapView.init(narrow_words[0..], capacity);
    const frontier_bitmap = BitmapView.init(frontier_words[0..], capacity);
    const expanded_bitmap = BitmapView.init(expanded_words[0..], capacity);
    const narrow_cpumask = CpuMaskView.init(narrow_words[0..], capacity);
    const frontier_cpumask = CpuMaskView.init(frontier_words[0..], capacity);
    const expanded_cpumask = CpuMaskView.init(expanded_words[0..], capacity);

    try std.testing.expect(narrow_bitmap.isSubsetOf(frontier_bitmap));
    try std.testing.expect(narrow_cpumask.isSubsetOf(frontier_cpumask));
    try std.testing.expect(frontier_bitmap.isSubsetOf(expanded_bitmap));
    try std.testing.expect(frontier_cpumask.isSubsetOf(expanded_cpumask));
    try std.testing.expect(!expanded_bitmap.isSubsetOf(frontier_bitmap));
    try std.testing.expect(!expanded_cpumask.isSubsetOf(frontier_cpumask));
    try std.testing.expect(narrow_bitmap.intersects(expanded_bitmap));
    try std.testing.expect(narrow_cpumask.intersects(expanded_cpumask));

    try expectCursorMirror(narrow_words[0..], capacity, 0, 5, 0);
    try expectCursorMirror(narrow_words[0..], capacity, 6, 10, 6);
    try expectCursorMirror(expanded_words[0..], capacity, word_bits + 18, word_bits + word_bits - 1, word_bits + 18);
    try expectCursorMirror(expanded_words[0..], capacity, word_bits * 3 + 4, word_bits * 3 + 11, word_bits * 3 + 4);
    try expectCursorMirror(expanded_words[0..], capacity, word_bits * 3 + 19, null, null);
}
