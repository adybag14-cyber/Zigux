const std = @import("std");
const live_hweight = @import("hweight");

fn maskForWidth32(comptime width: u6) u32 {
    return if (width == 32) std.math.maxInt(u32) else (@as(u32, 1) << width) - 1;
}

fn maskForWidth64(comptime width: u7) u64 {
    return if (width == 64) std.math.maxInt(u64) else (@as(u64, 1) << width) - 1;
}

fn expectToggleDelta32(comptime width: u6, value: u32, helper: *const fn (u32) u32) !void {
    const base = value & maskForWidth32(width);
    const before = helper(base);

    for (0..width) |bit| {
        const bit_mask: u32 = @as(u32, 1) << @intCast(bit);
        const after = helper(base ^ bit_mask);
        if ((base & bit_mask) == 0) {
            try std.testing.expectEqual(before + 1, after);
        } else {
            try std.testing.expectEqual(before - 1, after);
        }
    }
}

fn expectToggleDelta64(comptime width: u7, value: u64, helper: *const fn (u64) u64) !void {
    const base = value & maskForWidth64(width);
    const before = helper(base);

    for (0..width) |bit| {
        const bit_mask: u64 = @as(u64, 1) << @intCast(bit);
        const after = helper(base ^ bit_mask);
        if ((base & bit_mask) == 0) {
            try std.testing.expectEqual(before + 1, after);
        } else {
            try std.testing.expectEqual(before - 1, after);
        }
    }
}

fn expectToggleDeltaLong(value: usize) !void {
    const before = live_hweight.hweightLong(value);

    for (0..@bitSizeOf(usize)) |bit| {
        const bit_mask: usize = @as(usize, 1) << @intCast(bit);
        const after_primary = live_hweight.hweightLong(value ^ bit_mask);
        const after_alias = live_hweight.hweight_long(value ^ bit_mask);

        if ((value & bit_mask) == 0) {
            try std.testing.expectEqual(before + 1, after_primary);
            try std.testing.expectEqual(before + 1, after_alias);
        } else {
            try std.testing.expectEqual(before - 1, after_primary);
            try std.testing.expectEqual(before - 1, after_alias);
        }
    }
}

test "phase1 hweight toggle-delta replay keeps each narrow helper one bit apart" {
    const samples8 = [_]u32{
        0x00,
        0x01,
        0x55,
        0x80,
        0xa5,
        0xff,
    };
    for (samples8) |sample| {
        try expectToggleDelta32(8, sample, live_hweight.swHweight8);
        try expectToggleDelta32(8, sample, live_hweight.__sw_hweight8);
    }

    const samples16 = [_]u32{
        0x0000,
        0x0001,
        0x00ff,
        0x8000,
        0xa55a,
        0xffff,
    };
    for (samples16) |sample| {
        try expectToggleDelta32(16, sample, live_hweight.swHweight16);
        try expectToggleDelta32(16, sample, live_hweight.__sw_hweight16);
    }

    const samples32 = [_]u32{
        0x0000_0000,
        0x0000_0001,
        0x00ff_00ff,
        0x8000_0000,
        0xa55a_5aa5,
        0xffff_ffff,
    };
    for (samples32) |sample| {
        try expectToggleDelta32(32, sample, live_hweight.swHweight32);
        try expectToggleDelta32(32, sample, live_hweight.__sw_hweight32);
    }
}

test "phase1 hweight toggle-delta replay keeps wide and native helpers aligned" {
    const samples64 = [_]u64{
        0x0000_0000_0000_0000,
        0x0000_0000_0000_0001,
        0x00ff_00ff_00ff_00ff,
        0x8000_0000_0000_0000,
        0xa55a_5aa5_f00f_0ff0,
        0xffff_ffff_ffff_ffff,
    };
    for (samples64) |sample| {
        try expectToggleDelta64(64, sample, live_hweight.swHweight64);
        try expectToggleDelta64(64, sample, live_hweight.__sw_hweight64);
    }

    const native_samples = if (@sizeOf(usize) == 4)
        [_]usize{
            0x0000_0000,
            0x0000_0001,
            0x00ff_00ff,
            0x8000_0000,
            0xa55a_5aa5,
            0xffff_ffff,
        }
    else
        [_]usize{
            0x0000_0000_0000_0000,
            0x0000_0000_0000_0001,
            0x00ff_00ff_00ff_00ff,
            0x8000_0000_0000_0000,
            0xa55a_5aa5_f00f_0ff0,
            0xffff_ffff_ffff_ffff,
        };
    for (native_samples) |sample| {
        try expectToggleDeltaLong(sample);
    }
}
