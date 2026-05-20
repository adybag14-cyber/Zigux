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

fn expectClearLowestSetBitIdentity32(value: u32) !void {
    if (value == 0) return;
    const cleared = value & (value - 1);
    try std.testing.expectEqual(swHweight32(value) - 1, swHweight32(cleared));
    try std.testing.expectEqual(__sw_hweight32(value) - 1, __sw_hweight32(cleared));
}

fn expectClearLowestSetBitIdentity64(value: u64) !void {
    if (value == 0) return;
    const cleared = value & (value - 1);
    try std.testing.expectEqual(swHweight64(value) - 1, swHweight64(cleared));
    try std.testing.expectEqual(__sw_hweight64(value) - 1, __sw_hweight64(cleared));
}

fn expectClearLowestSetBitIdentityLong(value: usize) !void {
    if (value == 0) return;
    const cleared = value & (value - 1);
    try std.testing.expectEqual(hweightLong(value) - 1, hweightLong(cleared));
    try std.testing.expectEqual(hweight_long(value) - 1, hweight_long(cleared));
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

test "software hweight helpers drop exactly one bit when clearing the lowest set bit" {
    var value8: u32 = 1;
    while (value8 <= 0xff) : (value8 += 1) {
        const cleared = value8 & (value8 - 1);
        try std.testing.expectEqual(swHweight8(value8) - 1, swHweight8(cleared));
        try std.testing.expectEqual(__sw_hweight8(value8) - 1, __sw_hweight8(cleared));
    }

    var value16: u32 = 1;
    while (value16 <= 0xffff) : (value16 += 1) {
        const cleared = value16 & (value16 - 1);
        try std.testing.expectEqual(swHweight16(value16) - 1, swHweight16(cleared));
        try std.testing.expectEqual(__sw_hweight16(value16) - 1, __sw_hweight16(cleared));
    }

    var lcg32: u32 = 0x1234_5678;
    var iter32: usize = 0;
    while (iter32 < 256) : (iter32 += 1) {
        lcg32 = lcg32 *% 1_664_525 +% 1_013_904_223;
        try expectClearLowestSetBitIdentity32(lcg32);
    }
    try expectClearLowestSetBitIdentity32(0xffff_ffff);
    try expectClearLowestSetBitIdentity32(0x8000_0001);

    var lcg64: u64 = 0x0123_4567_89ab_cdef;
    var iter64: usize = 0;
    while (iter64 < 256) : (iter64 += 1) {
        lcg64 = lcg64 *% 6_364_136_223_846_793_005 +% 1_442_695_040_888_963_407;
        try expectClearLowestSetBitIdentity64(lcg64);
    }
    try expectClearLowestSetBitIdentity64(0xffff_ffff_ffff_ffff);
    try expectClearLowestSetBitIdentity64(0x8000_0000_0000_0001);

    var bit: usize = 0;
    while (bit < @bitSizeOf(usize)) : (bit += 1) {
        try expectClearLowestSetBitIdentityLong(@as(usize, 1) << @intCast(bit));
    }
    try expectClearLowestSetBitIdentityLong(std.math.maxInt(usize));
    try expectClearLowestSetBitIdentityLong(if (@sizeOf(usize) == 4) 0xdead_beef else 0xdead_beef_cafe_babe);
}
