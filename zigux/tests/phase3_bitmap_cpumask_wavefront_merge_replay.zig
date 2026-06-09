const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn tailNoise(valid_bits: usize) Word {
    if (valid_bits == 0) return std.math.maxInt(Word);
    if (valid_bits >= word_bits) return 0;
    return ~((@as(Word, 1) << @intCast(valid_bits)) - 1);
}

fn makeView(words: []const Word, bit_len: usize) bitmap_view.BitmapView {
    return bitmap_view.BitmapView.init(words, bit_len);
}

fn makeCpuMask(words: []const Word, cpu_capacity: usize) cpumask_view.CpuMaskView {
    return cpumask_view.CpuMaskView.init(words, cpu_capacity);
}

test "wavefront merge mirrors promoted bitmap and cpumask fronts" {
    const capacity = word_bits * 3 + 21;
    const front_a_words = [_]Word{
        bit(2) | bit(14) | bit(26) | bit(38) | bit(50) | bit(62),
        bit(word_bits + 1) | bit(word_bits + 13) | bit(word_bits + 25) |
            bit(word_bits + 37) | bit(word_bits + 49) | bit(word_bits + 61),
        bit(word_bits * 2 + 4) | bit(word_bits * 2 + 16) |
            bit(word_bits * 2 + 28) | bit(word_bits * 2 + 40) |
            bit(word_bits * 2 + 52),
        bit(word_bits * 3 + 3) | bit(word_bits * 3 + 15) |
            bit(word_bits * 3 + 20) | tailNoise(21),
    };
    const front_b_words = [_]Word{
        bit(5) | bit(17) | bit(29) | bit(41) | bit(53),
        bit(word_bits + 8) | bit(word_bits + 20) | bit(word_bits + 32) |
            bit(word_bits + 44) | bit(word_bits + 56),
        bit(word_bits * 2 + 7) | bit(word_bits * 2 + 19) |
            bit(word_bits * 2 + 31) | bit(word_bits * 2 + 43) |
            bit(word_bits * 2 + 55) | bit(word_bits * 2 + 63),
        bit(word_bits * 3 + 6) | bit(word_bits * 3 + 18) | tailNoise(21),
    };
    const merged_words = [_]Word{
        front_a_words[0] | front_b_words[0],
        front_a_words[1] | front_b_words[1],
        front_a_words[2] | front_b_words[2],
        front_a_words[3] | front_b_words[3],
    };
    const guard_words = [_]Word{
        bit(0) | bit(11) | bit(23) | bit(35) | bit(47) | bit(59),
        bit(word_bits + 3) | bit(word_bits + 15) | bit(word_bits + 27) |
            bit(word_bits + 39) | bit(word_bits + 51) | bit(word_bits + 63),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 10) |
            bit(word_bits * 2 + 22) | bit(word_bits * 2 + 34) |
            bit(word_bits * 2 + 46) | bit(word_bits * 2 + 58),
        bit(word_bits * 3 + 0) | bit(word_bits * 3 + 9) |
            bit(word_bits * 3 + 12),
    };

    const front_a = makeView(front_a_words[0..], capacity);
    const front_b = makeView(front_b_words[0..], capacity);
    const merged = makeView(merged_words[0..], capacity);
    const guard = makeView(guard_words[0..], capacity);
    const front_a_mask = makeCpuMask(front_a_words[0..], capacity);
    const front_b_mask = makeCpuMask(front_b_words[0..], capacity);
    const merged_mask = makeCpuMask(merged_words[0..], capacity);
    const guard_mask = makeCpuMask(guard_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 20), front_a.countSetBits());
    try std.testing.expectEqual(front_a.countSetBits(), front_a_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 18), front_b.countSetBits());
    try std.testing.expectEqual(front_b.countSetBits(), front_b_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 38), merged.countSetBits());
    try std.testing.expectEqual(merged.countSetBits(), merged_mask.countPresentCpus());

    try std.testing.expect(front_a.isSubsetOf(merged));
    try std.testing.expect(front_b.isSubsetOf(merged));
    try std.testing.expect(front_a_mask.isSubsetOf(merged_mask));
    try std.testing.expect(front_b_mask.isSubsetOf(merged_mask));
    try std.testing.expect(!merged.isSubsetOf(front_a));
    try std.testing.expect(!merged_mask.isSubsetOf(front_a_mask));
    try std.testing.expect(!front_a.intersects(front_b));
    try std.testing.expect(!front_a_mask.intersects(front_b_mask));
    try std.testing.expect(!merged.intersects(guard));
    try std.testing.expect(!merged_mask.intersects(guard_mask));

    try std.testing.expect(merged.isSet(word_bits * 3 + 20));
    try std.testing.expect(merged_mask.hasCpu(word_bits * 3 + 20));
    try std.testing.expectEqual(@as(?usize, 2), merged.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 2), merged_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 5), merged.nextSetBit(3));
    try std.testing.expectEqual(@as(?usize, 5), merged_mask.nextCpu(3));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), merged.nextSetBit(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), merged_mask.nextCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 28), merged.nextSetBit(word_bits * 2 + 20));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 28), merged_mask.nextCpu(word_bits * 2 + 20));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 20), merged.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 20), merged_mask.lastCpu());

    try std.testing.expectEqual(@as(?usize, 0), merged.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), merged_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 7), merged.nextClearBit(word_bits * 3 + 7));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 7), merged_mask.nextMissingCpu(word_bits * 3 + 7));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 19), merged.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 19), merged_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), merged.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), merged_mask.nextCpu(capacity));
}

