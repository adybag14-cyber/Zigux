// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");
const gcd_mod = @import("gcd.zig");

pub fn lcm(a: usize, b: usize) usize {
    if (a == 0 or b == 0) return 0;
    return (a / gcd_mod.gcd(a, b)) *% b;
}

pub fn lcmNotZero(a: usize, b: usize) usize {
    const value = lcm(a, b);
    if (value != 0) return value;
    return if (b != 0) b else a;
}

pub const lcm_not_zero = lcmNotZero;

test "lcm zero handling" {
    try std.testing.expectEqual(@as(usize, 0), lcm(0, 0));
    try std.testing.expectEqual(@as(usize, 0), lcm(0, 7));
    try std.testing.expectEqual(@as(usize, 0), lcm(7, 0));
}

test "lcm common values" {
    try std.testing.expectEqual(@as(usize, 1), lcm(1, 1));
    try std.testing.expectEqual(@as(usize, 12), lcm(3, 4));
    try std.testing.expectEqual(@as(usize, 42), lcm(21, 6));
    try std.testing.expectEqual(@as(usize, 84), lcm(28, 21));
}

test "lcm not zero mirrors Linux fallback" {
    try std.testing.expectEqual(@as(usize, 0), lcmNotZero(0, 0));
    try std.testing.expectEqual(@as(usize, 7), lcmNotZero(0, 7));
    try std.testing.expectEqual(@as(usize, 7), lcmNotZero(7, 0));
    try std.testing.expectEqual(@as(usize, 18), lcmNotZero(6, 9));
}

test "lcm not zero returns wrapped nonzero lcm" {
    const high = std.math.maxInt(usize) / 2 + 1;
    try std.testing.expectEqual(high, lcmNotZero(high, 3));
}
