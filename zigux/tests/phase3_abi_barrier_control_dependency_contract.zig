const std = @import("std");
const barrier = @import("barrier_helper");

const Packet = struct {
    ready: bool,
    staged: u32,
    consumed: u32,
    published: u32,
};

test "control dependency acquire consumes only the released ready path" {
    var packet = Packet{
        .ready = false,
        .staged = 0,
        .consumed = 0,
        .published = 0,
    };

    packet.staged = 0x2A;
    barrier.release();
    packet.ready = true;

    if (packet.ready) {
        barrier.acquireAfterControlDependency();
        packet.consumed = packet.staged;
    }

    try std.testing.expectEqual(@as(u32, 0x2A), packet.consumed);

    packet.ready = false;
    packet.staged = 0x5C;
    barrier.compiler();

    if (packet.ready) {
        barrier.acquireAfterControlDependency();
        packet.consumed = packet.staged;
    }

    try std.testing.expectEqual(@as(u32, 0x2A), packet.consumed);
    try std.testing.expectEqual(@as(u32, 0x5C), packet.staged);
}

test "store-load and read-write aliases preserve publication order" {
    var packet = Packet{
        .ready = false,
        .staged = 0x11,
        .consumed = 0,
        .published = 0,
    };

    barrier.writeBarrier();
    packet.published = packet.staged;
    barrier.storeLoad();
    packet.ready = true;

    barrier.readBarrier();
    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 0x11), packet.published);

    packet.consumed = packet.published;
    barrier.fullFence();
    try std.testing.expectEqual(packet.published, packet.consumed);

    packet.ready = false;
    packet.staged = 0x27;
    barrier.writeBarrier();
    packet.published = packet.staged;
    barrier.storeLoad();
    barrier.readBarrier();

    try std.testing.expect(!packet.ready);
    try std.testing.expectEqual(@as(u32, 0x27), packet.published);
    try std.testing.expectEqual(@as(u32, 0x11), packet.consumed);
}

test "post atomic barrier publishes updated counter without extra mutation" {
    const AtomicPacket = struct {
        counter: u32,
        before: u32,
        published: u32,
    };

    var packet = AtomicPacket{
        .counter = 3,
        .before = 0,
        .published = 0,
    };

    packet.before = try barrierAtomicAdd(&packet.counter, 9);
    barrier.afterAtomic();
    packet.published = packet.counter;
    barrier.fullFence();

    try std.testing.expectEqual(@as(u32, 3), packet.before);
    try std.testing.expectEqual(@as(u32, 12), packet.counter);
    try std.testing.expectEqual(packet.counter, packet.published);
}

test "invalid fence orders fail closed and leave packet state intact" {
    const packet = Packet{
        .ready = true,
        .staged = 0x31,
        .consumed = 0x62,
        .published = 0x93,
    };
    const before = packet;

    try std.testing.expect(!barrier.fenceOrderAllowed(.unordered));
    try std.testing.expect(!barrier.fenceOrderAllowed(.monotonic));
    try std.testing.expectError(error.InvalidFenceOrdering, barrier.fence(.unordered));
    try std.testing.expectError(error.InvalidFenceOrdering, barrier.fence(.monotonic));
    try std.testing.expectError(error.InvalidFenceOrdering, barrier.validateFenceOrder(.unordered));
    try std.testing.expectError(error.InvalidFenceOrdering, barrier.validateFenceOrder(.monotonic));

    try std.testing.expectEqual(before.ready, packet.ready);
    try std.testing.expectEqual(before.staged, packet.staged);
    try std.testing.expectEqual(before.consumed, packet.consumed);
    try std.testing.expectEqual(before.published, packet.published);
}

fn barrierAtomicAdd(ptr: *u32, value: u32) barrier.FenceError!u32 {
    const before = @atomicRmw(u32, ptr, .Add, value, .acq_rel);
    try barrier.fence(.seq_cst);
    return before;
}
