const std = @import("std");
const hweight = @import("hweight");

fn prefixFillU32(width: usize, bits: usize) u32 {
    if (bits == 0) return 0;
    if (bits == width) return std.math.maxInt(u32);
    return (@as(u32, 1) << @intCast(bits)) - 1;
}

fn prefixFillU64(width: usize, bits: usize) u64 {
    if (bits == 0) return 0;
    if (bits == width) return std.math.maxInt(u64);
    return (@as(u64, 1) << @intCast(bits)) - 1;
}

test "hweight prefix fills count every contiguous low-bit run exactly once" {
    var bits: usize = 0;
    while (bits <= 8) : (bits += 1) {
        const value = prefixFillU32(8, bits);
        try std.testing.expectEqual(@as(u32, @intCast(bits)), hweight.swHweight8(value));
        try std.testing.expectEqual(@as(u32, @intCast(bits)), hweight.__sw_hweight8(value));
    }

    bits = 0;
    while (bits <= 16) : (bits += 1) {
        const value = prefixFillU32(16, bits);
        try std.testing.expectEqual(@as(u32, @intCast(bits)), hweight.swHweight16(value));
        try std.testing.expectEqual(@as(u32, @intCast(bits)), hweight.__sw_hweight16(value));
    }

    bits = 0;
    while (bits <= 32) : (bits += 1) {
        const value = prefixFillU32(32, bits);
        try std.testing.expectEqual(@as(u32, @intCast(bits)), hweight.swHweight32(value));
        try std.testing.expectEqual(@as(u32, @intCast(bits)), hweight.__sw_hweight32(value));
    }

    bits = 0;
    while (bits <= 64) : (bits += 1) {
        const value = prefixFillU64(64, bits);
        try std.testing.expectEqual(@as(u64, @intCast(bits)), hweight.swHweight64(value));
        try std.testing.expectEqual(@as(u64, @intCast(bits)), hweight.__sw_hweight64(value));
    }
}

test "hweightLong prefix fills stay aligned with the native word width" {
    const native_bits = @bitSizeOf(usize);

    var bits: usize = 0;
    while (bits <= native_bits) : (bits += 1) {
        const expected: usize = bits;
        const value: usize = if (bits == 0)
            0
        else if (bits == native_bits)
            std.math.maxInt(usize)
        else
            (@as(usize, 1) << @intCast(bits)) - 1;

        try std.testing.expectEqual(expected, hweight.hweightLong(value));
        try std.testing.expectEqual(expected, hweight.hweight_long(value));
    }
}
