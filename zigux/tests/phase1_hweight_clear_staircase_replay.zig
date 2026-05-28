const std = @import("std");
const live_hweight = @import("hweight");

fn expectStaircase32(
    original: u32,
    comptime weight_fn: fn (u32) u32,
    comptime alias_fn: fn (u32) u32,
) !void {
    var current = original;
    var cleared_steps: u32 = 0;
    const expected = weight_fn(original);

    while (true) {
        const before = weight_fn(current);
        try std.testing.expectEqual(before, alias_fn(current));
        try std.testing.expectEqual(before, expected - cleared_steps);
        if (current == 0) break;

        current &= current - 1;
        cleared_steps += 1;
        try std.testing.expectEqual(before - 1, weight_fn(current));
    }

    try std.testing.expectEqual(expected, cleared_steps);
}

fn expectStaircase64(
    original: u64,
    comptime weight_fn: fn (u64) u64,
    comptime alias_fn: fn (u64) u64,
) !void {
    var current = original;
    var cleared_steps: u64 = 0;
    const expected = weight_fn(original);

    while (true) {
        const before = weight_fn(current);
        try std.testing.expectEqual(before, alias_fn(current));
        try std.testing.expectEqual(before, expected - cleared_steps);
        if (current == 0) break;

        current &= current - 1;
        cleared_steps += 1;
        try std.testing.expectEqual(before - 1, weight_fn(current));
    }

    try std.testing.expectEqual(expected, cleared_steps);
}

fn expectStaircaseLong(original: usize) !void {
    var current = original;
    var cleared_steps: usize = 0;
    const expected = live_hweight.hweightLong(original);

    while (true) {
        const before = live_hweight.hweightLong(current);
        try std.testing.expectEqual(before, live_hweight.hweight_long(current));
        try std.testing.expectEqual(before, expected - cleared_steps);
        if (current == 0) break;

        current &= current - 1;
        cleared_steps += 1;
        try std.testing.expectEqual(before - 1, live_hweight.hweightLong(current));
    }

    try std.testing.expectEqual(expected, cleared_steps);
}

test "phase1 hweight clear staircase replay drains every width to zero one bit at a time" {
    const values8 = [_]u32{ 0x00, 0x01, 0x81, 0x95, 0xf0, 0xff };
    for (values8) |value| {
        try expectStaircase32(value, live_hweight.swHweight8, live_hweight.__sw_hweight8);
    }

    const values16 = [_]u32{ 0x0000, 0x0001, 0x8001, 0x9249, 0xf0f0, 0xffff };
    for (values16) |value| {
        try expectStaircase32(value, live_hweight.swHweight16, live_hweight.__sw_hweight16);
    }

    const values32 = [_]u32{ 0x0000_0000, 0x0000_0001, 0x8000_0001, 0x9249_2492, 0xf0f0_f0f0, 0xffff_ffff };
    for (values32) |value| {
        try expectStaircase32(value, live_hweight.swHweight32, live_hweight.__sw_hweight32);
    }

    const values64 = [_]u64{
        0x0000_0000_0000_0000,
        0x0000_0000_0000_0001,
        0x8000_0000_0000_0001,
        0x9249_2492_4924_9249,
        0xf0f0_f0f0_f0f0_f0f0,
        0xffff_ffff_ffff_ffff,
    };
    for (values64) |value| {
        try expectStaircase64(value, live_hweight.swHweight64, live_hweight.__sw_hweight64);
    }

    const values_long = [_]usize{
        0,
        1,
        if (@sizeOf(usize) == 4) 0x8000_0001 else 0x8000_0000_0000_0001,
        if (@sizeOf(usize) == 4) 0x9249_2492 else 0x9249_2492_4924_9249,
        if (@sizeOf(usize) == 4) 0xf0f0_f0f0 else 0xf0f0_f0f0_f0f0_f0f0,
        if (@sizeOf(usize) == 4) 0xffff_ffff else 0xffff_ffff_ffff_ffff,
    };
    for (values_long) |value| {
        try expectStaircaseLong(value);
    }
}

test "phase1 hweight clear staircase replay matches manual clear counts on mixed masks" {
    const sample32 = [_]u32{ 0x0001_1110, 0x4000_0201, 0x5555_000f, 0x8000_ffff };
    for (sample32) |original| {
        var current = original;
        var cleared_steps: u32 = 0;
        while (current != 0) {
            current &= current - 1;
            cleared_steps += 1;
        }
        try std.testing.expectEqual(live_hweight.swHweight32(original), cleared_steps);
    }

    const sample64 = [_]u64{
        0x0000_0001_1111_0000,
        0x4000_0000_0000_0201,
        0x5555_5555_0000_000f,
        0x8000_ffff_ffff_ffff,
    };
    for (sample64) |original| {
        var current = original;
        var cleared_steps: u64 = 0;
        while (current != 0) {
            current &= current - 1;
            cleared_steps += 1;
        }
        try std.testing.expectEqual(live_hweight.swHweight64(original), cleared_steps);
    }
}
