// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub const Uuid = [16]u8;
pub const ParseError = error{ InvalidLength, InvalidCharacter, InvalidHyphen };

pub fn parse(text: []const u8) ParseError!Uuid {
    if (text.len != 36) return ParseError.InvalidLength;
    var out: Uuid = undefined;
    var out_idx: usize = 0;
    var idx: usize = 0;
    while (idx < text.len) {
        if (idx == 8 or idx == 13 or idx == 18 or idx == 23) {
            if (text[idx] != '-') return ParseError.InvalidHyphen;
            idx += 1;
            continue;
        }
        if (idx + 1 >= text.len) return ParseError.InvalidLength;
        out[out_idx] = (try hexValue(text[idx]) << 4) | try hexValue(text[idx + 1]);
        out_idx += 1;
        idx += 2;
    }
    return out;
}

pub fn formatLower(uuid: Uuid, out: []u8) ![]u8 {
    if (out.len < 36) return error.NoSpaceLeft;
    var pos: usize = 0;
    for (uuid, 0..) |byte, idx| {
        if (idx == 4 or idx == 6 or idx == 8 or idx == 10) {
            out[pos] = '-';
            pos += 1;
        }
        out[pos] = lower_hex[byte >> 4];
        out[pos + 1] = lower_hex[byte & 0x0f];
        pos += 2;
    }
    return out[0..36];
}

pub fn isNull(uuid: Uuid) bool {
    for (uuid) |byte| if (byte != 0) return false;
    return true;
}

const lower_hex = "0123456789abcdef";

fn hexValue(ch: u8) ParseError!u8 {
    return switch (ch) {
        '0'...'9' => ch - '0',
        'a'...'f' => ch - 'a' + 10,
        'A'...'F' => ch - 'A' + 10,
        else => ParseError.InvalidCharacter,
    };
}

test "uuid parse and lower format round trip" {
    const text = "00112233-4455-6677-8899-aabbccddeeff";
    const parsed = try parse(text);
    try std.testing.expectEqualSlices(u8, &.{ 0x00, 0x11, 0x22, 0x33 }, parsed[0..4]);
    try std.testing.expect(!isNull(parsed));

    var buf: [36]u8 = undefined;
    const rendered = try formatLower(parsed, &buf);
    try std.testing.expectEqualStrings(text, rendered);
}

test "uuid parser rejects malformed input" {
    try std.testing.expectError(ParseError.InvalidLength, parse("short"));
    try std.testing.expectError(ParseError.InvalidHyphen, parse("00112233x4455-6677-8899-aabbccddeeff"));
    try std.testing.expectError(ParseError.InvalidCharacter, parse("00112233-4455-6677-8899-aabbccddeezz"));
    try std.testing.expect(isNull(try parse("00000000-0000-0000-0000-000000000000")));
}
