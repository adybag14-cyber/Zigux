// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub const ETH_ALEN: usize = 6;
pub const MAC_ADDR_STR_LEN: usize = 17;
pub const MacAddress = [ETH_ALEN]u8;

pub fn macPton(s: []const u8, mac: *MacAddress) bool {
    if (s.len < MAC_ADDR_STR_LEN) return false;

    var parsed: MacAddress = undefined;
    for (0..ETH_ALEN) |i| {
        const pos = i * 3;
        const hi = hexToBin(s[pos]) orelse return false;
        const lo = hexToBin(s[pos + 1]) orelse return false;

        if (i != ETH_ALEN - 1 and s[pos + 2] != ':') return false;
        parsed[i] = (hi << 4) | lo;
    }

    mac.* = parsed;
    return true;
}

pub const mac_pton = macPton;

fn hexToBin(ch: u8) ?u8 {
    return switch (ch) {
        '0'...'9' => ch - '0',
        'a'...'f' => ch - 'a' + 10,
        'A'...'F' => ch - 'A' + 10,
        else => null,
    };
}

test "macPton accepts lowercase and uppercase hex" {
    var mac: MacAddress = .{ 0, 0, 0, 0, 0, 0 };
    const lower = [_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
    try std.testing.expect(macPton("aa:bb:cc:dd:ee:ff", &mac));
    try std.testing.expectEqualSlices(u8, &lower, &mac);

    const upper = [_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
    try std.testing.expect(macPton("AA:BB:CC:DD:EE:FF", &mac));
    try std.testing.expectEqualSlices(u8, &upper, &mac);
}

test "macPton rejects malformed strings" {
    var mac: MacAddress = .{ 0, 0, 0, 0, 0, 0 };
    try std.testing.expect(!macPton("aa:bb:cc:dd:ee:f", &mac));
    try std.testing.expect(!macPton("aa:bb:cc:dd:ee:gg", &mac));
    try std.testing.expect(!macPton("aa:bb:cc-dd:ee:ff", &mac));
}

test "macPton accepts trailing text like Linux mac_pton" {
    var mac: MacAddress = .{ 0, 0, 0, 0, 0, 0 };
    const expected = [_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
    try std.testing.expect(macPton("aa:bb:cc:dd:ee:ff trailing", &mac));
    try std.testing.expectEqualSlices(u8, &expected, &mac);
}

test "macPton leaves destination unchanged on failure" {
    var mac: MacAddress = .{ 1, 2, 3, 4, 5, 6 };
    const original = mac;
    try std.testing.expect(!macPton("aa:bb:cc:dd:ee:gg", &mac));
    try std.testing.expectEqualSlices(u8, &original, &mac);
}
