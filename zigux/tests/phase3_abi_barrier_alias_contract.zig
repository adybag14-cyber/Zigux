const std = @import("std");
const barrier = @import("barrier_helpers");

test "barrier alias contract keeps public alias roster routed through valid fences" {
    try barrier.validateFenceOrder(.acquire);
    try barrier.validateFenceOrder(.release);
    try barrier.validateFenceOrder(.acq_rel);
    try barrier.validateFenceOrder(.seq_cst);

    try std.testing.expect(barrier.fenceOrderAllowed(.acquire));
    try std.testing.expect(barrier.fenceOrderAllowed(.release));
    try std.testing.expect(barrier.fenceOrderAllowed(.acq_rel));
    try std.testing.expect(barrier.fenceOrderAllowed(.seq_cst));

    try std.testing.expect(!barrier.fenceOrderAllowed(.unordered));
    try std.testing.expect(!barrier.fenceOrderAllowed(.monotonic));
    try std.testing.expectError(error.InvalidFenceOrdering, barrier.validateFenceOrder(.unordered));
    try std.testing.expectError(error.InvalidFenceOrdering, barrier.validateFenceOrder(.monotonic));
}

test "barrier alias contract keeps read and write aliases paired with acquire and release" {
    const Packet = struct {
        staged: u32,
        visible: u32,
        ready: bool,
    };

    var packet = Packet{
        .staged = 0,
        .visible = 0,
        .ready = false,
    };

    packet.staged = 0x1020_3040;
    barrier.compiler();
    barrier.writeBarrier();
    packet.visible = packet.staged;
    packet.ready = true;

    barrier.readBarrier();
    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 0x1020_3040), packet.visible);

    packet.ready = false;
    packet.staged = 0x5060_7080;
    barrier.release();
    packet.visible = packet.staged;
    barrier.acquire();

    try std.testing.expect(!packet.ready);
    try std.testing.expectEqual(@as(u32, 0x5060_7080), packet.visible);
}

test "barrier alias contract keeps seq-cst aliases interchangeable for handoffs" {
    const Packet = struct {
        counter: u32,
        published: u32,
        consumed: u32,
    };

    var packet = Packet{
        .counter = 7,
        .published = 0,
        .consumed = 0,
    };

    packet.counter +%= 5;
    barrier.full();
    packet.published = packet.counter;
    barrier.fullFence();
    packet.consumed = packet.published;
    barrier.storeLoad();

    try barrier.fence(.seq_cst);
    try std.testing.expectEqual(@as(u32, 12), packet.counter);
    try std.testing.expectEqual(packet.counter, packet.published);
    try std.testing.expectEqual(packet.published, packet.consumed);
}

test "barrier alias contract keeps control-dependency and post-atomic aliases reviewable" {
    const Packet = struct {
        ready: bool,
        counter: u32,
        observed: u32,
    };

    var packet = Packet{
        .ready = false,
        .counter = 2,
        .observed = 0,
    };

    try std.testing.expectEqual(@as(u32, 2), @atomicRmw(u32, &packet.counter, .Add, 9, .acq_rel));
    barrier.afterAtomic();
    packet.ready = true;

    if (packet.ready) {
        barrier.acquireAfterControlDependency();
        packet.observed = packet.counter;
    }

    try std.testing.expectEqual(@as(u32, 11), packet.counter);
    try std.testing.expectEqual(packet.counter, packet.observed);

    packet.ready = false;
    packet.counter = 31;
    if (packet.ready) {
        barrier.acquireAfterControlDependency();
        packet.observed = packet.counter;
    }

    try std.testing.expectEqual(@as(u32, 11), packet.observed);
}
