const std = @import("std");
const hweight = @import("hweight");

fn toggledCount32(value: u32, mask: u32) u32 {
    return @popCount(value) + @popCount(mask & ~value) - @popCount(mask & value);
}

fn toggledCount64(value: u64, mask: u64) u64 {
    return @popCount(value) + @popCount(mask & ~value) - @popCount(mask & value);
}

fn toggledCountLong(value: usize, mask: usize) usize {
    return @popCount(value) + @popCount(mask & ~value) - @popCount(mask & value);
}

test "phase1 hweight replay keeps toggle deltas exact for narrow helpers" {
    const value8: u32 = 0b1011_0100;
    const mask8: u32 = 0b0101_1010;
    const toggled8 = value8 ^ mask8;
    try std.testing.expectEqual(toggledCount32(value8, mask8), hweight.swHweight8(toggled8));
    try std.testing.expectEqual(hweight.swHweight8(toggled8), hweight.__sw_hweight8(toggled8));

    const value16: u32 = 0xa53c;
    const mask16: u32 = 0x5a96;
    const toggled16 = value16 ^ mask16;
    try std.testing.expectEqual(toggledCount32(value16, mask16), hweight.swHweight16(toggled16));
    try std.testing.expectEqual(hweight.swHweight16(toggled16), hweight.__sw_hweight16(toggled16));

    const value32: u32 = 0xa53c_f00f;
    const mask32: u32 = 0x5ac3_0ff0;
    const toggled32 = value32 ^ mask32;
    try std.testing.expectEqual(toggledCount32(value32, mask32), hweight.swHweight32(toggled32));
    try std.testing.expectEqual(hweight.swHweight32(toggled32), hweight.__sw_hweight32(toggled32));
}

test "phase1 hweight replay keeps toggle deltas exact for 64-bit helpers" {
    const value64: u64 = 0xa53c_f00f_1357_2468;
    const mask64: u64 = 0x5ac3_0ff0_eca8_db97;
    const toggled64 = value64 ^ mask64;

    try std.testing.expectEqual(toggledCount64(value64, mask64), hweight.swHweight64(toggled64));
    try std.testing.expectEqual(hweight.swHweight64(toggled64), hweight.__sw_hweight64(toggled64));

    const lower_masked: u64 = toggled64 & 0xffff_ffff;
    const upper_masked: u64 = toggled64 >> 32;
    try std.testing.expectEqual(
        hweight.swHweight32(@intCast(lower_masked)) + hweight.swHweight32(@intCast(upper_masked)),
        hweight.swHweight64(toggled64),
    );
}

test "phase1 hweight replay keeps native-long toggle deltas aligned with aliases" {
    const value: usize = if (@sizeOf(usize) == 4)
        0x9249_00f1
    else
        0x9249_00f1_1357_2468;
    const mask: usize = if (@sizeOf(usize) == 4)
        0x6db6_ff0e
    else
        0x6db6_ff0e_eca8_db97;
    const toggled = value ^ mask;

    try std.testing.expectEqual(toggledCountLong(value, mask), hweight.hweightLong(toggled));
    try std.testing.expectEqual(hweight.hweightLong(toggled), hweight.hweight_long(toggled));
}
