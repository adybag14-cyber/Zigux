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

test "stride corridor keeps staggered rails aligned" {
    const capacity = word_bits * 2 + 19;
    const primary_words = [_]Word{
        bit(1) | bit(9) | bit(17) | bit(25),
        bit(word_bits + 3) | bit(word_bits + 11) | bit(word_bits + 19),
        bit(word_bits * 2 + 5) | bit(word_bits * 2 + 13) | tailNoise(19),
    };
    const guard_words = [_]Word{
        bit(4) | bit(12) | bit(20),
        bit(word_bits + 6) | bit(word_bits + 14) | bit(word_bits + 22),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 17) | tailNoise(19),
    };
    const corridor_words = [_]Word{
        primary_words[0] | guard_words[0],
        primary_words[1] | guard_words[1] | bit(word_bits + 31),
        primary_words[2] | guard_words[2],
    };
    const outside_words = [_]Word{
        bit(0) | bit(30),
        bit(word_bits + 1) | bit(word_bits + 32),
        bit(word_bits * 2 + 3) | bit(word_bits * 2 + 18),
    };

    const primary = makeView(primary_words[0..], capacity);
    const guard = makeView(guard_words[0..], capacity);
    const corridor = makeView(corridor_words[0..], capacity);
    const outside = makeView(outside_words[0..], capacity);

    const primary_mask = makeCpuMask(primary_words[0..], capacity);
    const guard_mask = makeCpuMask(guard_words[0..], capacity);
    const corridor_mask = makeCpuMask(corridor_words[0..], capacity);
    const outside_mask = makeCpuMask(outside_words[0..], capacity);

    try std.testing.expectEqual(primary.countSetBits(), primary_mask.countPresentCpus());
    try std.testing.expectEqual(guard.countSetBits(), guard_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 18), corridor.countSetBits());
    try std.testing.expectEqual(corridor.countSetBits(), corridor_mask.countPresentCpus());

    try std.testing.expect(primary.isSubsetOf(corridor));
    try std.testing.expect(guard.isSubsetOf(corridor));
    try std.testing.expect(primary_mask.isSubsetOf(corridor_mask));
    try std.testing.expect(guard_mask.isSubsetOf(corridor_mask));
    try std.testing.expect(!corridor.isSubsetOf(primary));
    try std.testing.expect(!corridor_mask.isSubsetOf(primary_mask));

    try std.testing.expect(!primary.intersects(guard));
    try std.testing.expect(!primary_mask.intersects(guard_mask));
    try std.testing.expect(!corridor.intersects(outside));
    try std.testing.expect(!corridor_mask.intersects(outside_mask));

    try std.testing.expectEqual(@as(?usize, 1), corridor.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 1), corridor_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 17), corridor.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 17), corridor_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 3), corridor.nextSetBit(26));
    try std.testing.expectEqual(@as(?usize, word_bits + 3), corridor_mask.nextCpu(26));
    try std.testing.expectEqual(@as(?usize, 0), corridor.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), corridor_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 18), corridor.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 18), corridor_mask.lastMissingCpu());
}

test "stride corridor rollback clips declared tail noise" {
    const capacity = word_bits + 11;
    const acquire_words = [_]Word{
        bit(0) | bit(7) | bit(14) | bit(28) | bit(35),
        bit(word_bits + 2) | bit(word_bits + 7) | bit(word_bits + 10) | tailNoise(11),
    };
    const release_words = [_]Word{
        bit(7) | bit(35),
        bit(word_bits + 7) | tailNoise(11),
    };
    const retained_words = [_]Word{
        bit(0) | bit(14) | bit(28),
        bit(word_bits + 2) | bit(word_bits + 10) | tailNoise(11),
    };

    const acquire = makeView(acquire_words[0..], capacity);
    const release = makeView(release_words[0..], capacity);
    const retained = makeView(retained_words[0..], capacity);
    const acquire_mask = makeCpuMask(acquire_words[0..], capacity);
    const release_mask = makeCpuMask(release_words[0..], capacity);
    const retained_mask = makeCpuMask(retained_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 8), acquire.countSetBits());
    try std.testing.expectEqual(acquire.countSetBits(), acquire_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 3), release.countSetBits());
    try std.testing.expectEqual(release.countSetBits(), release_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 5), retained.countSetBits());
    try std.testing.expectEqual(retained.countSetBits(), retained_mask.countPresentCpus());

    try std.testing.expect(release.isSubsetOf(acquire));
    try std.testing.expect(retained.isSubsetOf(acquire));
    try std.testing.expect(release_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(retained_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(!release.intersects(retained));
    try std.testing.expect(!release_mask.intersects(retained_mask));

    try std.testing.expectEqual(@as(?usize, word_bits + 7), release.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits + 7), release_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 10), release.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits + 10), release_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), release.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), release_mask.nextCpu(capacity));
}
