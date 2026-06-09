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

test "ripple gate mirrors staggered waves across bitmap and cpumask" {
    const capacity = word_bits * 4 + 17;
    const ripple_words = [_]Word{
        bit(1) | bit(8) | bit(15) | bit(22) | bit(29) | bit(36) | bit(43) | bit(50) | bit(57),
        bit(word_bits + 2) | bit(word_bits + 9) | bit(word_bits + 16) | bit(word_bits + 23) | bit(word_bits + 30) | bit(word_bits + 37) | bit(word_bits + 44) | bit(word_bits + 51) | bit(word_bits + 58),
        bit(word_bits * 2 + 3) | bit(word_bits * 2 + 10) | bit(word_bits * 2 + 17) | bit(word_bits * 2 + 24) | bit(word_bits * 2 + 31) | bit(word_bits * 2 + 38) | bit(word_bits * 2 + 45) | bit(word_bits * 2 + 52) | bit(word_bits * 2 + 59),
        bit(word_bits * 3 + 4) | bit(word_bits * 3 + 11) | bit(word_bits * 3 + 18) | bit(word_bits * 3 + 25) | bit(word_bits * 3 + 32) | bit(word_bits * 3 + 39) | bit(word_bits * 3 + 46) | bit(word_bits * 3 + 53) | bit(word_bits * 3 + 60),
        bit(word_bits * 4 + 5) | bit(word_bits * 4 + 12) | bit(word_bits * 4 + 16) | tailNoise(17),
    };
    const gate_words = [_]Word{
        bit(1) | bit(15) | bit(29) | bit(43) | bit(57),
        bit(word_bits + 2) | bit(word_bits + 16) | bit(word_bits + 30) | bit(word_bits + 44) | bit(word_bits + 58),
        bit(word_bits * 2 + 3) | bit(word_bits * 2 + 17) | bit(word_bits * 2 + 31) | bit(word_bits * 2 + 45) | bit(word_bits * 2 + 59),
        bit(word_bits * 3 + 4) | bit(word_bits * 3 + 18) | bit(word_bits * 3 + 32) | bit(word_bits * 3 + 46) | bit(word_bits * 3 + 60),
        bit(word_bits * 4 + 5) | bit(word_bits * 4 + 16) | tailNoise(17),
    };
    const release_words = [_]Word{
        bit(8) | bit(22) | bit(36) | bit(50),
        bit(word_bits + 9) | bit(word_bits + 23) | bit(word_bits + 37) | bit(word_bits + 51),
        bit(word_bits * 2 + 10) | bit(word_bits * 2 + 24) | bit(word_bits * 2 + 38) | bit(word_bits * 2 + 52),
        bit(word_bits * 3 + 11) | bit(word_bits * 3 + 25) | bit(word_bits * 3 + 39) | bit(word_bits * 3 + 53),
        bit(word_bits * 4 + 12) | tailNoise(17),
    };
    const guard_words = [_]Word{
        bit(0) | bit(7) | bit(14) | bit(21) | bit(28) | bit(35) | bit(42) | bit(49) | bit(56),
        bit(word_bits + 1) | bit(word_bits + 8) | bit(word_bits + 15) | bit(word_bits + 22) | bit(word_bits + 29) | bit(word_bits + 36) | bit(word_bits + 43) | bit(word_bits + 50) | bit(word_bits + 57),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 9) | bit(word_bits * 2 + 16) | bit(word_bits * 2 + 23) | bit(word_bits * 2 + 30) | bit(word_bits * 2 + 37) | bit(word_bits * 2 + 44) | bit(word_bits * 2 + 51) | bit(word_bits * 2 + 58),
        bit(word_bits * 3 + 3) | bit(word_bits * 3 + 10) | bit(word_bits * 3 + 17) | bit(word_bits * 3 + 24) | bit(word_bits * 3 + 31) | bit(word_bits * 3 + 38) | bit(word_bits * 3 + 45) | bit(word_bits * 3 + 52) | bit(word_bits * 3 + 59),
        bit(word_bits * 4 + 0) | bit(word_bits * 4 + 15),
    };

    const ripple = makeView(ripple_words[0..], capacity);
    const gate = makeView(gate_words[0..], capacity);
    const release = makeView(release_words[0..], capacity);
    const guard = makeView(guard_words[0..], capacity);

    const ripple_mask = makeCpuMask(ripple_words[0..], capacity);
    const gate_mask = makeCpuMask(gate_words[0..], capacity);
    const release_mask = makeCpuMask(release_words[0..], capacity);
    const guard_mask = makeCpuMask(guard_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 39), ripple.countSetBits());
    try std.testing.expectEqual(ripple.countSetBits(), ripple_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 22), gate.countSetBits());
    try std.testing.expectEqual(gate.countSetBits(), gate_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 17), release.countSetBits());
    try std.testing.expectEqual(release.countSetBits(), release_mask.countPresentCpus());

    try std.testing.expect(gate.isSubsetOf(ripple));
    try std.testing.expect(release.isSubsetOf(ripple));
    try std.testing.expect(gate_mask.isSubsetOf(ripple_mask));
    try std.testing.expect(release_mask.isSubsetOf(ripple_mask));
    try std.testing.expect(!ripple.isSubsetOf(gate));
    try std.testing.expect(!ripple_mask.isSubsetOf(gate_mask));

    try std.testing.expect(!gate.intersects(release));
    try std.testing.expect(!gate_mask.intersects(release_mask));
    try std.testing.expect(!ripple.intersects(guard));
    try std.testing.expect(!ripple_mask.intersects(guard_mask));

    try std.testing.expect(ripple.isSet(word_bits * 4 + 16));
    try std.testing.expect(ripple_mask.hasCpu(word_bits * 4 + 16));
    try std.testing.expectEqual(@as(?usize, 1), ripple.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 1), ripple_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 4 + 16), ripple.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 4 + 16), ripple_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 2), ripple.nextSetBit(58));
    try std.testing.expectEqual(@as(?usize, word_bits + 2), ripple_mask.nextCpu(58));
    try std.testing.expectEqual(@as(?usize, word_bits * 4 + 16), ripple.nextSetBit(word_bits * 4 + 13));
    try std.testing.expectEqual(@as(?usize, word_bits * 4 + 16), ripple_mask.nextCpu(word_bits * 4 + 13));
    try std.testing.expectEqual(@as(?usize, 0), ripple.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), ripple_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 4 + 15), ripple.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 4 + 15), ripple_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), ripple.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), ripple_mask.nextCpu(capacity));
}

