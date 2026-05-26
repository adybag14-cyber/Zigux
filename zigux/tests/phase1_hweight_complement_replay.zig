const std = @import("std");
const hweight = @import("hweight");

fn expectComplementPair8(sample: u32) !void {
    const mask: u32 = 0xff;
    const complement = (~sample) & mask;
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight8(sample) + hweight.swHweight8(complement));
    try std.testing.expectEqual(@as(u32, 8), hweight.__sw_hweight8(sample) + hweight.__sw_hweight8(complement));
}

fn expectComplementPair16(sample: u32) !void {
    const mask: u32 = 0xffff;
    const complement = (~sample) & mask;
    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight16(sample) + hweight.swHweight16(complement));
    try std.testing.expectEqual(@as(u32, 16), hweight.__sw_hweight16(sample) + hweight.__sw_hweight16(complement));
}

fn expectComplementPair32(sample: u32) !void {
    const complement = ~sample;
    try std.testing.expectEqual(@as(u32, 32), hweight.swHweight32(sample) + hweight.swHweight32(complement));
    try std.testing.expectEqual(@as(u32, 32), hweight.__sw_hweight32(sample) + hweight.__sw_hweight32(complement));
}

fn expectComplementPair64(sample: u64) !void {
    const complement = ~sample;
    try std.testing.expectEqual(@as(u64, 64), hweight.swHweight64(sample) + hweight.swHweight64(complement));
    try std.testing.expectEqual(@as(u64, 64), hweight.__sw_hweight64(sample) + hweight.__sw_hweight64(complement));
}

test "phase1 hweight width-specific helpers preserve complement population symmetry" {
    const samples8 = [_]u32{ 0x00, 0x01, 0x55, 0xa6, 0xff };
    for (samples8) |sample| {
        try expectComplementPair8(sample);
    }

    const samples16 = [_]u32{ 0x0000, 0x0001, 0x00f0, 0xa55a, 0xffff };
    for (samples16) |sample| {
        try expectComplementPair16(sample);
    }

    const samples32 = [_]u32{ 0x0000_0000, 0x0000_0001, 0x0f0f_f0f0, 0xdead_beef, 0xffff_ffff };
    for (samples32) |sample| {
        try expectComplementPair32(sample);
    }

    const samples64 = [_]u64{
        0x0000_0000_0000_0000,
        0x0000_0000_0000_0001,
        0x0123_4567_89ab_cdef,
        0xf0f0_0f0f_a5a5_5a5a,
        0xffff_ffff_ffff_ffff,
    };
    for (samples64) |sample| {
        try expectComplementPair64(sample);
    }
}

test "phase1 hweight long aliases keep the same complement symmetry" {
    const bits = @bitSizeOf(usize);
    const samples = [_]usize{
        0,
        1,
        0x55,
        if (@sizeOf(usize) == 4) 0x89ab_cdef else 0x0123_4567_89ab_cdef,
        std.math.maxInt(usize),
    };

    for (samples) |sample| {
        const complement = ~sample;
        try std.testing.expectEqual(bits, hweight.hweightLong(sample) + hweight.hweightLong(complement));
        try std.testing.expectEqual(bits, hweight.hweight_long(sample) + hweight.hweight_long(complement));
    }
}
