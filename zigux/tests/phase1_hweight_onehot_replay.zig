const std = @import("std");
const hweight = @import("hweight");

test "width-specific hweight helpers report one for every in-range one-hot bit" {
    for (0..8) |bit| {
        const shift: u5 = @intCast(bit);
        const value: u32 = @as(u32, 1) << shift;
        try std.testing.expectEqual(@as(u32, 1), hweight.swHweight8(value));
        try std.testing.expectEqual(@as(u32, 1), hweight.__sw_hweight8(value));
    }

    for (0..16) |bit| {
        const shift: u5 = @intCast(bit);
        const value: u32 = @as(u32, 1) << shift;
        try std.testing.expectEqual(@as(u32, 1), hweight.swHweight16(value));
        try std.testing.expectEqual(@as(u32, 1), hweight.__sw_hweight16(value));
    }

    for (0..32) |bit| {
        const shift: u5 = @intCast(bit);
        const value: u32 = @as(u32, 1) << shift;
        try std.testing.expectEqual(@as(u32, 1), hweight.swHweight32(value));
        try std.testing.expectEqual(@as(u32, 1), hweight.__sw_hweight32(value));
    }

    for (0..64) |bit| {
        const shift: u6 = @intCast(bit);
        const value: u64 = @as(u64, 1) << shift;
        try std.testing.expectEqual(@as(u64, 1), hweight.swHweight64(value));
        try std.testing.expectEqual(@as(u64, 1), hweight.__sw_hweight64(value));
    }
}

test "native-word hweight routing reports one for every in-range one-hot bit" {
    for (0..@bitSizeOf(usize)) |bit| {
        const shift: std.math.Log2Int(usize) = @intCast(bit);
        const value: usize = @as(usize, 1) << shift;
        try std.testing.expectEqual(@as(usize, 1), hweight.hweightLong(value));
        try std.testing.expectEqual(@as(usize, 1), hweight.hweight_long(value));
    }
}
