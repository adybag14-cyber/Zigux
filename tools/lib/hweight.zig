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

test "software hweight helpers preserve complement symmetry within helper width" {
    const cases8 = [_]u32{ 0x00, 0x01, 0xa5, 0xff, 0x1ff };
    for (cases8) |raw| {
        const value = raw & 0xff;
        try std.testing.expectEqual(@as(u32, 8), swHweight8(value) + swHweight8((~value) & 0xff));
    }

    const cases16 = [_]u32{ 0x0000, 0x0001, 0x9345, 0xffff, 0x1_ffff };
    for (cases16) |raw| {
        const value = raw & 0xffff;
        try std.testing.expectEqual(@as(u32, 16), swHweight16(value) + swHweight16((~value) & 0xffff));
    }

    const cases32 = [_]u32{ 0x0000_0000, 0x0000_0001, 0x89ab_cdef, 0xffff_ffff };
    for (cases32) |value| {
        try std.testing.expectEqual(@as(u32, 32), swHweight32(value) + swHweight32(~value));
    }

    const cases64 = [_]u64{ 0x0000_0000_0000_0000, 0x0000_0000_0000_0001, 0x0123_4567_89ab_cdef, 0xffff_ffff_ffff_ffff };
    for (cases64) |value| {
        try std.testing.expectEqual(@as(u64, 64), swHweight64(value) + swHweight64(~value));
    }

    const cases_long = if (@sizeOf(usize) == 4)
        [_]usize{ 0x0000_0000, 0x0000_0001, 0x89ab_cdef, 0xffff_ffff }
    else
        [_]usize{ 0x0000_0000_0000_0000, 0x0000_0000_0000_0001, 0x0123_4567_89ab_cdef, 0xffff_ffff_ffff_ffff };
    for (cases_long) |value| {
        try std.testing.expectEqual(@as(usize, @bitSizeOf(usize)), hweightLong(value) + hweightLong(~value));
    }
}

test "software hweight helpers agree across zero-extended widths" {
    const cases8 = [_]u8{ 0x00, 0x01, 0xa5, 0xff };
    for (cases8) |value| {
        const expected = swHweight8(value);
        try std.testing.expectEqual(expected, swHweight16(value));
        try std.testing.expectEqual(expected, swHweight32(value));
        try std.testing.expectEqual(@as(u64, expected), swHweight64(value));
        try std.testing.expectEqual(@as(usize, expected), hweightLong(value));
    }

    const cases16 = [_]u16{ 0x0000, 0x0001, 0x9345, 0xffff };
    for (cases16) |value| {
        const expected = swHweight16(value);
        try std.testing.expectEqual(expected, swHweight32(value));
        try std.testing.expectEqual(@as(u64, expected), swHweight64(value));
        try std.testing.expectEqual(@as(usize, expected), hweightLong(value));
    }

    const cases32 = [_]u32{ 0x0000_0000, 0x0000_0001, 0x89ab_cdef, 0xffff_ffff };
    for (cases32) |value| {
        const expected = swHweight32(value);
        try std.testing.expectEqual(@as(u64, expected), swHweight64(value));
        if (@sizeOf(usize) >= 4) {
            try std.testing.expectEqual(@as(usize, expected), hweightLong(value));
        }
    }
}

test "software hweight helpers preserve bit-reversal symmetry within helper width" {
    const cases8 = [_]u8{ 0x00, 0x01, 0x3c, 0xa5, 0xff };
    for (cases8) |value| {
        try std.testing.expectEqual(swHweight8(value), swHweight8(@bitReverse(value)));
    }

    const cases16 = [_]u16{ 0x0000, 0x0001, 0x00f0, 0x9345, 0xffff };
    for (cases16) |value| {
        try std.testing.expectEqual(swHweight16(value), swHweight16(@bitReverse(value)));
    }

    const cases32 = [_]u32{ 0x0000_0000, 0x0000_0001, 0x0000_f0f0, 0x89ab_cdef, 0xffff_ffff };
    for (cases32) |value| {
        try std.testing.expectEqual(swHweight32(value), swHweight32(@bitReverse(value)));
    }

    const cases64 = [_]u64{ 0x0000_0000_0000_0000, 0x0000_0000_0000_0001, 0x0000_0000_f0f0_0f0f, 0x0123_4567_89ab_cdef, 0xffff_ffff_ffff_ffff };
    for (cases64) |value| {
        try std.testing.expectEqual(swHweight64(value), swHweight64(@bitReverse(value)));
    }

    const cases_long = if (@sizeOf(usize) == 4)
        [_]usize{ 0x0000_0000, 0x0000_0001, 0x0f0f_f0f0, 0x89ab_cdef, 0xffff_ffff }
    else
        [_]usize{ 0x0000_0000_0000_0000, 0x0000_0000_0000_0001, 0x0f0f_f0f0_00ff_ff00, 0x0123_4567_89ab_cdef, 0xffff_ffff_ffff_ffff };
    for (cases_long) |value| {
        try std.testing.expectEqual(hweightLong(value), hweightLong(@bitReverse(value)));
    }
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
