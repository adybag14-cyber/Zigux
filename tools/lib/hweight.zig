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

fn expectUnionIntersectionIdentityU32(counter: fn (u32) u32, left: u32, right: u32) !void {
    try std.testing.expectEqual(counter(left | right) + counter(left & right), counter(left) + counter(right));
}

fn expectUnionIntersectionIdentityU64(counter: fn (u64) u64, left: u64, right: u64) !void {
    try std.testing.expectEqual(counter(left | right) + counter(left & right), counter(left) + counter(right));
}

fn bitMaskU32(bits: u6) u32 {
    return if (bits == 32) std.math.maxInt(u32) else (@as(u32, 1) << @intCast(bits)) - 1;
}

fn bitMaskU64(bits: u7) u64 {
    return if (bits == 64) std.math.maxInt(u64) else (@as(u64, 1) << @intCast(bits)) - 1;
}

fn rotateWithinU32(value: u32, amount: u6, bits: u6) u32 {
    const mask = bitMaskU32(bits);
    const narrowed = value & mask;
    const shift = amount % bits;
    if (shift == 0) {
        return narrowed;
    }
    return ((narrowed << @intCast(shift)) | (narrowed >> @intCast(bits - shift))) & mask;
}

fn rotateWithinU64(value: u64, amount: u7, bits: u7) u64 {
    const mask = bitMaskU64(bits);
    const narrowed = value & mask;
    const shift = amount % bits;
    if (shift == 0) {
        return narrowed;
    }
    return ((narrowed << @intCast(shift)) | (narrowed >> @intCast(bits - shift))) & mask;
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

test "software hweight helpers preserve union-intersection counts for overlaps" {
    const pairs8 = [_][2]u32{
        .{ 0xf3, 0x3f },
        .{ 0xc7, 0x7c },
        .{ 0xaa, 0xe3 },
    };
    for (pairs8) |pair| {
        try expectUnionIntersectionIdentityU32(swHweight8, pair[0], pair[1]);
        try std.testing.expectEqual(
            __sw_hweight8(pair[0] | pair[1]) + __sw_hweight8(pair[0] & pair[1]),
            __sw_hweight8(pair[0]) + __sw_hweight8(pair[1]),
        );
    }

    const pairs16 = [_][2]u32{
        .{ 0xf0f3, 0x3ff0 },
        .{ 0xc3c3, 0x33fc },
        .{ 0xaa55, 0xe31c },
    };
    for (pairs16) |pair| {
        try expectUnionIntersectionIdentityU32(swHweight16, pair[0], pair[1]);
        try std.testing.expectEqual(
            __sw_hweight16(pair[0] | pair[1]) + __sw_hweight16(pair[0] & pair[1]),
            __sw_hweight16(pair[0]) + __sw_hweight16(pair[1]),
        );
    }

    const pairs32 = [_][2]u32{
        .{ 0xf0f0_00f3, 0x3fff_f000 },
        .{ 0xc3c3_c3c3, 0x33fc_fc33 },
        .{ 0xaa55_aa55, 0xe31c_71c7 },
    };
    for (pairs32) |pair| {
        try expectUnionIntersectionIdentityU32(swHweight32, pair[0], pair[1]);
        try std.testing.expectEqual(
            __sw_hweight32(pair[0] | pair[1]) + __sw_hweight32(pair[0] & pair[1]),
            __sw_hweight32(pair[0]) + __sw_hweight32(pair[1]),
        );
    }

    const pairs64 = [_][2]u64{
        .{ 0xf0f0_00f3_3cff_c003, 0x3fff_f000_f0c3_c33c },
        .{ 0xc3c3_c3c3_0f0f_f0f0, 0x33fc_fc33_f0f0_0f0f },
        .{ 0xaa55_aa55_55aa_55aa, 0xe31c_71c7_1c63_c638 },
    };
    for (pairs64) |pair| {
        try expectUnionIntersectionIdentityU64(swHweight64, pair[0], pair[1]);
        try std.testing.expectEqual(
            __sw_hweight64(pair[0] | pair[1]) + __sw_hweight64(pair[0] & pair[1]),
            __sw_hweight64(pair[0]) + __sw_hweight64(pair[1]),
        );
    }

    const native_pairs = if (@sizeOf(usize) == 4)
        [_][2]usize{
            .{ 0xf0f0_00f3, 0x3fff_f000 },
            .{ 0xc3c3_c3c3, 0x33fc_fc33 },
        }
    else
        [_][2]usize{
            .{ 0xf0f0_00f3_3cff_c003, 0x3fff_f000_f0c3_c33c },
            .{ 0xc3c3_c3c3_0f0f_f0f0, 0x33fc_fc33_f0f0_0f0f },
        };
    for (native_pairs) |pair| {
        try std.testing.expectEqual(
            hweightLong(pair[0] | pair[1]) + hweightLong(pair[0] & pair[1]),
            hweightLong(pair[0]) + hweightLong(pair[1]),
        );
        try std.testing.expectEqual(
            hweight_long(pair[0] | pair[1]) + hweight_long(pair[0] & pair[1]),
            hweight_long(pair[0]) + hweight_long(pair[1]),
        );
    }
}

test "software hweight helpers preserve popcount under in-width rotations" {
    var value8: u32 = 0;
    while (value8 <= 0xff) : (value8 += 1) {
        var shift8: u6 = 0;
        while (shift8 < 8) : (shift8 += 1) {
            const rotated = rotateWithinU32(value8, shift8, 8);
            try std.testing.expectEqual(swHweight8(value8), swHweight8(rotated));
            try std.testing.expectEqual(__sw_hweight8(value8), __sw_hweight8(rotated));
        }
    }

    const cases16 = [_]u32{ 0x0001, 0x00f0, 0x1234, 0x8001, 0xa55a, 0xff00 };
    const shifts16 = [_]u6{ 1, 4, 7, 12, 15 };
    for (cases16) |value| {
        for (shifts16) |shift| {
            const rotated = rotateWithinU32(value, shift, 16);
            try std.testing.expectEqual(swHweight16(value), swHweight16(rotated));
            try std.testing.expectEqual(__sw_hweight16(value), __sw_hweight16(rotated));
        }
    }

    const cases32 = [_]u32{ 0x0000_0001, 0x00f0_f00f, 0x1234_5678, 0x8000_0001, 0xa55a_5aa5, 0xff00_ff00 };
    const shifts32 = [_]u6{ 1, 5, 13, 19, 31 };
    for (cases32) |value| {
        for (shifts32) |shift| {
            const rotated = rotateWithinU32(value, shift, 32);
            try std.testing.expectEqual(swHweight32(value), swHweight32(rotated));
            try std.testing.expectEqual(__sw_hweight32(value), __sw_hweight32(rotated));
        }
    }

    const cases64 = [_]u64{
        0x0000_0000_0000_0001,
        0x00f0_f00f_0ff0_f00f,
        0x1234_5678_9abc_def0,
        0x8000_0000_0000_0001,
        0xa55a_5aa5_9669_6996,
        0xff00_ff00_00ff_00ff,
    };
    const shifts64 = [_]u7{ 1, 7, 17, 29, 63 };
    for (cases64) |value| {
        for (shifts64) |shift| {
            const rotated = rotateWithinU64(value, shift, 64);
            try std.testing.expectEqual(swHweight64(value), swHweight64(rotated));
            try std.testing.expectEqual(__sw_hweight64(value), __sw_hweight64(rotated));
        }
    }

    const native_cases = if (@sizeOf(usize) == 4)
        [_]usize{ 0x0000_0001, 0x00f0_f00f, 0x1234_5678, 0xa55a_5aa5, 0xff00_ff00 }
    else
        [_]usize{
            0x0000_0000_0000_0001,
            0x00f0_f00f_0ff0_f00f,
            0x1234_5678_9abc_def0,
            0xa55a_5aa5_9669_6996,
            0xff00_ff00_00ff_00ff,
        };
    const native_shifts = if (@sizeOf(usize) == 4)
        [_]u7{ 1, 5, 13, 31 }
    else
        [_]u7{ 1, 7, 17, 63 };
    for (native_cases) |value| {
        for (native_shifts) |shift| {
            const rotated = if (@sizeOf(usize) == 4)
                @as(usize, @intCast(rotateWithinU32(@intCast(value), @intCast(shift), 32)))
            else
                @as(usize, @intCast(rotateWithinU64(@intCast(value), shift, 64)));
            try std.testing.expectEqual(hweightLong(value), hweightLong(rotated));
            try std.testing.expectEqual(hweight_long(value), hweight_long(rotated));
        }
    }
}
