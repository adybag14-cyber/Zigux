const std = @import("std");
const barrier = @import("barrier_helpers");

const Packet = struct {
    staged: u32,
    published: u32,
    consumed: u32,
    ready: bool,
};

test "barrier alias matrix keeps read and write handoffs aligned" {
    var packet = Packet{
        .staged = 0,
        .published = 0,
        .consumed = 0,
        .ready = false,
    };

    packet.staged = 0x31;
    barrier.compiler();
    barrier.writeBarrier();
    packet.published = packet.staged;
    packet.ready = true;

    barrier.readBarrier();
    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 0x31), packet.published);

    packet.ready = false;
    packet.staged = 0x74;
    barrier.compiler();
    barrier.writeBarrier();
    packet.published = packet.staged;

    barrier.readBarrier();
    try std.testing.expect(!packet.ready);
    try std.testing.expectEqual(@as(u32, 0x74), packet.published);
}

test "seq-cst barrier aliases preserve publication and consumption order" {
    var packet = Packet{
        .staged = 0,
        .published = 0,
        .consumed = 0,
        .ready = false,
    };

    packet.staged = 0x11;
    barrier.compiler();
    barrier.full();
    packet.published = packet.staged;
    barrier.fullFence();
    packet.ready = true;

    try barrier.fence(.seq_cst);
    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 0x11), packet.published);

    packet.consumed = packet.published;
    barrier.storeLoad();
    try std.testing.expectEqual(packet.published, packet.consumed);

    packet.ready = false;
    packet.staged = 0x22;
    barrier.compiler();
    try barrier.fence(.seq_cst);
    packet.published = packet.staged;
    barrier.full();
    packet.consumed = packet.published;
    barrier.fullFence();

    try std.testing.expect(!packet.ready);
    try std.testing.expectEqual(@as(u32, 0x22), packet.consumed);
}

test "control-dependency and post-atomic aliases are explicit non-mutating handoffs" {
    var packet = Packet{
        .staged = 0x61,
        .published = 0,
        .consumed = 0,
        .ready = true,
    };

    if (packet.ready) {
        barrier.acquireAfterControlDependency();
        packet.consumed = packet.staged;
    }

    try std.testing.expectEqual(@as(u32, 0x61), packet.consumed);

    packet.ready = false;
    packet.staged = 0x92;
    barrier.compiler();

    if (packet.ready) {
        barrier.acquireAfterControlDependency();
        packet.consumed = packet.staged;
    }

    try std.testing.expectEqual(@as(u32, 0x61), packet.consumed);

    packet.published = 7;
    try std.testing.expectEqual(@as(u32, 7), @atomicRmw(u32, &packet.published, .Add, 5, .acq_rel));
    barrier.afterAtomic();
    packet.consumed = packet.published;
    barrier.fullFence();

    try std.testing.expectEqual(@as(u32, 12), packet.published);
    try std.testing.expectEqual(packet.published, packet.consumed);
}

test "barrier generic fence rejects non-fence orderings without alias side effects" {
    const packet = Packet{
        .staged = 0xA0,
        .published = 0xB0,
        .consumed = 0xC0,
        .ready = true,
    };
    const before = packet;

    try std.testing.expect(barrier.fenceOrderAllowed(.acquire));
    try std.testing.expect(barrier.fenceOrderAllowed(.release));
    try std.testing.expect(barrier.fenceOrderAllowed(.acq_rel));
    try std.testing.expect(barrier.fenceOrderAllowed(.seq_cst));
    try std.testing.expect(!barrier.fenceOrderAllowed(.unordered));
    try std.testing.expect(!barrier.fenceOrderAllowed(.monotonic));

    try std.testing.expectError(error.InvalidFenceOrdering, barrier.fence(.unordered));
    try std.testing.expectError(error.InvalidFenceOrdering, barrier.fence(.monotonic));

    try std.testing.expectEqual(before.staged, packet.staged);
    try std.testing.expectEqual(before.published, packet.published);
    try std.testing.expectEqual(before.consumed, packet.consumed);
    try std.testing.expectEqual(before.ready, packet.ready);
}
