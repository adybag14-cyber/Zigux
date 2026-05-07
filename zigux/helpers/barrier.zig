const std = @import("std");

inline fn compilerBarrier() void {
    asm volatile ("" ::: .{ .memory = true });
}

pub fn acquire() void {
    compilerBarrier();
}

pub fn release() void {
    compilerBarrier();
}

pub fn full() void {
    compilerBarrier();
}

pub fn acquireRelease() void {
    compilerBarrier();
}

test "phase3 barrier wrappers compile" {
    acquire();
    release();
    full();
    acquireRelease();
}

test "phase3 barrier wrappers stay local to caller state" {
    var left: u8 = 7;
    var right: u8 = 19;
    const before_left = left;
    const before_right = right;

    acquire();
    release();
    full();
    acquireRelease();

    try std.testing.expectEqual(before_left, left);
    try std.testing.expectEqual(before_right, right);

    left +%= 1;
    right +%= 2;
    acquireRelease();

    try std.testing.expectEqual(@as(u8, 8), left);
    try std.testing.expectEqual(@as(u8, 21), right);
}

test "phase3 barrier wrappers keep acquire-release handoff reviewable" {
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
    release();
    packet.ready = true;

    acquire();
    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 41), packet.value);

    full();
    packet.mirror = packet.value;
    acquireRelease();

    try std.testing.expectEqual(@as(u32, 41), packet.mirror);

    packet.value = 73;
    release();
    packet.ready = false;
    acquire();
    try std.testing.expect(!packet.ready);
    try std.testing.expectEqual(@as(u32, 73), packet.value);
}
