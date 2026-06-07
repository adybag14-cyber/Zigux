const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn setBit(words: []Word, index: usize) void {
    words[index / word_bits] |= @as(Word, 1) << @as(std.math.Log2Int(Word), @intCast(index % word_bits));
}

fn setRange(words: []Word, start: usize, end_inclusive: usize) void {
    for (start..end_inclusive + 1) |index| {
        setBit(words, index);
    }
}

test "bitmap cpumask checkerboard lanes compress into a dense bridge" {
    const capacity = word_bits * 3 + 11;
    const tail_noise = ~@as(Word, 0) << @as(std.math.Log2Int(Word), @intCast(11));

    var checker_words = [_]Word{0} ** 4;
    var dense_words = [_]Word{0} ** 4;
    var envelope_words = [_]Word{0} ** 4;

    var index: usize = 0;
    while (index < capacity) : (index += 2) {
        setBit(checker_words[0..], index);
        setBit(envelope_words[0..], index);
    }

    setRange(dense_words[0..], word_bits - 3, word_bits + 5);
    setBit(dense_words[0..], capacity - 1);
    setRange(envelope_words[0..], word_bits - 3, word_bits + 5);
    setBit(envelope_words[0..], capacity - 1);
    checker_words[3] |= tail_noise;
    dense_words[3] |= tail_noise;
    envelope_words[3] |= tail_noise;

    const checker_bitmap = bitmap_view.BitmapView.init(checker_words[0..], capacity);
    const checker_mask = cpumask_view.CpuMaskView.init(checker_words[0..], capacity);
    const dense_bitmap = bitmap_view.BitmapView.init(dense_words[0..], capacity);
    const dense_mask = cpumask_view.CpuMaskView.init(dense_words[0..], capacity);
    const envelope_bitmap = bitmap_view.BitmapView.init(envelope_words[0..], capacity);
    const envelope_mask = cpumask_view.CpuMaskView.init(envelope_words[0..], capacity);

    try testing.expectEqual(checker_bitmap.countSetBits(), checker_mask.countPresentCpus());
    try testing.expectEqual(dense_bitmap.countSetBits(), dense_mask.countPresentCpus());
    try testing.expectEqual(envelope_bitmap.countSetBits(), envelope_mask.countPresentCpus());
    try testing.expectEqual(@as(usize, (capacity + 1) / 2), checker_mask.countPresentCpus());
    try testing.expectEqual(@as(usize, 10), dense_mask.countPresentCpus());
    try testing.expectEqual(@as(usize, ((capacity + 1) / 2) + 5), envelope_mask.countPresentCpus());

    try testing.expect(checker_bitmap.isSubsetOf(envelope_bitmap));
    try testing.expect(checker_mask.isSubsetOf(envelope_mask));
    try testing.expect(dense_bitmap.isSubsetOf(envelope_bitmap));
    try testing.expect(dense_mask.isSubsetOf(envelope_mask));
    try testing.expect(checker_bitmap.intersects(dense_bitmap));
    try testing.expect(checker_mask.intersects(dense_mask));
    try testing.expect(!envelope_bitmap.isSubsetOf(checker_bitmap));
    try testing.expect(!envelope_mask.isSubsetOf(checker_mask));

    try testing.expectEqual(@as(?usize, 0), checker_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), checker_mask.firstCpu());
    try testing.expectEqual(@as(?usize, 1), checker_bitmap.firstClearBit());
    try testing.expectEqual(@as(?usize, 1), checker_mask.firstMissingCpu());
    try testing.expectEqual(@as(?usize, word_bits - 3), dense_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, word_bits - 3), dense_mask.firstCpu());
    try testing.expectEqual(@as(?usize, word_bits + 6), dense_bitmap.nextClearBit(word_bits + 6));
    try testing.expectEqual(@as(?usize, word_bits + 6), dense_mask.nextMissingCpu(word_bits + 6));
    try testing.expect(!checker_mask.hasCpu(capacity - 2));
}

test "bitmap cpumask checkerboard compression preserves split-lane gaps" {
    const capacity = word_bits * 2 + 7;
    const tail_noise = ~@as(Word, 0) << @as(std.math.Log2Int(Word), @intCast(7));

    var left_lane_words = [_]Word{0} ** 3;
    var right_lane_words = [_]Word{0} ** 3;
    var joined_words = [_]Word{0} ** 3;

    const anchors = [_]usize{
        2,
        4,
        word_bits - 5,
        word_bits - 1,
        word_bits,
        word_bits + 4,
        word_bits * 2 + 1,
        word_bits * 2 + 6,
    };
    const bridge = word_bits + 2;

    for (anchors, 0..) |cpu, anchor_index| {
        if (anchor_index % 2 == 0) {
            setBit(left_lane_words[0..], cpu);
        } else {
            setBit(right_lane_words[0..], cpu);
        }
        setBit(joined_words[0..], cpu);
    }
    setBit(joined_words[0..], bridge);
    left_lane_words[2] |= tail_noise;
    right_lane_words[2] |= tail_noise;
    joined_words[2] |= tail_noise;

    const left_bitmap = bitmap_view.BitmapView.init(left_lane_words[0..], capacity);
    const left_mask = cpumask_view.CpuMaskView.init(left_lane_words[0..], capacity);
    const right_bitmap = bitmap_view.BitmapView.init(right_lane_words[0..], capacity);
    const right_mask = cpumask_view.CpuMaskView.init(right_lane_words[0..], capacity);
    const joined_bitmap = bitmap_view.BitmapView.init(joined_words[0..], capacity);
    const joined_mask = cpumask_view.CpuMaskView.init(joined_words[0..], capacity);

    try testing.expectEqual(@as(usize, 4), left_bitmap.countSetBits());
    try testing.expectEqual(left_bitmap.countSetBits(), left_mask.countPresentCpus());
    try testing.expectEqual(@as(usize, 4), right_mask.countPresentCpus());
    try testing.expectEqual(@as(usize, 9), joined_mask.countPresentCpus());

    try testing.expect(left_bitmap.isSubsetOf(joined_bitmap));
    try testing.expect(left_mask.isSubsetOf(joined_mask));
    try testing.expect(right_bitmap.isSubsetOf(joined_bitmap));
    try testing.expect(right_mask.isSubsetOf(joined_mask));
    try testing.expect(!left_bitmap.intersects(right_bitmap));
    try testing.expect(!left_mask.intersects(right_mask));
    try testing.expect(joined_bitmap.intersects(left_bitmap));
    try testing.expect(joined_mask.intersects(right_mask));

    try testing.expectEqual(@as(?usize, 2), left_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 2), left_mask.firstCpu());
    try testing.expectEqual(@as(?usize, 4), right_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 4), right_mask.firstCpu());
    try testing.expectEqual(@as(?usize, bridge), joined_bitmap.nextSetBit(word_bits + 1));
    try testing.expectEqual(@as(?usize, bridge), joined_mask.nextCpu(word_bits + 1));
    try testing.expectEqual(@as(?usize, bridge + 1), joined_bitmap.nextClearBit(bridge + 1));
    try testing.expectEqual(@as(?usize, bridge + 1), joined_mask.nextMissingCpu(bridge + 1));
    try testing.expect(!joined_mask.hasCpu(capacity - 2));
}
