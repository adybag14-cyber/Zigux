const std = @import("std");
const hweight = @import("hweight.zig");

test "phase1 hweight fixture shard replays committed width expectations" {
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(0xf0));
    try std.testing.expectEqual(@as(u32, 4), hweight.__sw_hweight8(0xf0));

    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight16(0xf0f0));
    try std.testing.expectEqual(@as(u32, 8), hweight.__sw_hweight16(0xf0f0));

    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight32(0xf0f0_f0f0));
    try std.testing.expectEqual(@as(u32, 16), hweight.__sw_hweight32(0xf0f0_f0f0));

    try std.testing.expectEqual(@as(u64, 32), hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0));
    try std.testing.expectEqual(@as(u64, 32), hweight.__sw_hweight64(0xf0f0_f0f0_f0f0_f0f0));

    try std.testing.expectEqual(@as(usize, 8), hweight.hweightLong(0xff));
    try std.testing.expectEqual(@as(usize, 8), hweight.hweight_long(0xff));
}
