const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const word_count = 3;
const capacity = word_bits * 2 + 9;

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
    return ~((@as(Word, 1) << 9) - 1);
}

fn subtractWords(base: [word_count]Word, remove: [word_count]Word) [word_count]Word {
    var result: [word_count]Word = undefined;
    for (0..word_count) |index| {
        result[index] = base[index] & ~remove[index];
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

test "bitmap and cpumask agree after subtracting shared cpu bits" {
    var requested = [_]Word{ 0, 0, tailNoise() };
    var excluded = [_]Word{ 0, 0, tailNoise() };

    for ([_]usize{ 0, 5, word_bits - 1, word_bits, word_bits + 6, word_bits * 2 + 2, word_bits * 2 + 8 }) |bit| {
        setBit(&requested, bit);
    }
    for ([_]usize{ 5, word_bits, word_bits * 2 + 8 }) |bit| {
        setBit(&excluded, bit);
    }

    const routable_words = subtractWords(requested, excluded);
    const requested_bitmap = bitmap_view.BitmapView.init(requested[0..], capacity);
    const excluded_bitmap = bitmap_view.BitmapView.init(excluded[0..], capacity);
    const routable_bitmap = bitmap_view.BitmapView.init(routable_words[0..], capacity);
    const routable_mask = cpumask_view.CpuMaskView.init(routable_words[0..], capacity);

    try expectMirroredView(routable_words[0..], 4, 0, 1);
    try testing.expect(routable_bitmap.isSubsetOf(requested_bitmap));
    try testing.expect(!routable_bitmap.intersects(excluded_bitmap));
    try testing.expectEqual(@as(?usize, word_bits - 1), routable_bitmap.nextSetBit(1));
    try testing.expectEqual(@as(?usize, word_bits - 1), routable_mask.nextCpu(1));
    try testing.expectEqual(@as(?usize, word_bits), routable_bitmap.nextClearBit(word_bits));
    try testing.expectEqual(@as(?usize, word_bits), routable_mask.nextMissingCpu(word_bits));
    try testing.expect(!routable_bitmap.isSet(word_bits * 2 + 8));
    try testing.expect(!routable_mask.hasCpu(word_bits * 2 + 8));
}

test "difference mirrors recompute after subtractive mask mutation" {
    var requested = [_]Word{ 0, 0, tailNoise() };
    var denied = [_]Word{ 0, 0, tailNoise() };

    for ([_]usize{ 2, 7, word_bits + 1, word_bits + 4, word_bits * 2 + 1, word_bits * 2 + 7 }) |bit| {
        setBit(&requested, bit);
    }
    for ([_]usize{ 7, word_bits * 2 + 7 }) |bit| {
        setBit(&denied, bit);
    }

    var available_words = subtractWords(requested, denied);
    try expectMirroredView(available_words[0..], 4, 2, 0);

    setBit(&denied, word_bits + 1);
    available_words = subtractWords(requested, denied);
    const available_after_deny = bitmap_view.BitmapView.init(available_words[0..], capacity);
    const denied_after_set = cpumask_view.CpuMaskView.init(denied[0..], capacity);

    try expectMirroredView(available_words[0..], 3, 2, 0);
    try testing.expect(!available_after_deny.intersects(denied_after_set.bitmap));
    try testing.expectEqual(@as(?usize, word_bits + 4), available_after_deny.nextSetBit(word_bits + 1));

    clearBit(&denied, 7);
    available_words = subtractWords(requested, denied);
    const available_after_clear = cpumask_view.CpuMaskView.init(available_words[0..], capacity);

    try expectMirroredView(available_words[0..], 4, 2, 0);
    try testing.expect(available_after_clear.hasCpu(7));
    try testing.expectEqual(@as(?usize, 7), available_after_clear.nextCpu(3));
    try testing.expectEqual(@as(?usize, word_bits + 1), available_after_clear.nextMissingCpu(word_bits + 1));
}
