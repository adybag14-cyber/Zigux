// SPDX-License-Identifier: GPL-2.0-or-later
const std = @import("std");

pub fn __ashrdi3(u: i64, b: u6) i64 {
    return u >> b;
}

test "ashrdi3 preserves the sign bit" {
    try std.testing.expectEqual(@as(i64, -1), __ashrdi3(-1, 1));
    try std.testing.expectEqual(@as(i64, -2), __ashrdi3(-4, 1));
    try std.testing.expectEqual(@as(i64, -1), __ashrdi3(@bitCast(@as(u64, 0x8000_0000_0000_0000)), 63));
    try std.testing.expectEqual(@as(i64, 0x091a_2b3c_4d5e_6f78), __ashrdi3(0x1234_5678_9abc_def0, 1));
}
