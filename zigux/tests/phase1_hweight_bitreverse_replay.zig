const std = @import("std");
const hweight = @import("hweight");

fn expectBitreverseInvariant(comptime T: type, value: T, counter: fn (T) u64) !void {
    const reversed = @bitReverse(value);
    try std.testing.expectEqual(counter(value), counter(reversed));
    try std.testing.expectEqual(@as(u64, @popCount(value)), counter(value));
    try std.testing.expectEqual(@as(u64, @popCount(reversed)), counter(reversed));
}

test "hweight entrypoints keep bit counts after width-preserving bit reversal" {
    try expectBitreverseInvariant(u8, 0x96, struct {
        fn run(value: u8) u64 {
            return hweight.swHweight8(value);
        }
    }.run);
    try expectBitreverseInvariant(u16, 0x12a5, struct {
        fn run(value: u16) u64 {
            return hweight.swHweight16(value);
        }
    }.run);
    try expectBitreverseInvariant(u32, 0x12a5_00f0, struct {
        fn run(value: u32) u64 {
            return hweight.swHweight32(value);
        }
    }.run);
    try expectBitreverseInvariant(u64, 0x0123_4567_89ab_cdef, struct {
        fn run(value: u64) u64 {
            return hweight.swHweight64(value);
        }
    }.run);
}

test "hweight aliases and hweightLong stay aligned on bit-reversed inputs" {
    const eight: u8 = 0xa6;
    try std.testing.expectEqual(hweight.swHweight8(eight), hweight.__sw_hweight8(@bitReverse(eight)));

    const sixteen: u16 = 0x3ca5;
    try std.testing.expectEqual(hweight.swHweight16(sixteen), hweight.__sw_hweight16(@bitReverse(sixteen)));

    const thirty_two: u32 = 0x80f0_12a5;
    try std.testing.expectEqual(hweight.swHweight32(thirty_two), hweight.__sw_hweight32(@bitReverse(thirty_two)));

    const sixty_four: u64 = 0xfedc_ba98_7654_3210;
    try std.testing.expectEqual(hweight.swHweight64(sixty_four), hweight.__sw_hweight64(@bitReverse(sixty_four)));

    const long_value: usize = if (@sizeOf(usize) == 4) 0x80f0_12a5 else 0xfedc_ba98_7654_3210;
    try std.testing.expectEqual(hweight.hweightLong(long_value), hweight.hweight_long(@bitReverse(long_value)));
}
