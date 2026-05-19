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

test "software hweight helpers stay aligned with direct popcount across sampled widths" {
    var byte_value: u16 = 0;
    while (byte_value <= std.math.maxInt(u8)) : (byte_value += 1) {
        const narrowed: u8 = @intCast(byte_value);
        try std.testing.expectEqual(@as(u32, @popCount(narrowed)), swHweight8(byte_value));
    }

    const values16 = [_]u16{
        0x0000,
        0x0001,
        0x00ff,
        0x0f0f,
        0x5555,
        0x8001,
        0xaaaa,
        0xff00,
        0xffff,
    };
    for (values16) |value| {
        try std.testing.expectEqual(@as(u32, @popCount(value)), swHweight16(value));
    }

    const values32 = [_]u32{
        0x0000_0000,
        0x0000_0001,
        0x00ff_00ff,
        0x0f0f_f0f0,
        0x1357_9bdf,
        0x8000_0001,
        0xaaaa_5555,
        0xff00_ff00,
        0xffff_ffff,
    };
    for (values32) |value| {
        try std.testing.expectEqual(@as(u32, @popCount(value)), swHweight32(value));
    }

    const values64 = [_]u64{
        0x0000_0000_0000_0000,
        0x0000_0000_0000_0001,
        0x00ff_00ff_00ff_00ff,
        0x0f0f_f0f0_0f0f_f0f0,
        0x0123_4567_89ab_cdef,
        0x8000_0000_0000_0001,
        0xaaaa_5555_3333_cccc,
        0xff00_ff00_00ff_00ff,
        0xffff_ffff_ffff_ffff,
    };
    for (values64) |value| {
        try std.testing.expectEqual(@as(u64, @popCount(value)), swHweight64(value));
    }
}

test "hweightLong stays aligned with direct popcount on native-word samples" {
    const native_values = if (@sizeOf(usize) == 4)
        [_]usize{
            0x0000_0000,
            0x0000_0001,
            0x00ff_00ff,
            0x0f0f_f0f0,
            0x8000_0001,
            0xffff_ffff,
        }
    else
        [_]usize{
            0x0000_0000_0000_0000,
            0x0000_0000_0000_0001,
            0x00ff_00ff_00ff_00ff,
            0x0f0f_f0f0_0f0f_f0f0,
            0x8000_0000_0000_0001,
            0xffff_ffff_ffff_ffff,
        };

    for (native_values) |value| {
        try std.testing.expectEqual(@popCount(value), hweightLong(value));
        try std.testing.expectEqual(hweightLong(value), hweight_long(value));
    }
}
