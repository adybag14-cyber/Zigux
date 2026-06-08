// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

fn makeByteRevTable() [256]u8 {
    var out: [256]u8 = undefined;
    for (&out, 0..) |*slot, idx| {
        slot.* = @bitReverse(@as(u8, @intCast(idx)));
    }
    return out;
}

pub const byte_rev_table = makeByteRevTable();

pub fn bitrev8(value: u8) u8 {
    return byte_rev_table[value];
}

pub fn bitrev16(value: u16) u16 {
    return @bitReverse(value);
}

pub fn bitrev32(value: u32) u32 {
    return @bitReverse(value);
}

pub fn bitrev64(value: u64) u64 {
    return @bitReverse(value);
}

test "byte reverse table matches Linux constants" {
    try std.testing.expectEqual(@as(u8, 0x00), byte_rev_table[0x00]);
    try std.testing.expectEqual(@as(u8, 0x80), byte_rev_table[0x01]);
    try std.testing.expectEqual(@as(u8, 0x40), byte_rev_table[0x02]);
    try std.testing.expectEqual(@as(u8, 0xf0), byte_rev_table[0x0f]);
    try std.testing.expectEqual(@as(u8, 0xff), byte_rev_table[0xff]);
}

test "bitrev helpers reverse full integer widths" {
    try std.testing.expectEqual(@as(u8, 0b0100_1000), bitrev8(0b0001_0010));
    try std.testing.expectEqual(@as(u16, 0x2c48), bitrev16(0x1234));
    try std.testing.expectEqual(@as(u32, 0x1e6a_2c48), bitrev32(0x1234_5678));
    try std.testing.expectEqual(@as(u64, 0xf7b3_d591_e6a2_c480), bitrev64(0x0123_4567_89ab_cdef));
}
