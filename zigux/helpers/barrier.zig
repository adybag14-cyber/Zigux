const std = @import("std");

pub const Ordering = std.builtin.AtomicOrder;
pub const FenceError = error{
    InvalidFenceOrdering,
};

pub fn fenceOrderAllowed(order: Ordering) bool {
    return switch (order) {
        .acquire, .release, .acq_rel, .seq_cst => true,
        .unordered, .monotonic => false,
    };
}

pub fn validateFenceOrder(comptime order: Ordering) FenceError!void {
    if (comptime !fenceOrderAllowed(order)) {
        return error.InvalidFenceOrdering;
    }
}

fn acquireImpl() void {
    var word: u8 = 0;
    _ = @atomicLoad(u8, &word, .acquire);
}

fn releaseImpl() void {
    var word: u8 = 0;
    @atomicStore(u8, &word, 0, .release);
}

fn fullImpl() void {
    var word: u8 = 0;
    _ = @atomicRmw(u8, &word, .Xchg, 0, .seq_cst);
}

fn acquireReleaseImpl() void {
    var word: u8 = 0;
    _ = @atomicRmw(u8, &word, .Xchg, 0, .acq_rel);
}

test "phase3 barrier wrappers compile" {
    compiler();
    acquire();
    release();
    readBarrier();
    writeBarrier();
    full();
    acquireRelease();
    acquireAfterControlDependency();
    fullFence();
    storeLoad();
    try fence(.acquire);
    try fence(.release);
    try fence(.acq_rel);
    try fence(.seq_cst);
}

test "phase3 barrier wrappers keep fence ordering rules explicit" {
    try std.testing.expect(fenceOrderAllowed(.acquire));
    try std.testing.expect(fenceOrderAllowed(.release));
    try std.testing.expect(fenceOrderAllowed(.acq_rel));
    try std.testing.expect(fenceOrderAllowed(.seq_cst));

    try std.testing.expect(!fenceOrderAllowed(.unordered));
    try std.testing.expect(!fenceOrderAllowed(.monotonic));

    try std.testing.expectError(error.InvalidFenceOrdering, fence(.unordered));
    try std.testing.expectError(error.InvalidFenceOrdering, fence(.monotonic));
}

test "phase3 barrier wrappers expose reusable fence-order validation" {
    try validateFenceOrder(.acquire);
    try validateFenceOrder(.release);
    try validateFenceOrder(.acq_rel);
    try validateFenceOrder(.seq_cst);

    try std.testing.expectError(error.InvalidFenceOrdering, validateFenceOrder(.unordered));
    try std.testing.expectError(error.InvalidFenceOrdering, validateFenceOrder(.monotonic));
}

test "phase3 barrier wrappers keep compiler fences reviewable" {
    var words = [_]u16{ 7, 11, 13, 17 };

    compiler();
    words[1] = words[0] + words[2];
    compiler();

    try std.testing.expectEqual(@as(u16, 7), words[0]);
    try std.testing.expectEqual(@as(u16, 20), words[1]);
    try std.testing.expectEqual(@as(u16, 13), words[2]);

    words[3] = words[1] + 5;
    compiler();
    try std.testing.expectEqual(@as(u16, 25), words[3]);
}

test "phase3 barrier wrappers keep barrier locality reviewable" {
    var left: u8 = 7;
    var right: u8 = 19;
    const before_left = left;
    const before_right = right;

    compiler();
    acquire();
    release();
    full();
    acquireRelease();
    acquireAfterControlDependency();

    try std.testing.expectEqual(before_left, left);
    try std.testing.expectEqual(before_right, right);

    left +%= 1;
    compiler();
    right +%= 2;
    acquireRelease();

    try std.testing.expectEqual(@as(u8, 8), left);
    try std.testing.expectEqual(@as(u8, 21), right);
}

test "phase3 barrier wrappers stay side-effect free on unrelated storage" {
    const Packet = struct {
        ready: bool,
        value: u32,
        mirror: u32,
    };

    const packet = Packet{
        .ready = false,
        .value = 11,
        .mirror = 29,
    };
    const before = packet;

    acquire();
    release();
    readBarrier();
    writeBarrier();
    full();
    acquireRelease();
    acquireAfterControlDependency();
    storeLoad();

    try std.testing.expectEqual(before.ready, packet.ready);
    try std.testing.expectEqual(before.value, packet.value);
    try std.testing.expectEqual(before.mirror, packet.mirror);
}

test "phase3 barrier wrappers keep barrier handoff reviewable" {
    const Packet = struct {
        ready: bool,
        value: u32,
        mirror: u32,
    };

    var packet = Packet{
        .ready = false,
        .value = 0,
        .mirror = 0,
    };

    packet.value = 41;
    compiler();
    release();
    packet.ready = true;

    acquire();
    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 41), packet.value);

    full();
    compiler();
    packet.mirror = packet.value;
    acquireRelease();

    try std.testing.expectEqual(@as(u32, 41), packet.mirror);

    packet.value = 73;
    compiler();
    release();
    packet.ready = false;
    acquire();
    try std.testing.expect(!packet.ready);
    try std.testing.expectEqual(@as(u32, 73), packet.value);
}

