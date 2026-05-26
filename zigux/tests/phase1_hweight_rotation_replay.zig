const std = @import("std");
const hweight = @import("hweight");

fn expectRotationInvariant8(value: u8, shift: u3) !void {
    const rotated = std.math.rotl(u8, value, shift);
    try std.testing.expectEqual(hweight.swHweight8(value), hweight.swHweight8(rotated));
    try std.testing.expectEqual(hweight.__sw_hweight8(value), hweight.__sw_hweight8(rotated));
    try std.testing.expectEqual(@as(u32, @popCount(value)), hweight.swHweight8(rotated));
}

fn expectRotationInvariant16(value: u16, shift: u4) !void {
    const rotated = std.math.rotl(u16, value, shift);
    try std.testing.expectEqual(hweight.swHweight16(value), hweight.swHweight16(rotated));
    try std.testing.expectEqual(hweight.__sw_hweight16(value), hweight.__sw_hweight16(rotated));
    try std.testing.expectEqual(@as(u32, @popCount(value)), hweight.swHweight16(rotated));
}

fn expectRotationInvariant32(value: u32, shift: u5) !void {
    const rotated = std.math.rotl(u32, value, shift);
    try std.testing.expectEqual(hweight.swHweight32(value), hweight.swHweight32(rotated));
    try std.testing.expectEqual(hweight.__sw_hweight32(value), hweight.__sw_hweight32(rotated));
    try std.testing.expectEqual(@as(u32, @popCount(value)), hweight.swHweight32(rotated));
}

fn expectRotationInvariant64(value: u64, shift: u6) !void {
    const rotated = std.math.rotl(u64, value, shift);
    try std.testing.expectEqual(hweight.swHweight64(value), hweight.swHweight64(rotated));
    try std.testing.expectEqual(hweight.__sw_hweight64(value), hweight.__sw_hweight64(rotated));
    try std.testing.expectEqual(@as(u64, @popCount(value)), hweight.swHweight64(rotated));
}

test "phase1 hweight width-specific helpers stay invariant under bit rotation" {
    const shifts8 = [_]u3{ 0, 1, 3, 7 };
    const samples8 = [_]u8{ 0x00, 0x01, 0x96, 0xff };
    for (samples8) |value| {
        for (shifts8) |shift| {
            try expectRotationInvariant8(value, shift);
        }
    }

    const shifts16 = [_]u4{ 0, 1, 5, 15 };
    const samples16 = [_]u16{ 0x0000, 0x0001, 0x9669, 0xffff };
    for (samples16) |value| {
        for (shifts16) |shift| {
            try expectRotationInvariant16(value, shift);
        }
    }

    const shifts32 = [_]u5{ 0, 1, 9, 31 };
    const samples32 = [_]u32{ 0x0000_0000, 0x0000_0001, 0x9669_6996, 0xffff_ffff };
    for (samples32) |value| {
        for (shifts32) |shift| {
            try expectRotationInvariant32(value, shift);
        }
    }

    const shifts64 = [_]u6{ 0, 1, 17, 63 };
    const samples64 = [_]u64{
        0x0000_0000_0000_0000,
        0x0000_0000_0000_0001,
        0x9669_6996_6996_9669,
        0xffff_ffff_ffff_ffff,
    };
    for (samples64) |value| {
        for (shifts64) |shift| {
            try expectRotationInvariant64(value, shift);
        }
    }
}

test "phase1 hweight long helper follows the same rotation invariant" {
    const Shift = std.math.Log2Int(usize);
    const shifts = if (@sizeOf(usize) == 4)
        [_]Shift{ 0, 1, 11, 31 }
    else
        [_]Shift{ 0, 1, 19, 63 };
    const samples = if (@sizeOf(usize) == 4)
        [_]usize{ 0x0000_0000, 0x0000_0001, 0x9669_6996, 0xffff_ffff }
    else
        [_]usize{ 0x0000_0000_0000_0000, 0x0000_0000_0000_0001, 0x9669_6996_6996_9669, 0xffff_ffff_ffff_ffff };

    for (samples) |value| {
        for (shifts) |shift| {
            const rotated = std.math.rotl(usize, value, shift);
            try std.testing.expectEqual(hweight.hweightLong(value), hweight.hweightLong(rotated));
            try std.testing.expectEqual(hweight.hweight_long(value), hweight.hweight_long(rotated));
            try std.testing.expectEqual(@as(usize, @popCount(value)), hweight.hweightLong(rotated));
        }
    }
}
