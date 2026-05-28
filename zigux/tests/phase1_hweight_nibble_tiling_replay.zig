const std = @import("std");
const hweight = @import("hweight");

fn repeatNibbleU32(width: usize, nibble: u32) u32 {
    var result: u32 = 0;
    var shift: usize = 0;
    while (shift < width) : (shift += 4) {
        result |= nibble << @intCast(shift);
    }
    return result;
}

fn repeatNibbleU64(width: usize, nibble: u64) u64 {
    var result: u64 = 0;
    var shift: usize = 0;
    while (shift < width) : (shift += 4) {
        result |= nibble << @intCast(shift);
    }
    return result;
}

test "hweight nibble tiling scales with repeated four-bit patterns" {
    var nibble: u32 = 0;
    while (nibble < 16) : (nibble += 1) {
        const nibble_count: u32 = @popCount(nibble);

        const value8 = repeatNibbleU32(8, nibble);
        try std.testing.expectEqual(nibble_count * 2, hweight.swHweight8(value8));
        try std.testing.expectEqual(nibble_count * 2, hweight.__sw_hweight8(value8));

        const value16 = repeatNibbleU32(16, nibble);
        try std.testing.expectEqual(nibble_count * 4, hweight.swHweight16(value16));
        try std.testing.expectEqual(nibble_count * 4, hweight.__sw_hweight16(value16));

        const value32 = repeatNibbleU32(32, nibble);
        try std.testing.expectEqual(nibble_count * 8, hweight.swHweight32(value32));
        try std.testing.expectEqual(nibble_count * 8, hweight.__sw_hweight32(value32));

        const value64 = repeatNibbleU64(64, nibble);
        const expected64 = @as(u64, nibble_count) * 16;
        try std.testing.expectEqual(expected64, hweight.swHweight64(value64));
        try std.testing.expectEqual(expected64, hweight.__sw_hweight64(value64));
    }
}

test "hweightLong nibble tiling stays aligned with native-word routing" {
    const native_bits = @bitSizeOf(usize);
    const repeats: usize = native_bits / 4;

    var nibble: usize = 0;
    while (nibble < 16) : (nibble += 1) {
        const nibble_count: usize = @popCount(nibble);
        const expected = nibble_count * repeats;
        const value = if (native_bits == 32)
            @as(usize, repeatNibbleU32(32, @intCast(nibble)))
        else
            @as(usize, @intCast(repeatNibbleU64(64, @intCast(nibble))));

        try std.testing.expectEqual(expected, hweight.hweightLong(value));
        try std.testing.expectEqual(expected, hweight.hweight_long(value));
    }
}
