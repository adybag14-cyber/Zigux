const std = @import("std");
const hweight = @import("hweight");

fn expectSplit16(value: u32) !void {
    const lower: u32 = value & 0x00ff;
    const upper: u32 = (value >> 8) & 0x00ff;

    const direct = hweight.swHweight16(value);
    const split = hweight.swHweight8(lower) + hweight.swHweight8(upper);
    const alias = hweight.__sw_hweight8(lower) + hweight.__sw_hweight8(upper);

    try std.testing.expectEqual(direct, split);
    try std.testing.expectEqual(direct, alias);
    try std.testing.expectEqual(direct, hweight.__sw_hweight16(value));
}

fn expectSplit32(value: u32) !void {
    const lower: u32 = value & 0xffff;
    const upper: u32 = value >> 16;

    const direct = hweight.swHweight32(value);
    const split = hweight.swHweight16(lower) + hweight.swHweight16(upper);
    const alias = hweight.__sw_hweight16(lower) + hweight.__sw_hweight16(upper);

    try std.testing.expectEqual(direct, split);
    try std.testing.expectEqual(direct, alias);
    try std.testing.expectEqual(direct, hweight.__sw_hweight32(value));
}

fn expectSplit64(value: u64) !void {
    const lower: u32 = @intCast(value & 0xffff_ffff);
    const upper: u32 = @intCast(value >> 32);

    const direct = hweight.swHweight64(value);
    const split = hweight.swHweight32(lower) + hweight.swHweight32(upper);
    const alias = hweight.__sw_hweight32(lower) + hweight.__sw_hweight32(upper);

    try std.testing.expectEqual(direct, split);
    try std.testing.expectEqual(direct, alias);
    try std.testing.expectEqual(direct, hweight.__sw_hweight64(value));
}

test "phase1 hweight 16-bit halves stay additive across byte splits" {
    try expectSplit16(0xa55a);
    try expectSplit16(0x0f30);
    try expectSplit16(0x8001);
}

test "phase1 hweight 32-bit halves stay additive across 16-bit splits" {
    try expectSplit32(0xa55a_c33c);
    try expectSplit32(0xf0f0_00ff);
    try expectSplit32(0x8000_0001);
}

test "phase1 hweight 64-bit and native-width aliases agree with split halves" {
    try expectSplit64(0xa55a_c33c_0f0f_f055);
    try expectSplit64(0xffff_0000_0000_ffff);
    try expectSplit64(0x8000_0000_0000_0001);

    const native_value: usize = if (@sizeOf(usize) == 4)
        0xa55a_c33c
    else
        0xa55a_c33c_0f0f_f055;

    const direct = hweight.hweightLong(native_value);
    const alias = hweight.hweight_long(native_value);
    try std.testing.expectEqual(direct, alias);

    const split: usize = if (@sizeOf(usize) == 4)
        @as(usize, hweight.swHweight16(@intCast(native_value & 0xffff))) +
            @as(usize, hweight.swHweight16(@intCast(native_value >> 16)))
    else
        @as(usize, @intCast(hweight.swHweight32(@intCast(native_value & 0xffff_ffff)))) +
            @as(usize, @intCast(hweight.swHweight32(@intCast(native_value >> 32))));

    try std.testing.expectEqual(direct, split);
}
