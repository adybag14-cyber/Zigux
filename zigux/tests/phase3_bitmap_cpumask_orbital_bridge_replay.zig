const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const word_bits = bitmap_view.word_bits;

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index % word_bits);
}

test "bitmap and cpumask agree across orbital bridge handoff" {
    const capacity = word_bits * 2 + 13;
    const tail_noise = bit(word_bits * 2 + 20);

    const core_words = [_]usize{
        bit(2),
        bit(word_bits + 3),
        bit(word_bits * 2 + 5) | tail_noise,
    };
    const bridge_words = [_]usize{
        bit(7),
        bit(word_bits + 3) | bit(word_bits + 9),
        bit(word_bits * 2 + 5) | tail_noise,
    };
    const orbit_words = [_]usize{
        bit(1) | bit(7),
        bit(word_bits + 3) | bit(word_bits + 9),
        bit(word_bits * 2 + 5) | bit(word_bits * 2 + 8) | tail_noise,
    };
    const release_words = [_]usize{
        bit(7),
        bit(word_bits + 9),
        tail_noise,
    };
    const disjoint_words = [_]usize{
        bit(0),
        bit(word_bits + 1),
        bit(word_bits * 2 + 3) | tail_noise,
    };

    const core = BitmapView.init(core_words[0..], capacity);
    const bridge = BitmapView.init(bridge_words[0..], capacity);
    const orbit = BitmapView.init(orbit_words[0..], capacity);
    const release = BitmapView.init(release_words[0..], capacity);
    const disjoint = BitmapView.init(disjoint_words[0..], capacity);

    const core_cpus = CpuMaskView.init(core_words[0..], capacity);
    const bridge_cpus = CpuMaskView.init(bridge_words[0..], capacity);
    const orbit_cpus = CpuMaskView.init(orbit_words[0..], capacity);
    const release_cpus = CpuMaskView.init(release_words[0..], capacity);
    const disjoint_cpus = CpuMaskView.init(disjoint_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 3), core.countSetBits());
    try std.testing.expectEqual(@as(usize, 4), bridge.countSetBits());
    try std.testing.expectEqual(@as(usize, 6), orbit.countSetBits());
    try std.testing.expectEqual(@as(usize, 2), release.countSetBits());
    try std.testing.expectEqual(@as(usize, 3), disjoint.countSetBits());

    try std.testing.expectEqual(core.countSetBits(), core_cpus.countPresentCpus());
    try std.testing.expectEqual(bridge.countSetBits(), bridge_cpus.countPresentCpus());
    try std.testing.expectEqual(orbit.countSetBits(), orbit_cpus.countPresentCpus());
    try std.testing.expectEqual(release.countSetBits(), release_cpus.countPresentCpus());

    try std.testing.expect(bridge.isSubsetOf(orbit));
    try std.testing.expect(release.isSubsetOf(bridge));
    try std.testing.expect(!core.isSubsetOf(bridge));
    try std.testing.expect(!orbit.isSubsetOf(bridge));
    try std.testing.expect(!disjoint.intersects(orbit));
    try std.testing.expect(core.intersects(bridge));

    try std.testing.expect(bridge_cpus.isSubsetOf(orbit_cpus));
    try std.testing.expect(release_cpus.isSubsetOf(bridge_cpus));
    try std.testing.expect(!core_cpus.isSubsetOf(bridge_cpus));
    try std.testing.expect(!disjoint_cpus.intersects(orbit_cpus));
    try std.testing.expect(core_cpus.intersects(bridge_cpus));

    try std.testing.expectEqual(@as(?usize, 1), orbit.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 7), orbit.nextSetBit(2));
    try std.testing.expectEqual(@as(?usize, word_bits + 3), orbit.nextSetBit(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 5), orbit.nextSetBit(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, null), orbit.nextSetBit(capacity));

    try std.testing.expectEqual(orbit.firstSetBit(), orbit_cpus.firstCpu());
    try std.testing.expectEqual(orbit.nextSetBit(2), orbit_cpus.nextCpu(2));
    try std.testing.expectEqual(orbit.nextSetBit(word_bits), orbit_cpus.nextCpu(word_bits));
    try std.testing.expectEqual(orbit.nextSetBit(word_bits * 2), orbit_cpus.nextCpu(word_bits * 2));

    try std.testing.expectEqual(@as(?usize, 0), orbit.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 2), orbit.nextClearBit(2));
    try std.testing.expectEqual(@as(?usize, word_bits + 4), orbit.nextClearBit(word_bits + 4));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 9), orbit.nextClearBit(word_bits * 2 + 9));
    try std.testing.expectEqual(@as(?usize, null), orbit.nextClearBit(capacity));

    try std.testing.expectEqual(orbit.firstClearBit(), orbit_cpus.firstMissingCpu());
    try std.testing.expectEqual(orbit.nextClearBit(2), orbit_cpus.nextMissingCpu(2));
    try std.testing.expectEqual(orbit.nextClearBit(word_bits + 4), orbit_cpus.nextMissingCpu(word_bits + 4));
    try std.testing.expectEqual(orbit.nextClearBit(word_bits * 2 + 9), orbit_cpus.nextMissingCpu(word_bits * 2 + 9));

    try std.testing.expect(orbit_cpus.hasCpu(word_bits * 2 + 8));
    try std.testing.expect(!orbit_cpus.hasCpu(word_bits * 2 + 9));
}

test "orbital bridge clipping ignores declared tail fill" {
    const capacity = word_bits + 5;
    const tail_noise = std.math.maxInt(usize) & ~((@as(usize, 1) << 5) - 1);

    const orbit_words = [_]usize{
        bit(0) | bit(4) | bit(9),
        bit(word_bits + 1) | bit(word_bits + 4) | tail_noise,
    };
    const bridge_words = [_]usize{
        bit(4),
        bit(word_bits + 4) | tail_noise,
    };
    const outside_words = [_]usize{
        bit(2),
        tail_noise,
    };

    const orbit = BitmapView.init(orbit_words[0..], capacity);
    const bridge = BitmapView.init(bridge_words[0..], capacity);
    const outside = BitmapView.init(outside_words[0..], capacity);
    const orbit_cpus = CpuMaskView.init(orbit_words[0..], capacity);
    const bridge_cpus = CpuMaskView.init(bridge_words[0..], capacity);
    const outside_cpus = CpuMaskView.init(outside_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 5), orbit.countSetBits());
    try std.testing.expectEqual(@as(usize, 2), bridge.countSetBits());
    try std.testing.expectEqual(@as(usize, 1), outside.countSetBits());
    try std.testing.expect(bridge.isSubsetOf(orbit));
    try std.testing.expect(!outside.intersects(orbit));

    try std.testing.expectEqual(orbit.countSetBits(), orbit_cpus.countPresentCpus());
    try std.testing.expectEqual(bridge.countSetBits(), bridge_cpus.countPresentCpus());
    try std.testing.expectEqual(outside.countSetBits(), outside_cpus.countPresentCpus());
    try std.testing.expect(bridge_cpus.isSubsetOf(orbit_cpus));
    try std.testing.expect(!outside_cpus.intersects(orbit_cpus));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), orbit.nextSetBit(word_bits));
    try std.testing.expectEqual(@as(?usize, null), orbit.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), orbit_cpus.nextCpu(capacity));
}
