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

test "delta funnel mirrors consolidated bitmap and cpumask lanes" {
    const capacity = word_bits * 3 + 13;
    const base_words = [_]Word{
        bit(2) | bit(18) | bit(34) | bit(50),
        bit(word_bits + 3) | bit(word_bits + 21) |
            bit(word_bits + 39) | bit(word_bits + 57),
        bit(word_bits * 2 + 6) | bit(word_bits * 2 + 24) |
            bit(word_bits * 2 + 42) | bit(word_bits * 2 + 60),
        bit(word_bits * 3 + 1) | bit(word_bits * 3 + 7) |
            bit(word_bits * 3 + 12) | tailNoise(13),
    };
    const delta_low_words = [_]Word{
        bit(5) | bit(22) | bit(37) | bit(53),
        bit(word_bits + 8) | bit(word_bits + 26) |
            bit(word_bits + 44) | bit(word_bits + 62),
        bit(word_bits * 2 + 11) | bit(word_bits * 2 + 29) |
            bit(word_bits * 2 + 47),
        bit(word_bits * 3 + 3) | bit(word_bits * 3 + 9) | tailNoise(13),
    };
    const delta_high_words = [_]Word{
        bit(9) | bit(27) | bit(45) | bit(61),
        bit(word_bits + 12) | bit(word_bits + 30) |
            bit(word_bits + 48),
        bit(word_bits * 2 + 15) | bit(word_bits * 2 + 33) |
            bit(word_bits * 2 + 51) | bit(word_bits * 2 + 63),
        bit(word_bits * 3 + 5) | bit(word_bits * 3 + 11) | tailNoise(13),
    };
    const funnel_words = [_]Word{
        base_words[0] | delta_low_words[0] | delta_high_words[0],
        base_words[1] | delta_low_words[1] | delta_high_words[1],
        base_words[2] | delta_low_words[2] | delta_high_words[2],
        base_words[3] | delta_low_words[3] | delta_high_words[3],
    };
    const guard_words = [_]Word{
        bit(0) | bit(13) | bit(31) | bit(49),
        bit(word_bits + 0) | bit(word_bits + 17) |
            bit(word_bits + 35) | bit(word_bits + 55),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 20) |
            bit(word_bits * 2 + 38) | bit(word_bits * 2 + 56),
        bit(word_bits * 3 + 0) | bit(word_bits * 3 + 4) |
            bit(word_bits * 3 + 6) | bit(word_bits * 3 + 10),
    };

    const base = makeView(base_words[0..], capacity);
    const delta_low = makeView(delta_low_words[0..], capacity);
    const delta_high = makeView(delta_high_words[0..], capacity);
    const funnel = makeView(funnel_words[0..], capacity);
    const guard = makeView(guard_words[0..], capacity);
    const base_mask = makeCpuMask(base_words[0..], capacity);
    const delta_low_mask = makeCpuMask(delta_low_words[0..], capacity);
    const delta_high_mask = makeCpuMask(delta_high_words[0..], capacity);
    const funnel_mask = makeCpuMask(funnel_words[0..], capacity);
    const guard_mask = makeCpuMask(guard_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 15), base.countSetBits());
    try std.testing.expectEqual(base.countSetBits(), base_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 13), delta_low.countSetBits());
    try std.testing.expectEqual(delta_low.countSetBits(), delta_low_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 13), delta_high.countSetBits());
    try std.testing.expectEqual(delta_high.countSetBits(), delta_high_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 41), funnel.countSetBits());
    try std.testing.expectEqual(funnel.countSetBits(), funnel_mask.countPresentCpus());

    try std.testing.expect(base.isSubsetOf(funnel));
    try std.testing.expect(delta_low.isSubsetOf(funnel));
    try std.testing.expect(delta_high.isSubsetOf(funnel));
    try std.testing.expect(base_mask.isSubsetOf(funnel_mask));
    try std.testing.expect(delta_low_mask.isSubsetOf(funnel_mask));
    try std.testing.expect(delta_high_mask.isSubsetOf(funnel_mask));
    try std.testing.expect(!funnel.isSubsetOf(base));
    try std.testing.expect(!funnel_mask.isSubsetOf(base_mask));
    try std.testing.expect(!base.intersects(delta_low));
    try std.testing.expect(!base_mask.intersects(delta_low_mask));
    try std.testing.expect(!delta_low.intersects(delta_high));
    try std.testing.expect(!delta_low_mask.intersects(delta_high_mask));
    try std.testing.expect(!funnel.intersects(guard));
    try std.testing.expect(!funnel_mask.intersects(guard_mask));

    try std.testing.expect(funnel.isSet(word_bits * 3 + 12));
    try std.testing.expect(funnel_mask.hasCpu(word_bits * 3 + 12));
    try std.testing.expectEqual(@as(?usize, 2), funnel.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 2), funnel_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 5), funnel.nextSetBit(3));
    try std.testing.expectEqual(@as(?usize, 5), funnel_mask.nextCpu(3));
    try std.testing.expectEqual(@as(?usize, word_bits + 62), funnel.nextSetBit(word_bits + 58));
    try std.testing.expectEqual(@as(?usize, word_bits + 62), funnel_mask.nextCpu(word_bits + 58));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 63), funnel.nextSetBit(word_bits * 2 + 61));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 63), funnel_mask.nextCpu(word_bits * 2 + 61));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 12), funnel.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 12), funnel_mask.lastCpu());

    try std.testing.expectEqual(@as(?usize, 0), funnel.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), funnel_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 2), funnel.nextClearBit(word_bits * 3 + 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 2), funnel_mask.nextMissingCpu(word_bits * 3 + 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 10), funnel.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 10), funnel_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), funnel.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), funnel_mask.nextCpu(capacity));
}

