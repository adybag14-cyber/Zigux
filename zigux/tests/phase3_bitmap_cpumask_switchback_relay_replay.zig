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

fn seedSwitchbackRelay() struct {
    outbound: [3]usize,
    inbound: [3]usize,
    relay: [3]usize,
    switched: [3]usize,
    rollback: [3]usize,
    isolated: [3]usize,
    noisy_switched: [3]usize,
} {
    var outbound = [_]usize{ 0, 0, 0 };
    var inbound = [_]usize{ 0, 0, 0 };
    var relay = [_]usize{ 0, 0, 0 };
    var switched = [_]usize{ 0, 0, 0 };
    var rollback = [_]usize{ 0, 0, 0 };
    var isolated = [_]usize{ 0, 0, 0 };

    for ([_]usize{ 3, 17, word_bits + 4, word_bits + 29, 2 * word_bits + 6 }) |bit| {
        setBit(&outbound, bit);
    }
    for ([_]usize{ 17, word_bits + 4, word_bits + 41, 2 * word_bits + 6, 2 * word_bits + 13 }) |bit| {
        setBit(&inbound, bit);
    }
    for ([_]usize{ 17, word_bits + 4, 2 * word_bits + 6 }) |bit| {
        setBit(&relay, bit);
    }
    for ([_]usize{ 3, 17, word_bits + 4, word_bits + 29, word_bits + 41, 2 * word_bits + 6, 2 * word_bits + 13 }) |bit| {
        setBit(&switched, bit);
    }
    for ([_]usize{ 3, 17, word_bits + 4, 2 * word_bits + 6 }) |bit| {
        setBit(&rollback, bit);
    }
    for ([_]usize{ 0, 9, word_bits + 11, 2 * word_bits + 2 }) |bit| {
        setBit(&isolated, bit);
    }

    return .{
        .outbound = outbound,
        .inbound = inbound,
        .relay = relay,
        .switched = switched,
        .rollback = rollback,
        .isolated = isolated,
        .noisy_switched = .{
            switched[0],
            switched[1],
            switched[2] | ~((@as(usize, 1) << 18) - 1),
        },
    };
}

test "switchback relay preserves relation mirrors across promotion" {
    const capacity = 2 * word_bits + 18;
    const fixture = seedSwitchbackRelay();

    const outbound = viewFrom(&fixture.outbound, capacity);
    const inbound = viewFrom(&fixture.inbound, capacity);
    const relay = viewFrom(&fixture.relay, capacity);
    const switched = viewFrom(&fixture.switched, capacity);
    const isolated = viewFrom(&fixture.isolated, capacity);

    const outbound_cpus = cpuViewFrom(&fixture.outbound, capacity);
    const inbound_cpus = cpuViewFrom(&fixture.inbound, capacity);
    const relay_cpus = cpuViewFrom(&fixture.relay, capacity);
    const switched_cpus = cpuViewFrom(&fixture.switched, capacity);
    const isolated_cpus = cpuViewFrom(&fixture.isolated, capacity);

    try std.testing.expectEqual(@as(usize, 5), outbound.countSetBits());
    try std.testing.expectEqual(outbound.countSetBits(), outbound_cpus.countPresentCpus());
    try std.testing.expectEqual(inbound.countSetBits(), inbound_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 3), relay.countSetBits());
    try std.testing.expectEqual(@as(usize, 7), switched.countSetBits());
    try std.testing.expectEqual(switched.countSetBits(), switched_cpus.countPresentCpus());

    try std.testing.expect(relay.isSubsetOf(outbound));
    try std.testing.expect(relay.isSubsetOf(inbound));
    try std.testing.expect(relay_cpus.isSubsetOf(outbound_cpus));
    try std.testing.expect(relay_cpus.isSubsetOf(inbound_cpus));

    try std.testing.expect(outbound.isSubsetOf(switched));
    try std.testing.expect(inbound.isSubsetOf(switched));
    try std.testing.expect(outbound_cpus.isSubsetOf(switched_cpus));
    try std.testing.expect(inbound_cpus.isSubsetOf(switched_cpus));

    try std.testing.expect(outbound.intersects(inbound));
    try std.testing.expect(outbound_cpus.intersects(inbound_cpus));
    try std.testing.expect(!isolated.intersects(switched));
    try std.testing.expect(!isolated_cpus.intersects(switched_cpus));
}

