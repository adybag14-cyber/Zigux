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

test "midpoint carry mirrors split lanes across bitmap and cpumask" {
    const capacity = word_bits * 2 + 13;
    const midpoint_words = [_]Word{
        bit(3) | bit(9) | bit(21) | bit(34) | bit(48) | bit(62),
        bit(word_bits + 0) | bit(word_bits + 4) | bit(word_bits + 11) |
            bit(word_bits + 23) | bit(word_bits + 39) | bit(word_bits + 58),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 7) |
            bit(word_bits * 2 + 12) | tailNoise(13),
    };
    const lower_lane_words = [_]Word{
        bit(3) | bit(21) | bit(48) | bit(62),
        bit(word_bits + 4) | bit(word_bits + 39),
        bit(word_bits * 2 + 7) | tailNoise(13),
    };
    const upper_lane_words = [_]Word{
        bit(9) | bit(34),
        bit(word_bits + 0) | bit(word_bits + 11) | bit(word_bits + 58),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 12) | tailNoise(13),
    };
    const bridge_words = [_]Word{
        0,
        bit(word_bits + 23),
        tailNoise(13),
    };
    const guard_words = [_]Word{
        bit(0) | bit(7) | bit(14) | bit(28) | bit(41) | bit(55),
        bit(word_bits + 2) | bit(word_bits + 8) | bit(word_bits + 16) |
            bit(word_bits + 31) | bit(word_bits + 47),
        bit(word_bits * 2 + 0) | bit(word_bits * 2 + 5) |
            bit(word_bits * 2 + 10),
    };

    const midpoint = makeView(midpoint_words[0..], capacity);
    const lower_lane = makeView(lower_lane_words[0..], capacity);
    const upper_lane = makeView(upper_lane_words[0..], capacity);
    const bridge = makeView(bridge_words[0..], capacity);
    const guard = makeView(guard_words[0..], capacity);
    const midpoint_mask = makeCpuMask(midpoint_words[0..], capacity);
    const lower_lane_mask = makeCpuMask(lower_lane_words[0..], capacity);
    const upper_lane_mask = makeCpuMask(upper_lane_words[0..], capacity);
    const bridge_mask = makeCpuMask(bridge_words[0..], capacity);
    const guard_mask = makeCpuMask(guard_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 15), midpoint.countSetBits());
    try std.testing.expectEqual(midpoint.countSetBits(), midpoint_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 7), lower_lane.countSetBits());
    try std.testing.expectEqual(lower_lane.countSetBits(), lower_lane_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 7), upper_lane.countSetBits());
    try std.testing.expectEqual(upper_lane.countSetBits(), upper_lane_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 1), bridge.countSetBits());
    try std.testing.expectEqual(bridge.countSetBits(), bridge_mask.countPresentCpus());

    try std.testing.expect(lower_lane.isSubsetOf(midpoint));
    try std.testing.expect(upper_lane.isSubsetOf(midpoint));
    try std.testing.expect(bridge.isSubsetOf(midpoint));
    try std.testing.expect(lower_lane_mask.isSubsetOf(midpoint_mask));
    try std.testing.expect(upper_lane_mask.isSubsetOf(midpoint_mask));
    try std.testing.expect(bridge_mask.isSubsetOf(midpoint_mask));
    try std.testing.expect(!midpoint.isSubsetOf(lower_lane));
    try std.testing.expect(!midpoint_mask.isSubsetOf(lower_lane_mask));

    try std.testing.expect(!lower_lane.intersects(upper_lane));
    try std.testing.expect(!lower_lane.intersects(bridge));
    try std.testing.expect(!upper_lane.intersects(bridge));
    try std.testing.expect(!lower_lane_mask.intersects(upper_lane_mask));
    try std.testing.expect(!lower_lane_mask.intersects(bridge_mask));
    try std.testing.expect(!upper_lane_mask.intersects(bridge_mask));
    try std.testing.expect(!midpoint.intersects(guard));
    try std.testing.expect(!midpoint_mask.intersects(guard_mask));

    try std.testing.expect(midpoint.isSet(word_bits * 2 + 12));
    try std.testing.expect(midpoint_mask.hasCpu(word_bits * 2 + 12));
    try std.testing.expectEqual(@as(?usize, 3), midpoint.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 3), midpoint_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 0), midpoint.nextSetBit(63));
    try std.testing.expectEqual(@as(?usize, word_bits + 0), midpoint_mask.nextCpu(63));
    try std.testing.expectEqual(@as(?usize, word_bits + 39), midpoint.nextSetBit(word_bits + 24));
    try std.testing.expectEqual(@as(?usize, word_bits + 39), midpoint_mask.nextCpu(word_bits + 24));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 12), midpoint.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 12), midpoint_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, 0), midpoint.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), midpoint_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), midpoint.nextClearBit(word_bits * 2 + 8));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), midpoint_mask.nextMissingCpu(word_bits * 2 + 8));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 11), midpoint.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 11), midpoint_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), midpoint.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), midpoint_mask.nextCpu(capacity));
}