test "delta funnel rollback keeps retained and released lanes disjoint" {
    const capacity = word_bits * 2 + 9;
    const retained_words = [_]Word{
        bit(4) | bit(20) | bit(36) | bit(52),
        bit(word_bits + 7) | bit(word_bits + 31) |
            bit(word_bits + 55),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 8) | tailNoise(9),
    };
    const released_words = [_]Word{
        bit(11) | bit(27) | bit(43) | bit(59),
        bit(word_bits + 15) | bit(word_bits + 39) |
            bit(word_bits + 63),
        bit(word_bits * 2 + 0) | bit(word_bits * 2 + 6) | tailNoise(9),
    };
    const staged_words = [_]Word{
        retained_words[0] | released_words[0],
        retained_words[1] | released_words[1],
        retained_words[2] | released_words[2],
    };

    const retained = makeView(retained_words[0..], capacity);
    const released = makeView(released_words[0..], capacity);
    const staged = makeView(staged_words[0..], capacity);
    const retained_mask = makeCpuMask(retained_words[0..], capacity);
    const released_mask = makeCpuMask(released_words[0..], capacity);
    const staged_mask = makeCpuMask(staged_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 9), retained.countSetBits());
    try std.testing.expectEqual(retained.countSetBits(), retained_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 9), released.countSetBits());
    try std.testing.expectEqual(released.countSetBits(), released_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 18), staged.countSetBits());
    try std.testing.expectEqual(staged.countSetBits(), staged_mask.countPresentCpus());

    try std.testing.expect(retained.isSubsetOf(staged));
    try std.testing.expect(released.isSubsetOf(staged));
    try std.testing.expect(retained_mask.isSubsetOf(staged_mask));
    try std.testing.expect(released_mask.isSubsetOf(staged_mask));
    try std.testing.expect(!staged.isSubsetOf(retained));
    try std.testing.expect(!staged_mask.isSubsetOf(retained_mask));
    try std.testing.expect(!retained.intersects(released));
    try std.testing.expect(!retained_mask.intersects(released_mask));

    try std.testing.expectEqual(@as(?usize, 4), retained.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 4), retained_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 20), retained.nextSetBit(5));
    try std.testing.expectEqual(@as(?usize, 20), retained_mask.nextCpu(5));
    try std.testing.expectEqual(@as(?usize, word_bits + 31), retained.nextSetBit(word_bits + 8));
    try std.testing.expectEqual(@as(?usize, word_bits + 31), retained_mask.nextCpu(word_bits + 8));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), retained.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), retained_mask.lastCpu());

    try std.testing.expectEqual(@as(?usize, 11), released.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 11), released_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 6), released.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 6), released_mask.lastCpu());

    try std.testing.expectEqual(@as(?usize, 0), retained.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), retained_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 3), retained.nextClearBit(word_bits * 2 + 3));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 3), retained_mask.nextMissingCpu(word_bits * 2 + 3));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 7), retained.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 7), retained_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), staged.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), staged_mask.nextCpu(capacity));
}
