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
