const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn tailNoise(valid_bits: usize) Word {
    return ~((@as(Word, 1) << @intCast(valid_bits)) - 1);
}

fn makeView(words: []const Word, bit_len: usize) bitmap_view.BitmapView {
    return bitmap_view.BitmapView.init(words, bit_len);
}

fn makeCpuMask(words: []const Word, cpu_capacity: usize) cpumask_view.CpuMaskView {
    return cpumask_view.CpuMaskView.init(words, cpu_capacity);
}

test "fanout bridge mirrors disjoint leaves across bitmap and cpumask" {
    const capacity = word_bits * 3 + 9;
    const fanout_words = [_]Word{
        bit(1) | bit(10) | bit(19) | bit(28) | bit(37) | bit(46) | bit(55),
        bit(word_bits + 2) | bit(word_bits + 14) | bit(word_bits + 26) |
            bit(word_bits + 38) | bit(word_bits + 50) | bit(word_bits + 62),
        bit(word_bits * 2 + 4) | bit(word_bits * 2 + 20) |
            bit(word_bits * 2 + 36) | bit(word_bits * 2 + 52),
        bit(word_bits * 3 + 0) | bit(word_bits * 3 + 5) |
            bit(word_bits * 3 + 8) | tailNoise(9),
    };
    const leaf_a_words = [_]Word{
        bit(1) | bit(28) | bit(55),
        bit(word_bits + 14) | bit(word_bits + 50),
        bit(word_bits * 2 + 20),
        bit(word_bits * 3 + 8) | tailNoise(9),
    };
    const leaf_b_words = [_]Word{
        bit(10) | bit(37),
        bit(word_bits + 2) | bit(word_bits + 38) | bit(word_bits + 62),
        bit(word_bits * 2 + 4) | bit(word_bits * 2 + 36),
        bit(word_bits * 3 + 5) | tailNoise(9),
    };
    const leaf_c_words = [_]Word{
        bit(19) | bit(46),
        bit(word_bits + 26),
        bit(word_bits * 2 + 52),
        bit(word_bits * 3 + 0) | tailNoise(9),
    };
    const guard_words = [_]Word{
        bit(0) | bit(7) | bit(14) | bit(21) | bit(35) | bit(42) | bit(49) | bit(56) | bit(63),
        bit(word_bits + 0) | bit(word_bits + 8) | bit(word_bits + 16) |
            bit(word_bits + 24) | bit(word_bits + 32) | bit(word_bits + 40) |
            bit(word_bits + 48) | bit(word_bits + 56),
        bit(word_bits * 2 + 0) | bit(word_bits * 2 + 12) |
            bit(word_bits * 2 + 24) | bit(word_bits * 2 + 48) |
            bit(word_bits * 2 + 60),
        bit(word_bits * 3 + 1) | bit(word_bits * 3 + 4) | bit(word_bits * 3 + 7),
    };

    const fanout = makeView(fanout_words[0..], capacity);
    const leaf_a = makeView(leaf_a_words[0..], capacity);
    const leaf_b = makeView(leaf_b_words[0..], capacity);
    const leaf_c = makeView(leaf_c_words[0..], capacity);
    const guard = makeView(guard_words[0..], capacity);
    const fanout_mask = makeCpuMask(fanout_words[0..], capacity);
    const leaf_a_mask = makeCpuMask(leaf_a_words[0..], capacity);
    const leaf_b_mask = makeCpuMask(leaf_b_words[0..], capacity);
    const leaf_c_mask = makeCpuMask(leaf_c_words[0..], capacity);
    const guard_mask = makeCpuMask(guard_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 20), fanout.countSetBits());
    try std.testing.expectEqual(fanout.countSetBits(), fanout_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 7), leaf_a.countSetBits());
    try std.testing.expectEqual(leaf_a.countSetBits(), leaf_a_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 8), leaf_b.countSetBits());
    try std.testing.expectEqual(leaf_b.countSetBits(), leaf_b_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 5), leaf_c.countSetBits());
    try std.testing.expectEqual(leaf_c.countSetBits(), leaf_c_mask.countPresentCpus());

    try std.testing.expect(leaf_a.isSubsetOf(fanout));
    try std.testing.expect(leaf_b.isSubsetOf(fanout));
    try std.testing.expect(leaf_c.isSubsetOf(fanout));
    try std.testing.expect(leaf_a_mask.isSubsetOf(fanout_mask));
    try std.testing.expect(leaf_b_mask.isSubsetOf(fanout_mask));
    try std.testing.expect(leaf_c_mask.isSubsetOf(fanout_mask));
    try std.testing.expect(!fanout.isSubsetOf(leaf_a));
    try std.testing.expect(!fanout_mask.isSubsetOf(leaf_a_mask));

    try std.testing.expect(!leaf_a.intersects(leaf_b));
    try std.testing.expect(!leaf_b.intersects(leaf_c));
    try std.testing.expect(!leaf_a.intersects(leaf_c));
    try std.testing.expect(!leaf_a_mask.intersects(leaf_b_mask));
    try std.testing.expect(!leaf_b_mask.intersects(leaf_c_mask));
    try std.testing.expect(!leaf_a_mask.intersects(leaf_c_mask));
    try std.testing.expect(!fanout.intersects(guard));
    try std.testing.expect(!fanout_mask.intersects(guard_mask));

    try std.testing.expect(fanout.isSet(word_bits * 3 + 8));
    try std.testing.expect(fanout_mask.hasCpu(word_bits * 3 + 8));
    try std.testing.expectEqual(@as(?usize, 1), fanout.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 1), fanout_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 8), fanout.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 8), fanout_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 2), fanout.nextSetBit(56));
    try std.testing.expectEqual(@as(?usize, word_bits + 2), fanout_mask.nextCpu(56));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 52), fanout.nextSetBit(word_bits * 2 + 37));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 52), fanout_mask.nextCpu(word_bits * 2 + 37));
    try std.testing.expectEqual(@as(?usize, 0), fanout.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), fanout_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 7), fanout.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 7), fanout_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), fanout.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), fanout_mask.nextCpu(capacity));
}

