// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub fn intPow(initial_base: u64, initial_exp: u32) u64 {
    var base = initial_base;
    var exp = initial_exp;
    var result: u64 = 1;

    while (exp != 0) {
        if ((exp & 1) != 0) result = result *% base;
        exp >>= 1;
        base = base *% base;
    }

    return result;
}

pub const int_pow = intPow;

test "int pow Linux KUnit vectors" {
    const cases = [_]struct {
        base: u64,
        exp: u32,
        want: u64,
    }{
        .{ .base = 64, .exp = 0, .want = 1 },
        .{ .base = 64, .exp = 1, .want = 64 },
        .{ .base = 0, .exp = 5, .want = 0 },
        .{ .base = 1, .exp = 64, .want = 1 },
        .{ .base = 2, .exp = 2, .want = 4 },
        .{ .base = 2, .exp = 3, .want = 8 },
        .{ .base = 5, .exp = 5, .want = 3125 },
        .{ .base = std.math.maxInt(u64), .exp = 1, .want = std.math.maxInt(u64) },
        .{ .base = 2, .exp = 63, .want = 9223372036854775808 },
    };

    for (cases) |tc| {
        try std.testing.expectEqual(tc.want, intPow(tc.base, tc.exp));
    }
}

test "int pow wraps like C unsigned u64" {
    try std.testing.expectEqual(@as(u64, 1), intPow(0, 0));
    try std.testing.expectEqual(@as(u64, 0), intPow(2, 64));
    try std.testing.expectEqual(@as(u64, 1), intPow(std.math.maxInt(u64), 2));
    try std.testing.expectEqual(std.math.maxInt(u64), intPow(std.math.maxInt(u64), 3));
    try std.testing.expectEqual(std.math.maxInt(u64), intPow(std.math.maxInt(u64), std.math.maxInt(u32)));
}
