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

test "cascade latch mirrors staged handoff across bitmap and cpumask" {
    const capacity = word_bits * 3 + 17;
    const cascade_words = [_]Word{
        bit(2) | bit(5) | bit(13) | bit(27) | bit(40) | bit(58) | bit(61),
        bit(word_bits + 1) | bit(word_bits + 8) | bit(word_bits + 16) |
            bit(word_bits + 24) | bit(word_bits + 33) | bit(word_bits + 47) |
            bit(word_bits + 59),
        bit(word_bits * 2 + 0) | bit(word_bits * 2 + 6) | bit(word_bits * 2 + 14) |
            bit(word_bits * 2 + 22) | bit(word_bits * 2 + 35) |
            bit(word_bits * 2 + 46) | bit(word_bits * 2 + 63),
        bit(word_bits * 3 + 3) | bit(word_bits * 3 + 9) |
            bit(word_bits * 3 + 16) | tailNoise(17),
    };
    const tier0_words = [_]Word{
        bit(2) | bit(27) | bit(61),
        bit(word_bits + 8) | bit(word_bits + 33),
        bit(word_bits * 2 + 0) | bit(word_bits * 2 + 35),
        bit(word_bits * 3 + 9) | tailNoise(17),
    };
    const tier1_words = [_]Word{
        bit(5) | bit(40),
        bit(word_bits + 1) | bit(word_bits + 24) | bit(word_bits + 47),
        bit(word_bits * 2 + 6) | bit(word_bits * 2 + 46),
        bit(word_bits * 3 + 3) | tailNoise(17),
    };
    const tier2_words = [_]Word{
        bit(13) | bit(58),
        bit(word_bits + 16) | bit(word_bits + 59),
        bit(word_bits * 2 + 14) | bit(word_bits * 2 + 22) | bit(word_bits * 2 + 63),
        bit(word_bits * 3 + 16) | tailNoise(17),
    };
    const guard_words = [_]Word{
        bit(0) | bit(7) | bit(21) | bit(35) | bit(50),
        bit(word_bits + 4) | bit(word_bits + 12) | bit(word_bits + 29) |
            bit(word_bits + 41) | bit(word_bits + 55),
        bit(word_bits * 2 + 3) | bit(word_bits * 2 + 11) |
            bit(word_bits * 2 + 31) | bit(word_bits * 2 + 50),
        bit(word_bits * 3 + 0) | bit(word_bits * 3 + 12),
    };

    const cascade = makeView(cascade_words[0..], capacity);
    const tier0 = makeView(tier0_words[0..], capacity);
    const tier1 = makeView(tier1_words[0..], capacity);
    const tier2 = makeView(tier2_words[0..], capacity);
    const guard = makeView(guard_words[0..], capacity);
    const cascade_mask = makeCpuMask(cascade_words[0..], capacity);
    const tier0_mask = makeCpuMask(tier0_words[0..], capacity);
    const tier1_mask = makeCpuMask(tier1_words[0..], capacity);
    const tier2_mask = makeCpuMask(tier2_words[0..], capacity);
    const guard_mask = makeCpuMask(guard_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 24), cascade.countSetBits());
    try std.testing.expectEqual(cascade.countSetBits(), cascade_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 8), tier0.countSetBits());
    try std.testing.expectEqual(tier0.countSetBits(), tier0_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 8), tier1.countSetBits());
    try std.testing.expectEqual(tier1.countSetBits(), tier1_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 8), tier2.countSetBits());
    try std.testing.expectEqual(tier2.countSetBits(), tier2_mask.countPresentCpus());

    try std.testing.expect(tier0.isSubsetOf(cascade));
    try std.testing.expect(tier1.isSubsetOf(cascade));
    try std.testing.expect(tier2.isSubsetOf(cascade));
    try std.testing.expect(tier0_mask.isSubsetOf(cascade_mask));
    try std.testing.expect(tier1_mask.isSubsetOf(cascade_mask));
    try std.testing.expect(tier2_mask.isSubsetOf(cascade_mask));
    try std.testing.expect(!cascade.isSubsetOf(tier0));
    try std.testing.expect(!cascade_mask.isSubsetOf(tier0_mask));

    try std.testing.expect(!tier0.intersects(tier1));
    try std.testing.expect(!tier0.intersects(tier2));
    try std.testing.expect(!tier1.intersects(tier2));
    try std.testing.expect(!tier0_mask.intersects(tier1_mask));
    try std.testing.expect(!tier0_mask.intersects(tier2_mask));
    try std.testing.expect(!tier1_mask.intersects(tier2_mask));
    try std.testing.expect(!cascade.intersects(guard));
    try std.testing.expect(!cascade_mask.intersects(guard_mask));

    try std.testing.expect(cascade.isSet(word_bits * 3 + 16));
    try std.testing.expect(cascade_mask.hasCpu(word_bits * 3 + 16));
    try std.testing.expectEqual(@as(?usize, 2), cascade.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 2), cascade_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 5), cascade.nextSetBit(3));
    try std.testing.expectEqual(@as(?usize, 5), cascade_mask.nextCpu(3));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), cascade.nextSetBit(62));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), cascade_mask.nextCpu(62));
    try std.testing.expectEqual(@as(?usize, word_bits + 47), cascade.nextSetBit(word_bits + 34));
    try std.testing.expectEqual(@as(?usize, word_bits + 47), cascade_mask.nextCpu(word_bits + 34));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 16), cascade.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 16), cascade_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, 0), cascade.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), cascade_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 10), cascade.nextClearBit(word_bits * 3 + 10));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 10), cascade_mask.nextMissingCpu(word_bits * 3 + 10));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 15), cascade.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 15), cascade_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), cascade.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), cascade_mask.nextCpu(capacity));
}

