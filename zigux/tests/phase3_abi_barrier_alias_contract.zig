const std = @import("std");

const barrier_helpers = @import("barrier_helpers");

test "phase3 barrier aliases preserve explicit fence order policy" {
    try std.testing.expect(barrier_helpers.fenceOrderAllowed(.acquire));
    try std.testing.expect(barrier_helpers.fenceOrderAllowed(.release));
    try std.testing.expect(barrier_helpers.fenceOrderAllowed(.acq_rel));
    try std.testing.expect(barrier_helpers.fenceOrderAllowed(.seq_cst));

    try std.testing.expect(!barrier_helpers.fenceOrderAllowed(.unordered));
    try std.testing.expect(!barrier_helpers.fenceOrderAllowed(.monotonic));

    try barrier_helpers.validateFenceOrder(.acquire);
    try barrier_helpers.validateFenceOrder(.release);
    try barrier_helpers.validateFenceOrder(.acq_rel);
    try barrier_helpers.validateFenceOrder(.seq_cst);

    try std.testing.expectError(error.InvalidFenceOrdering, barrier_helpers.validateFenceOrder(.unordered));
    try std.testing.expectError(error.InvalidFenceOrdering, barrier_helpers.validateFenceOrder(.monotonic));
    try std.testing.expectError(error.InvalidFenceOrdering, barrier_helpers.fence(.unordered));
    try std.testing.expectError(error.InvalidFenceOrdering, barrier_helpers.fence(.monotonic));
}

test "phase3 barrier aliases keep publish consume handoffs reviewable" {
    const Packet = struct {
        staged: u32,
        published: u32,
        consumed: u32,
        ready: bool,
    };

    var packet = Packet{
        .staged = 0,
        .published = 0,
        .consumed = 0,
        .ready = false,
    };

    packet.staged = 0x26;
    barrier_helpers.compiler();
    barrier_helpers.writeBarrier();
    packet.published = packet.staged;
    packet.ready = true;

    barrier_helpers.readBarrier();
    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 0x26), packet.published);

    packet.consumed = packet.published;
    barrier_helpers.storeLoad();
    try std.testing.expectEqual(packet.published, packet.consumed);

    packet.ready = false;
    packet.staged = 0x62;
    barrier_helpers.release();
    packet.published = packet.staged;
    barrier_helpers.acquire();

    try std.testing.expect(!packet.ready);
    try std.testing.expectEqual(@as(u32, 0x62), packet.published);
    try std.testing.expectEqual(@as(u32, 0x26), packet.consumed);
}

test "phase3 barrier aliases keep full fence family aligned" {
    const Packet = struct {
        before: u16,
        after: u16,
        mirror: u16,
    };

    var packet = Packet{
        .before = 11,
        .after = 0,
        .mirror = 0,
    };

    packet.after = packet.before + 7;
    barrier_helpers.full();
    packet.mirror = packet.after;
    barrier_helpers.fullFence();
    try barrier_helpers.fence(.seq_cst);

    try std.testing.expectEqual(@as(u16, 11), packet.before);
    try std.testing.expectEqual(@as(u16, 18), packet.after);
    try std.testing.expectEqual(packet.after, packet.mirror);
}

test "phase3 barrier aliases keep dependency and post-atomic boundaries explicit" {
    const Packet = struct {
        counter: u32,
        staged: u32,
        consumed: u32,
        ready: bool,
    };

    var packet = Packet{
        .counter = 1,
        .staged = 0,
        .consumed = 0,
        .ready = false,
    };

    try std.testing.expectEqual(@as(u32, 1), @atomicRmw(u32, &packet.counter, .Add, 5, .acq_rel));
    barrier_helpers.afterAtomic();
    packet.staged = packet.counter;
    barrier_helpers.release();
    packet.ready = true;

    if (packet.ready) {
        barrier_helpers.acquireAfterControlDependency();
        packet.consumed = packet.staged;
    }

    try std.testing.expectEqual(@as(u32, 6), packet.counter);
    try std.testing.expectEqual(packet.staged, packet.consumed);

    packet.ready = false;
    packet.staged = 19;
    barrier_helpers.compiler();

    if (packet.ready) {
        barrier_helpers.acquireAfterControlDependency();
        packet.consumed = packet.staged;
    }

    try std.testing.expectEqual(@as(u32, 6), packet.consumed);
}
