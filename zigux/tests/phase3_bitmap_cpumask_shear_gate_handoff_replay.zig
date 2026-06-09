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

test "shear gate handoff mirrors bitmap and cpumask lanes" {
    const capacity = word_bits * 3 + 19;
    const shear_words = [_]Word{
        bit(3) | bit(9) | bit(18) | bit(29) | bit(38) | bit(47) | bit(56) | bit(63),
        bit(word_bits + 2) | bit(word_bits + 11) | bit(word_bits + 20) |
            bit(word_bits + 31) | bit(word_bits + 42) | bit(word_bits + 53),
        bit(word_bits * 2 + 5) | bit(word_bits * 2 + 14) |
            bit(word_bits * 2 + 23) | bit(word_bits * 2 + 32) |
            bit(word_bits * 2 + 41) | bit(word_bits * 2 + 50) |
            bit(word_bits * 2 + 59),
        bit(word_bits * 3 + 1) | bit(word_bits * 3 + 8) |
            bit(word_bits * 3 + 18) | tailNoise(19),
    };
    const intake_words = [_]Word{
        bit(3) | bit(18) | bit(38) | bit(56),
        bit(word_bits + 11) | bit(word_bits + 31) | bit(word_bits + 53),
        bit(word_bits * 2 + 14) | bit(word_bits * 2 + 32) |
            bit(word_bits * 2 + 50),
        bit(word_bits * 3 + 8) | tailNoise(19),
    };
    const release_words = [_]Word{
        bit(9) | bit(29) | bit(47) | bit(63),
        bit(word_bits + 2) | bit(word_bits + 20) | bit(word_bits + 42),
        bit(word_bits * 2 + 5) | bit(word_bits * 2 + 23) |
            bit(word_bits * 2 + 41) | bit(word_bits * 2 + 59),
        bit(word_bits * 3 + 1) | bit(word_bits * 3 + 18) | tailNoise(19),
    };
    const guard_words = [_]Word{
        bit(0) | bit(7) | bit(23) | bit(34) | bit(51),
        bit(word_bits + 7) | bit(word_bits + 17) | bit(word_bits + 37) |
            bit(word_bits + 49) | bit(word_bits + 61),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 10) |
            bit(word_bits * 2 + 36) | bit(word_bits * 2 + 54),
        bit(word_bits * 3 + 0) | bit(word_bits * 3 + 17),
    };

    const shear = makeView(shear_words[0..], capacity);
    const intake = makeView(intake_words[0..], capacity);
    const release = makeView(release_words[0..], capacity);
    const guard = makeView(guard_words[0..], capacity);
    const shear_mask = makeCpuMask(shear_words[0..], capacity);
    const intake_mask = makeCpuMask(intake_words[0..], capacity);
    const release_mask = makeCpuMask(release_words[0..], capacity);
    const guard_mask = makeCpuMask(guard_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 24), shear.countSetBits());
    try std.testing.expectEqual(shear.countSetBits(), shear_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 11), intake.countSetBits());
    try std.testing.expectEqual(intake.countSetBits(), intake_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 13), release.countSetBits());
    try std.testing.expectEqual(release.countSetBits(), release_mask.countPresentCpus());

    try std.testing.expect(intake.isSubsetOf(shear));
    try std.testing.expect(release.isSubsetOf(shear));
    try std.testing.expect(intake_mask.isSubsetOf(shear_mask));
    try std.testing.expect(release_mask.isSubsetOf(shear_mask));
    try std.testing.expect(!shear.isSubsetOf(intake));
    try std.testing.expect(!shear_mask.isSubsetOf(intake_mask));
    try std.testing.expect(!intake.intersects(release));
    try std.testing.expect(!intake_mask.intersects(release_mask));
    try std.testing.expect(!shear.intersects(guard));
    try std.testing.expect(!shear_mask.intersects(guard_mask));

    try std.testing.expect(shear.isSet(word_bits * 3 + 18));
    try std.testing.expect(shear_mask.hasCpu(word_bits * 3 + 18));
    try std.testing.expectEqual(@as(?usize, 3), shear.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 3), shear_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 18), shear.nextSetBit(10));
    try std.testing.expectEqual(@as(?usize, 18), shear_mask.nextCpu(10));
    try std.testing.expectEqual(@as(?usize, word_bits + 2), shear.nextSetBit(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits + 2), shear_mask.nextCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 32), shear.nextSetBit(word_bits * 2 + 24));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 32), shear_mask.nextCpu(word_bits * 2 + 24));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 18), shear.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 18), shear_mask.lastCpu());

    try std.testing.expectEqual(@as(?usize, 0), shear.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), shear_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 9), shear.nextClearBit(word_bits * 3 + 9));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 9), shear_mask.nextMissingCpu(word_bits * 3 + 9));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 17), shear.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 17), shear_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), shear.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), shear_mask.nextCpu(capacity));
}

