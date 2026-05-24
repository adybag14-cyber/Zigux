const std = @import("std");
const hweight = @import("hweight");

test "hweight segment folds stay consistent across byte, halfword, and word groupings" {
    const b0: u32 = 0b1011_0001;
    const b1: u32 = 0b0101_0101;
    const b2: u32 = 0b1111_0000;
    const b3: u32 = 0b0000_1111;

    const low16: u32 = b0 | (b1 << 8);
    const high16: u32 = b2 | (b3 << 8);
    const full32: u32 = low16 | (high16 << 16);

    try std.testing.expectEqual(
        hweight.swHweight8(b0) + hweight.swHweight8(b1),
        hweight.swHweight16(low16),
    );
    try std.testing.expectEqual(
        hweight.swHweight8(b2) + hweight.swHweight8(b3),
        hweight.swHweight16(high16),
    );
    try std.testing.expectEqual(
        hweight.swHweight16(low16) + hweight.swHweight16(high16),
        hweight.swHweight32(full32),
    );
    try std.testing.expectEqual(
        hweight.swHweight8(b0) +
            hweight.swHweight8(b1) +
            hweight.swHweight8(b2) +
            hweight.swHweight8(b3),
        hweight.swHweight32(full32),
    );
}

test "swHweight64 matches the sum of its two 32-bit halves" {
    const low32: u32 = 0xf000_00f1;
    const high32: u32 = 0x0f0f_5500;
    const full64: u64 = @as(u64, low32) | (@as(u64, high32) << 32);

    try std.testing.expectEqual(
        @as(u64, hweight.swHweight32(low32)) + @as(u64, hweight.swHweight32(high32)),
        hweight.swHweight64(full64),
    );
}

test "hweightLong agrees with the native-width folded helper" {
    const value: usize = if (@sizeOf(usize) == 4)
        0xa10f_00f3
    else
        0xa10f_00f3_55aa_0f0f;

    const expected: usize = if (@sizeOf(usize) == 4)
        @intCast(hweight.swHweight32(@intCast(value)))
    else
        @intCast(hweight.swHweight64(@intCast(value)));

    try std.testing.expectEqual(expected, hweight.hweightLong(value));
}
