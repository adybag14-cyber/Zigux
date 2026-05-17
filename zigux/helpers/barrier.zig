const std = @import("std");

var fence_word: u8 = 0;

test "phase3 barrier wrappers compile" {
    compiler();
    acquire();
    release();
    full();
    acquireRelease();
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

    try std.testing.expectEqual(before_left, left);
    try std.testing.expectEqual(before_right, right);

    left +%= 1;
    compiler();
    right +%= 2;
    acquireRelease();

    try std.testing.expectEqual(@as(u8, 8), left);
    try std.testing.expectEqual(@as(u8, 21), right);
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

pub fn compiler() void {
    asm volatile ("" ::: .{ .memory = true });
}

pub fn acquire() void {
    _ = @atomicLoad(u8, &fence_word, .acquire);
}

pub fn release() void {
    @atomicStore(u8, &fence_word, 0, .release);
}

pub fn full() void {
    _ = @atomicRmw(u8, &fence_word, .Xchg, 0, .seq_cst);
}

pub fn acquireRelease() void {
    _ = @atomicRmw(u8, &fence_word, .Xchg, 0, .acq_rel);
}
