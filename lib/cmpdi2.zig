// SPDX-License-Identifier: GPL-2.0-or-later
const std = @import("std");

pub fn __cmpdi2(a: i64, b: i64) i32 {
    if (a < b) return 0;
    if (a > b) return 2;
    return 1;
}

test "cmpdi2 returns libgcc ordering tokens" {
    try std.testing.expectEqual(@as(i32, 0), __cmpdi2(-2, -1));
    try std.testing.expectEqual(@as(i32, 0), __cmpdi2(-1, 0));
    try std.testing.expectEqual(@as(i32, 1), __cmpdi2(42, 42));
    try std.testing.expectEqual(@as(i32, 2), __cmpdi2(1, -1));
    try std.testing.expectEqual(@as(i32, 2), __cmpdi2(std.math.maxInt(i64), std.math.minInt(i64)));
}
