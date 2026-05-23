const std = @import("std");
const hweight = @import("hweight");

fn expectWindowCount8(value: u32) !void {
    try std.testing.expectEqual(@as(u32, @popCount(value & 0xff)), hweight.swHweight8(value));
    try std.testing.expectEqual(hweight.swHweight8(value), hweight.__sw_hweight8(value));
}

fn expectWindowCount16(value: u32) !void {
    try std.testing.expectEqual(@as(u32, @popCount(value & 0xffff)), hweight.swHweight16(value));
    try std.testing.expectEqual(hweight.swHweight16(value), hweight.__sw_hweight16(value));
}

fn expectWindowCount32(value: u32) !void {
    try std.testing.expectEqual(@as(u32, @popCount(value)), hweight.swHweight32(value));
    try std.testing.expectEqual(hweight.swHweight32(value), hweight.__sw_hweight32(value));
}

fn expectWindowCount64(value: u64) !void {
    try std.testing.expectEqual(@as(u64, @popCount(value)), hweight.swHweight64(value));
    try std.testing.expectEqual(hweight.swHweight64(value), hweight.__sw_hweight64(value));
}

test "phase1 hweight helper smoke imports the live helper surface" {
    try std.testing.expect(@hasDecl(hweight, "swHweight8"));
    try std.testing.expect(@hasDecl(hweight, "swHweight16"));
    try std.testing.expect(@hasDecl(hweight, "swHweight32"));
    try std.testing.expect(@hasDecl(hweight, "swHweight64"));
    try std.testing.expect(@hasDecl(hweight, "hweightLong"));
    try std.testing.expect(@hasDecl(hweight, "__sw_hweight8"));
    try std.testing.expect(@hasDecl(hweight, "__sw_hweight16"));
    try std.testing.expect(@hasDecl(hweight, "__sw_hweight32"));
    try std.testing.expect(@hasDecl(hweight, "__sw_hweight64"));
    try std.testing.expect(@hasDecl(hweight, "hweight_long"));
}

test "phase1 hweight helper smoke keeps sliding windows aligned with popcount" {
    try expectWindowCount8(0b0111_1000);
    try expectWindowCount8(@as(u32, 0b0011_1110) << 1);

    try expectWindowCount16(0x0f80);
    try expectWindowCount16(@as(u32, 0x01ff) << 3);

    try expectWindowCount32(0x03ff_8000);
    try expectWindowCount32(0x80ff_00ff);

    try expectWindowCount64(0x0000_001f_ffff_0000);
    try expectWindowCount64(0xf000_0000_0000_000f);

    const long_value: usize = if (@sizeOf(usize) == 4) 0xf0f0_000f else 0xf0f0_0000_0000_000f;
    try std.testing.expectEqual(@popCount(long_value), hweight.hweightLong(long_value));
    try std.testing.expectEqual(hweight.hweightLong(long_value), hweight.hweight_long(long_value));
}

test "phase1 hweight helper smoke stays additive across disjoint width windows" {
    const low8: u32 = 0b0000_1111;
    const high8: u32 = 0b1111_0000;
    try std.testing.expectEqual(hweight.swHweight8(low8) + hweight.swHweight8(high8), hweight.swHweight8(low8 | high8));

    const low16: u32 = 0x003f;
    const high16: u32 = 0xfc00;
    try std.testing.expectEqual(hweight.swHweight16(low16) + hweight.swHweight16(high16), hweight.swHweight16(low16 | high16));

    const low32: u32 = 0x0000_ffff;
    const high32: u32 = 0xffff_0000;
    try std.testing.expectEqual(hweight.swHweight32(low32) + hweight.swHweight32(high32), hweight.swHweight32(low32 | high32));

    const low64: u64 = 0x0000_0000_ffff_ffff;
    const high64: u64 = 0xffff_ffff_0000_0000;
    try std.testing.expectEqual(hweight.swHweight64(low64) + hweight.swHweight64(high64), hweight.swHweight64(low64 | high64));

    const low_long: usize = if (@sizeOf(usize) == 4) 0x0000_ffff else 0x0000_0000_ffff_ffff;
    const high_long: usize = ~low_long;
    try std.testing.expectEqual(hweight.hweightLong(low_long) + hweight.hweightLong(high_long), hweight.hweightLong(low_long | high_long));
}
