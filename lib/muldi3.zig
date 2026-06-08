// SPDX-License-Identifier: GPL-2.0-or-later
const std = @import("std");

pub fn __muldi3(u: i64, v: i64) i64 {
    const lhs: u64 = @bitCast(u);
    const rhs: u64 = @bitCast(v);
    return @bitCast(lhs *% rhs);
}

test "muldi3 returns the low 64 bits of the product" {
    try std.testing.expectEqual(@as(i64, 0), __muldi3(0, 12345));
    try std.testing.expectEqual(@as(i64, -42), __muldi3(-1, 42));
    try std.testing.expectEqual(@as(i64, 0x0000_0001_0000_0000), __muldi3(0x1_0000, 0x1_0000));
    try std.testing.expectEqual(@as(i64, @bitCast(@as(u64, 0xffff_ffff_ffff_fffe))), __muldi3(std.math.maxInt(i64), 2));
}
