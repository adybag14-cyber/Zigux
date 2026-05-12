// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub const Variant = enum {
    standard,
    urlsafe,
    imap,
};

pub const Error = error{
    InvalidBase64,
    NoSpaceLeft,
    Overflow,
};

pub fn maxEncodedLen(nbytes: usize) Error!usize {
    const scaled = try std.math.mul(usize, nbytes, 4);
    const adjusted = try std.math.add(usize, scaled, 2);
    return adjusted / 3;
}

pub fn encodedLen(nbytes: usize, padding: bool) Error!usize {
    if (!padding) {
        return maxEncodedLen(nbytes);
    }

    const groups = try std.math.add(usize, nbytes / 3, @intFromBool(nbytes % 3 != 0));
    return std.math.mul(usize, groups, 4);
}

pub fn maxDecodedLen(encoded_len: usize) Error!usize {
    const scaled = try std.math.mul(usize, encoded_len, 3);
    return scaled / 4;
}

pub fn encode(src: []const u8, dst: []u8, padding: bool, variant: Variant) Error![]u8 {
    const needed = try encodedLen(src.len, padding);
    if (dst.len < needed) {
        return error.NoSpaceLeft;
    }

    const alphabet = alphabetFor(variant);
    var src_index: usize = 0;
    var dst_index: usize = 0;

    while (src_index + 3 <= src.len) : (src_index += 3) {
        const accum = (@as(u24, src[src_index]) << 16) |
            (@as(u24, src[src_index + 1]) << 8) |
            @as(u24, src[src_index + 2]);

        dst[dst_index] = alphabet[@intCast((accum >> 18) & 0x3f)];
        dst[dst_index + 1] = alphabet[@intCast((accum >> 12) & 0x3f)];
        dst[dst_index + 2] = alphabet[@intCast((accum >> 6) & 0x3f)];
        dst[dst_index + 3] = alphabet[@intCast(accum & 0x3f)];
        dst_index += 4;
    }

    switch (src.len - src_index) {
        0 => {},
        1 => {
            const accum = @as(u24, src[src_index]) << 16;
            dst[dst_index] = alphabet[@intCast((accum >> 18) & 0x3f)];
            dst[dst_index + 1] = alphabet[@intCast((accum >> 12) & 0x3f)];
            dst_index += 2;
            if (padding) {
                dst[dst_index] = '=';
                dst[dst_index + 1] = '=';
                dst_index += 2;
            }
        },
        2 => {
            const accum = (@as(u24, src[src_index]) << 16) |
                (@as(u24, src[src_index + 1]) << 8);
            dst[dst_index] = alphabet[@intCast((accum >> 18) & 0x3f)];
            dst[dst_index + 1] = alphabet[@intCast((accum >> 12) & 0x3f)];
            dst[dst_index + 2] = alphabet[@intCast((accum >> 6) & 0x3f)];
            dst_index += 3;
            if (padding) {
                dst[dst_index] = '=';
                dst_index += 1;
            }
        },
        else => unreachable,
    }

    return dst[0..dst_index];
}

pub fn decode(src: []const u8, dst: []u8, padding: bool, variant: Variant) Error![]u8 {
    const needed = try maxDecodedLen(src.len);
    if (dst.len < needed) {
        return error.NoSpaceLeft;
    }

    var src_index: usize = 0;
    var dst_index: usize = 0;

    while (src_index + 4 <= src.len) {
        const current = src[src_index .. src_index + 4];
        if (current[2] == '=' or current[3] == '=') {
            if (!padding or src_index + 4 != src.len) {
                return error.InvalidBase64;
            }

            const first = try decodeValue(current[0], variant);
            const second = try decodeValue(current[1], variant);
            const third: u6 = if (current[2] == '=') 0 else try decodeValue(current[2], variant);
            const fourth: u6 = if (current[3] == '=') 0 else try decodeValue(current[3], variant);
            const accum = (@as(u24, first) << 18) |
                (@as(u24, second) << 12) |
                (@as(u24, third) << 6) |
                @as(u24, fourth);

            dst[dst_index] = @intCast((accum >> 16) & 0xff);
            dst_index += 1;

            if (current[2] == '=') {
                if (current[3] != '=') {
                    return error.InvalidBase64;
                }
                if ((accum & 0x0000ffff) != 0) {
                    return error.InvalidBase64;
                }
            } else {
                dst[dst_index] = @intCast((accum >> 8) & 0xff);
                dst_index += 1;
                if (current[3] == '=') {
                    if ((accum & 0x000000ff) != 0) {
                        return error.InvalidBase64;
                    }
                } else {
                    dst[dst_index] = @intCast(accum & 0xff);
                    dst_index += 1;
                }
            }

            return dst[0..dst_index];
        }

        const first = try decodeValue(current[0], variant);
        const second = try decodeValue(current[1], variant);
        const third = try decodeValue(current[2], variant);
        const fourth = try decodeValue(current[3], variant);
        const accum = (@as(u24, first) << 18) |
            (@as(u24, second) << 12) |
            (@as(u24, third) << 6) |
            @as(u24, fourth);

        dst[dst_index] = @intCast((accum >> 16) & 0xff);
        dst[dst_index + 1] = @intCast((accum >> 8) & 0xff);
        dst[dst_index + 2] = @intCast(accum & 0xff);
        dst_index += 3;
        src_index += 4;
    }

    const tail_len = src.len - src_index;
    if (tail_len == 0) {
        return dst[0..dst_index];
    }
    if (padding or tail_len == 1) {
        return error.InvalidBase64;
    }

    const first = try decodeValue(src[src_index], variant);
    const second = try decodeValue(src[src_index + 1], variant);
    var accum = (@as(u24, first) << 12) | (@as(u24, second) << 6);
    dst[dst_index] = @intCast((accum >> 10) & 0xff);
    dst_index += 1;

    if (tail_len == 2) {
        if ((accum & 0x03ff) != 0) {
            return error.InvalidBase64;
        }
        return dst[0..dst_index];
    }

    const third = try decodeValue(src[src_index + 2], variant);
    accum |= third;
    if ((accum & 0x0003) != 0) {
        return error.InvalidBase64;
    }
    dst[dst_index] = @intCast((accum >> 2) & 0xff);
    dst_index += 1;
    return dst[0..dst_index];
}

