const std = @import("std");

pub fn swHweight8(value: u32) u32 {
    var result = value - ((value >> 1) & 0x55);
    result = (result & 0x33) + ((result >> 2) & 0x33);
    return (result + (result >> 4)) & 0x0f;
}

pub fn swHweight16(value: u32) u32 {
    var result = value - ((value >> 1) & 0x5555);
    result = (result & 0x3333) + ((result >> 2) & 0x3333);
    result = (result + (result >> 4)) & 0x0f0f;
    return (result + (result >> 8)) & 0x00ff;
}

pub fn swHweight32(value: u32) u32 {
    var result = value - ((value >> 1) & 0x5555_5555);
    result = (result & 0x3333_3333) + ((result >> 2) & 0x3333_3333);
    result = (result + (result >> 4)) & 0x0f0f_0f0f;
    result = result + (result >> 8);
    return (result + (result >> 16)) & 0x0000_00ff;
}

pub fn swHweight64(value: u64) u64 {
    if (@sizeOf(usize) == 4) {
        return swHweight32(@intCast(value >> 32)) + swHweight32(@intCast(value));
    }

    var result = value - ((value >> 1) & 0x5555_5555_5555_5555);
    result = (result & 0x3333_3333_3333_3333) + ((result >> 2) & 0x3333_3333_3333_3333);
    result = (result + (result >> 4)) & 0x0f0f_0f0f_0f0f_0f0f;
    result = result + (result >> 8);
    result = result + (result >> 16);
    return (result + (result >> 32)) & 0x0000_0000_0000_00ff;
}

pub fn hweightLong(value: usize) usize {
    return if (@sizeOf(usize) == 4)
        @intCast(swHweight32(@intCast(value)))
    else
        @intCast(swHweight64(@intCast(value)));
}

pub const __sw_hweight8 = swHweight8;
pub const __sw_hweight16 = swHweight16;
pub const __sw_hweight32 = swHweight32;
pub const __sw_hweight64 = swHweight64;
pub const hweight_long = hweightLong;

test "software hweight helpers match popcount" {
    try std.testing.expectEqual(@as(u32, 4), swHweight8(0b1111_0000));
    try std.testing.expectEqual(@as(u32, 8), swHweight16(0b1111_0000_1111_0000));
    try std.testing.expectEqual(@as(u32, 16), swHweight32(0xf0f0_f0f0));
    try std.testing.expectEqual(@as(u64, 32), swHweight64(0xf0f0_f0f0_f0f0_f0f0));
    try std.testing.expectEqual(@popCount(@as(usize, 0xf0f0)), hweightLong(0xf0f0));
}

test "software hweight helpers keep low-width limits and full-width boundaries" {
    try std.testing.expectEqual(@as(u32, 0), swHweight8(0x100));
    try std.testing.expectEqual(@as(u32, 8), swHweight8(0x1ff));
    try std.testing.expectEqual(@as(u32, 0), swHweight16(0x1_0000));
    try std.testing.expectEqual(@as(u32, 16), swHweight16(0x1_ffff));
    try std.testing.expectEqual(@as(u32, 0), swHweight32(0));
    try std.testing.expectEqual(@as(u32, 32), swHweight32(0xffff_ffff));
    try std.testing.expectEqual(@as(u64, 0), swHweight64(0));
    try std.testing.expectEqual(@as(u64, 64), swHweight64(0xffff_ffff_ffff_ffff));
    try std.testing.expectEqual(@as(usize, @popCount(@as(usize, 0x1_0000))), hweightLong(0x1_0000));
    try std.testing.expectEqual(@as(usize, @bitSizeOf(usize)), hweightLong(std.math.maxInt(usize)));
}

test "software hweight helpers truncate sparse overflow bits to helper width" {
    try std.testing.expectEqual(@as(u32, @popCount(@as(u8, 0xa5))), swHweight8(0x1a5));
    try std.testing.expectEqual(@as(u32, @popCount(@as(u16, 0x9345))), swHweight16(0x2_9345));
    try std.testing.expectEqual(@as(u32, @popCount(@as(u32, 0x8000_0001))), swHweight32(0x8000_0001));
    try std.testing.expectEqual(@as(u64, @popCount(@as(u64, 0x8000_0000_0000_0001))), swHweight64(0x8000_0000_0000_0001));

    const long_value: usize = if (@sizeOf(usize) == 4) 0x8000_0001 else 0x8000_0000_0000_0001;
    try std.testing.expectEqual(@as(usize, @popCount(long_value)), hweightLong(long_value));
}

test "Linux-style hweight aliases mirror the primary helper surface" {
    try std.testing.expectEqual(swHweight8(0xf0), __sw_hweight8(0xf0));
    try std.testing.expectEqual(swHweight16(0xf0f0), __sw_hweight16(0xf0f0));
    try std.testing.expectEqual(swHweight32(0xf0f0_f0f0), __sw_hweight32(0xf0f0_f0f0));
    try std.testing.expectEqual(
        swHweight64(0xf0f0_f0f0_f0f0_f0f0),
        __sw_hweight64(0xf0f0_f0f0_f0f0_f0f0),
    );
    try std.testing.expectEqual(hweightLong(0xf0f0), hweight_long(0xf0f0));
}