test "ripple gate rollback clips final-bank tail noise" {
    const capacity = word_bits * 2 + 3;
    const acquire_words = [_]Word{
        bit(0) | bit(31) | bit(word_bits - 1),
        bit(word_bits + 5) | bit(word_bits + 17) | bit(word_bits + 45),
        bit(word_bits * 2 + 0) | bit(word_bits * 2 + 2) | tailNoise(3),
    };
    const gate_words = [_]Word{
        bit(31),
        bit(word_bits + 17),
        bit(word_bits * 2 + 2) | tailNoise(3),
    };
    const rollback_words = [_]Word{
        bit(0) | bit(word_bits - 1),
        bit(word_bits + 5) | bit(word_bits + 45),
        bit(word_bits * 2 + 0) | tailNoise(3),
    };

    const acquire = makeView(acquire_words[0..], capacity);
    const gate = makeView(gate_words[0..], capacity);
    const rollback = makeView(rollback_words[0..], capacity);
    const acquire_mask = makeCpuMask(acquire_words[0..], capacity);
    const gate_mask = makeCpuMask(gate_words[0..], capacity);
    const rollback_mask = makeCpuMask(rollback_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 8), acquire.countSetBits());
    try std.testing.expectEqual(acquire.countSetBits(), acquire_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 3), gate.countSetBits());
    try std.testing.expectEqual(gate.countSetBits(), gate_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 5), rollback.countSetBits());
    try std.testing.expectEqual(rollback.countSetBits(), rollback_mask.countPresentCpus());

    try std.testing.expect(gate.isSubsetOf(acquire));
    try std.testing.expect(rollback.isSubsetOf(acquire));
    try std.testing.expect(gate_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(rollback_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(!gate.intersects(rollback));
    try std.testing.expect(!gate_mask.intersects(rollback_mask));

    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 2), gate.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 2), gate_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 1), gate.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 1), gate_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), gate.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), gate_mask.nextCpu(capacity));
}
