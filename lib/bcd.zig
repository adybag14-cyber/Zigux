// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub fn bcd2bin(val: u8) u32 {
    return @as(u32, val & 0x0f) + @as(u32, val >> 4) * 10;
}

pub fn bin2bcd(val: u32) u8 {
    const t = (val * 103) >> 10;
    return @truncate((t << 4) | (val - t * 10));
}

pub const _bcd2bin = bcd2bin;
pub const _bin2bcd = bin2bcd;

test "bcd conversion matches Linux helper arithmetic" {
    try std.testing.expectEqual(@as(u32, 0), bcd2bin(0x00));
    try std.testing.expectEqual(@as(u32, 9), bcd2bin(0x09));
    try std.testing.expectEqual(@as(u32, 42), bcd2bin(0x42));
    try std.testing.expectEqual(@as(u32, 99), bcd2bin(0x99));

    try std.testing.expectEqual(@as(u8, 0x00), bin2bcd(0));
    try std.testing.expectEqual(@as(u8, 0x09), bin2bcd(9));
    try std.testing.expectEqual(@as(u8, 0x42), bin2bcd(42));
    try std.testing.expectEqual(@as(u8, 0x99), bin2bcd(99));
}

test "bcd round trips valid two digit values" {
    var value: u32 = 0;
    while (value < 100) : (value += 1) {
        try std.testing.expectEqual(value, bcd2bin(bin2bcd(value)));
    }
}
