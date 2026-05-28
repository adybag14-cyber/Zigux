const std = @import("std");
const hweight = @import("hweight");

test "phase1 hweight sparse byte lanes stay additive when folded upward" {
    const low8: u32 = 0b1000_0001;
    const high8: u32 = 0b0100_1000;
    const merged8 = low8 | high8;
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(merged8));
    try std.testing.expectEqual(hweight.swHweight8(low8) + hweight.swHweight8(high8), hweight.swHweight8(merged8));
    try std.testing.expectEqual(hweight.__sw_hweight8(merged8), hweight.swHweight8(merged8));

    const folded16: u32 = merged8 | (merged8 << 8);
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight16(folded16));
    try std.testing.expectEqual(hweight.swHweight8(merged8) * 2, hweight.swHweight16(folded16));

    const folded32: u32 = folded16 | (folded16 << 16);
    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight32(folded32));
    try std.testing.expectEqual(hweight.swHweight16(folded16) * 2, hweight.swHweight32(folded32));

    const folded64: u64 = @as(u64, folded32) | (@as(u64, folded32) << 32);
    try std.testing.expectEqual(@as(u64, 32), hweight.swHweight64(folded64));
    try std.testing.expectEqual(hweight.swHweight32(folded32) * 2, hweight.swHweight64(folded64));
}

test "phase1 hweight toggle deltas track added and removed sparse bits" {
    const base16: u32 = 0b1001_0000_0000_0111;
    const toggled16: u32 = 0b1011_0000_0010_0011;
    const added16 = toggled16 & ~base16;
    const removed16 = base16 & ~toggled16;
    try std.testing.expectEqual(
        hweight.swHweight16(base16) + hweight.swHweight16(added16) - hweight.swHweight16(removed16),
        hweight.swHweight16(toggled16),
    );

    const base32: u32 = 0x9000_0701;
    const toggled32: u32 = 0xb002_0301;
    const added32 = toggled32 & ~base32;
    const removed32 = base32 & ~toggled32;
    try std.testing.expectEqual(
        hweight.__sw_hweight32(base32) + hweight.__sw_hweight32(added32) - hweight.__sw_hweight32(removed32),
        hweight.__sw_hweight32(toggled32),
    );

    const base64: u64 = 0x9000_0007_0000_0101;
    const toggled64: u64 = 0xb002_0003_0000_0301;
    const added64 = toggled64 & ~base64;
    const removed64 = base64 & ~toggled64;
    try std.testing.expectEqual(
        hweight.swHweight64(base64) + hweight.swHweight64(added64) - hweight.swHweight64(removed64),
        hweight.swHweight64(toggled64),
    );
}

test "phase1 hweight long aliases match the native sparse fold surface" {
    const sparse_long: usize = if (@sizeOf(usize) == 4)
        0x8102_4018
    else
        0x8102_4018_1804_2081;
    const expanded_long: usize = sparse_long | (sparse_long >> 1);

    const expected_native: usize = if (@sizeOf(usize) == 4)
        @as(usize, @intCast(hweight.swHweight32(@intCast(expanded_long))))
    else
        @as(usize, @intCast(hweight.swHweight64(@intCast(expanded_long))));

    try std.testing.expectEqual(expected_native, hweight.hweightLong(expanded_long));
    try std.testing.expectEqual(hweight.hweightLong(expanded_long), hweight.hweight_long(expanded_long));
    try std.testing.expect(hweight.hweightLong(expanded_long) >= hweight.hweightLong(sparse_long));
}
