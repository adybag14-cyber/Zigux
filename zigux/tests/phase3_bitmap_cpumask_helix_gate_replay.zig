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

test "helix gate mirrors promoted bitmap and cpumask rails" {
    const capacity = word_bits * 3 + 12;
    const north_words = [_]Word{
        bit(2) | bit(18) | bit(34) | bit(50),
        bit(word_bits + 7) | bit(word_bits + 23) |
            bit(word_bits + 39) | bit(word_bits + 55),
        bit(word_bits * 2 + 4) | bit(word_bits * 2 + 20) |
            bit(word_bits * 2 + 36) | bit(word_bits * 2 + 52),
        bit(word_bits * 3 + 3) | bit(word_bits * 3 + 9) | tailNoise(12),
    };
    const south_words = [_]Word{
        bit(5) | bit(21) | bit(37) | bit(53),
        bit(word_bits + 10) | bit(word_bits + 26) |
            bit(word_bits + 42) | bit(word_bits + 58),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 17) |
            bit(word_bits * 2 + 33) | bit(word_bits * 2 + 49),
        bit(word_bits * 3 + 6) | tailNoise(12),
    };
    const gate_words = [_]Word{
        north_words[0] | south_words[0],
        north_words[1] | south_words[1],
        north_words[2] | south_words[2],
        north_words[3] | south_words[3],
    };
    const guard_words = [_]Word{
        bit(0) | bit(16) | bit(32) | bit(48),
        bit(word_bits + 2) | bit(word_bits + 18) |
            bit(word_bits + 34) | bit(word_bits + 50),
        bit(word_bits * 2 + 7) | bit(word_bits * 2 + 23) |
            bit(word_bits * 2 + 39) | bit(word_bits * 2 + 55),
        bit(word_bits * 3 + 0) | bit(word_bits * 3 + 11),
    };

    const north = makeView(north_words[0..], capacity);
    const south = makeView(south_words[0..], capacity);
    const gate = makeView(gate_words[0..], capacity);
    const guard = makeView(guard_words[0..], capacity);
    const north_mask = makeCpuMask(north_words[0..], capacity);
    const south_mask = makeCpuMask(south_words[0..], capacity);
    const gate_mask = makeCpuMask(gate_words[0..], capacity);
    const guard_mask = makeCpuMask(guard_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 14), north.countSetBits());
    try std.testing.expectEqual(north.countSetBits(), north_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 13), south.countSetBits());
    try std.testing.expectEqual(south.countSetBits(), south_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 27), gate.countSetBits());
    try std.testing.expectEqual(gate.countSetBits(), gate_mask.countPresentCpus());

    try std.testing.expect(north.isSubsetOf(gate));
    try std.testing.expect(south.isSubsetOf(gate));
    try std.testing.expect(north_mask.isSubsetOf(gate_mask));
    try std.testing.expect(south_mask.isSubsetOf(gate_mask));
    try std.testing.expect(!gate.isSubsetOf(north));
    try std.testing.expect(!gate_mask.isSubsetOf(north_mask));
    try std.testing.expect(!north.intersects(south));
    try std.testing.expect(!north_mask.intersects(south_mask));
    try std.testing.expect(!gate.intersects(guard));
    try std.testing.expect(!gate_mask.intersects(guard_mask));

    try std.testing.expect(gate.isSet(word_bits * 3 + 9));
    try std.testing.expect(gate_mask.hasCpu(word_bits * 3 + 9));
    try std.testing.expectEqual(@as(?usize, 2), gate.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 2), gate_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 5), gate.nextSetBit(3));
    try std.testing.expectEqual(@as(?usize, 5), gate_mask.nextCpu(3));
    try std.testing.expectEqual(@as(?usize, word_bits + 58), gate.nextSetBit(word_bits + 56));
    try std.testing.expectEqual(@as(?usize, word_bits + 58), gate_mask.nextCpu(word_bits + 56));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 52), gate.nextSetBit(word_bits * 2 + 50));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 52), gate_mask.nextCpu(word_bits * 2 + 50));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 9), gate.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 9), gate_mask.lastCpu());

    try std.testing.expectEqual(@as(?usize, 0), gate.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), gate_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 4), gate.nextClearBit(word_bits * 3 + 4));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 4), gate_mask.nextMissingCpu(word_bits * 3 + 4));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 11), gate.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 11), gate_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), gate.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), gate_mask.nextCpu(capacity));
}

test "helix gate rollback keeps bypass and release masks disjoint" {
    const capacity = word_bits * 2 + 13;
    const bypass_words = [_]Word{
        bit(1) | bit(9) | bit(25) | bit(41) | bit(57),
        bit(word_bits + 4) | bit(word_bits + 20) |
            bit(word_bits + 36) | bit(word_bits + 52),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 12) | tailNoise(13),
    };
    const release_words = [_]Word{
        bit(6) | bit(14) | bit(30) | bit(46) | bit(62),
        bit(word_bits + 11) | bit(word_bits + 27) |
            bit(word_bits + 43) | bit(word_bits + 59),
        bit(word_bits * 2 + 7) | tailNoise(13),
    };
    const rollback_words = [_]Word{
        bypass_words[0] | release_words[0],
        bypass_words[1] | release_words[1],
        bypass_words[2] | release_words[2],
    };

    const bypass = makeView(bypass_words[0..], capacity);
    const release = makeView(release_words[0..], capacity);
    const rollback = makeView(rollback_words[0..], capacity);
    const bypass_mask = makeCpuMask(bypass_words[0..], capacity);
    const release_mask = makeCpuMask(release_words[0..], capacity);
    const rollback_mask = makeCpuMask(rollback_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 11), bypass.countSetBits());
    try std.testing.expectEqual(bypass.countSetBits(), bypass_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 10), release.countSetBits());
    try std.testing.expectEqual(release.countSetBits(), release_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 21), rollback.countSetBits());
    try std.testing.expectEqual(rollback.countSetBits(), rollback_mask.countPresentCpus());

    try std.testing.expect(bypass.isSubsetOf(rollback));
    try std.testing.expect(release.isSubsetOf(rollback));
    try std.testing.expect(bypass_mask.isSubsetOf(rollback_mask));
    try std.testing.expect(release_mask.isSubsetOf(rollback_mask));
    try std.testing.expect(!rollback.isSubsetOf(release));
    try std.testing.expect(!rollback_mask.isSubsetOf(release_mask));
    try std.testing.expect(!bypass.intersects(release));
    try std.testing.expect(!bypass_mask.intersects(release_mask));

    try std.testing.expectEqual(@as(?usize, 1), bypass.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 1), bypass_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 25), bypass.nextSetBit(10));
    try std.testing.expectEqual(@as(?usize, 25), bypass_mask.nextCpu(10));
    try std.testing.expectEqual(@as(?usize, word_bits + 52), bypass.nextSetBit(word_bits + 37));
    try std.testing.expectEqual(@as(?usize, word_bits + 52), bypass_mask.nextCpu(word_bits + 37));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 12), bypass.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 12), bypass_mask.lastCpu());

    try std.testing.expectEqual(@as(?usize, 6), release.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 6), release_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 7), release.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 7), release_mask.lastCpu());

    try std.testing.expectEqual(@as(?usize, 0), rollback.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), rollback_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 3), rollback.nextClearBit(word_bits * 2 + 3));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 3), rollback_mask.nextMissingCpu(word_bits * 2 + 3));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 11), rollback.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 11), rollback_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), rollback.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), rollback_mask.nextCpu(capacity));
}
