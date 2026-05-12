// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub const Variant = enum {
    std,
    urlsafe,
    imap,
};

pub const EncodeError = error{
    DestinationTooSmall,
};

pub const DecodeError = error{
    DestinationTooSmall,
    InvalidInput,
};

pub const EncodeAllocError = std.mem.Allocator.Error || EncodeError;
pub const DecodeAllocError = std.mem.Allocator.Error || DecodeError;

const ReverseMap = [256]i8;
const invalid_reverse_value: i8 = -1;

const std_table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
const urlsafe_table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
const imap_table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+,";

const std_reverse_map = initReverseMap('+', '/');
const urlsafe_reverse_map = initReverseMap('-', '_');
const imap_reverse_map = initReverseMap('+', ',');

pub fn paddedChars(nbytes: usize) usize {
    const full_groups = (nbytes / 3) * 4;
    return full_groups + @as(usize, if (nbytes % 3 == 0) 0 else 4);
}

pub fn chars(nbytes: usize, padding: bool) usize {
    if (padding) {
        return paddedChars(nbytes);
    }

    const full_groups = (nbytes / 3) * 4;
    return full_groups + @as(usize, switch (nbytes % 3) {
        0 => 0,
        1 => 2,
        2 => 3,
        else => unreachable,
    });
}

pub fn maxDecodedBytes(nchars: usize) usize {
    const full_quartets = (nchars / 4) * 3;
    return full_quartets + @as(usize, switch (nchars % 4) {
        0, 1 => 0,
        2 => 1,
        3 => 2,
        else => unreachable,
    });
}

pub fn bytes(src: []const u8, padding: bool, variant: Variant) DecodeError!usize {
    return decodedLength(src, padding, variant);
}

pub fn encode(dst: []u8, src: []const u8, padding: bool, variant: Variant) EncodeError!usize {
    const needed = chars(src.len, padding);
    if (dst.len < needed) {
        return error.DestinationTooSmall;
    }

    const alphabet = alphabetFor(variant);
    var src_index: usize = 0;
    var dst_index: usize = 0;

    while (src_index + 3 <= src.len) : (src_index += 3) {
        const accum = (@as(u32, src[src_index]) << 16) |
            (@as(u32, src[src_index + 1]) << 8) |
            @as(u32, src[src_index + 2]);

        dst[dst_index] = alphabet[(accum >> 18) & 0x3f];
        dst[dst_index + 1] = alphabet[(accum >> 12) & 0x3f];
        dst[dst_index + 2] = alphabet[(accum >> 6) & 0x3f];
        dst[dst_index + 3] = alphabet[accum & 0x3f];
        dst_index += 4;
    }

    switch (src.len - src_index) {
        0 => {},
        1 => {
            const accum = @as(u32, src[src_index]) << 16;
            dst[dst_index] = alphabet[(accum >> 18) & 0x3f];
            dst[dst_index + 1] = alphabet[(accum >> 12) & 0x3f];
            dst_index += 2;
            if (padding) {
                dst[dst_index] = '=';
                dst[dst_index + 1] = '=';
                dst_index += 2;
            }
        },
        2 => {
            const accum = (@as(u32, src[src_index]) << 16) |
                (@as(u32, src[src_index + 1]) << 8);
            dst[dst_index] = alphabet[(accum >> 18) & 0x3f];
            dst[dst_index + 1] = alphabet[(accum >> 12) & 0x3f];
            dst[dst_index + 2] = alphabet[(accum >> 6) & 0x3f];
            dst_index += 3;
            if (padding) {
                dst[dst_index] = '=';
                dst_index += 1;
            }
        },
        else => unreachable,
    }

    return dst_index;
}

pub fn encodeAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool, variant: Variant) EncodeAllocError![]u8 {
    const needed = chars(src.len, padding);
    var out = try allocator.alloc(u8, needed);
    errdefer allocator.free(out);

    const written = try encode(out, src, padding, variant);
    return out[0..written];
}