test "cascade latch rollback keeps retained and released tiers disjoint" {
    const capacity = word_bits * 2 + 9;
    const acquire_words = [_]Word{
        bit(1) | bit(6) | bit(11) | bit(16) | bit(21) | bit(26) | bit(31) |
            bit(36) | bit(41) | bit(46) | bit(51) | bit(56) | bit(61),
        bit(word_bits + 2) | bit(word_bits + 9) | bit(word_bits + 18) |
            bit(word_bits + 27) | bit(word_bits + 36) | bit(word_bits + 45) |
            bit(word_bits + 54) | bit(word_bits + 63),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 4) |
            bit(word_bits * 2 + 8) | tailNoise(9),
    };
    const retain_words = [_]Word{
        bit(1) | bit(21) | bit(41) | bit(61),
        bit(word_bits + 9) | bit(word_bits + 36) | bit(word_bits + 63),
        bit(word_bits * 2 + 4) | tailNoise(9),
    };
    const release_words = [_]Word{
        bit(6) | bit(11) | bit(16) | bit(26) | bit(31) | bit(36) |
            bit(46) | bit(51) | bit(56),
        bit(word_bits + 2) | bit(word_bits + 18) | bit(word_bits + 27) |
            bit(word_bits + 45) | bit(word_bits + 54),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 8) | tailNoise(9),
    };

    const acquire = makeView(acquire_words[0..], capacity);
    const retain = makeView(retain_words[0..], capacity);
    const release = makeView(release_words[0..], capacity);
    const acquire_mask = makeCpuMask(acquire_words[0..], capacity);
    const retain_mask = makeCpuMask(retain_words[0..], capacity);
    const release_mask = makeCpuMask(release_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 24), acquire.countSetBits());
    try std.testing.expectEqual(acquire.countSetBits(), acquire_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 8), retain.countSetBits());
    try std.testing.expectEqual(retain.countSetBits(), retain_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 16), release.countSetBits());
    try std.testing.expectEqual(release.countSetBits(), release_mask.countPresentCpus());

    try std.testing.expect(retain.isSubsetOf(acquire));
    try std.testing.expect(release.isSubsetOf(acquire));
    try std.testing.expect(retain_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(release_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(!retain.intersects(release));
    try std.testing.expect(!retain_mask.intersects(release_mask));

    try std.testing.expectEqual(@as(?usize, 1), retain.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 1), retain_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 21), retain.nextSetBit(2));
    try std.testing.expectEqual(@as(?usize, 21), retain_mask.nextCpu(2));
    try std.testing.expectEqual(@as(?usize, word_bits + 36), retain.nextSetBit(word_bits + 10));
    try std.testing.expectEqual(@as(?usize, word_bits + 36), retain_mask.nextCpu(word_bits + 10));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 4), retain.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 4), retain_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, 0), retain.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), retain_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 5), retain.nextClearBit(word_bits * 2 + 5));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 5), retain_mask.nextMissingCpu(word_bits * 2 + 5));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), retain.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), retain_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), retain.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), retain_mask.nextCpu(capacity));
}
