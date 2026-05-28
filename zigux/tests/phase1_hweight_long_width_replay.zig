const std = @import("std");
const hweight = @import("hweight");

fn expectedLongWeight(value: usize) usize {
    return if (@sizeOf(usize) == 4)
        @intCast(hweight.swHweight32(@intCast(value)))
    else
        @intCast(hweight.swHweight64(@intCast(value)));
}

test "hweightLong follows the native word-size helper" {
    const cases = [_]usize{
        0,
        1,
        0xff,
        0x1010,
        0x5555,
        0x8000_0000,
        ~@as(usize, 0),
    };

    for (cases) |value| {
        try std.testing.expectEqual(expectedLongWeight(value), hweight.hweightLong(value));
        try std.testing.expectEqual(@popCount(value), hweight.hweightLong(value));
    }

    if (@sizeOf(usize) == 8) {
        const wide_cases = [_]usize{
            0x1_0000_0000,
            0x8000_0000_0000_0000,
            0xf0f0_0000_0000_0f0f,
        };

        for (wide_cases) |value| {
            try std.testing.expectEqual(expectedLongWeight(value), hweight.hweightLong(value));
            try std.testing.expectEqual(@popCount(value), hweight.hweightLong(value));
        }
    }
}

test "hweightLong keeps split high and low words additive" {
    const low: usize = 0x0000_ffff;
    const high: usize = if (@sizeOf(usize) == 4) 0xffff_0000 else 0xffff_0000_0000_0000;
    const combined = low | high;

    try std.testing.expectEqual(
        hweight.hweightLong(low) + hweight.hweightLong(high),
        hweight.hweightLong(combined),
    );
}

test "Linux hweight_long alias preserves native-width selection" {
    const value: usize = if (@sizeOf(usize) == 4) 0xa5a5_5001 else 0xa5a5_5001_8000_ffff;

    try std.testing.expectEqual(hweight.hweightLong(value), hweight.hweight_long(value));
    try std.testing.expectEqual(expectedLongWeight(value), hweight.hweight_long(value));
}
