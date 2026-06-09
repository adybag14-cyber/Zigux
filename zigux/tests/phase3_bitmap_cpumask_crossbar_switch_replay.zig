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

test "crossbar switch keeps low and high rails aligned" {
    const capacity = word_bits * 2 + 17;
    const low_words = [_]Word{
        bit(2) | bit(9) | bit(17),
        bit(word_bits + 3) | bit(word_bits + 11),
        bit(word_bits * 2 + 4) | tailNoise(17),
    };
    const high_words = [_]Word{
        bit(5) | bit(14),
        bit(word_bits + 7) | bit(word_bits + 19) | bit(word_bits + 23),
        bit(word_bits * 2 + 12) | tailNoise(17),
    };
    const bridge_words = [_]Word{
        low_words[0] | high_words[0],
        low_words[1] | high_words[1] | bit(word_bits + 15),
        low_words[2] | high_words[2],
    };
    const outside_words = [_]Word{
        bit(0) | bit(40),
        bit(word_bits + 1) | bit(word_bits + 27),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 16),
    };

    const low = makeView(low_words[0..], capacity);
    const high = makeView(high_words[0..], capacity);
    const bridge = makeView(bridge_words[0..], capacity);
    const outside = makeView(outside_words[0..], capacity);

    const low_mask = makeCpuMask(low_words[0..], capacity);
    const high_mask = makeCpuMask(high_words[0..], capacity);
    const bridge_mask = makeCpuMask(bridge_words[0..], capacity);
    const outside_mask = makeCpuMask(outside_words[0..], capacity);

    try std.testing.expectEqual(low.countSetBits(), low_mask.countPresentCpus());
    try std.testing.expectEqual(high.countSetBits(), high_mask.countPresentCpus());
    try std.testing.expectEqual(13, bridge.countSetBits());
    try std.testing.expectEqual(bridge.countSetBits(), bridge_mask.countPresentCpus());

    try std.testing.expect(low.isSubsetOf(bridge));
    try std.testing.expect(high.isSubsetOf(bridge));
    try std.testing.expect(low_mask.isSubsetOf(bridge_mask));
    try std.testing.expect(high_mask.isSubsetOf(bridge_mask));
    try std.testing.expect(!bridge.isSubsetOf(low));
    try std.testing.expect(!bridge_mask.isSubsetOf(low_mask));

    try std.testing.expect(!low.intersects(high));
    try std.testing.expect(!low_mask.intersects(high_mask));
    try std.testing.expect(!bridge.intersects(outside));
    try std.testing.expect(!bridge_mask.intersects(outside_mask));

    try std.testing.expectEqual(@as(?usize, 2), bridge.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 2), bridge_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 12), bridge.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 12), bridge_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 15), bridge.nextSetBit(word_bits + 12));
    try std.testing.expectEqual(@as(?usize, word_bits + 15), bridge_mask.nextCpu(word_bits + 12));
    try std.testing.expectEqual(@as(?usize, 0), bridge.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), bridge_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 16), bridge.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 16), bridge_mask.lastMissingCpu());
}

test "crossbar switch release lane preserves declared tail clipping" {
    const capacity = word_bits + 13;
    const acquire_words = [_]Word{
        bit(1) | bit(6) | bit(12) | bit(21),
        bit(word_bits + 2) | bit(word_bits + 8) | tailNoise(13),
    };
    const release_words = [_]Word{
        bit(1) | bit(12),
        bit(word_bits + 8) | tailNoise(13),
    };
    const retained_words = [_]Word{
        bit(6) | bit(21),
        bit(word_bits + 2) | tailNoise(13),
    };

    const acquire = makeView(acquire_words[0..], capacity);
    const release = makeView(release_words[0..], capacity);
    const retained = makeView(retained_words[0..], capacity);
    const acquire_mask = makeCpuMask(acquire_words[0..], capacity);
    const release_mask = makeCpuMask(release_words[0..], capacity);
    const retained_mask = makeCpuMask(retained_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 6), acquire.countSetBits());
    try std.testing.expectEqual(acquire.countSetBits(), acquire_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 3), release.countSetBits());
    try std.testing.expectEqual(release.countSetBits(), release_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 3), retained.countSetBits());
    try std.testing.expectEqual(retained.countSetBits(), retained_mask.countPresentCpus());

    try std.testing.expect(release.isSubsetOf(acquire));
    try std.testing.expect(retained.isSubsetOf(acquire));
    try std.testing.expect(release_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(retained_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(!release.intersects(retained));
    try std.testing.expect(!release_mask.intersects(retained_mask));

    try std.testing.expectEqual(@as(?usize, word_bits + 8), release.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits + 8), release_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 12), release.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits + 12), release_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), release.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), release_mask.nextCpu(capacity));
}
