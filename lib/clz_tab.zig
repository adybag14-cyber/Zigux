// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

fn clzTabValue(byte: u8) u8 {
    return if (byte == 0) 0 else 8 - @as(u8, @intCast(@clz(byte)));
}

fn makeClzTab() [256]u8 {
    var table: [256]u8 = undefined;
    for (&table, 0..) |*slot, i| {
        const byte: u8 = @intCast(i);
        slot.* = clzTabValue(byte);
    }
    return table;
}

pub const __clz_tab: [256]u8 = makeClzTab();

test "clz table spot checks match Linux table" {
    try std.testing.expectEqual(@as(u8, 0), __clz_tab[0]);
    try std.testing.expectEqual(@as(u8, 1), __clz_tab[1]);
    try std.testing.expectEqual(@as(u8, 2), __clz_tab[2]);
    try std.testing.expectEqual(@as(u8, 2), __clz_tab[3]);
    try std.testing.expectEqual(@as(u8, 3), __clz_tab[4]);
    try std.testing.expectEqual(@as(u8, 7), __clz_tab[127]);
    try std.testing.expectEqual(@as(u8, 8), __clz_tab[128]);
    try std.testing.expectEqual(@as(u8, 8), __clz_tab[255]);
}

test "clz table matches byte width formula" {
    for (__clz_tab, 0..) |value, i| {
        const byte: u8 = @intCast(i);
        try std.testing.expectEqual(clzTabValue(byte), value);
    }
}
