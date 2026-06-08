// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub fn __ctzsi2(val: i32) i32 {
    return @intCast(@ctz(@as(u32, @bitCast(val))));
}

pub fn __clzsi2(val: i32) i32 {
    return @intCast(@clz(@as(u32, @bitCast(val))));
}

pub fn __ctzdi2(val: u64) i32 {
    return @intCast(@ctz(val));
}

pub fn __clzdi2(val: u64) i32 {
    return @intCast(@clz(val));
}

test "clz helpers match Linux fls-derived results" {
    try std.testing.expectEqual(@as(i32, 32), __clzsi2(0));
    try std.testing.expectEqual(@as(i32, 31), __clzsi2(1));
    try std.testing.expectEqual(@as(i32, 0), __clzsi2(@bitCast(@as(u32, 0x8000_0000))));
    try std.testing.expectEqual(@as(i32, 64), __clzdi2(0));
    try std.testing.expectEqual(@as(i32, 63), __clzdi2(1));
    try std.testing.expectEqual(@as(i32, 0), __clzdi2(0x8000_0000_0000_0000));
}

test "ctz helpers return first set bit indexes" {
    try std.testing.expectEqual(@as(i32, 0), __ctzsi2(1));
    try std.testing.expectEqual(@as(i32, 5), __ctzsi2(0b100000));
    try std.testing.expectEqual(@as(i32, 31), __ctzsi2(@bitCast(@as(u32, 0x8000_0000))));
    try std.testing.expectEqual(@as(i32, 0), __ctzdi2(1));
    try std.testing.expectEqual(@as(i32, 40), __ctzdi2(@as(u64, 1) << 40));
    try std.testing.expectEqual(@as(i32, 63), __ctzdi2(@as(u64, 1) << 63));
}
