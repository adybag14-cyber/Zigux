const std = @import("std");
const hweight = @import("hweight");

fn byteLaneCount16(value: u32) u32 {
    return hweight.swHweight8(value & 0xff) +
        hweight.swHweight8((value >> 8) & 0xff);
}

fn byteLaneCount32(value: u32) u32 {
    var total: u32 = 0;
    for ([_]u5{ 0, 8, 16, 24 }) |shift| {
        total += hweight.swHweight8((value >> shift) & 0xff);
    }
    return total;
}

fn byteLaneCount64(value: u64) u64 {
    var total: u64 = 0;
    for ([_]u6{ 0, 8, 16, 24, 32, 40, 48, 56 }) |shift| {
        total += hweight.swHweight8(@intCast((value >> shift) & 0xff));
    }
    return total;
}

fn byteLaneCountLong(value: usize) usize {
    return if (@sizeOf(usize) == 4)
        @intCast(byteLaneCount32(@intCast(value)))
    else
        @intCast(byteLaneCount64(@intCast(value)));
}

test "phase1 hweight byte-lane accumulation stays aligned for width-specific helpers" {
    const samples16 = [_]u32{ 0x0000, 0x00f1, 0xa15c, 0xffff };
    for (samples16) |sample| {
        try std.testing.expectEqual(byteLaneCount16(sample), hweight.swHweight16(sample));
        try std.testing.expectEqual(byteLaneCount16(sample), hweight.__sw_hweight16(sample));
    }

    const samples32 = [_]u32{ 0x0000_0000, 0x0102_0304, 0xdead_beef, 0xffff_ffff };
    for (samples32) |sample| {
        try std.testing.expectEqual(byteLaneCount32(sample), hweight.swHweight32(sample));
        try std.testing.expectEqual(byteLaneCount32(sample), hweight.__sw_hweight32(sample));
    }

    const samples64 = [_]u64{
        0x0000_0000_0000_0000,
        0x0102_0304_0506_0708,
        0x0123_4567_89ab_cdef,
        0xffff_ffff_ffff_ffff,
    };
    for (samples64) |sample| {
        try std.testing.expectEqual(byteLaneCount64(sample), hweight.swHweight64(sample));
        try std.testing.expectEqual(byteLaneCount64(sample), hweight.__sw_hweight64(sample));
    }
}

test "phase1 hweight long helpers follow the same byte-lane total" {
    const samples = [_]usize{
        0,
        0x0102,
        if (@sizeOf(usize) == 4) 0x89ab_cdef else 0x0123_4567_89ab_cdef,
        std.math.maxInt(usize),
    };

    for (samples) |sample| {
        try std.testing.expectEqual(byteLaneCountLong(sample), hweight.hweightLong(sample));
        try std.testing.expectEqual(byteLaneCountLong(sample), hweight.hweight_long(sample));
    }
}
