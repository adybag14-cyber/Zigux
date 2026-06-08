// SPDX-License-Identifier: GPL-2.0-or-later
const std = @import("std");

pub fn __ashldi3(u: i64, b: u6) i64 {
    return @bitCast(@as(u64, @bitCast(u)) << b);
}

test "ashldi3 shifts low and high words like libgcc helper" {
    try std.testing.expectEqual(@as(i64, 0x0000_0001_0000_0000), __ashldi3(1, 32));
    try std.testing.expectEqual(@as(i64, 0x0000_0002_0000_0000), __ashldi3(1, 33));
    try std.testing.expectEqual(@as(i64, @bitCast(@as(u64, 0xffff_ffff_ffff_fffe))), __ashldi3(-1, 1));
    try std.testing.expectEqual(@as(i64, 0x1234_5678_9abc_def0), __ashldi3(0x1234_5678_9abc_def0, 0));
}
