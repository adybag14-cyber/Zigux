const std = @import("std");
const hweight = @import("hweight");

fn expect16SplitFold(value: u16) !void {
    const lower = hweight.swHweight8(@intCast(value & 0x00ff));
    const upper = hweight.swHweight8(@intCast((value >> 8) & 0x00ff));

    try std.testing.expectEqual(
        hweight.swHweight16(value),
        lower + upper,
    );
}

fn expect32SplitFold(value: u32) !void {
    const lower = hweight.swHweight16(value & 0x0000_ffff);
    const upper = hweight.swHweight16((value >> 16) & 0x0000_ffff);

    try std.testing.expectEqual(
        hweight.swHweight32(value),
        lower + upper,
    );
}

fn expect64SplitFold(value: u64) !void {
    const lower = hweight.swHweight32(@intCast(value & 0xffff_ffff));
    const upper = hweight.swHweight32(@intCast(value >> 32));

    try std.testing.expectEqual(
        hweight.swHweight64(value),
        lower + upper,
    );
}

test "phase 1 hweight split fold keeps byte pairs aligned with swHweight16" {
    const cases = [_]u16{
        0x0000,
        0x00ff,
        0xff00,
        0x0f0f,
        0x55aa,
        0x9669,
        0xffff,
    };

    for (cases) |value| {
        try expect16SplitFold(value);
    }
}

test "phase 1 hweight split fold keeps word halves aligned with swHweight32 and swHweight64" {
    const cases32 = [_]u32{
        0x0000_0000,
        0x0000_ffff,
        0xffff_0000,
        0xf0f0_0f0f,
        0x1234_5678,
        0xffff_ffff,
    };
    const cases64 = [_]u64{
        0x0000_0000_0000_0000,
        0x0000_0000_ffff_ffff,
        0xffff_ffff_0000_0000,
        0xf0f0_f0f0_0f0f_0f0f,
        0x0123_4567_89ab_cdef,
        0xffff_ffff_ffff_ffff,
    };

    for (cases32) |value| {
        try expect32SplitFold(value);
    }

    for (cases64) |value| {
        try expect64SplitFold(value);
    }
}

test "phase 1 hweight split fold keeps hweightLong aligned with native halves" {
    const cases = [_]usize{
        0,
        1,
        0x00ff,
        0xf0f0,
        0x1234_5678,
        std.math.maxInt(usize),
    };

    for (cases) |value| {
        const expected = @popCount(value);
        const actual = hweight.hweightLong(value);
        try std.testing.expectEqual(expected, actual);

        if (@sizeOf(usize) == 4) {
            const lower = hweight.swHweight16(@intCast(value & 0x0000_ffff));
            const upper = hweight.swHweight16(@intCast((value >> 16) & 0x0000_ffff));
            try std.testing.expectEqual(actual, lower + upper);
        } else {
            const lower = hweight.swHweight32(@intCast(value & 0xffff_ffff));
            const upper = hweight.swHweight32(@intCast(value >> 32));
            try std.testing.expectEqual(actual, lower + upper);
        }
    }
}
