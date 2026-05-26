const std = @import("std");
const hweight = @import("hweight");

fn expectCascade8(value: u8) !void {
    const count = hweight.swHweight8(value);
    try std.testing.expectEqual(@as(u32, @popCount(value)), count);
    try std.testing.expectEqual(count, hweight.__sw_hweight8(value));
}

fn expectCascade16(value: u16) !void {
    const low: u8 = @truncate(value);
    const high: u8 = @truncate(value >> 8);
    const count = hweight.swHweight16(value);

    try std.testing.expectEqual(@as(u32, @popCount(value)), count);
    try std.testing.expectEqual(count, hweight.__sw_hweight16(value));
    try std.testing.expectEqual(
        hweight.swHweight8(low) + hweight.swHweight8(high),
        count,
    );
    try std.testing.expectEqual(
        hweight.__sw_hweight8(low) + hweight.__sw_hweight8(high),
        hweight.__sw_hweight16(value),
    );
}

fn expectCascade32(value: u32) !void {
    const low: u16 = @truncate(value);
    const high: u16 = @truncate(value >> 16);
    const count = hweight.swHweight32(value);

    try std.testing.expectEqual(@as(u32, @popCount(value)), count);
    try std.testing.expectEqual(count, hweight.__sw_hweight32(value));
    try std.testing.expectEqual(
        hweight.swHweight16(low) + hweight.swHweight16(high),
        count,
    );
    try std.testing.expectEqual(
        hweight.__sw_hweight16(low) + hweight.__sw_hweight16(high),
        hweight.__sw_hweight32(value),
    );
}

fn expectCascade64(value: u64) !void {
    const low: u32 = @truncate(value);
    const high: u32 = @truncate(value >> 32);
    const count = hweight.swHweight64(value);

    try std.testing.expectEqual(@as(u64, @popCount(value)), count);
    try std.testing.expectEqual(count, hweight.__sw_hweight64(value));
    try std.testing.expectEqual(
        @as(u64, hweight.swHweight32(low)) + @as(u64, hweight.swHweight32(high)),
        count,
    );
    try std.testing.expectEqual(
        @as(u64, hweight.__sw_hweight32(low)) + @as(u64, hweight.__sw_hweight32(high)),
        hweight.__sw_hweight64(value),
    );
}

test "phase1 hweight helpers stay consistent when widened values are split through the next smaller helper" {
    const values8 = [_]u8{ 0x00, 0x01, 0x96, 0xff };
    for (values8) |value| {
        try expectCascade8(value);
    }

    const values16 = [_]u16{ 0x0000, 0x0001, 0x9669, 0xffff };
    for (values16) |value| {
        try expectCascade16(value);
    }

    const values32 = [_]u32{ 0x0000_0000, 0x0000_0001, 0x9669_6996, 0xffff_ffff };
    for (values32) |value| {
        try expectCascade32(value);
    }

    const values64 = [_]u64{
        0x0000_0000_0000_0000,
        0x0000_0000_0000_0001,
        0x9669_6996_6996_9669,
        0xffff_ffff_ffff_ffff,
    };
    for (values64) |value| {
        try expectCascade64(value);
    }
}

test "phase1 hweight long helper matches the same cascade count as the usize-wide helper surface" {
    const values = if (@sizeOf(usize) == 4)
        [_]usize{ 0x0000_0000, 0x0000_0001, 0x9669_6996, 0xffff_ffff }
    else
        [_]usize{
            0x0000_0000_0000_0000,
            0x0000_0000_0000_0001,
            0x9669_6996_6996_9669,
            0xffff_ffff_ffff_ffff,
        };

    for (values) |value| {
        const count = hweight.hweightLong(value);
        try std.testing.expectEqual(@as(usize, @popCount(value)), count);
        try std.testing.expectEqual(count, hweight.hweight_long(value));

        if (@sizeOf(usize) == 4) {
            const low: u16 = @truncate(value);
            const high: u16 = @truncate(value >> 16);
            try std.testing.expectEqual(
                @as(usize, hweight.swHweight16(low) + hweight.swHweight16(high)),
                count,
            );
        } else {
            const low: u32 = @truncate(value);
            const high: u32 = @truncate(value >> 32);
            try std.testing.expectEqual(
                @as(usize, hweight.swHweight32(low) + hweight.swHweight32(high)),
                count,
            );
        }
    }
}
