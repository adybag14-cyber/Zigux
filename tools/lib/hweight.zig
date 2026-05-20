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

fn contiguousMask32(width: u8, start: u8, len: u8) u32 {
    std.debug.assert(start + len <= width);
    if (len == 0) {
        return 0;
    }

    const right_shift: u5 = @intCast(width - len);
    const left_shift: u5 = @intCast(start);
    const all_bits: u32 = std.math.maxInt(u32);
    const width_bits: u32 = if (width == 32) all_bits else all_bits >> @as(u5, @intCast(32 - width));
    const right_trimmed: u32 = if (len == width) width_bits else width_bits >> right_shift;
    return right_trimmed << left_shift;
}

fn contiguousMask64(width: u8, start: u8, len: u8) u64 {
    std.debug.assert(start + len <= width);
    if (len == 0) {
        return 0;
    }

    const right_shift: u6 = @intCast(width - len);
    const left_shift: u6 = @intCast(start);
    const all_bits: u64 = std.math.maxInt(u64);
    const width_bits: u64 = if (width == 64) all_bits else all_bits >> @as(u6, @intCast(64 - width));
    const right_trimmed: u64 = if (len == width) width_bits else width_bits >> right_shift;
    return right_trimmed << left_shift;
}

fn contiguousMaskLong(width: u8, start: u8, len: u8) usize {
    std.debug.assert(start + len <= width);
    if (len == 0) {
        return 0;
    }

    const Shift = if (@sizeOf(usize) == 4) u5 else u6;
    const right_shift: Shift = @intCast(width - len);
    const left_shift: Shift = @intCast(start);
    const all_bits: usize = std.math.maxInt(usize);
    const total_width: u8 = @bitSizeOf(usize);
    const width_bits: usize = if (width == total_width) all_bits else all_bits >> @as(Shift, @intCast(total_width - width));
    const right_trimmed: usize = if (len == width) width_bits else width_bits >> right_shift;
    return right_trimmed << left_shift;
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

test "hweight helpers count contiguous bit runs by exact run length" {
    var len8: u8 = 0;
    while (len8 <= 8) : (len8 += 1) {
        var start8: u8 = 0;
        while (start8 + len8 <= 8) : (start8 += 1) {
            const value = contiguousMask32(8, start8, len8);
            try std.testing.expectEqual(@as(u32, len8), swHweight8(value));
            try std.testing.expectEqual(@as(u32, len8), __sw_hweight8(value));
        }
    }

    var len16: u8 = 0;
    while (len16 <= 16) : (len16 += 1) {
        var start16: u8 = 0;
        while (start16 + len16 <= 16) : (start16 += 1) {
            const value = contiguousMask32(16, start16, len16);
            try std.testing.expectEqual(@as(u32, len16), swHweight16(value));
            try std.testing.expectEqual(@as(u32, len16), __sw_hweight16(value));
        }
    }

    var len32: u8 = 0;
    while (len32 <= 32) : (len32 += 1) {
        var start32: u8 = 0;
        while (start32 + len32 <= 32) : (start32 += 1) {
            const value = contiguousMask32(32, start32, len32);
            try std.testing.expectEqual(@as(u32, len32), swHweight32(value));
            try std.testing.expectEqual(@as(u32, len32), __sw_hweight32(value));
        }
    }

    var len64: u8 = 0;
    while (len64 <= 64) : (len64 += 1) {
        var start64: u8 = 0;
        while (start64 + len64 <= 64) : (start64 += 1) {
            const value = contiguousMask64(64, start64, len64);
            try std.testing.expectEqual(@as(u64, len64), swHweight64(value));
            try std.testing.expectEqual(@as(u64, len64), __sw_hweight64(value));
        }
    }

    const long_width: u8 = if (@sizeOf(usize) == 4) 32 else 64;
    var long_len: u8 = 0;
    while (long_len <= long_width) : (long_len += 1) {
        var long_start: u8 = 0;
        while (long_start + long_len <= long_width) : (long_start += 1) {
            const value = contiguousMaskLong(long_width, long_start, long_len);
            try std.testing.expectEqual(@as(usize, long_len), hweightLong(value));
            try std.testing.expectEqual(@as(usize, long_len), hweight_long(value));
        }
    }
}