test "wavefront rollback keeps retained and drained lanes bounded" {
    const capacity = word_bits * 2 + 17;
    const staged_words = [_]Word{
        bit(1) | bit(9) | bit(17) | bit(25) | bit(33) | bit(41) |
            bit(49) | bit(57),
        bit(word_bits + 4) | bit(word_bits + 12) | bit(word_bits + 20) |
            bit(word_bits + 28) | bit(word_bits + 36) | bit(word_bits + 44) |
            bit(word_bits + 52) | bit(word_bits + 60),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 8) |
            bit(word_bits * 2 + 14) | bit(word_bits * 2 + 16) | tailNoise(17),
    };
    const retained_words = [_]Word{
        bit(1) | bit(25) | bit(49),
        bit(word_bits + 12) | bit(word_bits + 36) | bit(word_bits + 60),
        bit(word_bits * 2 + 8) | bit(word_bits * 2 + 16) | tailNoise(17),
    };
    const drained_words = [_]Word{
        bit(9) | bit(17) | bit(33) | bit(41) | bit(57),
        bit(word_bits + 4) | bit(word_bits + 20) | bit(word_bits + 28) |
            bit(word_bits + 44) | bit(word_bits + 52),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 14) | tailNoise(17),
    };

    const staged = makeView(staged_words[0..], capacity);
    const retained = makeView(retained_words[0..], capacity);
    const drained = makeView(drained_words[0..], capacity);
    const staged_mask = makeCpuMask(staged_words[0..], capacity);
    const retained_mask = makeCpuMask(retained_words[0..], capacity);
    const drained_mask = makeCpuMask(drained_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 20), staged.countSetBits());
    try std.testing.expectEqual(staged.countSetBits(), staged_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 8), retained.countSetBits());
    try std.testing.expectEqual(retained.countSetBits(), retained_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 12), drained.countSetBits());
    try std.testing.expectEqual(drained.countSetBits(), drained_mask.countPresentCpus());

    try std.testing.expect(retained.isSubsetOf(staged));
    try std.testing.expect(drained.isSubsetOf(staged));
    try std.testing.expect(retained_mask.isSubsetOf(staged_mask));
    try std.testing.expect(drained_mask.isSubsetOf(staged_mask));
    try std.testing.expect(!retained.intersects(drained));
    try std.testing.expect(!retained_mask.intersects(drained_mask));
    try std.testing.expect(!staged.isSubsetOf(retained));
    try std.testing.expect(!staged_mask.isSubsetOf(retained_mask));

    try std.testing.expectEqual(@as(?usize, 1), retained.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 1), retained_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 25), retained.nextSetBit(2));
    try std.testing.expectEqual(@as(?usize, 25), retained_mask.nextCpu(2));
    try std.testing.expectEqual(@as(?usize, word_bits + 36), retained.nextSetBit(word_bits + 13));
    try std.testing.expectEqual(@as(?usize, word_bits + 36), retained_mask.nextCpu(word_bits + 13));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 16), retained.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 16), retained_mask.lastCpu());

    try std.testing.expectEqual(@as(?usize, 0), retained.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), retained_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 9), retained.nextClearBit(word_bits * 2 + 9));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 9), retained_mask.nextMissingCpu(word_bits * 2 + 9));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 15), retained.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 15), retained_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), retained.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), retained_mask.nextCpu(capacity));
}