test "fanout bridge rollback clips final-bank tail noise" {
    const capacity = word_bits * 2 + 11;
    const acquire_words = [_]Word{
        bit(0) | bit(6) | bit(12) | bit(18) | bit(24) | bit(30) |
            bit(36) | bit(42) | bit(48) | bit(54) | bit(60),
        bit(word_bits + 3) | bit(word_bits + 17) | bit(word_bits + 31) |
            bit(word_bits + 45) | bit(word_bits + 59),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 6) |
            bit(word_bits * 2 + 10) | tailNoise(11),
    };
    const keep_words = [_]Word{
        bit(0) | bit(24) | bit(48),
        bit(word_bits + 17) | bit(word_bits + 45),
        bit(word_bits * 2 + 10) | tailNoise(11),
    };
    const release_words = [_]Word{
        bit(6) | bit(12) | bit(18) | bit(30) | bit(36) | bit(42) |
            bit(54) | bit(60),
        bit(word_bits + 3) | bit(word_bits + 31) | bit(word_bits + 59),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 6) | tailNoise(11),
    };

    const acquire = makeView(acquire_words[0..], capacity);
    const keep = makeView(keep_words[0..], capacity);
    const release = makeView(release_words[0..], capacity);
    const acquire_mask = makeCpuMask(acquire_words[0..], capacity);
    const keep_mask = makeCpuMask(keep_words[0..], capacity);
    const release_mask = makeCpuMask(release_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 19), acquire.countSetBits());
    try std.testing.expectEqual(acquire.countSetBits(), acquire_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 6), keep.countSetBits());
    try std.testing.expectEqual(keep.countSetBits(), keep_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 13), release.countSetBits());
    try std.testing.expectEqual(release.countSetBits(), release_mask.countPresentCpus());

    try std.testing.expect(keep.isSubsetOf(acquire));
    try std.testing.expect(release.isSubsetOf(acquire));
    try std.testing.expect(keep_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(release_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(!keep.intersects(release));
    try std.testing.expect(!keep_mask.intersects(release_mask));

    try std.testing.expectEqual(@as(?usize, 0), keep.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 0), keep_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 24), keep.nextSetBit(1));
    try std.testing.expectEqual(@as(?usize, 24), keep_mask.nextCpu(1));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 10), keep.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 10), keep_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, 1), keep.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 1), keep_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 9), keep.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 9), keep_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), keep.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), keep_mask.nextCpu(capacity));
}
