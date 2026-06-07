const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const word_count = 3;
const capacity = word_bits * word_count - 11;

fn bitMask(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn setBit(words: *[word_count]Word, bit_index: usize) void {
    std.debug.assert(bit_index < capacity);
    words[bit_index / word_bits] |= bitMask(bit_index);
}

fn fillBits(comptime bits: []const usize) [word_count]Word {
    var words = [_]Word{0} ** word_count;
    inline for (bits) |bit| {
        setBit(&words, bit);
    }
    return words;
}

fn withTailNoise(words: [word_count]Word) [word_count]Word {
    var noisy = words;
    const first_tail_bit = capacity % word_bits;
    if (first_tail_bit != 0) {
        noisy[word_count - 1] |= (~@as(Word, 0)) << @intCast(first_tail_bit);
    }
    return noisy;
}

fn expectBitmapCpuMaskMirror(words: [word_count]Word) !void {
    const bitmap = BitmapView.init(words[0..], capacity);
    const cpumask = CpuMaskView.init(words[0..], capacity);

    try std.testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try std.testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    var cursor: usize = 0;
    while (cursor < capacity) : (cursor += 7) {
        try std.testing.expectEqual(bitmap.nextSetBit(cursor), cpumask.nextCpu(cursor));
        try std.testing.expectEqual(bitmap.nextClearBit(cursor), cpumask.nextMissingCpu(cursor));
    }

    for (0..capacity) |cpu| {
        try std.testing.expectEqual(bitmap.isSet(cpu), cpumask.hasCpu(cpu));
    }
}

test "phase3 bitmap cpumask radial windows preserve mirrored cursors" {
    const radial_bits = [_]usize{
        3,
        11,
        word_bits - 9,
        word_bits - 1,
        word_bits,
        word_bits + 6,
        word_bits + 19,
        word_bits * 2 - 4,
        word_bits * 2,
        word_bits * 2 + 17,
        capacity - 1,
    };
    const bridge_bits = [_]usize{
        word_bits - 1,
        word_bits,
        word_bits + 6,
        word_bits * 2,
    };
    const disjoint_bits = [_]usize{
        24,
        word_bits + 33,
        word_bits * 2 + 9,
    };

    const radial_words = withTailNoise(fillBits(radial_bits[0..]));
    const bridge_words = withTailNoise(fillBits(bridge_bits[0..]));
    const disjoint_words = withTailNoise(fillBits(disjoint_bits[0..]));

    try expectBitmapCpuMaskMirror(radial_words);

    const radial_bitmap = BitmapView.init(radial_words[0..], capacity);
    const bridge_bitmap = BitmapView.init(bridge_words[0..], capacity);
    const disjoint_bitmap = BitmapView.init(disjoint_words[0..], capacity);
    const radial_mask = CpuMaskView.init(radial_words[0..], capacity);
    const bridge_mask = CpuMaskView.init(bridge_words[0..], capacity);
    const disjoint_mask = CpuMaskView.init(disjoint_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, radial_bits.len), radial_bitmap.countSetBits());
    try std.testing.expectEqual(@as(?usize, 3), radial_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits - 9), radial_mask.nextCpu(12));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), radial_mask.nextMissingCpu(word_bits + 1));
    try std.testing.expectEqual(@as(?usize, capacity - 1), radial_bitmap.nextSetBit(capacity - 4));
    try std.testing.expectEqual(@as(?usize, null), radial_mask.nextCpu(capacity));

    try std.testing.expect(bridge_bitmap.isSubsetOf(radial_bitmap));
    try std.testing.expect(bridge_mask.isSubsetOf(radial_mask));
    try std.testing.expect(!radial_bitmap.isSubsetOf(bridge_bitmap));
    try std.testing.expect(!radial_mask.isSubsetOf(bridge_mask));
    try std.testing.expect(!radial_bitmap.intersects(disjoint_bitmap));
    try std.testing.expect(!radial_mask.intersects(disjoint_mask));
}

test "phase3 bitmap cpumask radial contraction and refill stay bounded" {
    const outer_bits = [_]usize{
        2,
        18,
        word_bits - 3,
        word_bits + 2,
        word_bits + 31,
        word_bits * 2 - 2,
        word_bits * 2 + 5,
        capacity - 2,
    };
    const core_bits = [_]usize{
        word_bits - 3,
        word_bits + 2,
        word_bits + 31,
    };
    const refill_bits = [_]usize{
        2,
        word_bits - 3,
        word_bits + 2,
        word_bits + 31,
        word_bits * 2 - 2,
        capacity - 2,
    };

    const outer_words = withTailNoise(fillBits(outer_bits[0..]));
    const core_words = withTailNoise(fillBits(core_bits[0..]));
    const refill_words = withTailNoise(fillBits(refill_bits[0..]));

    try expectBitmapCpuMaskMirror(outer_words);
    try expectBitmapCpuMaskMirror(core_words);
    try expectBitmapCpuMaskMirror(refill_words);

    const outer_bitmap = BitmapView.init(outer_words[0..], capacity);
    const core_bitmap = BitmapView.init(core_words[0..], capacity);
    const refill_bitmap = BitmapView.init(refill_words[0..], capacity);
    const outer_mask = CpuMaskView.init(outer_words[0..], capacity);
    const core_mask = CpuMaskView.init(core_words[0..], capacity);
    const refill_mask = CpuMaskView.init(refill_words[0..], capacity);

    try std.testing.expect(core_bitmap.isSubsetOf(outer_bitmap));
    try std.testing.expect(core_mask.isSubsetOf(outer_mask));
    try std.testing.expect(core_bitmap.isSubsetOf(refill_bitmap));
    try std.testing.expect(core_mask.isSubsetOf(refill_mask));
    try std.testing.expect(!refill_bitmap.isSubsetOf(core_bitmap));
    try std.testing.expect(!refill_mask.isSubsetOf(core_mask));
    try std.testing.expect(refill_bitmap.intersects(outer_bitmap));
    try std.testing.expect(refill_mask.intersects(outer_mask));

    try std.testing.expectEqual(@as(usize, outer_bits.len), outer_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, core_bits.len), core_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, refill_bits.len), refill_mask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, word_bits - 3), core_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 2), core_mask.nextCpu(word_bits - 2));
    try std.testing.expectEqual(@as(?usize, null), core_mask.nextCpu(word_bits + 32));
    try std.testing.expectEqual(@as(?usize, capacity - 3), refill_bitmap.nextClearBit(capacity - 3));
}
