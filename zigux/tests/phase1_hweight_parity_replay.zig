const std = @import("std");
const hweight = @import("hweight");

fn parityFromCount(count: anytype) u1 {
    return @intCast(count & 1);
}

fn parityOf(comptime T: type, value: T) u1 {
    return @intCast(@popCount(value) & 1);
}

test "width-specific hweight helpers preserve popcount parity" {
    const values8 = [_]u32{ 0x00, 0x01, 0x03, 0x7f, 0x80, 0xa5, 0xf0, 0xff };
    for (values8) |value| {
        try std.testing.expectEqual(parityOf(u8, @truncate(value)), parityFromCount(hweight.swHweight8(value)));
        try std.testing.expectEqual(parityOf(u8, @truncate(value)), parityFromCount(hweight.__sw_hweight8(value)));
    }

    const values16 = [_]u32{ 0x0000, 0x0001, 0x00ff, 0x0f0f, 0x8001, 0xa55a, 0xffff };
    for (values16) |value| {
        try std.testing.expectEqual(parityOf(u16, @truncate(value)), parityFromCount(hweight.swHweight16(value)));
        try std.testing.expectEqual(parityOf(u16, @truncate(value)), parityFromCount(hweight.__sw_hweight16(value)));
    }

    const values32 = [_]u32{ 0x0000_0000, 0x0000_0001, 0x0000_ffff, 0x0f0f_f0f0, 0x8000_0001, 0xa5a5_5a5a, 0xffff_ffff };
    for (values32) |value| {
        try std.testing.expectEqual(parityOf(u32, value), parityFromCount(hweight.swHweight32(value)));
        try std.testing.expectEqual(parityOf(u32, value), parityFromCount(hweight.__sw_hweight32(value)));
    }

    const values64 = [_]u64{
        0x0000_0000_0000_0000,
        0x0000_0000_0000_0001,
        0x0000_0000_ffff_ffff,
        0x0f0f_f0f0_a5a5_5a5a,
        0x8000_0000_0000_0001,
        0xa5a5_5a5a_ffff_0000,
        0xffff_ffff_ffff_ffff,
    };
    for (values64) |value| {
        try std.testing.expectEqual(parityOf(u64, value), parityFromCount(hweight.swHweight64(value)));
        try std.testing.expectEqual(parityOf(u64, value), parityFromCount(hweight.__sw_hweight64(value)));
    }
}

test "native-word hweight routing preserves popcount parity" {
    const values = [_]usize{
        0,
        1,
        0xff,
        0x0f0f,
        if (@sizeOf(usize) == 4) 0x8000_0001 else 0x8000_0000_0000_0001,
        if (@sizeOf(usize) == 4) 0xa55a_f00f else 0xa55a_f00f_cc33_55aa,
        std.math.maxInt(usize),
    };

    for (values) |value| {
        try std.testing.expectEqual(parityOf(usize, value), parityFromCount(hweight.hweightLong(value)));
        try std.testing.expectEqual(parityOf(usize, value), parityFromCount(hweight.hweight_long(value)));
    }
}