test "midpoint carry rollback keeps retained and released lanes disjoint" {
    const capacity = word_bits * 2 + 5;
    const acquire_words = [_]Word{
        bit(0) | bit(6) | bit(12) | bit(18) | bit(24) | bit(30) |
            bit(36) | bit(42) | bit(48) | bit(54) | bit(60),
        bit(word_bits + 1) | bit(word_bits + 7) | bit(word_bits + 13) |
            bit(word_bits + 27) | bit(word_bits + 41) | bit(word_bits + 55) |
            bit(word_bits + 63),
        bit(word_bits * 2 + 0) | bit(word_bits * 2 + 4) | tailNoise(5),
    };
    const retain_words = [_]Word{
        bit(0) | bit(24) | bit(48),
        bit(word_bits + 13) | bit(word_bits + 41),
        bit(word_bits * 2 + 4) | tailNoise(5),
    };
    const release_words = [_]Word{
        bit(6) | bit(12) | bit(18) | bit(30) | bit(36) | bit(42) |
            bit(54) | bit(60),
        bit(word_bits + 1) | bit(word_bits + 7) | bit(word_bits + 27) |
            bit(word_bits + 55) | bit(word_bits + 63),
        bit(word_bits * 2 + 0) | tailNoise(5),
    };

    const acquire = makeView(acquire_words[0..], capacity);
    const retain = makeView(retain_words[0..], capacity);
    const release = makeView(release_words[0..], capacity);
    const acquire_mask = makeCpuMask(acquire_words[0..], capacity);
    const retain_mask = makeCpuMask(retain_words[0..], capacity);
    const release_mask = makeCpuMask(release_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 20), acquire.countSetBits());
    try std.testing.expectEqual(acquire.countSetBits(), acquire_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 6), retain.countSetBits());
    try std.testing.expectEqual(retain.countSetBits(), retain_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 14), release.countSetBits());
    try std.testing.expectEqual(release.countSetBits(), release_mask.countPresentCpus());

    try std.testing.expect(retain.isSubsetOf(acquire));
    try std.testing.expect(release.isSubsetOf(acquire));
    try std.testing.expect(retain_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(release_mask.isSubsetOf(acquire_mask));
    try std.testing.expect(!retain.intersects(release));
    try std.testing.expect(!retain_mask.intersects(release_mask));

    try std.testing.expectEqual(@as(?usize, 0), retain.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 0), retain_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 24), retain.nextSetBit(1));
    try std.testing.expectEqual(@as(?usize, 24), retain_mask.nextCpu(1));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 4), retain.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 4), retain_mask.lastCpu());
    try std.testing.expectEqual(@as(?usize, 1), retain.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 1), retain_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 3), retain.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 3), retain_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), retain.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), retain_mask.nextCpu(capacity));
}
