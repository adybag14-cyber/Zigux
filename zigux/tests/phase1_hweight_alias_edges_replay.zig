const std = @import("std");
const hweight = @import("hweight");

test "phase1 hweight aliases mirror direct helpers on width-edge masks" {
    const byte_cases = [_]u32{
        0x00,
        0x01,
        0x80,
        0x81,
        0x55,
        0xaa,
        0xff,
    };
    for (byte_cases) |value| {
        try std.testing.expectEqual(hweight.swHweight8(value), hweight.__sw_hweight8(value));
        try std.testing.expectEqual(@as(u32, @popCount(@as(u8, @intCast(value)))), hweight.swHweight8(value));
    }

    const halfword_cases = [_]u32{
        0x0000,
        0x0001,
        0x8000,
        0x8001,
        0x5555,
        0xaaaa,
        0xffff,
    };
    for (halfword_cases) |value| {
        try std.testing.expectEqual(hweight.swHweight16(value), hweight.__sw_hweight16(value));
        try std.testing.expectEqual(@as(u32, @popCount(@as(u16, @intCast(value)))), hweight.swHweight16(value));
    }

    const word_cases = [_]u32{
        0x0000_0000,
        0x0000_0001,
        0x8000_0000,
        0x8000_0001,
        0x5555_5555,
        0xaaaa_aaaa,
        0xffff_ffff,
    };
    for (word_cases) |value| {
        try std.testing.expectEqual(hweight.swHweight32(value), hweight.__sw_hweight32(value));
        try std.testing.expectEqual(@as(u32, @popCount(value)), hweight.swHweight32(value));
    }

    const doubleword_cases = [_]u64{
        0x0000_0000_0000_0000,
        0x0000_0000_0000_0001,
        0x8000_0000_0000_0000,
        0x8000_0000_0000_0001,
        0x5555_5555_5555_5555,
        0xaaaa_aaaa_aaaa_aaaa,
        0xffff_ffff_ffff_ffff,
    };
    for (doubleword_cases) |value| {
        try std.testing.expectEqual(hweight.swHweight64(value), hweight.__sw_hweight64(value));
        try std.testing.expectEqual(@as(u64, @popCount(value)), hweight.swHweight64(value));
    }
}

test "phase1 hweight long aliases stay aligned on boundary-spanning masks" {
    const top_bit: usize = @as(usize, 1) << (@bitSizeOf(usize) - 1);
    const cases = [_]usize{
        0,
        1,
        top_bit,
        top_bit | 1,
        0x55,
        0xaa,
        if (@sizeOf(usize) == 4) 0x5555_5555 else 0x5555_5555_5555_5555,
        if (@sizeOf(usize) == 4) 0xaaaa_aaaa else 0xaaaa_aaaa_aaaa_aaaa,
        std.math.maxInt(usize),
    };

    for (cases) |value| {
        try std.testing.expectEqual(hweight.hweightLong(value), hweight.hweight_long(value));
        try std.testing.expectEqual(@popCount(value), hweight.hweightLong(value));
    }
}
