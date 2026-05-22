const std = @import("std");
const hweight = @import("hweight");

fn expectAliasParity8(value: u32) !void {
    if (@hasDecl(hweight, "__sw_hweight8")) {
        try std.testing.expectEqual(hweight.swHweight8(value), hweight.__sw_hweight8(value));
    }
}

fn expectAliasParity16(value: u32) !void {
    if (@hasDecl(hweight, "__sw_hweight16")) {
        try std.testing.expectEqual(hweight.swHweight16(value), hweight.__sw_hweight16(value));
    }
}

fn expectAliasParity32(value: u32) !void {
    if (@hasDecl(hweight, "__sw_hweight32")) {
        try std.testing.expectEqual(hweight.swHweight32(value), hweight.__sw_hweight32(value));
    }
}

fn expectAliasParity64(value: u64) !void {
    if (@hasDecl(hweight, "__sw_hweight64")) {
        try std.testing.expectEqual(hweight.swHweight64(value), hweight.__sw_hweight64(value));
    }
}

fn expectAliasParityLong(value: usize) !void {
    if (@hasDecl(hweight, "hweight_long")) {
        try std.testing.expectEqual(hweight.hweightLong(value), hweight.hweight_long(value));
    }
}

test "hweight byte and halfword windows match popcount" {
    const packed32: u32 = 0xb4f0_168f;
    const byte_shifts = [_]u5{ 0, 8, 16, 24 };

    var byte_total: u32 = 0;
    for (byte_shifts) |shift| {
        const window: u32 = (packed32 >> shift) & 0xff;
        const expected = @popCount(@as(u8, @intCast(window)));
        try std.testing.expectEqual(@as(u32, expected), hweight.swHweight8(window));
        try expectAliasParity8(window);
        byte_total += expected;
    }
    try std.testing.expectEqual(byte_total, hweight.swHweight32(packed32));

    const halfword_shifts = [_]u5{ 0, 16 };
    var halfword_total: u32 = 0;
    for (halfword_shifts) |shift| {
        const window: u32 = (packed32 >> shift) & 0xffff;
        const expected = @popCount(@as(u16, @intCast(window)));
        try std.testing.expectEqual(@as(u32, expected), hweight.swHweight16(window));
        try expectAliasParity16(window);
        halfword_total += expected;
    }
    try std.testing.expectEqual(halfword_total, hweight.swHweight32(packed32));
}

test "hweight doubleword windows decompose additively" {
    const packed64: u64 = 0xf0f0_0f0f_a55a_33cc;
    const low32: u32 = @intCast(packed64 & 0xffff_ffff);
    const high32: u32 = @intCast(packed64 >> 32);

    try std.testing.expectEqual(
        hweight.swHweight32(low32) + hweight.swHweight32(high32),
        @as(u32, @intCast(hweight.swHweight64(packed64))),
    );
    try expectAliasParity32(low32);
    try expectAliasParity32(high32);
    try expectAliasParity64(packed64);

    const quarter_shifts = [_]u6{ 0, 16, 32, 48 };
    var quarter_total: u64 = 0;
    for (quarter_shifts) |shift| {
        const window: u32 = @intCast((packed64 >> shift) & 0xffff);
        const expected = @popCount(@as(u16, @intCast(window)));
        try std.testing.expectEqual(@as(u32, expected), hweight.swHweight16(window));
        quarter_total += expected;
    }
    try std.testing.expectEqual(quarter_total, hweight.swHweight64(packed64));
}

test "hweightLong matches rolling usize windows" {
    var value: usize = 0;
    var index: usize = 0;
    while (index < @bitSizeOf(usize)) : (index += 3) {
        value |= @as(usize, 1) << @intCast(index);
    }

    const expected = @popCount(value);
    try std.testing.expectEqual(expected, hweight.hweightLong(value));
    try expectAliasParityLong(value);

    const lower_mask: usize = (@as(usize, 1) << @intCast(@bitSizeOf(usize) / 2)) - 1;
    const low = value & lower_mask;
    const high = value & ~lower_mask;

    try std.testing.expectEqual(
        hweight.hweightLong(low) + hweight.hweightLong(high),
        hweight.hweightLong(value),
    );
}
