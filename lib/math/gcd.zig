// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub fn gcd(a_in: usize, b_in: usize) usize {
    return gcdUnsigned(usize, a_in, b_in);
}

pub fn gcdUnsigned(comptime T: type, a_in: T, b_in: T) T {
    const Shift = std.math.Log2Int(T);
    var a = a_in;
    var b = b_in;
    const r = a | b;

    if (a == 0 or b == 0) return r;

    b >>= @as(Shift, @intCast(@ctz(b)));
    if (b == 1) return r & (0 -% r);

    while (true) {
        a >>= @as(Shift, @intCast(@ctz(a)));
        if (a == 1) return r & (0 -% r);
        if (a == b) return a << @as(Shift, @intCast(@ctz(r)));

        if (a < b) std.mem.swap(T, &a, &b);
        a -= b;
    }
}

test "gcd Linux KUnit vectors" {
    const max = std.math.maxInt(usize);
    const cases = [_]struct {
        a: usize,
        b: usize,
        want: usize,
    }{
        .{ .a = 48, .b = 18, .want = 6 },
        .{ .a = 18, .b = 48, .want = 6 },
        .{ .a = 56, .b = 98, .want = 14 },
        .{ .a = 17, .b = 13, .want = 1 },
        .{ .a = 101, .b = 103, .want = 1 },
        .{ .a = 270, .b = 192, .want = 6 },
        .{ .a = 0, .b = 5, .want = 5 },
        .{ .a = 7, .b = 0, .want = 7 },
        .{ .a = 36, .b = 36, .want = 36 },
        .{ .a = max, .b = 1, .want = 1 },
        .{ .a = max, .b = max, .want = max },
    };

    for (cases) |tc| {
        try std.testing.expectEqual(tc.want, gcd(tc.a, tc.b));
    }
}

test "gcd zero and powers of two" {
    try std.testing.expectEqual(@as(usize, 0), gcd(0, 0));
    try std.testing.expectEqual(@as(usize, 8), gcd(24, 40));
    try std.testing.expectEqual(@as(usize, 1 << 20), gcd(1 << 20, 3 << 20));
}

test "gcd unsigned helper supports fixed widths" {
    try std.testing.expectEqual(@as(u32, 6), gcdUnsigned(u32, 270, 192));
    try std.testing.expectEqual(@as(u64, 1), gcdUnsigned(u64, std.math.maxInt(u64), 2));
    try std.testing.expectEqual(@as(u64, 1 << 32), gcdUnsigned(u64, 3 << 32, 5 << 32));
}