test "phase3 barrier wrappers keep generic fence dispatch handoffs reviewable" {
    const Packet = struct {
        staged: u32,
        published: u32,
        ready: bool,
    };

    var packet = Packet{
        .staged = 0,
        .published = 0,
        .ready = false,
    };

    packet.staged = 0x24;
    compiler();
    try fence(.release);
    packet.published = packet.staged;
    packet.ready = true;

    try fence(.acquire);
    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 0x24), packet.published);

    packet.ready = false;
    packet.staged = 0x57;
    compiler();
    try fence(.acq_rel);
    packet.published = packet.staged;
    try fence(.seq_cst);

    try std.testing.expect(!packet.ready);
    try std.testing.expectEqual(@as(u32, 0x57), packet.published);
}

test "phase3 barrier wrappers keep read and write barrier aliases aligned" {
    const Packet = struct {
        staged: u32,
        published: u32,
        ready: bool,
    };

    var packet = Packet{
        .staged = 0,
        .published = 0,
        .ready = false,
    };

    packet.staged = 0x31;
    compiler();
    writeBarrier();
    packet.published = packet.staged;
    packet.ready = true;

    readBarrier();
    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 0x31), packet.published);

    packet.ready = false;
    packet.staged = 0x74;
    compiler();
    writeBarrier();
    packet.published = packet.staged;

    readBarrier();
    try std.testing.expect(!packet.ready);
    try std.testing.expectEqual(@as(u32, 0x74), packet.published);
}

test "phase3 barrier wrappers keep store-load handoffs reviewable" {
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

    packet.staged = 0x44;
    compiler();
    release();
    packet.published = packet.staged;
    storeLoad();
    packet.ready = true;

    acquire();
    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 0x44), packet.published);

    packet.consumed = packet.published;
    storeLoad();
    try std.testing.expectEqual(packet.published, packet.consumed);

    packet.ready = false;
    packet.staged = 0x73;
    compiler();
    release();
    packet.published = packet.staged;
    storeLoad();
    acquire();
    try std.testing.expect(!packet.ready);
    try std.testing.expectEqual(@as(u32, 0x73), packet.published);
}

test "phase3 barrier wrappers keep non-mutating full fences reviewable" {
    const Packet = struct {
        published: u32,
        consumed: u32,
        ready: bool,
    };

    var packet = Packet{
        .published = 21,
        .consumed = 0,
        .ready = false,
    };

    packet.published +%= 8;
    fullFence();
    packet.consumed = packet.published;
    packet.ready = true;
    fullFence();

    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 29), packet.published);
    try std.testing.expectEqual(packet.published, packet.consumed);
}

test "phase3 barrier wrappers keep seq-cst aliases aligned" {
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

    packet.staged = 0x11;
    compiler();
    full();
    packet.published = packet.staged;
    fullFence();
    packet.ready = true;

    try fence(.seq_cst);
    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 0x11), packet.published);

    packet.consumed = packet.published;
    storeLoad();
    try std.testing.expectEqual(packet.published, packet.consumed);

    packet.ready = false;
    packet.staged = 0x22;
    compiler();
    try fence(.seq_cst);
    packet.published = packet.staged;
    full();
    packet.consumed = packet.published;
    fullFence();

    try std.testing.expect(!packet.ready);
    try std.testing.expectEqual(@as(u32, 0x22), packet.consumed);
}

test "phase3 barrier wrappers keep acquire-after-control-dependency handoffs reviewable" {
    const Packet = struct {
        ready: bool,
        staged: u32,
        consumed: u32,
    };

    var packet = Packet{
        .ready = false,
        .staged = 0,
        .consumed = 0,
    };

    packet.staged = 0x61;
    release();
    packet.ready = true;

    if (packet.ready) {
        acquireAfterControlDependency();
        packet.consumed = packet.staged;
    }

    try std.testing.expectEqual(@as(u32, 0x61), packet.consumed);

    packet.ready = false;
    packet.staged = 0x92;
    compiler();

    if (packet.ready) {
        acquireAfterControlDependency();
        packet.consumed = packet.staged;
    }

    try std.testing.expectEqual(@as(u32, 0x61), packet.consumed);
}

pub fn compiler() void {
    asm volatile ("" ::: .{ .memory = true });
}

pub fn fence(comptime order: Ordering) FenceError!void {
    try validateFenceOrder(order);

    switch (order) {
        .acquire => acquireImpl(),
        .release => releaseImpl(),
        .acq_rel => acquireReleaseImpl(),
        .seq_cst => fullImpl(),
        .unordered, .monotonic => unreachable,
    }
}

pub fn acquire() void {
    fence(.acquire) catch unreachable;
}

pub fn release() void {
    fence(.release) catch unreachable;
}

pub fn readBarrier() void {
    acquire();
}

pub fn writeBarrier() void {
    release();
}

pub fn full() void {
    fence(.seq_cst) catch unreachable;
}

pub fn acquireRelease() void {
    fence(.acq_rel) catch unreachable;
}

pub fn acquireAfterControlDependency() void {
    compiler();
    acquire();
}

pub fn fullFence() void {
    fence(.seq_cst) catch unreachable;
}

pub fn storeLoad() void {
    fence(.seq_cst) catch unreachable;
}
