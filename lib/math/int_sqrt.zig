// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub fn intSqrt(x: usize) usize {
    return intSqrtUnsigned(usize, x);
}

pub fn int_sqrt(x: usize) usize {
    return intSqrt(x);
}

pub fn intSqrt64(x: u64) u32 {
    return @intCast(intSqrtUnsigned(u64, x));
}

pub fn int_sqrt64(x: u64) u32 {
    return intSqrt64(x);
}

fn intSqrtUnsigned(comptime T: type, input: T) T {
    const Shift = std.math.Log2Int(T);
    var x = input;
    var y: T = 0;

    if (x <= 1) return x;

    var m: T = @as(T, 1) << @as(Shift, @intCast(@bitSizeOf(T) - 2));
    while (m > x) : (m >>= 2) {}

    while (m != 0) : (m >>= 2) {
        const b = y +% m;
        y >>= 1;

        if (x >= b) {
            x -= b;
            y += m;
        }
    }

    return y;
}

test "int sqrt Linux KUnit vectors" {
    const cases = [_]struct {
        x: usize,
        want: usize,
    }{
        .{ .x = 0, .want = 0 },
        .{ .x = 1, .want = 1 },
        .{ .x = 2, .want = 1 },
        .{ .x = 3, .want = 1 },
        .{ .x = 4, .want = 2 },
        .{ .x = 5, .want = 2 },
        .{ .x = 6, .want = 2 },
        .{ .x = 7, .want = 2 },
        .{ .x = 8, .want = 2 },
        .{ .x = 9, .want = 3 },
        .{ .x = 15, .want = 3 },
        .{ .x = 16, .want = 4 },
        .{ .x = 17, .want = 4 },
        .{ .x = 80, .want = 8 },
        .{ .x = 81, .want = 9 },
        .{ .x = 82, .want = 9 },
        .{ .x = 255, .want = 15 },
        .{ .x = 256, .want = 16 },
        .{ .x = 257, .want = 16 },
        .{ .x = 2147483648, .want = 46340 },
        .{ .x = 4294967295, .want = 65535 },
    };

    for (cases) |tc| {
        try std.testing.expectEqual(tc.want, intSqrt(tc.x));
    }
}

test "int sqrt64 full u64 boundaries" {
    try std.testing.expectEqual(@as(u32, 0), intSqrt64(0));
    try std.testing.expectEqual(@as(u32, 1), intSqrt64(1));
    try std.testing.expectEqual(@as(u32, 4294967294), intSqrt64(18446744065119617024));
    try std.testing.expectEqual(@as(u32, 4294967295), intSqrt64(18446744065119617025));
    try std.testing.expectEqual(@as(u32, 4294967295), intSqrt64(std.math.maxInt(u64)));
}
