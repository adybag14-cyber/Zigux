// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub const hex_asc = "0123456789abcdef";
pub const hex_asc_upper = "0123456789ABCDEF";

pub const HexError = error{
    InvalidHexDigit,
    InvalidSourceLength,
    DestinationTooSmall,
};

pub fn hexToBin(ch: u8) i32 {
    const cu = ch & 0xdf;
    return -1 +
        ((@as(i32, ch) - '0' + 1) & @as(i32, @bitCast(((@as(i32, ch) - '9' - 1) & ('0' - 1 - @as(i32, ch))) >> 8))) +
        ((@as(i32, cu) - 'A' + 11) & @as(i32, @bitCast(((@as(i32, cu) - 'F' - 1) & ('A' - 1 - @as(i32, cu))) >> 8)));
}

pub fn hex2bin(dst: []u8, src: []const u8) HexError!void {
    if (src.len != dst.len * 2) {
        return error.InvalidSourceLength;
    }

    for (dst, 0..) |*out, index| {
        const hi = hexToBin(src[index * 2]);
        if (hi < 0) {
            return error.InvalidHexDigit;
        }

        const lo = hexToBin(src[index * 2 + 1]);
        if (lo < 0) {
            return error.InvalidHexDigit;
        }

        out.* = (@as(u8, @intCast(hi)) << 4) | @as(u8, @intCast(lo));
    }
}

pub fn bin2hex(dst: []u8, src: []const u8) HexError![]u8 {
    if (dst.len < src.len * 2) {
        return error.DestinationTooSmall;
    }

    for (src, 0..) |byte, index| {
        dst[index * 2] = hex_asc[byte >> 4];
        dst[index * 2 + 1] = hex_asc[byte & 0x0f];
    }

    return dst[0 .. src.len * 2];
}

test "hexToBin accepts lower, upper, and rejects non-hex digits" {
    try std.testing.expectEqual(@as(i32, 0), hexToBin('0'));
    try std.testing.expectEqual(@as(i32, 9), hexToBin('9'));
    try std.testing.expectEqual(@as(i32, 10), hexToBin('a'));
    try std.testing.expectEqual(@as(i32, 15), hexToBin('F'));
    try std.testing.expectEqual(@as(i32, -1), hexToBin('/'));
    try std.testing.expectEqual(@as(i32, -1), hexToBin('g'));
}

test "hex2bin decodes mixed-case input" {
    var decoded: [6]u8 = undefined;
    try hex2bin(&decoded, "DeAdBEEF0123");
    try std.testing.expectEqualSlices(u8, &.{ 0xde, 0xad, 0xbe, 0xef, 0x01, 0x23 }, &decoded);
}

test "hex2bin rejects malformed source lengths and invalid digits" {
    var decoded: [2]u8 = undefined;

    try std.testing.expectError(error.InvalidSourceLength, hex2bin(&decoded, "abc"));
    try std.testing.expectError(error.InvalidHexDigit, hex2bin(&decoded, "0x00"));
}

test "bin2hex encodes bytes and round-trips through hex2bin" {
    const source = [_]u8{ 0x00, 0x12, 0xab, 0xff, 0x34 };
    var encoded: [source.len * 2]u8 = undefined;
    var decoded: [source.len]u8 = undefined;

    const written = try bin2hex(&encoded, &source);
    try std.testing.expectEqualStrings("0012abff34", written);

    try hex2bin(&decoded, written);
    try std.testing.expectEqualSlices(u8, &source, &decoded);
}

test "bin2hex reports short destinations" {
    const source = [_]u8{ 0xaa, 0xbb };
    var encoded: [3]u8 = undefined;

    try std.testing.expectError(error.DestinationTooSmall, bin2hex(&encoded, &source));
}
