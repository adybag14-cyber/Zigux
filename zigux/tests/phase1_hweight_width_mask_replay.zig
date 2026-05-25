const std = @import("std");
const hweight = @import("hweight");

test "phase1 hweight width-specific helpers ignore bits outside their native window" {
    const source: u64 = 0xff00_aa55_f0f0_00f3;

    try std.testing.expectEqual(@as(u32, @popCount(@as(u8, @truncate(source)))), hweight.swHweight8(@intCast(@as(u32, @truncate(source)))));
    try std.testing.expectEqual(@as(u32, @popCount(@as(u16, @truncate(source)))), hweight.swHweight16(@intCast(@as(u32, @truncate(source)))));
    try std.testing.expectEqual(@as(u32, @popCount(@as(u32, @truncate(source)))), hweight.swHweight32(@intCast(@as(u32, @truncate(source)))));
}

test "phase1 hweight64 agrees with split 32-bit halves on mixed high and low masks" {
    const source: u64 = 0xf000_0001_00ff_8003;
    const upper: u32 = @truncate(source >> 32);
    const lower: u32 = @truncate(source);

    try std.testing.expectEqual(hweight.swHweight32(upper) + hweight.swHweight32(lower), hweight.swHweight64(source));
}

test "phase1 hweightLong tracks the current native-width view of a wider source pattern" {
    const source: u64 = 0x8001_f0f0_0000_00ff;
    const native: usize = @truncate(source);

    const expected: usize = if (@sizeOf(usize) == 4)
        @intCast(hweight.swHweight32(@intCast(native)))
    else
        @intCast(hweight.swHweight64(@intCast(native)));

    try std.testing.expectEqual(@as(usize, @popCount(native)), hweight.hweightLong(native));
    try std.testing.expectEqual(expected, hweight.hweightLong(native));
}