pub fn decode(dst: []u8, src: []const u8, padding: bool, variant: Variant) DecodeError!usize {
    const exact_len = try bytes(src, padding, variant);
    if (dst.len < exact_len) {
        return error.DestinationTooSmall;
    }

    const map = reverseMap(variant);
    var src_index: usize = 0;
    var dst_index: usize = 0;

    while (src_index + 4 <= src.len) : (src_index += 4) {
        const a = try decodeMapValue(map, src[src_index]);
        const b = try decodeMapValue(map, src[src_index + 1]);
        const third_char = src[src_index + 2];
        const fourth_char = src[src_index + 3];

        if (third_char == '=') {
            dst[dst_index] = @truncate((@as(u32, a) << 2) | (@as(u32, b) >> 4));
            dst_index += 1;
            return dst_index;
        }

        const c = try decodeMapValue(map, third_char);
        if (fourth_char == '=') {
            dst[dst_index] = @truncate((@as(u32, a) << 2) | (@as(u32, b) >> 4));
            dst[dst_index + 1] = @truncate((@as(u32, b) << 4) | (@as(u32, c) >> 2));
            dst_index += 2;
            return dst_index;
        }

        const d = try decodeMapValue(map, fourth_char);
        const value = (@as(u32, a) << 18) |
            (@as(u32, b) << 12) |
            (@as(u32, c) << 6) |
            @as(u32, d);

        dst[dst_index] = @truncate(value >> 16);
        dst[dst_index + 1] = @truncate(value >> 8);
        dst[dst_index + 2] = @truncate(value);
        dst_index += 3;
    }

    const tail = src.len - src_index;
    if (tail == 0) {
        return dst_index;
    }

    const a = try decodeMapValue(map, src[src_index]);
    const b = try decodeMapValue(map, src[src_index + 1]);

    dst[dst_index] = @truncate((@as(u32, a) << 2) | (@as(u32, b) >> 4));
    dst_index += 1;

    if (tail == 2) {
        return dst_index;
    }

    const c = try decodeMapValue(map, src[src_index + 2]);
    dst[dst_index] = @truncate((@as(u32, b) << 4) | (@as(u32, c) >> 2));
    dst_index += 1;
    return dst_index;
}

pub fn decodeAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool, variant: Variant) DecodeAllocError![]u8 {
    const exact_len = try bytes(src, padding, variant);
    var out = try allocator.alloc(u8, exact_len);
    errdefer allocator.free(out);

    const written = try decode(out, src, padding, variant);
    return out[0..written];
}

fn alphabetFor(variant: Variant) []const u8 {
    return switch (variant) {
        .std => std_table,
        .urlsafe => urlsafe_table,
        .imap => imap_table,
    };
}

fn reverseMap(variant: Variant) *const ReverseMap {
    return switch (variant) {
        .std => &std_reverse_map,
        .urlsafe => &urlsafe_reverse_map,
        .imap => &imap_reverse_map,
    };
}

fn initReverseMap(comptime ch62: u8, comptime ch63: u8) ReverseMap {
    var map = [_]i8{invalid_reverse_value} ** 256;

    inline for ('A'..('Z' + 1)) |ch| {
        map[ch] = @as(i8, @intCast(ch - 'A'));
    }
    inline for ('a'..('z' + 1)) |ch| {
        map[ch] = @as(i8, @intCast(ch - 'a' + 26));
    }
    inline for ('0'..('9' + 1)) |ch| {
        map[ch] = @as(i8, @intCast(ch - '0' + 52));
    }

    map[ch62] = 62;
    map[ch63] = 63;
    return map;
}

fn decodeMapValue(map: *const ReverseMap, ch: u8) DecodeError!u6 {
    const value = map[ch];
    if (value < 0) {
        return error.InvalidInput;
    }
    return @intCast(value);
}

fn decodedLength(src: []const u8, padding: bool, variant: Variant) DecodeError!usize {
    if (padding and src.len % 4 != 0) {
        return error.InvalidInput;
    }
    if (!padding and src.len % 4 == 1) {
        return error.InvalidInput;
    }

    const map = reverseMap(variant);
    var src_index: usize = 0;
    var out_len: usize = 0;

    while (src_index + 4 <= src.len) : (src_index += 4) {
        const a = try decodeMapValue(map, src[src_index]);
        const b = try decodeMapValue(map, src[src_index + 1]);
        const third_char = src[src_index + 2];
        const fourth_char = src[src_index + 3];

        if (third_char == '=') {
            if (!padding or fourth_char != '=' or src_index + 4 != src.len or (b & 0x0f) != 0) {
                return error.InvalidInput;
            }
            return out_len + 1;
        }

        const c = try decodeMapValue(map, third_char);
        if (fourth_char == '=') {
            if (!padding or src_index + 4 != src.len or (c & 0x03) != 0) {
                return error.InvalidInput;
            }
            return out_len + 2;
        }

        _ = a;
        _ = try decodeMapValue(map, fourth_char);
        out_len += 3;
    }

    const tail = src.len - src_index;
    if (tail == 0) {
        return out_len;
    }
    if (padding or tail == 1) {
        return error.InvalidInput;
    }

    _ = try decodeMapValue(map, src[src_index]);
    const b = try decodeMapValue(map, src[src_index + 1]);
    if (tail == 2) {
        if ((b & 0x0f) != 0) {
            return error.InvalidInput;
        }
        return out_len + 1;
    }

    const c = try decodeMapValue(map, src[src_index + 2]);
    if ((c & 0x03) != 0) {
        return error.InvalidInput;
    }
    return out_len + 2;
}

