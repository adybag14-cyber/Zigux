const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const word_bits = bitmap_view.word_bits;

fn setBit(words: *[3]usize, bit: usize) void {
    words[bit / word_bits] |= @as(usize, 1) << @intCast(bit % word_bits);
}

fn viewFrom(words: *const [3]usize, capacity: usize) BitmapView {
    return BitmapView.init(words[0..], capacity);
}

fn cpuViewFrom(words: *const [3]usize, capacity: usize) CpuMaskView {
    return CpuMaskView.init(words[0..], capacity);
}

fn seedPhaseWindow() struct {
    stable: [3]usize,
    handoff: [3]usize,
    promoted: [3]usize,
    bridge: [3]usize,
    outside: [3]usize,
    noisy_full: [3]usize,
} {
    var stable = [_]usize{ 0, 0, 0 };
    var handoff = [_]usize{ 0, 0, 0 };
    var bridge = [_]usize{ 0, 0, 0 };
    var outside = [_]usize{ 0, 0, 0 };

    for ([_]usize{ 1, 7, word_bits + 5, word_bits + 18, 2 * word_bits + 4 }) |bit| {
        setBit(&stable, bit);
    }
    for ([_]usize{ 12, word_bits + 5, word_bits + 18, word_bits + 31, 2 * word_bits + 10 }) |bit| {
        setBit(&handoff, bit);
    }
    for ([_]usize{ word_bits + 5, word_bits + 18 }) |bit| {
        setBit(&bridge, bit);
    }
    for ([_]usize{ 3, word_bits + 9, 2 * word_bits + 1 }) |bit| {
        setBit(&outside, bit);
    }

    return .{
        .stable = stable,
        .handoff = handoff,
        .promoted = .{
            stable[0] | handoff[0],
            stable[1] | handoff[1],
            stable[2] | handoff[2],
        },
        .bridge = bridge,
        .outside = outside,
        .noisy_full = .{
            stable[0] | handoff[0],
            stable[1] | handoff[1],
            stable[2] | handoff[2] | ~((@as(usize, 1) << 13) - 1),
        },
    };
}

test "phase window handoff keeps bitmap and cpumask relation mirrors" {
    const capacity = 2 * word_bits + 13;
    const window = seedPhaseWindow();

    const stable = viewFrom(&window.stable, capacity);
    const handoff = viewFrom(&window.handoff, capacity);
    const promoted = viewFrom(&window.promoted, capacity);
    const bridge = viewFrom(&window.bridge, capacity);
    const outside = viewFrom(&window.outside, capacity);

    const stable_cpus = cpuViewFrom(&window.stable, capacity);
    const handoff_cpus = cpuViewFrom(&window.handoff, capacity);
    const promoted_cpus = cpuViewFrom(&window.promoted, capacity);
    const bridge_cpus = cpuViewFrom(&window.bridge, capacity);
    const outside_cpus = cpuViewFrom(&window.outside, capacity);

    try std.testing.expectEqual(@as(usize, 5), stable.countSetBits());
    try std.testing.expectEqual(stable.countSetBits(), stable_cpus.countPresentCpus());
    try std.testing.expectEqual(handoff.countSetBits(), handoff_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 8), promoted.countSetBits());
    try std.testing.expectEqual(promoted.countSetBits(), promoted_cpus.countPresentCpus());

    try std.testing.expect(bridge.isSubsetOf(stable));
    try std.testing.expect(bridge.isSubsetOf(handoff));
    try std.testing.expect(bridge_cpus.isSubsetOf(stable_cpus));
    try std.testing.expect(bridge_cpus.isSubsetOf(handoff_cpus));

    try std.testing.expect(stable.isSubsetOf(promoted));
    try std.testing.expect(handoff.isSubsetOf(promoted));
    try std.testing.expect(stable_cpus.isSubsetOf(promoted_cpus));
    try std.testing.expect(handoff_cpus.isSubsetOf(promoted_cpus));
    try std.testing.expect(!promoted.isSubsetOf(stable));
    try std.testing.expect(!promoted_cpus.isSubsetOf(stable_cpus));

    try std.testing.expect(promoted.intersects(bridge));
    try std.testing.expect(promoted_cpus.intersects(bridge_cpus));
    try std.testing.expect(!outside.intersects(promoted));
    try std.testing.expect(!outside_cpus.intersects(promoted_cpus));
}

