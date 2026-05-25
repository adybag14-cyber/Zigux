const std = @import("std");
const hweight = @import("hweight");

fn expectMaskMonotonic(comptime T: type, value: T, mask: T, counter: fn (T) u64) !void {
    const masked = value & mask;
    try std.testing.expect(counter(masked) <= counter(value));
    try std.testing.expectEqual(@as(u64, @popCount(value)), counter(value));
    try std.testing.expectEqual(@as(u64, @popCount(masked)), counter(masked));
}

test "hweight entrypoints never gain set bits after masking" {
    try expectMaskMonotonic(u8, 0b1110_1101, 0b1011_0100, struct {
        fn run(value: u8) u64 {
            return hweight.swHweight8(value);
        }
    }.run);
    try expectMaskMonotonic(u16, 0xecad, 0x94b4, struct {
        fn run(value: u16) u64 {
            return hweight.swHweight16(value);
        }
    }.run);
    try expectMaskMonotonic(u32, 0xecad_1357, 0x94b4_1206, struct {
        fn run(value: u32) u64 {
            return hweight.swHweight32(value);
        }
    }.run);
    try expectMaskMonotonic(u64, 0xf0ed_cba9_8765_4321, 0x90a4_8a20_0644_0220, struct {
        fn run(value: u64) u64 {
            return hweight.swHweight64(value);
        }
    }.run);
}

test "hweight aliases and hweightLong stay monotonic on masked inputs" {
    const eight_value: u8 = 0xd7;
    const eight_mask: u8 = 0x54;
    try std.testing.expect(hweight.__sw_hweight8(eight_value & eight_mask) <= hweight.__sw_hweight8(eight_value));

    const sixteen_value: u16 = 0xd7c3;
    const sixteen_mask: u16 = 0x5482;
    try std.testing.expect(hweight.__sw_hweight16(sixteen_value & sixteen_mask) <= hweight.__sw_hweight16(sixteen_value));

    const thirty_two_value: u32 = 0xd7c3_b591;
    const thirty_two_mask: u32 = 0x5482_1410;
    try std.testing.expect(hweight.__sw_hweight32(thirty_two_value & thirty_two_mask) <= hweight.__sw_hweight32(thirty_two_value));

    const sixty_four_value: u64 = 0xd7c3_b591_ef6d_2a18;
    const sixty_four_mask: u64 = 0x5482_1410_a448_2208;
    try std.testing.expect(hweight.__sw_hweight64(sixty_four_value & sixty_four_mask) <= hweight.__sw_hweight64(sixty_four_value));

    const long_value: usize = if (@sizeOf(usize) == 4) 0xd7c3_b591 else 0xd7c3_b591_ef6d_2a18;
    const long_mask: usize = if (@sizeOf(usize) == 4) 0x5482_1410 else 0x5482_1410_a448_2208;
    const masked_long = long_value & long_mask;
    try std.testing.expect(hweight.hweightLong(masked_long) <= hweight.hweightLong(long_value));
    try std.testing.expectEqual(hweight.hweightLong(masked_long), hweight.hweight_long(masked_long));
    try std.testing.expectEqual(hweight.hweightLong(long_value), hweight.hweight_long(long_value));
}
