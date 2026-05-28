const std = @import("std");
const hweight = @import("hweight");

fn reverseLowBitsU32(comptime width: u6, value: u32) u32 {
    return @bitReverse(value) >> @intCast(@bitSizeOf(u32) - width);
}

fn reverseLowBitsU64(comptime width: u7, value: u64) u64 {
    return @bitReverse(value) >> @intCast(@bitSizeOf(u64) - width);
}

test "hweight bit reversal replay keeps counts aligned across fixed widths" {
    var value8: u32 = 0;
    while (value8 < 0x100) : (value8 += 1) {
        const reversed = reverseLowBitsU32(8, value8);
        try std.testing.expectEqual(hweight.swHweight8(value8), hweight.swHweight8(reversed));
        try std.testing.expectEqual(hweight.__sw_hweight8(value8), hweight.__sw_hweight8(reversed));
    }

    for ([_]u32{ 0x0000, 0x0001, 0x00f1, 0x1234, 0x8001, 0xa55a, 0xffff }) |value16| {
        const reversed = reverseLowBitsU32(16, value16);
        try std.testing.expectEqual(hweight.swHweight16(value16), hweight.swHweight16(reversed));
        try std.testing.expectEqual(hweight.__sw_hweight16(value16), hweight.__sw_hweight16(reversed));
    }

    for ([_]u32{ 0x0000_0000, 0x0000_0001, 0x0123_4567, 0x89ab_cdef, 0x8000_0001, 0xa55a_5aa5, 0xffff_ffff }) |value32| {
        const reversed = reverseLowBitsU32(32, value32);
        try std.testing.expectEqual(hweight.swHweight32(value32), hweight.swHweight32(reversed));
        try std.testing.expectEqual(hweight.__sw_hweight32(value32), hweight.__sw_hweight32(reversed));
    }

    for ([_]u64{
        0x0000_0000_0000_0000,
        0x0000_0000_0000_0001,
        0x0123_4567_89ab_cdef,
        0xfedc_ba98_7654_3210,
        0x8000_0000_0000_0001,
        0xa55a_5aa5_c33c_3cc3,
        0xffff_ffff_ffff_ffff,
    }) |value64| {
        const reversed = reverseLowBitsU64(64, value64);
        try std.testing.expectEqual(hweight.swHweight64(value64), hweight.swHweight64(reversed));
        try std.testing.expectEqual(hweight.__sw_hweight64(value64), hweight.__sw_hweight64(reversed));
    }
}

test "hweightLong bit reversal replay stays aligned with native routing" {
    if (@sizeOf(usize) == 4) {
        for ([_]usize{
            0x0000_0000,
            0x0000_0001,
            0x0123_4567,
            0x89ab_cdef,
            0x8000_0001,
            0xa55a_5aa5,
            0xffff_ffff,
        }) |value| {
            const reversed = @as(usize, reverseLowBitsU32(32, @intCast(value)));
            try std.testing.expectEqual(hweight.hweightLong(value), hweight.hweightLong(reversed));
            try std.testing.expectEqual(hweight.hweight_long(value), hweight.hweight_long(reversed));
        }
    } else {
        for ([_]usize{
            0x0000_0000_0000_0000,
            0x0000_0000_0000_0001,
            0x0123_4567_89ab_cdef,
            0xfedc_ba98_7654_3210,
            0x8000_0000_0000_0001,
            0xa55a_5aa5_c33c_3cc3,
            0xffff_ffff_ffff_ffff,
        }) |value| {
            const reversed = @as(usize, @intCast(reverseLowBitsU64(64, @intCast(value))));
            try std.testing.expectEqual(hweight.hweightLong(value), hweight.hweightLong(reversed));
            try std.testing.expectEqual(hweight.hweight_long(value), hweight.hweight_long(reversed));
        }
    }
}
