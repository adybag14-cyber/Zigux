const std = @import("std");
const hweight = @import("hweight");

fn expectHweight8(value: u32) !void {
    const expected: u32 = @popCount(@as(u8, @truncate(value)));
    try std.testing.expectEqual(expected, hweight.swHweight8(value));
    try std.testing.expectEqual(expected, hweight.__sw_hweight8(value));
}

fn expectHweight16(value: u32) !void {
    const expected: u32 = @popCount(@as(u16, @truncate(value)));
    try std.testing.expectEqual(expected, hweight.swHweight16(value));
    try std.testing.expectEqual(expected, hweight.__sw_hweight16(value));
}

fn expectHweight32(value: u32) !void {
    const expected: u32 = @popCount(value);
    try std.testing.expectEqual(expected, hweight.swHweight32(value));
    try std.testing.expectEqual(expected, hweight.__sw_hweight32(value));
}

fn expectHweight64(value: u64) !void {
    const expected: u64 = @popCount(value);
    try std.testing.expectEqual(expected, hweight.swHweight64(value));
    try std.testing.expectEqual(expected, hweight.__sw_hweight64(value));
}

test "narrow hweight helpers ignore bits outside their lane" {
    const high_noise: u32 = 0xffff_ff00;
    try expectHweight8(high_noise);
    try expectHweight8(high_noise | 0x5a);
    try expectHweight8(0x0100_00ff);

    try expectHweight16(0xffff_0000);
    try expectHweight16(0xffff_0000 | 0xa55a);
    try expectHweight16(0x8000_ffff);
}

test "wide hweight helpers count all bits at dense boundaries" {
    try expectHweight32(0xffff_ffff);
    try expectHweight32(0x8000_0001);
    try expectHweight32(0xaaaa_5555);

    try expectHweight64(0xffff_ffff_ffff_ffff);
    try expectHweight64(0x8000_0000_0000_0001);
    try expectHweight64(0xaaaa_5555_ffff_0000);
}

test "hweight long aliases mirror native-width popcount" {
    const all_bits: usize = ~@as(usize, 0);
    const edge_bits: usize = (@as(usize, 1) << (@bitSizeOf(usize) - 1)) | 1;
    const alternating: usize = if (@sizeOf(usize) == 4)
        0xaaaa_5555
    else
        0xaaaa_5555_ffff_0000;

    try std.testing.expectEqual(@as(usize, @popCount(all_bits)), hweight.hweightLong(all_bits));
    try std.testing.expectEqual(hweight.hweightLong(all_bits), hweight.hweight_long(all_bits));

    try std.testing.expectEqual(@as(usize, @popCount(edge_bits)), hweight.hweightLong(edge_bits));
    try std.testing.expectEqual(hweight.hweightLong(edge_bits), hweight.hweight_long(edge_bits));

    try std.testing.expectEqual(@as(usize, @popCount(alternating)), hweight.hweightLong(alternating));
    try std.testing.expectEqual(hweight.hweightLong(alternating), hweight.hweight_long(alternating));
}
