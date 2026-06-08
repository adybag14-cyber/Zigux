// SPDX-License-Identifier: GPL-2.0-or-later
const std = @import("std");

pub fn __ucmpdi2(a: u64, b: u64) i32 {
    if (a < b) return 0;
    if (a > b) return 2;
    return 1;
}

test "ucmpdi2 compares unsigned 64 bit values" {
    try std.testing.expectEqual(@as(i32, 0), __ucmpdi2(0, 1));
    try std.testing.expectEqual(@as(i32, 1), __ucmpdi2(0xffff_ffff_0000_0000, 0xffff_ffff_0000_0000));
    try std.testing.expectEqual(@as(i32, 2), __ucmpdi2(0xffff_ffff_ffff_ffff, 0));
    try std.testing.expectEqual(@as(i32, 2), __ucmpdi2(0x0000_0001_0000_0000, 0xffff_ffff));
}
