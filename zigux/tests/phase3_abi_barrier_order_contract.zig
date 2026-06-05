const std = @import("std");
const barrier = @import("barrier_helpers");

const Ordering = std.builtin.AtomicOrder;

fn expectAllowed(comptime order: Ordering) !void {
    try std.testing.expect(barrier.fenceOrderAllowed(order));
    try barrier.validateFenceOrder(order);
    try barrier.fence(order);
}

fn expectRejected(comptime order: Ordering) !void {
    try std.testing.expect(!barrier.fenceOrderAllowed(order));
    try std.testing.expectError(error.InvalidFenceOrdering, barrier.validateFenceOrder(order));
    try std.testing.expectError(error.InvalidFenceOrdering, barrier.fence(order));
}

test "phase3 ABI barrier order contract keeps allowed fence orders explicit" {
    try expectAllowed(.acquire);
    try expectAllowed(.release);
    try expectAllowed(.acq_rel);
    try expectAllowed(.seq_cst);
}

test "phase3 ABI barrier order contract rejects non-fence atomic orders" {
    try expectRejected(.unordered);
    try expectRejected(.monotonic);
}

test "phase3 ABI barrier order contract keeps public aliases routed through valid fences" {
    var packet = struct {
        staged: u32,
        published: u32,
        consumed: u32,
        ready: bool,
    }{
        .staged = 0,
        .published = 0,
        .consumed = 0,
        .ready = false,
    };

    packet.staged = 0x26;
    barrier.compiler();
    barrier.writeBarrier();
    barrier.release();
    packet.published = packet.staged;
    barrier.storeLoad();
    packet.ready = true;

    barrier.readBarrier();
    barrier.acquire();
    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 0x26), packet.published);

    barrier.full();
    barrier.fullFence();
    packet.consumed = packet.published;
    barrier.afterAtomic();

    try std.testing.expectEqual(packet.published, packet.consumed);
}

test "phase3 ABI barrier order contract keeps control-dependency acquire non-mutating" {
    var ready = true;
    var value: u32 = 0x41;
    var consumed: u32 = 0;

    if (ready) {
        barrier.acquireAfterControlDependency();
        consumed = value;
    }

    try std.testing.expectEqual(@as(u32, 0x41), consumed);

    ready = false;
    value = 0x52;
    if (ready) {
        barrier.acquireAfterControlDependency();
        consumed = value;
    }

    try std.testing.expectEqual(@as(u32, 0x41), consumed);
}
