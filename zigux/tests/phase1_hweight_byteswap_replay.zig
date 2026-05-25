const std = @import("std");
const hweight = @import("hweight");

fn expectByteswapInvariant(comptime T: type, value: T, counter: fn (T) u64) !void {
    try std.testing.expectEqual(counter(value), counter(@byteSwap(value)));
    try std.testing.expectEqual(@as(u64, @popCount(value)), counter(value));
    try std.testing.expectEqual(@as(u64, @popCount(value)), counter(@byteSwap(value)));
}

test "hweight entrypoints keep bit counts after width-preserving byte swaps" {
    try expectByteswapInvariant(u8, 0x96, struct {
        fn run(value: u8) u64 {
            return hweight.swHweight8(value);
        }
    }.run);
    try expectByteswapInvariant(u16, 0x12a5, struct {
        fn run(value: u16) u64 {
            return hweight.swHweight16(value);
        }
    }.run);
    try expectByteswapInvariant(u32, 0x12a5_00f0, struct {
        fn run(value: u32) u64 {
            return hweight.swHweight32(value);
        }
    }.run);
    try expectByteswapInvariant(u64, 0x0123_4567_89ab_cdef, struct {
        fn run(value: u64) u64 {
            return hweight.swHweight64(value);
        }
    }.run);
}

test "hweight aliases and hweightLong stay aligned on byte-swapped inputs" {
    const eight: u8 = 0xa6;
    try std.testing.expectEqual(hweight.swHweight8(eight), hweight.__sw_hweight8(@byteSwap(eight)));

    const sixteen: u16 = 0x3ca5;
    try std.testing.expectEqual(hweight.swHweight16(sixteen), hweight.__sw_hweight16(@byteSwap(sixteen)));

    const thirty_two: u32 = 0x80f0_12a5;
    try std.testing.expectEqual(hweight.swHweight32(thirty_two), hweight.__sw_hweight32(@byteSwap(thirty_two)));

    const sixty_four: u64 = 0xfedc_ba98_7654_3210;
    try std.testing.expectEqual(hweight.swHweight64(sixty_four), hweight.__sw_hweight64(@byteSwap(sixty_four)));

    const long_value: usize = if (@sizeOf(usize) == 4) 0x80f0_12a5 else 0xfedc_ba98_7654_3210;
    try std.testing.expectEqual(hweight.hweightLong(long_value), hweight.hweight_long(@byteSwap(long_value)));
}
