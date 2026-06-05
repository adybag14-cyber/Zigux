const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const empty_bank_count = 101;
const first_word_index = 0;
const tail_word_index = first_word_index + empty_bank_count + 1;
const word_count = tail_word_index + 1;
const tail_valid_bits = 14;
const bit_len = tail_word_index * word_bits + tail_valid_bits;
const first_bit = 7;
const tail_base = tail_word_index * word_bits;
const tail_a = tail_base + 2;
const tail_b = tail_base + 9;
const tail_c = tail_base + 13;

fn localBit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn fixtureWords() [word_count]Word {
    var words = std.mem.zeroes([word_count]Word);
    words[0] = localBit(first_bit);
    words[tail_word_index] =
        localBit(tail_a) |
        localBit(tail_b) |
        localBit(tail_c) |
        localBit(tail_base + tail_valid_bits) |
        localBit(tail_base + tail_valid_bits + 7);
    return words;
}

fn supersetWords() [word_count]Word {
    var words = fixtureWords();
    words[tail_word_index] |= localBit(tail_base + 4);
    return words;
}

fn disjointWords() [word_count]Word {
    var words = std.mem.zeroes([word_count]Word);
    words[0] = localBit(first_bit + 1);
    words[tail_word_index] =
        localBit(tail_base + 5) |
        localBit(tail_base + tail_valid_bits) |
        localBit(tail_base + tail_valid_bits + 11);
    return words;
}

test "bitmap view crosses centumunum empty banks before masked tail" {
    const words = fixtureWords();
    const view = bitmap_view.BitmapView.init(words[0..], bit_len);

    try std.testing.expectEqual(@as(usize, word_count), view.activeWordLen());
    try std.testing.expectEqual(@as(usize, 4), view.countSetBits());
    try std.testing.expectEqual(@as(?usize, first_bit), view.firstSetBit());
    try std.testing.expectEqual(@as(?usize, tail_a), view.nextSetBit(first_bit + 1));
    try std.testing.expectEqual(@as(?usize, tail_b), view.nextSetBit(tail_a + 1));
    try std.testing.expectEqual(@as(?usize, tail_c), view.nextSetBit(tail_b + 1));
    try std.testing.expectEqual(@as(?usize, null), view.nextSetBit(tail_c + 1));

    try std.testing.expectEqual(@as(?usize, first_bit + 1), view.nextClearBit(first_bit + 1));
    try std.testing.expectEqual(@as(?usize, tail_a + 1), view.nextClearBit(tail_a + 1));
    try std.testing.expectEqual(@as(?usize, null), view.nextClearBit(bit_len));
}

test "cpumask view mirrors bitmap traversal across centumunum empty banks" {
    const words = fixtureWords();
    const mask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try std.testing.expect(mask.hasCpu(first_bit));
    try std.testing.expect(mask.hasCpu(tail_c));
    try std.testing.expect(!mask.hasCpu(tail_base + 4));
    try std.testing.expectEqual(@as(usize, 4), mask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, first_bit), mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, tail_a), mask.nextCpu(first_bit + 1));
    try std.testing.expectEqual(@as(?usize, tail_b), mask.nextCpu(tail_a + 1));
    try std.testing.expectEqual(@as(?usize, tail_c), mask.nextCpu(tail_b + 1));
    try std.testing.expectEqual(@as(?usize, null), mask.nextCpu(tail_c + 1));
    try std.testing.expectEqual(@as(?usize, first_bit + 1), mask.nextMissingCpu(first_bit + 1));
}

test "bitmap and cpumask masks ignore centumunum tail noise in relations" {
    const base_words = fixtureWords();
    const superset_words = supersetWords();
    const disjoint_words = disjointWords();

    const base = bitmap_view.BitmapView.init(base_words[0..], bit_len);
    const superset = bitmap_view.BitmapView.init(superset_words[0..], bit_len);
    const disjoint = bitmap_view.BitmapView.init(disjoint_words[0..], bit_len);

    try std.testing.expect(base.isSubsetOf(superset));
    try std.testing.expect(!superset.isSubsetOf(base));
    try std.testing.expect(base.intersects(superset));
    try std.testing.expect(!base.intersects(disjoint));

    const base_mask = cpumask_view.CpuMaskView.init(base_words[0..], bit_len);
    const superset_mask = cpumask_view.CpuMaskView.init(superset_words[0..], bit_len);
    const disjoint_mask = cpumask_view.CpuMaskView.init(disjoint_words[0..], bit_len);

    try std.testing.expect(base_mask.isSubsetOf(superset_mask));
    try std.testing.expect(!superset_mask.isSubsetOf(base_mask));
    try std.testing.expect(base_mask.intersects(superset_mask));
    try std.testing.expect(!base_mask.intersects(disjoint_mask));
}
