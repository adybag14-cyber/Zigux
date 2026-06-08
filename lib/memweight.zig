// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub fn memweight(bytes: []const u8) usize {
    var total: usize = 0;
    for (bytes) |byte| {
        total += @as(usize, @popCount(byte));
    }
    return total;
}

pub const memWeight = memweight;

test "memweight handles empty and zero-filled memory" {
    try std.testing.expectEqual(@as(usize, 0), memweight(&.{}));

    const bytes = [_]u8{ 0x00, 0x00, 0x00, 0x00 };
    try std.testing.expectEqual(@as(usize, 0), memweight(&bytes));
}

test "memweight counts mixed bytes" {
    const bytes = [_]u8{ 0x00, 0xff, 0x0f, 0x80, 0x55 };
    try std.testing.expectEqual(@as(usize, 17), memweight(&bytes));
}

test "memweight is independent of slice offset alignment" {
    const bytes = [_]u8{ 0xaa, 0x01, 0x03, 0x7f, 0x80, 0xff };
    try std.testing.expectEqual(@as(usize, 11), memweight(bytes[1..5]));
    try std.testing.expectEqual(@as(usize, 10), memweight(bytes[2..5]));
}
