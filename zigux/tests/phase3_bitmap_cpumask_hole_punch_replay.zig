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

test "phase3 bitmap cpumask hole punch exposes matching gaps" {
    const capacity = word_bits * 2 + 23;
    const dense_words = [_]Word{
        std.math.maxInt(Word),
        std.math.maxInt(Word),
        lowMask(23) | bit(57),
    };
    const punched_words = [_]Word{
        std.math.maxInt(Word) & ~bit(0) & ~bit(9) & ~bit(word_bits - 1),
        std.math.maxInt(Word) & ~bit(3) & ~bit(22) & ~bit(word_bits - 2),
        (lowMask(23) & ~bit(4) & ~bit(17) & ~bit(22)) | bit(57),
    };

    try expectMirrors(dense_words[0..], capacity, capacity, 0, null);
    try expectMirrors(punched_words[0..], capacity, capacity - 9, 1, 0);
    try expectCursorMirror(punched_words[0..], capacity, 0, 1, 0);
    try expectCursorMirror(punched_words[0..], capacity, 9, 10, 9);
    try expectCursorMirror(punched_words[0..], capacity, word_bits - 1, word_bits, word_bits - 1);
    try expectCursorMirror(punched_words[0..], capacity, word_bits + 3, word_bits + 4, word_bits + 3);
    try expectCursorMirror(punched_words[0..], capacity, word_bits * 2 + 4, word_bits * 2 + 5, word_bits * 2 + 4);
    try expectCursorMirror(punched_words[0..], capacity, word_bits * 2 + 23, null, null);

    const punched_bitmap = BitmapView.init(punched_words[0..], capacity);
    const dense_bitmap = BitmapView.init(dense_words[0..], capacity);
    const punched_cpumask = CpuMaskView.init(punched_words[0..], capacity);
    const dense_cpumask = CpuMaskView.init(dense_words[0..], capacity);

    try std.testing.expect(punched_bitmap.isSubsetOf(dense_bitmap));
    try std.testing.expect(punched_cpumask.isSubsetOf(dense_cpumask));
    try std.testing.expect(!dense_bitmap.isSubsetOf(punched_bitmap));
    try std.testing.expect(!dense_cpumask.isSubsetOf(punched_cpumask));
    try std.testing.expect(punched_bitmap.intersects(dense_bitmap));
    try std.testing.expect(punched_cpumask.intersects(dense_cpumask));
    try std.testing.expect(!punched_cpumask.hasCpu(0));
    try std.testing.expect(!punched_cpumask.hasCpu(word_bits * 2 + 22));
}

test "phase3 bitmap cpumask hole punch refill preserves declared tail masking" {
    const capacity = word_bits * 2 + 23;
    const punched_words = [_]Word{
        std.math.maxInt(Word) & ~bit(0) & ~bit(9) & ~bit(word_bits - 1),
        std.math.maxInt(Word) & ~bit(3) & ~bit(22) & ~bit(word_bits - 2),
        (lowMask(23) & ~bit(4) & ~bit(17) & ~bit(22)) | bit(57),
    };
    const refilled_words = [_]Word{
        punched_words[0] | bit(0) | bit(9),
        punched_words[1] | bit(3) | bit(22),
        punched_words[2] | bit(4) | bit(22) | bit(51),
    };
    const narrow_words = [_]Word{
        bit(9),
        bit(22),
        bit(4) | bit(57),
    };

    try expectMirrors(refilled_words[0..], capacity, capacity - 3, 0, word_bits - 1);
    try expectMirrors(narrow_words[0..], capacity, 3, 9, 0);
    try expectCursorMirror(refilled_words[0..], capacity, word_bits - 1, word_bits, word_bits - 1);
    try expectCursorMirror(refilled_words[0..], capacity, word_bits * 2 + 17, word_bits * 2 + 18, word_bits * 2 + 17);
    try expectCursorMirror(refilled_words[0..], capacity, word_bits * 2 + 22, word_bits * 2 + 22, null);
    try expectCursorMirror(refilled_words[0..], capacity, capacity, null, null);

    const narrow_bitmap = BitmapView.init(narrow_words[0..], capacity);
    const refilled_bitmap = BitmapView.init(refilled_words[0..], capacity);
    const punched_bitmap = BitmapView.init(punched_words[0..], capacity);
    const narrow_cpumask = CpuMaskView.init(narrow_words[0..], capacity);
    const refilled_cpumask = CpuMaskView.init(refilled_words[0..], capacity);
    const punched_cpumask = CpuMaskView.init(punched_words[0..], capacity);

    try std.testing.expect(narrow_bitmap.isSubsetOf(refilled_bitmap));
    try std.testing.expect(narrow_cpumask.isSubsetOf(refilled_cpumask));
    try std.testing.expect(punched_bitmap.isSubsetOf(refilled_bitmap));
    try std.testing.expect(punched_cpumask.isSubsetOf(refilled_cpumask));
    try std.testing.expect(!refilled_bitmap.isSubsetOf(punched_bitmap));
    try std.testing.expect(!refilled_cpumask.isSubsetOf(punched_cpumask));
    try std.testing.expect(!narrow_bitmap.intersects(punched_bitmap));
    try std.testing.expect(!narrow_cpumask.intersects(punched_cpumask));
    try std.testing.expect(narrow_bitmap.intersects(refilled_bitmap));
    try std.testing.expect(narrow_cpumask.intersects(refilled_cpumask));
}
