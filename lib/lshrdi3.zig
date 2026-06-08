// SPDX-License-Identifier: GPL-2.0-or-later
const std = @import("std");

pub fn __lshrdi3(u: i64, b: u6) i64 {
    return @bitCast(@as(u64, @bitCast(u)) >> b);
}

pub fn lshrdi3Unsigned(u: u64, b: u6) u64 {
    return u >> b;
}

test "lshrdi3 inserts zeros from the top" {
    try std.testing.expectEqual(@as(u64, 0x4000_0000_0000_0000), lshrdi3Unsigned(0x8000_0000_0000_0000, 1));
    try std.testing.expectEqual(@as(u64, 1), lshrdi3Unsigned(0x8000_0000_0000_0000, 63));
    try std.testing.expectEqual(@as(i64, 0x7fff_ffff_ffff_ffff), __lshrdi3(-1, 1));
    try std.testing.expectEqual(@as(i64, 0x1234_5678_9abc_def0), __lshrdi3(0x1234_5678_9abc_def0, 0));
}
