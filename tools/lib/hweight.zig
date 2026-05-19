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

fn expectDisjointAdditivityU32(counter: fn (u32) u32, left: u32, right: u32) !void {
    try std.testing.expectEqual(@as(u32, 0), left & right);
    try std.testing.expectEqual(counter(left) + counter(right), counter(left | right));
}

fn expectDisjointAdditivityU64(counter: fn (u64) u64, left: u64, right: u64) !void {
    try std.testing.expectEqual(@as(u64, 0), left & right);
    try std.testing.expectEqual(counter(left) + counter(right), counter(left | right));
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

test "software hweight helpers stay additive across disjoint masks" {
    const pairs8 = [_][2]u32{
        .{ 0x55, 0xaa },
        .{ 0x0f, 0xf0 },
        .{ 0x81, 0x42 },
    };
    for (pairs8) |pair| {
        try expectDisjointAdditivityU32(swHweight8, pair[0], pair[1]);
        try std.testing.expectEqual(__sw_hweight8(pair[0]) + __sw_hweight8(pair[1]), __sw_hweight8(pair[0] | pair[1]));
    }

    const pairs16 = [_][2]u32{
        .{ 0x5555, 0xaaaa },
        .{ 0x00ff, 0xff00 },
        .{ 0x8001, 0x4210 },
    };
    for (pairs16) |pair| {
        try expectDisjointAdditivityU32(swHweight16, pair[0], pair[1]);
        try std.testing.expectEqual(__sw_hweight16(pair[0]) + __sw_hweight16(pair[1]), __sw_hweight16(pair[0] | pair[1]));
    }

    const pairs32 = [_][2]u32{
        .{ 0x5555_5555, 0xaaaa_aaaa },
        .{ 0x0000_ffff, 0xffff_0000 },
        .{ 0x8000_0001, 0x4210_8420 },
    };
    for (pairs32) |pair| {
        try expectDisjointAdditivityU32(swHweight32, pair[0], pair[1]);
        try std.testing.expectEqual(__sw_hweight32(pair[0]) + __sw_hweight32(pair[1]), __sw_hweight32(pair[0] | pair[1]));
    }

    const pairs64 = [_][2]u64{
        .{ 0x5555_5555_5555_5555, 0xaaaa_aaaa_aaaa_aaaa },
        .{ 0x0000_0000_ffff_ffff, 0xffff_ffff_0000_0000 },
        .{ 0x8000_0000_0000_0001, 0x4210_8421_0842_1084 },
    };
    for (pairs64) |pair| {
        try expectDisjointAdditivityU64(swHweight64, pair[0], pair[1]);
        try std.testing.expectEqual(__sw_hweight64(pair[0]) + __sw_hweight64(pair[1]), __sw_hweight64(pair[0] | pair[1]));
    }

    const native_pairs = if (@sizeOf(usize) == 4)
        [_][2]usize{
            .{ 0x5555_5555, 0xaaaa_aaaa },
            .{ 0x0000_ffff, 0xffff_0000 },
        }
    else
        [_][2]usize{
            .{ 0x5555_5555_5555_5555, 0xaaaa_aaaa_aaaa_aaaa },
            .{ 0x0000_0000_ffff_ffff, 0xffff_ffff_0000_0000 },
        };
    for (native_pairs) |pair| {
        try std.testing.expectEqual(@as(usize, 0), pair[0] & pair[1]);
        try std.testing.expectEqual(hweightLong(pair[0]) + hweightLong(pair[1]), hweightLong(pair[0] | pair[1]));
        try std.testing.expectEqual(hweight_long(pair[0]) + hweight_long(pair[1]), hweight_long(pair[0] | pair[1]));
    }
}
