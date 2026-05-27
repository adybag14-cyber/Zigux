const std = @import("std");
const hweight = @import("hweight");

fn expectByteSwapInvariantU16(value: u16) !void {
    try std.testing.expectEqual(hweight.swHweight16(value), hweight.swHweight16(@byteSwap(value)));
    try std.testing.expectEqual(hweight.__sw_hweight16(value), hweight.__sw_hweight16(@byteSwap(value)));
}

fn expectByteSwapInvariantU32(value: u32) !void {
    try std.testing.expectEqual(hweight.swHweight32(value), hweight.swHweight32(@byteSwap(value)));
    try std.testing.expectEqual(hweight.__sw_hweight32(value), hweight.__sw_hweight32(@byteSwap(value)));
}

fn expectByteSwapInvariantU64(value: u64) !void {
    try std.testing.expectEqual(hweight.swHweight64(value), hweight.swHweight64(@byteSwap(value)));
    try std.testing.expectEqual(hweight.__sw_hweight64(value), hweight.__sw_hweight64(@byteSwap(value)));
}

fn expectByteSwapInvariantLong(value: usize) !void {
    try std.testing.expectEqual(hweight.hweightLong(value), hweight.hweightLong(@byteSwap(value)));
    try std.testing.expectEqual(hweight.hweight_long(value), hweight.hweight_long(@byteSwap(value)));
}

test "phase 1 hweight byteswap replay keeps width-local helpers invariant under byte order reversal" {
    const u16_cases = [_]u16{
        0x0001,
        0x00f0,
        0xa5f0,
        0x8001,
        0x7fff,
    };
    for (u16_cases) |value| {
        try expectByteSwapInvariantU16(value);
    }

    const u32_cases = [_]u32{
        0x0000_0001,
        0x00f0_0f00,
        0xa5f0_c33c,
        0x8000_0001,
        0x7fff_ffff,
    };
    for (u32_cases) |value| {
        try expectByteSwapInvariantU32(value);
    }

    const u64_cases = [_]u64{
        0x0000_0000_0000_0001,
        0x00f0_0f00_f000_0ff0,
        0xa5f0_c33c_8001_00ff,
        0x8000_0000_0000_0001,
        0x7fff_ffff_ffff_ffff,
    };
    for (u64_cases) |value| {
        try expectByteSwapInvariantU64(value);
    }
}

test "phase 1 hweight byteswap replay keeps native routing aligned with the swapped word image" {
    const cases = if (@sizeOf(usize) == 4)
        [_]usize{
            0x0000_0001,
            0x00f0_0f00,
            0xa5f0_c33c,
            0x8000_0001,
            0x7fff_ffff,
        }
    else
        [_]usize{
            0x0000_0000_0000_0001,
            0x00f0_0f00_f000_0ff0,
            0xa5f0_c33c_8001_00ff,
            0x8000_0000_0000_0001,
            0x7fff_ffff_ffff_ffff,
        };

    for (cases) |value| {
        try expectByteSwapInvariantLong(value);
    }
}
