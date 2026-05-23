const std = @import("std");
const hweight = @import("hweight");

test "hweight helper smoke follows popcount across representative masks" {
    const cases8 = [_]u32{ 0x00, 0x81, 0x5a, 0xff };
    for (cases8) |value| {
        try std.testing.expectEqual(@popCount(value & 0xff), hweight.swHweight8(value));
    }

    const cases16 = [_]u32{ 0x0000, 0x8001, 0x5aa5, 0xffff };
    for (cases16) |value| {
        try std.testing.expectEqual(@popCount(value & 0xffff), hweight.swHweight16(value));
    }

    const cases32 = [_]u32{ 0x0000_0000, 0x8000_0001, 0x55aa_33cc, 0xffff_ffff };
    for (cases32) |value| {
        try std.testing.expectEqual(@popCount(value), hweight.swHweight32(value));
    }

    const cases64 = [_]u64{
        0x0000_0000_0000_0000,
        0x8000_0000_0000_0001,
        0x55aa_33cc_0f0f_f0f0,
        0xffff_ffff_ffff_ffff,
    };
    for (cases64) |value| {
        try std.testing.expectEqual(@popCount(value), hweight.swHweight64(value));
    }
}

test "hweight helper smoke keeps Linux-style aliases aligned" {
    const value8: u32 = 0xa5;
    const value16: u32 = 0xa55a;
    const value32: u32 = 0xdead_beef;
    const value64: u64 = 0xfedc_ba98_7654_3210;
    const value_long: usize = if (@sizeOf(usize) == 4) 0xc3c3_0f0f else 0xc3c3_0f0f_5a5a_a5a5;

    try std.testing.expectEqual(hweight.swHweight8(value8), hweight.__sw_hweight8(value8));
    try std.testing.expectEqual(hweight.swHweight16(value16), hweight.__sw_hweight16(value16));
    try std.testing.expectEqual(hweight.swHweight32(value32), hweight.__sw_hweight32(value32));
    try std.testing.expectEqual(hweight.swHweight64(value64), hweight.__sw_hweight64(value64));
    try std.testing.expectEqual(hweight.hweightLong(value_long), hweight.hweight_long(value_long));
}

test "hweight helper smoke stays additive for disjoint bands" {
    const low32: u32 = 0x0000_00f3;
    const high32: u32 = 0xf300_0000;
    try std.testing.expectEqual(
        hweight.swHweight32(low32) + hweight.swHweight32(high32),
        hweight.swHweight32(low32 | high32),
    );

    const low64: u64 = 0x0000_0000_00f3_0000;
    const high64: u64 = 0xf300_0000_0000_0000;
    try std.testing.expectEqual(
        hweight.swHweight64(low64) + hweight.swHweight64(high64),
        hweight.swHweight64(low64 | high64),
    );

    const low_long: usize = if (@sizeOf(usize) == 4) 0x0000_00f3 else 0x0000_0000_00f3_0000;
    const high_long: usize = if (@sizeOf(usize) == 4) 0xf300_0000 else 0xf300_0000_0000_0000;
    try std.testing.expectEqual(
        hweight.hweightLong(low_long) + hweight.hweightLong(high_long),
        hweight.hweightLong(low_long | high_long),
    );
}
