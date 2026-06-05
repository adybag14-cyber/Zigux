const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const empty_banks: usize = 100;
const tail_word_index: usize = empty_banks + 1;
const word_count: usize = tail_word_index + 1;
const tail_bits: usize = 11;
const bit_len: usize = tail_word_index * word_bits + tail_bits;
const lead_bit: usize = 2;
const tail_bit: usize = tail_word_index * word_bits + 5;

fn bit(offset: usize) Word {
    return @as(Word, 1) << @intCast(offset % word_bits);
}

fn tailNoise() Word {
    const valid_tail_mask = (@as(Word, 1) << @intCast(tail_bits)) - 1;
    return ~valid_tail_mask;
}

fn novemdecemoogintupleWords() [word_count]Word {
    var words = [_]Word{0} ** word_count;
    words[0] = bit(lead_bit);
    words[tail_word_index] = bit(5) | tailNoise();
    return words;
}

test "novemdecemoogintuple trailing empty banks keep bitmap and cpumask traversal aligned" {
    const words = novemdecemoogintupleWords();
    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try std.testing.expectEqual(@as(usize, word_count), bitmap.activeWordLen());
    try std.testing.expectEqual(@as(usize, 2), bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 2), cpumask.countPresentCpus());

    try std.testing.expect(bitmap.isSet(lead_bit));
    try std.testing.expect(cpumask.hasCpu(lead_bit));
    try std.testing.expect(bitmap.isSet(tail_bit));
    try std.testing.expect(cpumask.hasCpu(tail_bit));

    try std.testing.expectEqual(@as(?usize, lead_bit), bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, lead_bit), cpumask.firstCpu());
    try std.testing.expectEqual(@as(?usize, tail_bit), bitmap.nextSetBit(lead_bit + 1));
    try std.testing.expectEqual(@as(?usize, tail_bit), cpumask.nextCpu(lead_bit + 1));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(tail_bit + 1));
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextCpu(tail_bit + 1));

    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), cpumask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, tail_word_index * word_bits), bitmap.nextClearBit(tail_word_index * word_bits));
    try std.testing.expectEqual(@as(?usize, tail_word_index * word_bits), cpumask.nextMissingCpu(tail_word_index * word_bits));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextClearBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextMissingCpu(bit_len));
}

test "novemdecemoogintuple trailing empty banks keep subset and overlap tail bounded" {
    const base_words = novemdecemoogintupleWords();

    var superset_words = [_]Word{0} ** word_count;
    superset_words[0] = bit(lead_bit) | bit(lead_bit + 3);
    superset_words[tail_word_index] = bit(5) | bit(7);

    var disjoint_words = [_]Word{0} ** word_count;
    disjoint_words[0] = bit(lead_bit + 1);
    disjoint_words[tail_word_index] = bit(6);

    var tail_noise_words = [_]Word{0} ** word_count;
    tail_noise_words[tail_word_index] = tailNoise();

    const base_bitmap = bitmap_view.BitmapView.init(base_words[0..], bit_len);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], bit_len);
    const disjoint_bitmap = bitmap_view.BitmapView.init(disjoint_words[0..], bit_len);
    const tail_noise_bitmap = bitmap_view.BitmapView.init(tail_noise_words[0..], bit_len);

    const base_mask = cpumask_view.CpuMaskView.init(base_words[0..], bit_len);
    const superset_mask = cpumask_view.CpuMaskView.init(superset_words[0..], bit_len);
    const disjoint_mask = cpumask_view.CpuMaskView.init(disjoint_words[0..], bit_len);
    const tail_noise_mask = cpumask_view.CpuMaskView.init(tail_noise_words[0..], bit_len);

    try std.testing.expect(base_bitmap.isSubsetOf(superset_bitmap));
    try std.testing.expect(base_mask.isSubsetOf(superset_mask));
    try std.testing.expect(!superset_bitmap.isSubsetOf(base_bitmap));
    try std.testing.expect(!superset_mask.isSubsetOf(base_mask));

    try std.testing.expect(base_bitmap.intersects(superset_bitmap));
    try std.testing.expect(base_mask.intersects(superset_mask));
    try std.testing.expect(!base_bitmap.intersects(disjoint_bitmap));
    try std.testing.expect(!base_mask.intersects(disjoint_mask));
    try std.testing.expect(!base_bitmap.intersects(tail_noise_bitmap));
    try std.testing.expect(!base_mask.intersects(tail_noise_mask));
    try std.testing.expectEqual(@as(usize, 0), tail_noise_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 0), tail_noise_mask.countPresentCpus());
}
