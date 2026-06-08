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

fn seedPhaseBraid() struct {
    phase_a: [3]usize,
    phase_b: [3]usize,
    bridge: [3]usize,
    handback: [3]usize,
    isolated: [3]usize,
    noisy_handback: [3]usize,
} {
    var phase_a = [_]usize{ 0, 0, 0 };
    var phase_b = [_]usize{ 0, 0, 0 };
    var bridge = [_]usize{ 0, 0, 0 };
    var handback = [_]usize{ 0, 0, 0 };
    var isolated = [_]usize{ 0, 0, 0 };

    for ([_]usize{ 2, 9, word_bits + 6, word_bits + 21, 2 * word_bits + 3 }) |bit| {
        setBit(&phase_a, bit);
    }
    for ([_]usize{ 9, word_bits + 6, word_bits + 35, 2 * word_bits + 3, 2 * word_bits + 12 }) |bit| {
        setBit(&phase_b, bit);
    }
    for ([_]usize{ 9, word_bits + 6, 2 * word_bits + 3 }) |bit| {
        setBit(&bridge, bit);
    }
    for ([_]usize{ 2, 9, word_bits + 6, word_bits + 21, word_bits + 35, 2 * word_bits + 3 }) |bit| {
        setBit(&handback, bit);
    }
    for ([_]usize{ 0, 14, word_bits + 2, 2 * word_bits + 8 }) |bit| {
        setBit(&isolated, bit);
    }

    return .{
        .phase_a = phase_a,
        .phase_b = phase_b,
        .bridge = bridge,
        .handback = handback,
        .isolated = isolated,
        .noisy_handback = .{
            handback[0],
            handback[1],
            handback[2] | ~((@as(usize, 1) << 15) - 1),
        },
    };
}

test "phase braid handback keeps relation mirrors explicit" {
    const capacity = 2 * word_bits + 15;
    const braid = seedPhaseBraid();

    const phase_a = viewFrom(&braid.phase_a, capacity);
    const phase_b = viewFrom(&braid.phase_b, capacity);
    const bridge = viewFrom(&braid.bridge, capacity);
    const handback = viewFrom(&braid.handback, capacity);
    const isolated = viewFrom(&braid.isolated, capacity);

    const phase_a_cpus = cpuViewFrom(&braid.phase_a, capacity);
    const phase_b_cpus = cpuViewFrom(&braid.phase_b, capacity);
    const bridge_cpus = cpuViewFrom(&braid.bridge, capacity);
    const handback_cpus = cpuViewFrom(&braid.handback, capacity);
    const isolated_cpus = cpuViewFrom(&braid.isolated, capacity);

    try std.testing.expectEqual(@as(usize, 5), phase_a.countSetBits());
    try std.testing.expectEqual(phase_a.countSetBits(), phase_a_cpus.countPresentCpus());
    try std.testing.expectEqual(phase_b.countSetBits(), phase_b_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 3), bridge.countSetBits());
    try std.testing.expectEqual(@as(usize, 6), handback.countSetBits());
    try std.testing.expectEqual(handback.countSetBits(), handback_cpus.countPresentCpus());

    try std.testing.expect(bridge.isSubsetOf(phase_a));
    try std.testing.expect(bridge.isSubsetOf(phase_b));
    try std.testing.expect(bridge_cpus.isSubsetOf(phase_a_cpus));
    try std.testing.expect(bridge_cpus.isSubsetOf(phase_b_cpus));

    try std.testing.expect(phase_a.isSubsetOf(handback));
    try std.testing.expect(!phase_b.isSubsetOf(handback));
    try std.testing.expect(phase_a_cpus.isSubsetOf(handback_cpus));
    try std.testing.expect(!phase_b_cpus.isSubsetOf(handback_cpus));

    try std.testing.expect(phase_a.intersects(phase_b));
    try std.testing.expect(phase_a_cpus.intersects(phase_b_cpus));
    try std.testing.expect(!isolated.intersects(handback));
    try std.testing.expect(!isolated_cpus.intersects(handback_cpus));
}

test "phase braid handback keeps cursor mirrors after rollback" {
    const capacity = 2 * word_bits + 15;
    const braid = seedPhaseBraid();

    const handback = viewFrom(&braid.handback, capacity);
    const handback_cpus = cpuViewFrom(&braid.handback, capacity);
    const rollback = viewFrom(&braid.phase_a, capacity);
    const rollback_cpus = cpuViewFrom(&braid.phase_a, capacity);

    try std.testing.expectEqual(@as(?usize, 2), handback.firstSetBit());
    try std.testing.expectEqual(handback.firstSetBit(), handback_cpus.firstCpu());
    try std.testing.expectEqual(@as(?usize, 9), handback.nextSetBit(3));
    try std.testing.expectEqual(handback.nextSetBit(3), handback_cpus.nextCpu(3));
    try std.testing.expectEqual(@as(?usize, word_bits + 35), handback.nextSetBit(word_bits + 22));
    try std.testing.expectEqual(handback.nextSetBit(word_bits + 22), handback_cpus.nextCpu(word_bits + 22));
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 3), handback.nextSetBit(2 * word_bits));
    try std.testing.expectEqual(handback.nextSetBit(2 * word_bits), handback_cpus.nextCpu(2 * word_bits));
    try std.testing.expectEqual(@as(?usize, null), handback.nextSetBit(capacity));
    try std.testing.expectEqual(handback.nextSetBit(capacity), handback_cpus.nextCpu(capacity));

    try std.testing.expectEqual(@as(?usize, 0), handback.firstClearBit());
    try std.testing.expectEqual(handback.firstClearBit(), handback_cpus.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 4), handback.nextClearBit(2 * word_bits + 4));
    try std.testing.expectEqual(handback.nextClearBit(2 * word_bits + 4), handback_cpus.nextMissingCpu(2 * word_bits + 4));

    try std.testing.expectEqual(@as(usize, 5), rollback.countSetBits());
    try std.testing.expectEqual(rollback.countSetBits(), rollback_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, word_bits + 21), rollback.nextSetBit(word_bits + 7));
    try std.testing.expectEqual(rollback.nextSetBit(word_bits + 7), rollback_cpus.nextCpu(word_bits + 7));
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 4), rollback.nextClearBit(2 * word_bits + 4));
    try std.testing.expectEqual(rollback.nextClearBit(2 * word_bits + 4), rollback_cpus.nextMissingCpu(2 * word_bits + 4));
}

test "phase braid handback clips declared tail noise" {
    const capacity = 2 * word_bits + 15;
    const braid = seedPhaseBraid();

    const handback = viewFrom(&braid.handback, capacity);
    const noisy_handback = viewFrom(&braid.noisy_handback, capacity);
    const noisy_cpus = cpuViewFrom(&braid.noisy_handback, capacity);

    try std.testing.expectEqual(handback.countSetBits(), noisy_handback.countSetBits());
    try std.testing.expectEqual(noisy_handback.countSetBits(), noisy_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 3), noisy_handback.nextSetBit(2 * word_bits));
    try std.testing.expectEqual(noisy_handback.nextSetBit(2 * word_bits), noisy_cpus.nextCpu(2 * word_bits));
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 4), noisy_handback.nextClearBit(2 * word_bits + 4));
    try std.testing.expectEqual(noisy_handback.nextClearBit(2 * word_bits + 4), noisy_cpus.nextMissingCpu(2 * word_bits + 4));
    try std.testing.expectEqual(@as(?usize, null), noisy_handback.nextSetBit(capacity));
    try std.testing.expectEqual(noisy_handback.nextSetBit(capacity), noisy_cpus.nextCpu(capacity));
}
