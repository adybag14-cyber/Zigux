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

test "hweight helpers stay additive for disjoint masks" {
    const low8: u32 = 0b0001_0101;
    const high8: u32 = 0b1010_0000;
    try std.testing.expectEqual(swHweight8(low8) + swHweight8(high8), swHweight8(low8 | high8));
    try std.testing.expectEqual(__sw_hweight8(low8) + __sw_hweight8(high8), __sw_hweight8(low8 | high8));

    const low16: u32 = 0x0155;
    const high16: u32 = 0xa800;
    try std.testing.expectEqual(swHweight16(low16) + swHweight16(high16), swHweight16(low16 | high16));
    try std.testing.expectEqual(__sw_hweight16(low16) + __sw_hweight16(high16), __sw_hweight16(low16 | high16));

    const low32: u32 = 0x0001_5555;
    const high32: u32 = 0xa800_0000;
    try std.testing.expectEqual(swHweight32(low32) + swHweight32(high32), swHweight32(low32 | high32));
    try std.testing.expectEqual(__sw_hweight32(low32) + __sw_hweight32(high32), __sw_hweight32(low32 | high32));

    const low64: u64 = 0x0000_0000_0001_5555;
    const high64: u64 = 0xa800_0000_0000_0000;
    try std.testing.expectEqual(swHweight64(low64) + swHweight64(high64), swHweight64(low64 | high64));
    try std.testing.expectEqual(__sw_hweight64(low64) + __sw_hweight64(high64), __sw_hweight64(low64 | high64));

    const low_long: usize = 0x1555;
    const high_long: usize = if (@sizeOf(usize) == 4) 0xa800_0000 else 0xa800_0000_0000_0000;
    try std.testing.expectEqual(hweightLong(low_long) + hweightLong(high_long), hweightLong(low_long | high_long));
    try std.testing.expectEqual(hweight_long(low_long) + hweight_long(high_long), hweight_long(low_long | high_long));
}

test "narrow hweight helpers ignore bits outside their low lane" {
    const high_only: u32 = 0xffff_0000;
    try std.testing.expectEqual(@as(u32, 0), swHweight8(high_only));
    try std.testing.expectEqual(@as(u32, 0), __sw_hweight8(high_only));
    try std.testing.expectEqual(@as(u32, 0), swHweight16(high_only));
    try std.testing.expectEqual(@as(u32, 0), __sw_hweight16(high_only));

    const mixed8: u32 = 0xffff_ff81;
    try std.testing.expectEqual(@as(u32, 2), swHweight8(mixed8));
    try std.testing.expectEqual(@as(u32, 2), __sw_hweight8(mixed8));

    const mixed16: u32 = 0xffff_8001;
    try std.testing.expectEqual(@as(u32, 2), swHweight16(mixed16));
    try std.testing.expectEqual(@as(u32, 2), __sw_hweight16(mixed16));
}

test "hweight complement masks add up to lane widths" {
    const mask8: u32 = 0b0101_1010;
    try std.testing.expectEqual(@as(u32, 8), swHweight8(mask8) + swHweight8(~mask8));
    try std.testing.expectEqual(@as(u32, 8), __sw_hweight8(mask8) + __sw_hweight8(~mask8));

    const mask16: u32 = 0x5aa5;
    try std.testing.expectEqual(@as(u32, 16), swHweight16(mask16) + swHweight16(~mask16));
    try std.testing.expectEqual(@as(u32, 16), __sw_hweight16(mask16) + __sw_hweight16(~mask16));

    const mask32: u32 = 0x5aa5_c33c;
    try std.testing.expectEqual(@as(u32, 32), swHweight32(mask32) + swHweight32(~mask32));
    try std.testing.expectEqual(@as(u32, 32), __sw_hweight32(mask32) + __sw_hweight32(~mask32));

    const mask64: u64 = 0x5aa5_c33c_f00f_9669;
    try std.testing.expectEqual(@as(u64, 64), swHweight64(mask64) + swHweight64(~mask64));
    try std.testing.expectEqual(@as(u64, 64), __sw_hweight64(mask64) + __sw_hweight64(~mask64));

    const mask_long: usize = if (@sizeOf(usize) == 4) 0x5aa5_c33c else 0x5aa5_c33c_f00f_9669;
    try std.testing.expectEqual(@as(usize, @bitSizeOf(usize)), hweightLong(mask_long) + hweightLong(~mask_long));
    try std.testing.expectEqual(@as(usize, @bitSizeOf(usize)), hweight_long(mask_long) + hweight_long(~mask_long));
}
