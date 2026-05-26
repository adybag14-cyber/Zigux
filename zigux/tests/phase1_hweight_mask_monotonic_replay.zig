const std = @import("std");
const hweight = @import("hweight");

fn expectMaskMonotonic8(value: u32, mask: u32) !void {
    const masked = value & mask;
    try std.testing.expect(hweight.swHweight8(masked) <= hweight.swHweight8(value));
    try std.testing.expect(hweight.__sw_hweight8(masked) <= hweight.__sw_hweight8(value));
}

fn expectMaskMonotonic16(value: u32, mask: u32) !void {
    const masked = value & mask;
    try std.testing.expect(hweight.swHweight16(masked) <= hweight.swHweight16(value));
    try std.testing.expect(hweight.__sw_hweight16(masked) <= hweight.__sw_hweight16(value));
}

fn expectMaskMonotonic32(value: u32, mask: u32) !void {
    const masked = value & mask;
    try std.testing.expect(hweight.swHweight32(masked) <= hweight.swHweight32(value));
    try std.testing.expect(hweight.__sw_hweight32(masked) <= hweight.__sw_hweight32(value));
}

fn expectMaskMonotonic64(value: u64, mask: u64) !void {
    const masked = value & mask;
    try std.testing.expect(hweight.swHweight64(masked) <= hweight.swHweight64(value));
    try std.testing.expect(hweight.__sw_hweight64(masked) <= hweight.__sw_hweight64(value));
}

fn expectMaskMonotonicLong(value: usize, mask: usize) !void {
    const masked = value & mask;
    try std.testing.expect(hweight.hweightLong(masked) <= hweight.hweightLong(value));
    try std.testing.expect(hweight.hweight_long(masked) <= hweight.hweight_long(value));
}

test "phase1 hweight width-specific helpers stay monotonic under masking" {
    const samples8 = [_]struct { value: u32, mask: u32 }{
        .{ .value = 0x00, .mask = 0x00 },
        .{ .value = 0xff, .mask = 0x00 },
        .{ .value = 0xb6, .mask = 0x3c },
        .{ .value = 0x5a, .mask = 0xf0 },
        .{ .value = 0xe1, .mask = 0x7f },
    };
    for (samples8) |sample| {
        try expectMaskMonotonic8(sample.value, sample.mask);
    }

    const samples16 = [_]struct { value: u32, mask: u32 }{
        .{ .value = 0x0000, .mask = 0xffff },
        .{ .value = 0xffff, .mask = 0x0f0f },
        .{ .value = 0xa55a, .mask = 0x33cc },
        .{ .value = 0xf00f, .mask = 0x0ff0 },
        .{ .value = 0x1357, .mask = 0x1244 },
    };
    for (samples16) |sample| {
        try expectMaskMonotonic16(sample.value, sample.mask);
    }

    const samples32 = [_]struct { value: u32, mask: u32 }{
        .{ .value = 0x0000_0000, .mask = 0xffff_ffff },
        .{ .value = 0xffff_ffff, .mask = 0x0f0f_0f0f },
        .{ .value = 0xdead_beef, .mask = 0x55aa_ff00 },
        .{ .value = 0x1357_9bdf, .mask = 0x0246_8ace },
        .{ .value = 0xf0f0_00ff, .mask = 0x00ff_f0f0 },
    };
    for (samples32) |sample| {
        try expectMaskMonotonic32(sample.value, sample.mask);
    }

    const samples64 = [_]struct { value: u64, mask: u64 }{
        .{ .value = 0x0000_0000_0000_0000, .mask = 0xffff_ffff_ffff_ffff },
        .{ .value = 0xffff_ffff_ffff_ffff, .mask = 0x0f0f_0f0f_0f0f_0f0f },
        .{ .value = 0x0123_4567_89ab_cdef, .mask = 0x00ff_ff00_f0f0_0f0f },
        .{ .value = 0xfedc_ba98_7654_3210, .mask = 0x5555_aaaa_3333_cccc },
        .{ .value = 0x8000_0000_0000_0001, .mask = 0x7fff_ffff_ffff_fffe },
    };
    for (samples64) |sample| {
        try expectMaskMonotonic64(sample.value, sample.mask);
    }
}

test "phase1 hweight long helpers follow the same mask monotonic contract" {
    const samples = [_]struct { value: usize, mask: usize }{
        .{ .value = 0, .mask = std.math.maxInt(usize) },
        .{ .value = std.math.maxInt(usize), .mask = if (@sizeOf(usize) == 4) 0x0f0f_0f0f else 0x0f0f_0f0f_0f0f_0f0f },
        .{ .value = if (@sizeOf(usize) == 4) 0x89ab_cdef else 0x0123_4567_89ab_cdef, .mask = if (@sizeOf(usize) == 4) 0x00ff_f0f0 else 0x00ff_f0f0_0f0f_ff00 },
        .{ .value = if (@sizeOf(usize) == 4) 0xf0f0_00ff else 0xfedc_ba98_7654_3210, .mask = if (@sizeOf(usize) == 4) 0x0ff0_ff00 else 0x5555_aaaa_3333_cccc },
    };

    for (samples) |sample| {
        try expectMaskMonotonicLong(sample.value, sample.mask);
    }
}
