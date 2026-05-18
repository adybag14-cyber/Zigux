const std = @import("std");

test "phase3 barrier wrappers compile" {
    compiler();
    acquire();
    release();
    full();
    acquireRelease();
    fullFence();
    storeLoad();
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
    storeLoad();

    try std.testing.expectEqual(before_left, left);
    try std.testing.expectEqual(before_right, right);

    left +%= 1;
    compiler();
    right +%= 2;
    acquireRelease();
    storeLoad();

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
    full();
    acquireRelease();
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
    storeLoad();

    try std.testing.expectEqual(@as(u32, 41), packet.mirror);

    packet.value = 73;
    compiler();
    release();
    packet.ready = false;
    acquire();
    try std.testing.expect(!packet.ready);
    try std.testing.expectEqual(@as(u32, 73), packet.value);
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

test "phase3 barrier wrappers keep named store-load fences reviewable" {
    const Packet = struct {
        published: u32,
        observed: u32,
        ready: bool,
    };

    var packet = Packet{
        .published = 9,
        .observed = 0,
        .ready = false,
    };

    packet.published = 44;
    release();
    packet.ready = true;

    storeLoad();
    try std.testing.expect(packet.ready);
    packet.observed = packet.published;
    try std.testing.expectEqual(@as(u32, 44), packet.observed);
}

pub fn compiler() void {
    asm volatile ("" ::: .{ .memory = true });
}

pub fn acquire() void {
    var word: u8 = 0;
    _ = @atomicLoad(u8, &word, .acquire);
}

pub fn release() void {
    var word: u8 = 0;
    @atomicStore(u8, &word, 0, .release);
}

pub fn full() void {
    var word: u8 = 0;
    _ = @atomicRmw(u8, &word, .Xchg, 0, .seq_cst);
}

pub fn acquireRelease() void {
    var word: u8 = 0;
    _ = @atomicRmw(u8, &word, .Xchg, 0, .acq_rel);
}

pub fn fullFence() void {
    var word: u8 = 0;
    _ = @atomicRmw(u8, &word, .Xchg, 0, .seq_cst);
}

pub fn storeLoad() void {
    var word: u8 = 0;
    _ = @atomicRmw(u8, &word, .Xchg, 0, .seq_cst);
}
