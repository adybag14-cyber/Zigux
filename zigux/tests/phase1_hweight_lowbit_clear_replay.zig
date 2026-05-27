const std = @import("std");
const hweight = @import("hweight");

fn expectLowbitDropU8(value: u8) !void {
    try std.testing.expect(value != 0);

    const cleared = value & (value - 1);
    try std.testing.expectEqual(hweight.swHweight8(value), hweight.swHweight8(cleared) + 1);
    try std.testing.expectEqual(hweight.__sw_hweight8(value), hweight.__sw_hweight8(cleared) + 1);
}

fn expectLowbitDropU16(value: u16) !void {
    try std.testing.expect(value != 0);

    const cleared = value & (value - 1);
    try std.testing.expectEqual(hweight.swHweight16(value), hweight.swHweight16(cleared) + 1);
    try std.testing.expectEqual(hweight.__sw_hweight16(value), hweight.__sw_hweight16(cleared) + 1);
}

fn expectLowbitDropU32(value: u32) !void {
    try std.testing.expect(value != 0);

    const cleared = value & (value - 1);
    try std.testing.expectEqual(hweight.swHweight32(value), hweight.swHweight32(cleared) + 1);
    try std.testing.expectEqual(hweight.__sw_hweight32(value), hweight.__sw_hweight32(cleared) + 1);
}

fn expectLowbitDropU64(value: u64) !void {
    try std.testing.expect(value != 0);

    const cleared = value & (value - 1);
    try std.testing.expectEqual(hweight.swHweight64(value), hweight.swHweight64(cleared) + 1);
    try std.testing.expectEqual(hweight.__sw_hweight64(value), hweight.__sw_hweight64(cleared) + 1);
}

fn expectLowbitDropLong(value: usize) !void {
    try std.testing.expect(value != 0);

    const cleared = value & (value - 1);
    try std.testing.expectEqual(hweight.hweightLong(value), hweight.hweightLong(cleared) + 1);
    try std.testing.expectEqual(hweight.hweight_long(value), hweight.hweight_long(cleared) + 1);
}

test "phase 1 hweight lowbit clear replay decrements every helper by one through full clear chains" {
    const u8_cases = [_]u8{ 0b1110_1010, 0b1000_0001, 0b0111_1111 };
    for (u8_cases) |initial| {
        var value = initial;
        while (value != 0) : (value &= value - 1) {
            try expectLowbitDropU8(value);
        }
    }

    const u16_cases = [_]u16{ 0xA5F0, 0x8001, 0x7FFF };
    for (u16_cases) |initial| {
        var value = initial;
        while (value != 0) : (value &= value - 1) {
            try expectLowbitDropU16(value);
        }
    }

    const u32_cases = [_]u32{ 0xA5F0_C33C, 0x8000_0001, 0x7FFF_FFFF };
    for (u32_cases) |initial| {
        var value = initial;
        while (value != 0) : (value &= value - 1) {
            try expectLowbitDropU32(value);
        }
    }

    const u64_cases = [_]u64{
        0xA5F0_C33C_8001_00FF,
        0x8000_0000_0000_0001,
        0x7FFF_FFFF_FFFF_FFFF,
    };
    for (u64_cases) |initial| {
        var value = initial;
        while (value != 0) : (value &= value - 1) {
            try expectLowbitDropU64(value);
        }
    }
}

test "phase 1 hweight lowbit clear replay keeps native-word routing aligned with width-local clearing" {
    const cases = if (@sizeOf(usize) == 4)
        [_]usize{ 0xA5F0_C33C, 0x8000_0001, 0x7FFF_FFFF }
    else
        [_]usize{
            0xA5F0_C33C_8001_00FF,
            0x8000_0000_0000_0001,
            0x7FFF_FFFF_FFFF_FFFF,
        };

    for (cases) |initial| {
        var value = initial;
        while (value != 0) : (value &= value - 1) {
            try expectLowbitDropLong(value);
        }
    }
}
