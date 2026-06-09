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

test "apex span mirrors split rails across bitmap and cpumask" {
    const capacity = word_bits * 3 + 13;
    const apex_words = [_]Word{
        bit(2) | bit(9) | bit(16) | bit(23) | bit(30) | bit(37) | bit(44) | bit(51) | bit(58),
        bit(word_bits + 4) | bit(word_bits + 12) | bit(word_bits + 20) | bit(word_bits + 28) |
            bit(word_bits + 36) | bit(word_bits + 44) | bit(word_bits + 52) | bit(word_bits + 60),
        bit(word_bits * 2 + 6) | bit(word_bits * 2 + 18) | bit(word_bits * 2 + 30) |
            bit(word_bits * 2 + 42) | bit(word_bits * 2 + 54),
        bit(word_bits * 3 + 1) | bit(word_bits * 3 + 7) | bit(word_bits * 3 + 12) | tailNoise(13),
    };
    const lower_words = [_]Word{
        bit(2) | bit(23) | bit(44),
        bit(word_bits + 12) | bit(word_bits + 36) | bit(word_bits + 60),
        bit(word_bits * 2 + 18) | bit(word_bits * 2 + 42),
        bit(word_bits * 3 + 7) | bit(word_bits * 3 + 12) | tailNoise(13),
    };
    const crown_words = [_]Word{
        bit(9) | bit(16) | bit(30) | bit(37) | bit(51) | bit(58),
        bit(word_bits + 4) | bit(word_bits + 20) | bit(word_bits + 28) |
            bit(word_bits + 44) | bit(word_bits + 52),
        bit(word_bits * 2 + 6) | bit(word_bits * 2 + 30) | bit(word_bits * 2 + 54),
        bit(word_bits * 3 + 1) | tailNoise(13),
    };
    const guard_words = [_]Word{
        bit(0) | bit(7) | bit(14) | bit(21) | bit(28) | bit(35) | bit(42) | bit(49) | bit(56),
        bit(word_bits + 1) | bit(word_bits + 8) | bit(word_bits + 15) | bit(word_bits + 22) |
            bit(word_bits + 29) | bit(word_bits + 43) | bit(word_bits + 50) | bit(word_bits + 57),
        bit(word_bits * 2 + 0) | bit(word_bits * 2 + 12) | bit(word_bits * 2 + 24) |
            bit(word_bits * 2 + 36) | bit(word_bits * 2 + 48),
        bit(word_bits * 3 + 0) | bit(word_bits * 3 + 6) | bit(word_bits * 3 + 11),
    };

    const apex = makeView(apex_words[0..], capacity);
    const lower = makeView(lower_words[0..], capacity);
    const crown = makeView(crown_words[0..], capacity);
    const guard = makeView(guard_words[0..], capacity);
    const apex_mask = makeCpuMask(apex_words[0..], capacity);
    const lower_mask = makeCpuMask(lower_words[0..], capacity);
    const crown_mask = makeCpuMask(crown_words[0..], capacity);
    const guard_mask = makeCpuMask(guard_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 25), apex.countSetBits());
    try std.testing.expectEqual(apex.countSetBits(), apex_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 10), lower.countSetBits());
    try std.testing.expectEqual(lower.countSetBits(), lower_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 15), crown.countSetBits());
    try std.testing.expectEqual(crown.countSetBits(), crown_mask.countPresentCpus());

    try std.testing.expect(lower.isSubsetOf(apex));
    try std.testing.expect(crown.isSubsetOf(apex));
    try std.testing.expect(lower_mask.isSubsetOf(apex_mask));
    try std.testing.expect(crown_mask.isSubsetOf(apex_mask));
    try std.testing.expect(!apex.isSubsetOf(lower));
    try std.testing.expect(!apex_mask.isSubsetOf(lower_mask));
    try std.testing.expect(!lower.intersects(crown));
    try std.testing.expect(!lower_mask.intersects(crown_mask));
    try std.testing.expect(!apex.intersects(guard));
    try std.testing.expect(!apex_mask.intersects(guard_mask));

    try std.testing.expect(apex.isSet(word_bits * 3 + 12));
    try std.testing.expect(apex_mask.hasCpu(word_bits * 3 + 12));
    try std.testing.expectEqual(@as(?usize, 2), apex.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 2), apex_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 12), apex.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 12), apex_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 4), apex.nextSetBit(59));
    try std.testing.expectEqual(@as(?usize, word_bits + 4), apex_mask.nextCpu(59));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 12), apex.nextSetBit(word_bits * 3 + 8));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 12), apex_mask.nextCpu(word_bits * 3 + 8));
    try std.testing.expectEqual(@as(?usize, 0), apex.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), apex_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 11), apex.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 11), apex_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), apex.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), apex_mask.nextCpu(capacity));
}

test "apex span rollback clips final-bank tail noise" {
    const capacity = word_bits * 2 + 6;
    const acquire_words = [_]Word{
        bit(0) | bit(10) | bit(20) | bit(30) | bit(40) | bit(50) | bit(word_bits - 1),
        bit(word_bits + 3) | bit(word_bits + 15) | bit(word_bits + 27) |
            bit(word_bits + 39) | bit(word_bits + 51),
        bit(word_bits * 2 + 0) | bit(word_bits * 2 + 5) | tailNoise(6),
    };
    const keep_words = [_]Word{
        bit(0) | bit(30) | bit(word_bits - 1),
        bit(word_bits + 15) | bit(word_bits + 39),
        bit(word_bits * 2 + 5) | tailNoise(6),
    };
    const release_words = [_]Word{
        bit(10) | bit(20) | bit(40) | bit(50),
        bit(word_bits + 3) | bit(word_bits + 27) | bit(word_bits + 51),
        bit(word_bits * 2 + 0) | tailNoise(6),
    };

    const acquire = makeView(acquire_words[0..], capacity);
    const keep = makeView(keep_words[0..], capacity);
    const release = makeView(release_words[0..], capacity);
    const acquire_mask = makeCpuMask(acquire_words[0..], capacity);
    const keep_mask = makeCpuMask(keep_words[0..], capacity);
    const release_mask = makeCpuMask(release_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 14), acquire.countSetBits());
    try std.testing.expectEqual(acquire.countSetBits(), acquire_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 6), keep.countSetBits());
    try std.testing.expectEqual(keep.countSetBits(), keep_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 8), release.countSetBits());
    try std.testing.expectEqual(release.countSetBits(), release_mask.countPresentCpus());

    try std.testing.expect(keep.isSubsetOf(acquire));
    try std.testing.expect(release.isSubsetOf(acquire));
    try std.testing.expect(keep_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(release_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(!keep.intersects(release));
    try std.testing.expect(!keep_mask.intersects(release_mask));

    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 5), keep.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 5), keep_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 4), keep.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 4), keep_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), keep.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), keep_mask.nextCpu(capacity));
}
