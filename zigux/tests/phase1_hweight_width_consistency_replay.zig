const std = @import("std");
const hweight = @import("hweight");

fn expectEmbeddedWidthConsistency(byte: u8) !void {
    const expected32: u32 = @popCount(byte);
    const expected64: u64 = expected32;
    const expected_usize: usize = expected32;

    const widened16: u32 = byte;
    const widened32: u32 = byte;
    const widened64: u64 = byte;
    const widened_long: usize = byte;

    try std.testing.expectEqual(expected32, hweight.swHweight8(widened16));
    try std.testing.expectEqual(expected32, hweight.__sw_hweight8(widened16));
    try std.testing.expectEqual(expected32, hweight.swHweight16(widened16));
    try std.testing.expectEqual(expected32, hweight.__sw_hweight16(widened16));
    try std.testing.expectEqual(expected32, hweight.swHweight32(widened32));
    try std.testing.expectEqual(expected32, hweight.__sw_hweight32(widened32));
    try std.testing.expectEqual(expected64, hweight.swHweight64(widened64));
    try std.testing.expectEqual(expected64, hweight.__sw_hweight64(widened64));
    try std.testing.expectEqual(expected_usize, hweight.hweightLong(widened_long));
    try std.testing.expectEqual(expected_usize, hweight.hweight_long(widened_long));
}

test "zero-extended bytes keep the same population count across widths" {
    const bytes = [_]u8{ 0x00, 0x01, 0x03, 0x55, 0x80, 0xA5, 0xF0, 0xFF };
    for (bytes) |byte| {
        try expectEmbeddedWidthConsistency(byte);
    }
}

test "packed subwords add back to the wider count" {
    const lower16: u32 = 0xA53C;
    const upper16: u32 = 0x0F80;
    const packed32: u32 = lower16 | (upper16 << 16);

    try std.testing.expectEqual(
        hweight.swHweight16(lower16) + hweight.swHweight16(upper16),
        hweight.swHweight32(packed32),
    );
    try std.testing.expectEqual(
        hweight.__sw_hweight16(lower16) + hweight.__sw_hweight16(upper16),
        hweight.__sw_hweight32(packed32),
    );

    const lower32: u64 = 0xA53C_0F80;
    const upper32: u64 = 0x1001_FF00;
    const packed64: u64 = lower32 | (upper32 << 32);

    try std.testing.expectEqual(
        @as(u64, hweight.swHweight32(@intCast(lower32))) + hweight.swHweight32(@intCast(upper32)),
        hweight.swHweight64(packed64),
    );
    try std.testing.expectEqual(
        @as(u64, hweight.__sw_hweight32(@intCast(lower32))) + hweight.__sw_hweight32(@intCast(upper32)),
        hweight.__sw_hweight64(packed64),
    );

    const packed_long: usize = if (@sizeOf(usize) == 4)
        @intCast(packed32)
    else
        @intCast(packed64);
    const expected_long: usize = if (@sizeOf(usize) == 4)
        @intCast(hweight.swHweight32(packed32))
    else
        @intCast(hweight.swHweight64(packed64));

    try std.testing.expectEqual(expected_long, hweight.hweightLong(packed_long));
    try std.testing.expectEqual(expected_long, hweight.hweight_long(packed_long));
}
