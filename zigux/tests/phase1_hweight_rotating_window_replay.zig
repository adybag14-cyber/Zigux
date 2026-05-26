const std = @import("std");
const hweight = @import("hweight");

test "phase1 hweight replay keeps complement symmetry exact at each width" {
    const value8: u32 = 0b1010_0110;
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight8(value8) + hweight.swHweight8((~value8) & 0xff));

    const value16: u32 = 0xa5c3;
    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight16(value16) + hweight.swHweight16((~value16) & 0xffff));

    const value32: u32 = 0xa5c3_f00f;
    try std.testing.expectEqual(@as(u32, 32), hweight.swHweight32(value32) + hweight.swHweight32(~value32));

    const value64: u64 = 0xa5c3_f00f_1357_2468;
    try std.testing.expectEqual(@as(u64, 64), hweight.swHweight64(value64) + hweight.swHweight64(~value64));
}

test "phase1 hweight replay keeps byte-lane accumulation aligned across widths" {
    const lanes = [_]u8{ 0x81, 0x3c, 0xe7, 0x18, 0xaa, 0x11, 0x7f, 0x80 };

    const pair16: u32 = lanes[0] | (@as(u32, lanes[1]) << 8);
    try std.testing.expectEqual(
        hweight.swHweight8(lanes[0]) + hweight.swHweight8(lanes[1]),
        hweight.swHweight16(pair16),
    );

    const quad32: u32 = pair16 |
        (@as(u32, lanes[2]) << 16) |
        (@as(u32, lanes[3]) << 24);
    try std.testing.expectEqual(
        hweight.swHweight8(lanes[0]) +
            hweight.swHweight8(lanes[1]) +
            hweight.swHweight8(lanes[2]) +
            hweight.swHweight8(lanes[3]),
        hweight.swHweight32(quad32),
    );

    const octet64: u64 = @as(u64, lanes[0]) |
        (@as(u64, lanes[1]) << 8) |
        (@as(u64, lanes[2]) << 16) |
        (@as(u64, lanes[3]) << 24) |
        (@as(u64, lanes[4]) << 32) |
        (@as(u64, lanes[5]) << 40) |
        (@as(u64, lanes[6]) << 48) |
        (@as(u64, lanes[7]) << 56);
    try std.testing.expectEqual(
        @as(u64, hweight.swHweight32(quad32)) +
            hweight.swHweight8(lanes[4]) +
            hweight.swHweight8(lanes[5]) +
            hweight.swHweight8(lanes[6]) +
            hweight.swHweight8(lanes[7]),
        hweight.swHweight64(octet64),
    );
}

test "phase1 hweight replay keeps native long aggregation aligned with popcount" {
    const value: usize = if (@sizeOf(usize) == 4)
        0x9249_00f1
    else
        0x9249_00f1_1357_2468;

    const expected = @popCount(value);
    try std.testing.expectEqual(expected, hweight.hweightLong(value));

    if (@sizeOf(usize) == 4) {
        const lower: u32 = @intCast(value & 0xffff);
        const upper: u32 = @intCast(value >> 16);
        try std.testing.expectEqual(
            @as(usize, hweight.swHweight16(lower)) + @as(usize, hweight.swHweight16(upper)),
            hweight.hweightLong(value),
        );
    } else {
        const lower: u64 = @intCast(value & 0xffff_ffff);
        const upper: u64 = @intCast(value >> 32);
        try std.testing.expectEqual(
            @as(usize, hweight.swHweight32(@intCast(lower))) +
                @as(usize, hweight.swHweight32(@intCast(upper))),
            hweight.hweightLong(value),
        );
    }
}
