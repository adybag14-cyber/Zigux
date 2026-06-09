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

test "crest braid keeps alternating crests aligned" {
    const capacity = word_bits * 3 + 23;
    const low_crest_words = [_]Word{
        bit(2) | bit(10) | bit(18) | bit(26),
        bit(word_bits + 4) | bit(word_bits + 12) | bit(word_bits + 20) | bit(word_bits + 28),
        bit(word_bits * 2 + 6) | bit(word_bits * 2 + 14) | bit(word_bits * 2 + 22) | bit(word_bits * 2 + 30),
        bit(word_bits * 3 + 5) | bit(word_bits * 3 + 13) | tailNoise(23),
    };
    const high_crest_words = [_]Word{
        bit(5) | bit(13) | bit(21) | bit(29),
        bit(word_bits + 1) | bit(word_bits + 9) | bit(word_bits + 17) | bit(word_bits + 25),
        bit(word_bits * 2 + 3) | bit(word_bits * 2 + 11) | bit(word_bits * 2 + 19) | bit(word_bits * 2 + 27),
        bit(word_bits * 3 + 2) | bit(word_bits * 3 + 21) | tailNoise(23),
    };
    const braid_words = [_]Word{
        low_crest_words[0] | high_crest_words[0] | bit(31),
        low_crest_words[1] | high_crest_words[1] | bit(word_bits + 31),
        low_crest_words[2] | high_crest_words[2],
        low_crest_words[3] | high_crest_words[3] | bit(word_bits * 3 + 16),
    };
    const outside_words = [_]Word{
        bit(0) | bit(32),
        bit(word_bits + 2) | bit(word_bits + 34),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 33),
        bit(word_bits * 3 + 1) | bit(word_bits * 3 + 22),
    };

    const low_crest = makeView(low_crest_words[0..], capacity);
    const high_crest = makeView(high_crest_words[0..], capacity);
    const braid = makeView(braid_words[0..], capacity);
    const outside = makeView(outside_words[0..], capacity);

    const low_crest_mask = makeCpuMask(low_crest_words[0..], capacity);
    const high_crest_mask = makeCpuMask(high_crest_words[0..], capacity);
    const braid_mask = makeCpuMask(braid_words[0..], capacity);
    const outside_mask = makeCpuMask(outside_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 14), low_crest.countSetBits());
    try std.testing.expectEqual(low_crest.countSetBits(), low_crest_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 14), high_crest.countSetBits());
    try std.testing.expectEqual(high_crest.countSetBits(), high_crest_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 31), braid.countSetBits());
    try std.testing.expectEqual(braid.countSetBits(), braid_mask.countPresentCpus());

    try std.testing.expect(low_crest.isSubsetOf(braid));
    try std.testing.expect(high_crest.isSubsetOf(braid));
    try std.testing.expect(low_crest_mask.isSubsetOf(braid_mask));
    try std.testing.expect(high_crest_mask.isSubsetOf(braid_mask));
    try std.testing.expect(!braid.isSubsetOf(low_crest));
    try std.testing.expect(!braid_mask.isSubsetOf(low_crest_mask));

    try std.testing.expect(!low_crest.intersects(high_crest));
    try std.testing.expect(!low_crest_mask.intersects(high_crest_mask));
    try std.testing.expect(!braid.intersects(outside));
    try std.testing.expect(!braid_mask.intersects(outside_mask));

    try std.testing.expect(braid.isSet(word_bits * 3 + 16));
    try std.testing.expect(braid_mask.hasCpu(word_bits * 3 + 16));
    try std.testing.expectEqual(@as(?usize, 2), braid.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 2), braid_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 21), braid.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 21), braid_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, 31), braid.nextSetBit(30));
    try std.testing.expectEqual(@as(?usize, 31), braid_mask.nextCpu(30));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), braid.nextSetBit(32));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), braid_mask.nextCpu(32));
    try std.testing.expectEqual(@as(?usize, 0), braid.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), braid_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 22), braid.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 22), braid_mask.lastMissingCpu());
}

test "crest braid rollback clips declared tail noise" {
    const capacity = word_bits * 2 + 9;
    const acquire_words = [_]Word{
        bit(0) | bit(7) | bit(14) | bit(21) | bit(28) | bit(35),
        bit(word_bits + 2) | bit(word_bits + 9) | bit(word_bits + 16) | bit(word_bits + 23) | bit(word_bits + 31),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 8) | tailNoise(9),
    };
    const release_words = [_]Word{
        bit(7) | bit(28),
        bit(word_bits + 9) | bit(word_bits + 31),
        bit(word_bits * 2 + 8) | tailNoise(9),
    };
    const retained_words = [_]Word{
        bit(0) | bit(14) | bit(21) | bit(35),
        bit(word_bits + 2) | bit(word_bits + 16) | bit(word_bits + 23),
        bit(word_bits * 2 + 1) | tailNoise(9),
    };

    const acquire = makeView(acquire_words[0..], capacity);
    const release = makeView(release_words[0..], capacity);
    const retained = makeView(retained_words[0..], capacity);
    const acquire_mask = makeCpuMask(acquire_words[0..], capacity);
    const release_mask = makeCpuMask(release_words[0..], capacity);
    const retained_mask = makeCpuMask(retained_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 13), acquire.countSetBits());
    try std.testing.expectEqual(acquire.countSetBits(), acquire_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 5), release.countSetBits());
    try std.testing.expectEqual(release.countSetBits(), release_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 8), retained.countSetBits());
    try std.testing.expectEqual(retained.countSetBits(), retained_mask.countPresentCpus());

    try std.testing.expect(release.isSubsetOf(acquire));
    try std.testing.expect(retained.isSubsetOf(acquire));
    try std.testing.expect(release_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(retained_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(!release.intersects(retained));
    try std.testing.expect(!release_mask.intersects(retained_mask));

    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), release.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), release_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 7), release.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 7), release_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), release.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), release_mask.nextCpu(capacity));
}
