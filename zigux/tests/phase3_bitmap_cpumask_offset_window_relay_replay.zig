const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(offset: usize) Word {
    std.debug.assert(offset < word_bits);
    return @as(Word, 1) << @intCast(offset);
}

const capacity = word_bits * 2 + 11;

const base_words = [_]Word{
    bit(2) | bit(5) | bit(13),
    bit(1) | bit(9) | bit(17),
    bit(4) | bit(9) | bit(20),
};

const relay_words = [_]Word{
    base_words[0] | bit(21),
    base_words[1] | bit(22),
    base_words[2] | bit(10) | bit(24),
};

const release_words = [_]Word{
    bit(21),
    bit(22),
    bit(10) | bit(24),
};

const gap_words = [_]Word{
    bit(0) | bit(7),
    bit(3),
    bit(2) | bit(30),
};

test "offset window relay mirrors bitmap and cpumask cursors" {
    const base = BitmapView.init(base_words[0..], capacity);
    const relay = BitmapView.init(relay_words[0..], capacity);
    const base_cpus = CpuMaskView.init(base_words[0..], capacity);
    const relay_cpus = CpuMaskView.init(relay_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 8), base.countSetBits());
    try std.testing.expectEqual(base.countSetBits(), base_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 2), base.firstSetBit());
    try std.testing.expectEqual(base.firstSetBit(), base_cpus.firstCpu());
    try std.testing.expectEqual(@as(?usize, 5), base.nextSetBit(3));
    try std.testing.expectEqual(base.nextSetBit(word_bits), base_cpus.nextCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 9), base.lastSetBit());
    try std.testing.expectEqual(base.lastSetBit(), base_cpus.lastCpu());

    try std.testing.expectEqual(@as(usize, 11), relay.countSetBits());
    try std.testing.expectEqual(relay.countSetBits(), relay_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 10), relay.lastSetBit());
    try std.testing.expectEqual(relay.lastSetBit(), relay_cpus.lastCpu());
    try std.testing.expect(relay_cpus.hasCpu(word_bits * 2 + 10));

    try std.testing.expectEqual(@as(?usize, 0), base.firstClearBit());
    try std.testing.expectEqual(base.firstClearBit(), base_cpus.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, 3), base.nextClearBit(2));
    try std.testing.expectEqual(base.nextClearBit(word_bits + 1), base_cpus.nextMissingCpu(word_bits + 1));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 10), base.lastClearBit());
    try std.testing.expectEqual(base.lastClearBit(), base_cpus.lastMissingCpu());

    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), relay.lastClearBit());
    try std.testing.expectEqual(relay.lastClearBit(), relay_cpus.lastMissingCpu());
}

test "offset window relay keeps relation and release masks bounded" {
    const base = BitmapView.init(base_words[0..], capacity);
    const relay = BitmapView.init(relay_words[0..], capacity);
    const release = BitmapView.init(release_words[0..], capacity);
    const gap = BitmapView.init(gap_words[0..], capacity);

    const base_cpus = CpuMaskView.init(base_words[0..], capacity);
    const relay_cpus = CpuMaskView.init(relay_words[0..], capacity);
    const release_cpus = CpuMaskView.init(release_words[0..], capacity);
    const gap_cpus = CpuMaskView.init(gap_words[0..], capacity);

    try std.testing.expect(base.isSubsetOf(relay));
    try std.testing.expect(base_cpus.isSubsetOf(relay_cpus));
    try std.testing.expect(!relay.isSubsetOf(base));
    try std.testing.expect(!relay_cpus.isSubsetOf(base_cpus));

    try std.testing.expect(release.isSubsetOf(relay));
    try std.testing.expect(release_cpus.isSubsetOf(relay_cpus));
    try std.testing.expect(!release.intersects(base));
    try std.testing.expect(!release_cpus.intersects(base_cpus));

    try std.testing.expect(base.intersects(relay));
    try std.testing.expect(base_cpus.intersects(relay_cpus));
    try std.testing.expect(!gap.intersects(relay));
    try std.testing.expect(!gap_cpus.intersects(relay_cpus));

    try std.testing.expectEqual(@as(usize, 3), release.countSetBits());
    try std.testing.expectEqual(release.countSetBits(), release_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 21), release.firstSetBit());
    try std.testing.expectEqual(release.firstSetBit(), release_cpus.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 10), release.lastSetBit());
    try std.testing.expectEqual(release.lastSetBit(), release_cpus.lastCpu());
}