fn alphabetFor(variant: Variant) *const [64]u8 {
    return switch (variant) {
        .standard => "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
        .urlsafe => "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_",
        .imap => "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+,",
    };
}

fn decodeValue(ch: u8, variant: Variant) Error!u6 {
    return switch (ch) {
        'A'...'Z' => @intCast(ch - 'A'),
        'a'...'z' => @intCast(ch - 'a' + 26),
        '0'...'9' => @intCast(ch - '0' + 52),
        '+' => 62,
        '/' => if (variant == .standard) 63 else error.InvalidBase64,
        '-' => if (variant == .urlsafe) 62 else error.InvalidBase64,
        '_' => if (variant == .urlsafe) 63 else error.InvalidBase64,
        ',' => if (variant == .imap) 63 else error.InvalidBase64,
        else => error.InvalidBase64,
    };
}

test "base64 standard encoding matches Linux-style padded output" {
    var out: [8]u8 = undefined;
    const encoded = try encode("hi", &out, true, .standard);
    try std.testing.expectEqualStrings("aGk=", encoded);
}

test "base64 standard decoding round-trips padded input" {
    var out: [8]u8 = undefined;
    const decoded = try decode("aGk=", &out, true, .standard);
    try std.testing.expectEqualStrings("hi", decoded);
}

test "base64 urlsafe encoding swaps the variant alphabet and omits padding when requested" {
    var out: [8]u8 = undefined;
    const encoded = try encode(&[_]u8{ 0xfb, 0xff, 0xff }, &out, false, .urlsafe);
    try std.testing.expectEqualStrings("-___", encoded);
}

test "base64 imap decoding accepts comma as the variant-specific 63rd symbol" {
    var out: [8]u8 = undefined;
    const decoded = try decode("+,,,", &out, false, .imap);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xfb, 0xff, 0xff }, decoded);
}

test "base64 unpadded decode rejects a dangling single-character tail" {
    var out: [8]u8 = undefined;
    try std.testing.expectError(error.InvalidBase64, decode("A", &out, false, .standard));
}

test "base64 padded decode rejects misplaced trailing padding" {
    var out: [8]u8 = undefined;
    try std.testing.expectError(error.InvalidBase64, decode("AA=A", &out, true, .standard));
}

test "base64 decode rejects variant-specific alphabet drift" {
    var out: [8]u8 = undefined;
    try std.testing.expectError(error.InvalidBase64, decode("-___", &out, false, .standard));
    try std.testing.expectError(error.InvalidBase64, decode("+///", &out, false, .urlsafe));
    try std.testing.expectError(error.InvalidBase64, decode("+///", &out, false, .imap));
}

test "base64 length helpers mirror padded and unpadded Linux sizing rules" {
    try std.testing.expectEqual(@as(usize, 0), try maxEncodedLen(0));
    try std.testing.expectEqual(@as(usize, 2), try maxEncodedLen(1));
    try std.testing.expectEqual(@as(usize, 3), try maxEncodedLen(2));
    try std.testing.expectEqual(@as(usize, 4), try maxEncodedLen(3));
    try std.testing.expectEqual(@as(usize, 4), try encodedLen(1, true));
    try std.testing.expectEqual(@as(usize, 4), try encodedLen(2, true));
    try std.testing.expectEqual(@as(usize, 4), try encodedLen(3, true));
    try std.testing.expectEqual(@as(usize, 6), try maxDecodedLen(8));
}
