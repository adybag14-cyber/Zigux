const std = @import("std");
const hweight = @import("hweight");

fn expect8(value: u32, expected: u32) !void {
    try std.testing.expectEqual(expected, hweight.swHweight8(value));
    try std.testing.expectEqual(expected, hweight.__sw_hweight8(value));
}

fn expect16(value: u32, expected: u32) !void {
    try std.testing.expectEqual(expected, hweight.swHweight16(value));
    try std.testing.expectEqual(expected, hweight.__sw_hweight16(value));
}

fn expect32(value: u32, expected: u32) !void {
    try std.testing.expectEqual(expected, hweight.swHweight32(value));
    try std.testing.expectEqual(expected, hweight.__sw_hweight32(value));
}

fn expect64(value: u64, expected: u64) !void {
    try std.testing.expectEqual(expected, hweight.swHweight64(value));
    try std.testing.expectEqual(expected, hweight.__sw_hweight64(value));
}

test "phase1 hweight extreme masks keep narrow helpers lane bounded" {
    try expect8(0x0000_0000, 0);
    try expect8(0x0000_00ff, 8);
    try expect8(0xffff_ff00, 0);
    try expect8(0xffff_ffff, 8);

    try expect16(0x0000_0000, 0);
    try expect16(0x0000_ffff, 16);
    try expect16(0xffff_0000, 0);
    try expect16(0xffff_ffff, 16);
}

test "phase1 hweight extreme masks cover full 32 and 64 bit surfaces" {
    try expect32(0x0000_0000, 0);
    try expect32(0xffff_ffff, 32);
    try expect32(0x8000_0001, 2);
    try expect32(0x7fff_fffe, 30);

    try expect64(0x0000_0000_0000_0000, 0);
    try expect64(0xffff_ffff_ffff_ffff, 64);
    try expect64(0x8000_0000_0000_0001, 2);
    try expect64(0x7fff_ffff_ffff_fffe, 62);
}

test "phase1 hweight long follows native usize extremes" {
    const all_bits = std.math.maxInt(usize);
    const edge_bits: usize = (@as(usize, 1) << (@bitSizeOf(usize) - 1)) | 1;
    const middle_bits = all_bits ^ edge_bits;

    try std.testing.expectEqual(@as(usize, 0), hweight.hweightLong(0));
    try std.testing.expectEqual(@as(usize, @bitSizeOf(usize)), hweight.hweightLong(all_bits));
    try std.testing.expectEqual(@as(usize, 2), hweight.hweightLong(edge_bits));
    try std.testing.expectEqual(@as(usize, @bitSizeOf(usize) - 2), hweight.hweightLong(middle_bits));

    try std.testing.expectEqual(hweight.hweightLong(all_bits), hweight.hweight_long(all_bits));
    try std.testing.expectEqual(hweight.hweightLong(edge_bits), hweight.hweight_long(edge_bits));
}