test "base64 standard encoding matches Linux-style padded output" {
    var out: [8]u8 = undefined;
    const written = try encode(out[0..], "hi", true, .std);
    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqualStrings("aGk=", out[0..written]);
}

test "base64 standard decoding round-trips padded input" {
    var out: [8]u8 = undefined;
    const written = try decode(out[0..], "aGk=", true, .std);
    try std.testing.expectEqual(@as(usize, 2), written);
    try std.testing.expectEqualStrings("hi", out[0..written]);
}

test "base64 urlsafe encoding swaps the variant alphabet and omits padding when requested" {
    var out: [8]u8 = undefined;
    const written = try encode(out[0..], &[_]u8{ 0xfb, 0xff, 0xff }, false, .urlsafe);
    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqualStrings("-___", out[0..written]);
}

test "base64 imap decoding accepts comma as the variant-specific 63rd symbol" {
    var out: [8]u8 = undefined;
    const written = try decode(out[0..], "+,,,", false, .imap);
    try std.testing.expectEqual(@as(usize, 3), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xfb, 0xff, 0xff }, out[0..written]);
}

test "base64 helpers keep padded and unpadded sizing explicit" {
    try std.testing.expectEqual(@as(usize, 0), paddedChars(0));
    try std.testing.expectEqual(@as(usize, 2), chars(1, false));
    try std.testing.expectEqual(@as(usize, 4), chars(1, true));
    try std.testing.expectEqual(@as(usize, 3), chars(2, false));
    try std.testing.expectEqual(@as(usize, 4), chars(2, true));
    try std.testing.expectEqual(@as(usize, 3), maxDecodedBytes(4));
    try std.testing.expectEqual(@as(usize, 2), try bytes("aGk=", true, .std));
    try std.testing.expectEqual(@as(usize, 2), try bytes("aGk", false, .std));
}

test "base64 allocator wrappers allocate exact encoded and decoded lengths" {
    const encoded = try encodeAlloc(std.testing.allocator, "hi", true, .std);
    defer std.testing.allocator.free(encoded);
    try std.testing.expectEqualStrings("aGk=", encoded);

    const decoded = try decodeAlloc(std.testing.allocator, "-___", false, .urlsafe);
    defer std.testing.allocator.free(decoded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xfb, 0xff, 0xff }, decoded);
}

test "base64 reports exact destination-too-small errors" {
    var encoded: [3]u8 = [_]u8{0xaa} ** 3;
    try std.testing.expectError(error.DestinationTooSmall, encode(encoded[0..], "hi", true, .std));
    try std.testing.expectEqual(@as(u8, 0xaa), encoded[0]);

    var decoded: [1]u8 = [_]u8{0xdd} ** 1;
    try std.testing.expectError(error.DestinationTooSmall, decode(decoded[0..], "aGk=", true, .std));
    try std.testing.expectEqual(@as(u8, 0xdd), decoded[0]);
}

test "base64 rejects malformed tails and variant drift through bytes and decode" {
    var out: [8]u8 = undefined;
    try std.testing.expectError(error.InvalidInput, bytes("A", false, .std));
    try std.testing.expectError(error.InvalidInput, decode(out[0..], "A", false, .std));
    try std.testing.expectError(error.InvalidInput, bytes("AA=A", true, .std));
    try std.testing.expectError(error.InvalidInput, decode(out[0..], "AA=A", true, .std));
    try std.testing.expectError(error.InvalidInput, bytes("-___", false, .std));
    try std.testing.expectError(error.InvalidInput, decode(out[0..], "-___", false, .std));
    try std.testing.expectError(error.InvalidInput, bytes("+///", false, .urlsafe));
    try std.testing.expectError(error.InvalidInput, decode(out[0..], "+///", false, .imap));
}
