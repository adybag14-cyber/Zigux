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

fn rotateLeft8(value: u32, shift: usize) u32 {
    const masked = value & 0xff;
    const amount: u5 = @intCast(shift % 8);
    if (amount == 0) {
        return masked;
    }
    return ((masked << amount) | (masked >> @as(u5, @intCast(8 - amount)))) & 0xff;
}

fn rotateLeft16(value: u32, shift: usize) u32 {
    const masked = value & 0xffff;
    const amount: u5 = @intCast(shift % 16);
    if (amount == 0) {
        return masked;
    }
    return ((masked << amount) | (masked >> @as(u5, @intCast(16 - amount)))) & 0xffff;
}

fn rotateLeft32(value: u32, shift: usize) u32 {
    const amount: u5 = @intCast(shift % 32);
    if (amount == 0) {
        return value;
    }
    const back: u5 = 0 -% amount;
    return (value << amount) | (value >> back);
}

fn rotateLeft64(value: u64, shift: usize) u64 {
    const amount: u6 = @intCast(shift % 64);
    if (amount == 0) {
        return value;
    }
    const back: u6 = 0 -% amount;
    return (value << amount) | (value >> back);
}

fn rotateLeftLong(value: usize, shift: usize) usize {
    return if (@sizeOf(usize) == 4)
        @intCast(rotateLeft32(@intCast(value), shift))
    else
        @intCast(rotateLeft64(@intCast(value), shift));
}

fn expectRotateInvariant8(value: u32) !void {
    const expected = swHweight8(value & 0xff);
    var shift: usize = 0;
    while (shift < 8) : (shift += 1) {
        const rotated = rotateLeft8(value, shift);
        try std.testing.expectEqual(expected, swHweight8(rotated));
        try std.testing.expectEqual(expected, __sw_hweight8(rotated));
    }
}

fn expectRotateInvariant16(value: u32) !void {
    const expected = swHweight16(value & 0xffff);
    var shift: usize = 0;
    while (shift < 16) : (shift += 1) {
        const rotated = rotateLeft16(value, shift);
        try std.testing.expectEqual(expected, swHweight16(rotated));
        try std.testing.expectEqual(expected, __sw_hweight16(rotated));
    }
}

fn expectRotateInvariant32(value: u32) !void {
    const expected = swHweight32(value);
    var shift: usize = 0;
    while (shift < 32) : (shift += 1) {
        const rotated = rotateLeft32(value, shift);
        try std.testing.expectEqual(expected, swHweight32(rotated));
        try std.testing.expectEqual(expected, __sw_hweight32(rotated));
    }
}

fn expectRotateInvariant64(value: u64) !void {
    const expected = swHweight64(value);
    var shift: usize = 0;
    while (shift < 64) : (shift += 1) {
        const rotated = rotateLeft64(value, shift);
        try std.testing.expectEqual(expected, swHweight64(rotated));
        try std.testing.expectEqual(expected, __sw_hweight64(rotated));
    }
}

fn expectRotateInvariantLong(value: usize) !void {
    const expected = hweightLong(value);
    var shift: usize = 0;
    while (shift < @bitSizeOf(usize)) : (shift += 1) {
        const rotated = rotateLeftLong(value, shift);
        try std.testing.expectEqual(expected, hweightLong(rotated));
        try std.testing.expectEqual(expected, hweight_long(rotated));
    }
}

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

test "hweight helpers stay invariant under in-width bit rotation" {
    try expectRotateInvariant8(0x00);
    try expectRotateInvariant8(0x96);
    try expectRotateInvariant8(0xff);
    try expectRotateInvariant16(0x0000);
    try expectRotateInvariant16(0x963c);
    try expectRotateInvariant16(0xffff);
    try expectRotateInvariant32(0x0000_0000);
    try expectRotateInvariant32(0x963c_5aa5);
    try expectRotateInvariant32(0xffff_ffff);
    try expectRotateInvariant64(0x0000_0000_0000_0000);
    try expectRotateInvariant64(0x963c_5aa5_0f0f_f0f0);
    try expectRotateInvariant64(0xffff_ffff_ffff_ffff);
    try expectRotateInvariantLong(0);
    try expectRotateInvariantLong(if (@sizeOf(usize) == 4) 0x963c_5aa5 else 0x963c_5aa5_0f0f_f0f0);
    try expectRotateInvariantLong(std.math.maxInt(usize));
}
