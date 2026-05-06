const std = @import("std");

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
    _ = @atomicLoad(u8, &word, .acquire);
    @atomicStore(u8, &word, 0, .release);
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
