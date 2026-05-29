const std = @import("std");
const hweight = @import("hweight");

fn expectAllWidths(value: u64) !void {
    const value32: u32 = @truncate(value);
    try std.testing.expectEqual(
        @as(u32, @intCast(@popCount(@as(u8, @truncate(value32))))),
        hweight.swHweight8(value32),
    );
    try std.testing.expectEqual(
        @as(u32, @intCast(@popCount(@as(u16, @truncate(value32))))),
        hweight.swHweight16(value32),
    );
    try std.testing.expectEqual(
        @as(u32, @intCast(@popCount(value32))),
        hweight.swHweight32(value32),
    );
    try std.testing.expectEqual(@as(u64, @intCast(@popCount(value))), hweight.swHweight64(value));
}

test "Linux hweight aliases match canonical helper names" {
    const values = [_]u64{
        0,
        1,
        0xff,
        0x0101,
        0x8000_0000,
        0xf0f0_f0f0_f0f0_f0f0,
        0xffff_ffff_ffff_ffff,
    };

    for (values) |value| {
        const value32: u32 = @truncate(value);
        try std.testing.expectEqual(hweight.swHweight8(value32), hweight.__sw_hweight8(value32));
        try std.testing.expectEqual(hweight.swHweight16(value32), hweight.__sw_hweight16(value32));
        try std.testing.expectEqual(hweight.swHweight32(value32), hweight.__sw_hweight32(value32));
        try std.testing.expectEqual(hweight.swHweight64(value), hweight.__sw_hweight64(value));
    }

    const long_value: usize = if (@sizeOf(usize) == 4) 0xa5a5_0101 else 0xa5a5_0101_8000_ffff;
    try std.testing.expectEqual(hweight.hweightLong(long_value), hweight.hweight_long(long_value));
}

test "narrow hweight helpers ignore bits outside their advertised width" {
    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight8(0xffff_ff00));
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight8(0xffff_ffff));
    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight16(0xffff_0000));
    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight16(0xffff_ffff));
    try std.testing.expectEqual(@as(u32, 32), hweight.swHweight32(0xffff_ffff));

    try expectAllWidths(0xffff_0000_0000_00ff);
    try expectAllWidths(0x8000_0001_ffff_0000);
}

test "hweight_long follows native usize width" {
    const all_ones = ~@as(usize, 0);
    try std.testing.expectEqual(@as(usize, @bitSizeOf(usize)), hweight.hweightLong(all_ones));
    try std.testing.expectEqual(@as(usize, @bitSizeOf(usize)), hweight.hweight_long(all_ones));

    const high_native_bit = @as(usize, 1) << (@bitSizeOf(usize) - 1);
    try std.testing.expectEqual(@as(usize, 1), hweight.hweightLong(high_native_bit));
    try std.testing.expectEqual(@as(usize, 1), hweight.hweight_long(high_native_bit));
}