test "shear gate rollback keeps retained and drained spans bounded" {
    const capacity = word_bits * 2 + 23;
    const staged_words = [_]Word{
        bit(4) | bit(12) | bit(20) | bit(28) | bit(36) | bit(44) |
            bit(52) | bit(60),
        bit(word_bits + 3) | bit(word_bits + 15) | bit(word_bits + 27) |
            bit(word_bits + 39) | bit(word_bits + 51) | bit(word_bits + 63),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 10) |
            bit(word_bits * 2 + 18) | bit(word_bits * 2 + 22) | tailNoise(23),
    };
    const retained_words = [_]Word{
        bit(4) | bit(28) | bit(52),
        bit(word_bits + 15) | bit(word_bits + 39) | bit(word_bits + 63),
        bit(word_bits * 2 + 10) | bit(word_bits * 2 + 22) | tailNoise(23),
    };
    const drained_words = [_]Word{
        bit(12) | bit(20) | bit(36) | bit(44) | bit(60),
        bit(word_bits + 3) | bit(word_bits + 27) | bit(word_bits + 51),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 18) | tailNoise(23),
    };

    const staged = makeView(staged_words[0..], capacity);
    const retained = makeView(retained_words[0..], capacity);
    const drained = makeView(drained_words[0..], capacity);
    const staged_mask = makeCpuMask(staged_words[0..], capacity);
    const retained_mask = makeCpuMask(retained_words[0..], capacity);
    const drained_mask = makeCpuMask(drained_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 18), staged.countSetBits());
    try std.testing.expectEqual(staged.countSetBits(), staged_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 8), retained.countSetBits());
    try std.testing.expectEqual(retained.countSetBits(), retained_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 10), drained.countSetBits());
    try std.testing.expectEqual(drained.countSetBits(), drained_mask.countPresentCpus());

    try std.testing.expect(retained.isSubsetOf(staged));
    try std.testing.expect(drained.isSubsetOf(staged));
    try std.testing.expect(retained_mask.isSubsetOf(staged_mask));
    try std.testing.expect(drained_mask.isSubsetOf(staged_mask));
    try std.testing.expect(!retained.intersects(drained));
    try std.testing.expect(!retained_mask.intersects(drained_mask));

    try std.testing.expectEqual(@as(?usize, 4), retained.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 4), retained_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 28), retained.nextSetBit(5));
    try std.testing.expectEqual(@as(?usize, 28), retained_mask.nextCpu(5));
    try std.testing.expectEqual(@as(?usize, word_bits + 39), retained.nextSetBit(word_bits + 16));
    try std.testing.expectEqual(@as(?usize, word_bits + 39), retained_mask.nextCpu(word_bits + 16));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 22), retained.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 22), retained_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, 0), retained.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), retained_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 11), retained.nextClearBit(word_bits * 2 + 11));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 11), retained_mask.nextMissingCpu(word_bits * 2 + 11));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 21), retained.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 21), retained_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), retained.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), retained_mask.nextCpu(capacity));
}