test "phase window handoff keeps cursor mirrors across rollback" {
    const capacity = 2 * word_bits + 13;
    const window = seedPhaseWindow();

    const promoted = viewFrom(&window.promoted, capacity);
    const promoted_cpus = cpuViewFrom(&window.promoted, capacity);
    const rollback = viewFrom(&window.stable, capacity);
    const rollback_cpus = cpuViewFrom(&window.stable, capacity);

    try std.testing.expectEqual(@as(?usize, 1), promoted.firstSetBit());
    try std.testing.expectEqual(promoted.firstSetBit(), promoted_cpus.firstCpu());
    try std.testing.expectEqual(@as(?usize, 12), promoted.nextSetBit(8));
    try std.testing.expectEqual(promoted.nextSetBit(8), promoted_cpus.nextCpu(8));
    try std.testing.expectEqual(@as(?usize, word_bits + 31), promoted.nextSetBit(word_bits + 19));
    try std.testing.expectEqual(promoted.nextSetBit(word_bits + 19), promoted_cpus.nextCpu(word_bits + 19));
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 10), promoted.nextSetBit(2 * word_bits + 5));
    try std.testing.expectEqual(promoted.nextSetBit(2 * word_bits + 5), promoted_cpus.nextCpu(2 * word_bits + 5));
    try std.testing.expectEqual(@as(?usize, null), promoted.nextSetBit(capacity));
    try std.testing.expectEqual(promoted.nextSetBit(capacity), promoted_cpus.nextCpu(capacity));

    try std.testing.expectEqual(@as(?usize, 0), promoted.firstClearBit());
    try std.testing.expectEqual(promoted.firstClearBit(), promoted_cpus.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 5), promoted.nextClearBit(2 * word_bits + 5));
    try std.testing.expectEqual(promoted.nextClearBit(2 * word_bits + 5), promoted_cpus.nextMissingCpu(2 * word_bits + 5));

    try std.testing.expectEqual(@as(usize, 5), rollback.countSetBits());
    try std.testing.expectEqual(rollback.countSetBits(), rollback_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 4), rollback.nextSetBit(2 * word_bits));
    try std.testing.expectEqual(rollback.nextSetBit(2 * word_bits), rollback_cpus.nextCpu(2 * word_bits));
}

test "phase window handoff clips declared tail noise" {
    const capacity = 2 * word_bits + 13;
    const window = seedPhaseWindow();

    const promoted = viewFrom(&window.promoted, capacity);
    const noisy_full = viewFrom(&window.noisy_full, capacity);
    const noisy_cpus = cpuViewFrom(&window.noisy_full, capacity);

    try std.testing.expectEqual(promoted.countSetBits(), noisy_full.countSetBits());
    try std.testing.expectEqual(noisy_full.countSetBits(), noisy_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 10), noisy_full.nextSetBit(2 * word_bits + 5));
    try std.testing.expectEqual(noisy_full.nextSetBit(2 * word_bits + 5), noisy_cpus.nextCpu(2 * word_bits + 5));
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 11), noisy_full.nextClearBit(2 * word_bits + 11));
    try std.testing.expectEqual(noisy_full.nextClearBit(2 * word_bits + 11), noisy_cpus.nextMissingCpu(2 * word_bits + 11));
    try std.testing.expectEqual(@as(?usize, null), noisy_full.nextSetBit(capacity));
    try std.testing.expectEqual(noisy_full.nextSetBit(capacity), noisy_cpus.nextCpu(capacity));
}
