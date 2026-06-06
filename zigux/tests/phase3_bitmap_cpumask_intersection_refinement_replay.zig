const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const word_count = 3;
const capacity = word_bits * 2 + 13;

fn bitMask(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn setBit(words: *[word_count]Word, bit_index: usize) void {
    words[bit_index / word_bits] |= bitMask(bit_index);
}

fn clearBit(words: *[word_count]Word, bit_index: usize) void {
    words[bit_index / word_bits] &= ~bitMask(bit_index);
}

fn tailNoise() Word {
    return ~((@as(Word, 1) << 13) - 1);
}

fn intersectWords(left: [word_count]Word, right: [word_count]Word) [word_count]Word {
    var result: [word_count]Word = undefined;
    for (0..word_count) |index| {
        result[index] = left[index] & right[index];
    }
    return result;
}

fn expectMirroredView(words: []const Word, expected_count: usize, first_set: ?usize, first_clear: ?usize) !void {
    const bitmap = bitmap_view.BitmapView.init(words, capacity);
    const mask = cpumask_view.CpuMaskView.init(words, capacity);

    try testing.expectEqual(expected_count, bitmap.countSetBits());
    try testing.expectEqual(expected_count, mask.countPresentCpus());
    try testing.expectEqual(first_set, bitmap.firstSetBit());
    try testing.expectEqual(first_set, mask.firstCpu());
    try testing.expectEqual(first_clear, bitmap.firstClearBit());
    try testing.expectEqual(first_clear, mask.firstMissingCpu());
}

test "bitmap and cpumask agree across intersection-refined masks" {
    var runnable = [_]Word{ 0, 0, tailNoise() };
    var allowed = [_]Word{ 0, 0, tailNoise() };

    for ([_]usize{ 1, 4, word_bits - 2, word_bits + 3, word_bits + 11, word_bits * 2 + 1, word_bits * 2 + 12 }) |bit| {
        setBit(&runnable, bit);
    }
    for ([_]usize{ 0, 4, word_bits - 2, word_bits + 5, word_bits + 11, word_bits * 2 + 1, word_bits * 2 + 8 }) |bit| {
        setBit(&allowed, bit);
    }

    const shared_words = intersectWords(runnable, allowed);
    const runnable_bitmap = bitmap_view.BitmapView.init(runnable[0..], capacity);
    const allowed_bitmap = bitmap_view.BitmapView.init(allowed[0..], capacity);
    const shared_bitmap = bitmap_view.BitmapView.init(shared_words[0..], capacity);
    const shared_mask = cpumask_view.CpuMaskView.init(shared_words[0..], capacity);

    try expectMirroredView(shared_words[0..], 4, 4, 0);
    try testing.expect(shared_bitmap.isSubsetOf(runnable_bitmap));
    try testing.expect(shared_bitmap.isSubsetOf(allowed_bitmap));
    try testing.expect(runnable_bitmap.intersects(allowed_bitmap));
    try testing.expect(shared_mask.isSubsetOf(cpumask_view.CpuMaskView.init(runnable[0..], capacity)));
    try testing.expect(shared_mask.isSubsetOf(cpumask_view.CpuMaskView.init(allowed[0..], capacity)));
    try testing.expectEqual(@as(?usize, word_bits - 2), shared_bitmap.nextSetBit(5));
    try testing.expectEqual(@as(?usize, word_bits - 2), shared_mask.nextCpu(5));
    try testing.expectEqual(@as(?usize, word_bits + 12), shared_bitmap.nextClearBit(word_bits + 12));
    try testing.expectEqual(@as(?usize, word_bits + 12), shared_mask.nextMissingCpu(word_bits + 12));
    try testing.expect(shared_bitmap.isSet(word_bits * 2 + 1));
    try testing.expect(shared_mask.hasCpu(word_bits * 2 + 1));
}

test "intersection refinement mirrors shrink and expand after mutations" {
    var active = [_]Word{ 0, 0, tailNoise() };
    var candidate = [_]Word{ 0, 0, tailNoise() };

    for ([_]usize{ 2, 6, word_bits + 1, word_bits + 7, word_bits * 2 + 3, word_bits * 2 + 10 }) |bit| {
        setBit(&active, bit);
    }
    for ([_]usize{ 6, 9, word_bits + 7, word_bits + 9, word_bits * 2 + 3 }) |bit| {
        setBit(&candidate, bit);
    }

    var shared_words = intersectWords(active, candidate);
    try expectMirroredView(shared_words[0..], 3, 6, 0);

    clearBit(&candidate, word_bits + 7);
    shared_words = intersectWords(active, candidate);
    const narrowed_bitmap = bitmap_view.BitmapView.init(shared_words[0..], capacity);
    const narrowed_mask = cpumask_view.CpuMaskView.init(shared_words[0..], capacity);

    try expectMirroredView(shared_words[0..], 2, 6, 0);
    try testing.expect(!narrowed_bitmap.isSet(word_bits + 7));
    try testing.expect(!narrowed_mask.hasCpu(word_bits + 7));
    try testing.expectEqual(@as(?usize, word_bits * 2 + 3), narrowed_mask.nextCpu(word_bits + 8));

    setBit(&candidate, word_bits * 2 + 10);
    shared_words = intersectWords(active, candidate);
    const expanded_bitmap = bitmap_view.BitmapView.init(shared_words[0..], capacity);
    const expanded_mask = cpumask_view.CpuMaskView.init(shared_words[0..], capacity);

    try expectMirroredView(shared_words[0..], 3, 6, 0);
    try testing.expect(expanded_bitmap.isSet(word_bits * 2 + 10));
    try testing.expect(expanded_mask.hasCpu(word_bits * 2 + 10));
    try testing.expectEqual(@as(?usize, word_bits * 2 + 10), expanded_bitmap.nextSetBit(word_bits * 2 + 4));

    clearBit(&active, 6);
    shared_words = intersectWords(active, candidate);
    const final_mask = cpumask_view.CpuMaskView.init(shared_words[0..], capacity);

    try expectMirroredView(shared_words[0..], 2, word_bits * 2 + 3, 0);
    try testing.expect(!final_mask.hasCpu(6));
    try testing.expectEqual(@as(?usize, 6), final_mask.nextMissingCpu(6));
}