test "switchback relay keeps cursor mirrors after rollback" {
    const capacity = 2 * word_bits + 18;
    const fixture = seedSwitchbackRelay();

    const switched = viewFrom(&fixture.switched, capacity);
    const switched_cpus = cpuViewFrom(&fixture.switched, capacity);
    const rollback = viewFrom(&fixture.rollback, capacity);
    const rollback_cpus = cpuViewFrom(&fixture.rollback, capacity);

    try std.testing.expectEqual(@as(?usize, 3), switched.firstSetBit());
    try std.testing.expectEqual(switched.firstSetBit(), switched_cpus.firstCpu());
    try std.testing.expectEqual(@as(?usize, 17), switched.nextSetBit(4));
    try std.testing.expectEqual(switched.nextSetBit(4), switched_cpus.nextCpu(4));
    try std.testing.expectEqual(@as(?usize, word_bits + 41), switched.nextSetBit(word_bits + 30));
    try std.testing.expectEqual(switched.nextSetBit(word_bits + 30), switched_cpus.nextCpu(word_bits + 30));
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 6), switched.nextSetBit(2 * word_bits));
    try std.testing.expectEqual(switched.nextSetBit(2 * word_bits), switched_cpus.nextCpu(2 * word_bits));
    try std.testing.expectEqual(@as(?usize, null), switched.nextSetBit(capacity));
    try std.testing.expectEqual(switched.nextSetBit(capacity), switched_cpus.nextCpu(capacity));

    try std.testing.expectEqual(@as(?usize, 0), switched.firstClearBit());
    try std.testing.expectEqual(switched.firstClearBit(), switched_cpus.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 7), switched.nextClearBit(2 * word_bits + 7));
    try std.testing.expectEqual(switched.nextClearBit(2 * word_bits + 7), switched_cpus.nextMissingCpu(2 * word_bits + 7));

    try std.testing.expectEqual(@as(usize, 4), rollback.countSetBits());
    try std.testing.expectEqual(rollback.countSetBits(), rollback_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 6), rollback.nextSetBit(word_bits + 5));
    try std.testing.expectEqual(rollback.nextSetBit(word_bits + 5), rollback_cpus.nextCpu(word_bits + 5));
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 7), rollback.nextClearBit(2 * word_bits + 7));
    try std.testing.expectEqual(rollback.nextClearBit(2 * word_bits + 7), rollback_cpus.nextMissingCpu(2 * word_bits + 7));
}

test "switchback relay clips declared tail noise" {
    const capacity = 2 * word_bits + 18;
    const fixture = seedSwitchbackRelay();

    const switched = viewFrom(&fixture.switched, capacity);
    const noisy_switched = viewFrom(&fixture.noisy_switched, capacity);
    const noisy_cpus = cpuViewFrom(&fixture.noisy_switched, capacity);

    try std.testing.expectEqual(switched.countSetBits(), noisy_switched.countSetBits());
    try std.testing.expectEqual(noisy_switched.countSetBits(), noisy_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 6), noisy_switched.nextSetBit(2 * word_bits));
    try std.testing.expectEqual(noisy_switched.nextSetBit(2 * word_bits), noisy_cpus.nextCpu(2 * word_bits));
    try std.testing.expectEqual(@as(?usize, 2 * word_bits + 7), noisy_switched.nextClearBit(2 * word_bits + 7));
    try std.testing.expectEqual(noisy_switched.nextClearBit(2 * word_bits + 7), noisy_cpus.nextMissingCpu(2 * word_bits + 7));
    try std.testing.expectEqual(@as(?usize, null), noisy_switched.nextSetBit(capacity));
    try std.testing.expectEqual(noisy_switched.nextSetBit(capacity), noisy_cpus.nextCpu(capacity));
}
