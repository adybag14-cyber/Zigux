const std = @import("std");
const live_hweight = @import("hweight");

fn maskForWidth(comptime T: type, comptime width: u16) T {
    return if (width >= @bitSizeOf(T))
        std.math.maxInt(T)
    else
        (@as(T, 1) << width) - 1;
}

fn expectedCount32(comptime width: u16, value: u32) u32 {
    return @popCount(value & maskForWidth(u32, width));
}

fn expectedCount64(comptime width: u16, value: u64) u64 {
    return @popCount(value & maskForWidth(u64, width));
}

test "phase1 hweight width-mask replay keeps narrow helper contracts explicit" {
    const samples32 = [_]u32{
        0,
        1,
        0xff,
        0x100,
        0x01ff,
        0xa5a5,
        0xf0f0_f0f0,
        0xffff_0001,
        0x8000_00ff,
        0xffff_ffff,
    };

    for (samples32) |sample| {
        try std.testing.expectEqual(expectedCount32(8, sample), live_hweight.swHweight8(sample));
        try std.testing.expectEqual(expectedCount32(16, sample), live_hweight.swHweight16(sample));
        try std.testing.expectEqual(expectedCount32(32, sample), live_hweight.swHweight32(sample));
    }

    const samples64 = [_]u64{
        0,
        1,
        0xff,
        0x01ff,
        0x1_0000_0000,
        0xffff_ffff_0000_0001,
        0x8000_0000_0000_00ff,
        0xf0f0_f0f0_f0f0_f0f0,
        0xffff_ffff_ffff_ffff,
    };

    for (samples64) |sample| {
        try std.testing.expectEqual(expectedCount64(64, sample), live_hweight.swHweight64(sample));
    }
}

test "phase1 hweight width-mask replay keeps native-word routing aligned with popcount" {
    const native_samples = if (@sizeOf(usize) == 4)
        [_]usize{
            0,
            1,
            0x00ff,
            0x0101_0101,
            0x8000_00ff,
            0xffff_ffff,
        }
    else
        [_]usize{
            0,
            1,
            0x00ff,
            0x0101_0101_0101_0101,
            0x8000_0000_0000_00ff,
            0xffff_ffff_ffff_ffff,
        };

    for (native_samples) |sample| {
        try std.testing.expectEqual(@popCount(sample), live_hweight.hweightLong(sample));
    }
}
