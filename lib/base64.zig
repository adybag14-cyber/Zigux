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

pub fn encodeStd(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {
    return encode(dst, src, padding, .std);
}

pub fn encodeUrlsafe(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {
    return encode(dst, src, padding, .urlsafe);
}

pub fn encodeImap(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {
    return encode(dst, src, padding, .imap);
}

pub fn encodeAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool, variant: Variant) EncodeAllocError![]u8 {
    const needed = chars(src.len, padding);
    var out = try allocator.alloc(u8, needed);
    errdefer allocator.free(out);

    const written = try encode(out, src, padding, variant);
    return out[0..written];
}

pub fn encodeStdAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool) EncodeAllocError![]u8 {
    return encodeAlloc(allocator, src, padding, .std);
}

pub fn encodeUrlsafeAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool) EncodeAllocError![]u8 {
    return encodeAlloc(allocator, src, padding, .urlsafe);
}

pub fn encodeImapAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool) EncodeAllocError![]u8 {
    return encodeAlloc(allocator, src, padding, .imap);
}

pub fn encodeSlice(dst: []u8, src: []const u8, padding: bool, variant: Variant) EncodeError![]u8 {
    const written = try encode(dst, src, padding, variant);
    return dst[0..written];
}

pub fn encodeStdSlice(dst: []u8, src: []const u8, padding: bool) EncodeError![]u8 {
    return encodeSlice(dst, src, padding, .std);
}

pub fn encodeUrlsafeSlice(dst: []u8, src: []const u8, padding: bool) EncodeError![]u8 {
    return encodeSlice(dst, src, padding, .urlsafe);
}

pub fn encodeImapSlice(dst: []u8, src: []const u8, padding: bool) EncodeError![]u8 {
    return encodeSlice(dst, src, padding, .imap);
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

pub fn decodeStd(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {
    return decode(dst, src, padding, .std);
}

pub fn decodeUrlsafe(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {
    return decode(dst, src, padding, .urlsafe);
}

pub fn decodeImap(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {
    return decode(dst, src, padding, .imap);
}

pub fn decodeAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool, variant: Variant) DecodeAllocError![]u8 {
    const exact_len = try bytes(src, padding, variant);
    var out = try allocator.alloc(u8, exact_len);
    errdefer allocator.free(out);

    const written = try decode(out, src, padding, variant);
    return out[0..written];
}

pub fn decodeStdAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool) DecodeAllocError![]u8 {
    return decodeAlloc(allocator, src, padding, .std);
}

pub fn decodeUrlsafeAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool) DecodeAllocError![]u8 {
    return decodeAlloc(allocator, src, padding, .urlsafe);
}

pub fn decodeImapAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool) DecodeAllocError![]u8 {
    return decodeAlloc(allocator, src, padding, .imap);
}

pub fn decodeSlice(dst: []u8, src: []const u8, padding: bool, variant: Variant) DecodeError![]u8 {
    const written = try decode(dst, src, padding, variant);
    return dst[0..written];
}

pub fn decodeStdSlice(dst: []u8, src: []const u8, padding: bool) DecodeError![]u8 {
    return decodeSlice(dst, src, padding, .std);
}

pub fn decodeUrlsafeSlice(dst: []u8, src: []const u8, padding: bool) DecodeError![]u8 {
    return decodeSlice(dst, src, padding, .urlsafe);
}

pub fn decodeImapSlice(dst: []u8, src: []const u8, padding: bool) DecodeError![]u8 {
    return decodeSlice(dst, src, padding, .imap);
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

fn expectExhaustivePaddedTailCanonicality(variant: Variant) !void {
    const alphabet = alphabetFor(variant);
    var padded_two_char_tail: [4]u8 = undefined;
    var padded_three_char_tail: [4]u8 = undefined;
    var one_byte_out: [1]u8 = undefined;
    var two_byte_out: [2]u8 = undefined;

    for (0..64) |raw_a| {
        const a: u8 = @intCast(raw_a);
        for (0..64) |raw_b| {
            const b: u8 = @intCast(raw_b);
            padded_two_char_tail[0] = alphabet[a];
            padded_two_char_tail[1] = alphabet[b];
            padded_two_char_tail[2] = '=';
            padded_two_char_tail[3] = '=';

            if ((b & 0x0f) == 0) {
                const expected = @as(u8, @intCast((@as(u16, a) << 2) | (@as(u16, b) >> 4)));
                try std.testing.expectEqual(@as(usize, 1), try bytes(padded_two_char_tail[0..], true, variant));
                try std.testing.expectEqual(@as(usize, 1), try decode(one_byte_out[0..], padded_two_char_tail[0..], true, variant));
                try std.testing.expectEqual(expected, one_byte_out[0]);
            } else {
                try std.testing.expectError(error.InvalidInput, bytes(padded_two_char_tail[0..], true, variant));
                try std.testing.expectError(error.InvalidInput, decode(one_byte_out[0..], padded_two_char_tail[0..], true, variant));
            }

            for (0..64) |raw_c| {
                const c: u8 = @intCast(raw_c);
                padded_three_char_tail[0] = alphabet[a];
                padded_three_char_tail[1] = alphabet[b];
                padded_three_char_tail[2] = alphabet[c];
                padded_three_char_tail[3] = '=';

                if ((c & 0x03) == 0) {
                    const expected = [_]u8{
                        @as(u8, @intCast((@as(u16, a) << 2) | (@as(u16, b) >> 4))),
                        @as(u8, @intCast(((@as(u16, b) & 0x0f) << 4) | (@as(u16, c) >> 2))),
                    };
                    try std.testing.expectEqual(@as(usize, 2), try bytes(padded_three_char_tail[0..], true, variant));
                    try std.testing.expectEqual(@as(usize, 2), try decode(two_byte_out[0..], padded_three_char_tail[0..], true, variant));
                    try std.testing.expectEqualSlices(u8, &expected, two_byte_out[0..]);
                } else {
                    try std.testing.expectError(error.InvalidInput, bytes(padded_three_char_tail[0..], true, variant));
                    try std.testing.expectError(error.InvalidInput, decode(two_byte_out[0..], padded_three_char_tail[0..], true, variant));
                }
            }
        }
    }
}

fn expectExhaustiveUnpaddedTailCanonicality(variant: Variant) !void {
    const alphabet = alphabetFor(variant);
    var two_char_tail: [2]u8 = undefined;
    var three_char_tail: [3]u8 = undefined;
    var one_byte_out: [1]u8 = undefined;
    var two_byte_out: [2]u8 = undefined;

    for (0..64) |raw_a| {
        const a: u8 = @intCast(raw_a);
        for (0..64) |raw_b| {
            const b: u8 = @intCast(raw_b);
            two_char_tail[0] = alphabet[a];
            two_char_tail[1] = alphabet[b];

            if ((b & 0x0f) == 0) {
                const expected = @as(u8, @intCast((@as(u16, a) << 2) | (@as(u16, b) >> 4)));
                try std.testing.expectEqual(@as(usize, 1), try bytes(two_char_tail[0..], false, variant));
                try std.testing.expectEqual(@as(usize, 1), try decode(one_byte_out[0..], two_char_tail[0..], false, variant));
                try std.testing.expectEqual(expected, one_byte_out[0]);
            } else {
                try std.testing.expectError(error.InvalidInput, bytes(two_char_tail[0..], false, variant));
                try std.testing.expectError(error.InvalidInput, decode(one_byte_out[0..], two_char_tail[0..], false, variant));
            }

            for (0..64) |raw_c| {
                const c: u8 = @intCast(raw_c);
                three_char_tail[0] = alphabet[a];
                three_char_tail[1] = alphabet[b];
                three_char_tail[2] = alphabet[c];

                if ((c & 0x03) == 0) {
                    const expected = [_]u8{
                        @as(u8, @intCast((@as(u16, a) << 2) | (@as(u16, b) >> 4))),
                        @as(u8, @intCast(((@as(u16, b) & 0x0f) << 4) | (@as(u16, c) >> 2))),
                    };
                    try std.testing.expectEqual(@as(usize, 2), try bytes(three_char_tail[0..], false, variant));
                    try std.testing.expectEqual(@as(usize, 2), try decode(two_byte_out[0..], three_char_tail[0..], false, variant));
                    try std.testing.expectEqualSlices(u8, &expected, two_byte_out[0..]);
                } else {
                    try std.testing.expectError(error.InvalidInput, bytes(three_char_tail[0..], false, variant));
                    try std.testing.expectError(error.InvalidInput, decode(two_byte_out[0..], three_char_tail[0..], false, variant));
                }
            }
        }
    }
}

fn expectExhaustiveReverseMapClassification(variant: Variant) !void {
    const alphabet = alphabetFor(variant);
    const map = reverseMap(variant);
    var expected_lookup = [_]i8{invalid_reverse_value} ** 256;

    for (alphabet, 0..) |ch, idx| {
        expected_lookup[ch] = @as(i8, @intCast(idx));
    }

    for (0..256) |raw_ch| {
        const ch: u8 = @intCast(raw_ch);
        const expected = expected_lookup[ch];
        try std.testing.expectEqual(expected, map[ch]);

        if (expected < 0) {
            try std.testing.expectError(error.InvalidInput, decodeMapValue(map, ch));
        } else {
            try std.testing.expectEqual(@as(u6, @intCast(expected)), try decodeMapValue(map, ch));
        }
    }
}

fn expectExhaustiveEncodeShortTailCanonicality(variant: Variant, padding: bool) !void {
    const alphabet = alphabetFor(variant);
    var one_byte_input: [1]u8 = undefined;
    var two_byte_input: [2]u8 = undefined;
    var encoded: [4]u8 = undefined;
    var decoded_one_byte: [1]u8 = undefined;
    var decoded_two_byte: [2]u8 = undefined;

    for (0..256) |raw_first| {
        const first: u8 = @intCast(raw_first);
        one_byte_input[0] = first;

        const one_byte_expected = [_]u8{
            alphabet[first >> 2],
            alphabet[(first & 0x03) << 4],
            '=',
            '=',
        };
        const one_byte_written = try encode(encoded[0..], one_byte_input[0..], padding, variant);
        if (padding) {
            try std.testing.expectEqual(@as(usize, 4), one_byte_written);
            try std.testing.expectEqualSlices(u8, one_byte_expected[0..], encoded[0..one_byte_written]);
        } else {
            try std.testing.expectEqual(@as(usize, 2), one_byte_written);
            try std.testing.expectEqualSlices(u8, one_byte_expected[0..2], encoded[0..one_byte_written]);
        }
        try std.testing.expectEqual(@as(usize, 1), try bytes(encoded[0..one_byte_written], padding, variant));
        const one_byte_decoded_len = try decode(decoded_one_byte[0..], encoded[0..one_byte_written], padding, variant);
        try std.testing.expectEqual(@as(usize, 1), one_byte_decoded_len);
        try std.testing.expectEqualSlices(u8, one_byte_input[0..], decoded_one_byte[0..one_byte_decoded_len]);

        for (0..256) |raw_second| {
            const second: u8 = @intCast(raw_second);
            two_byte_input[0] = first;
            two_byte_input[1] = second;

            const two_byte_expected = [_]u8{
                alphabet[first >> 2],
                alphabet[((first & 0x03) << 4) | (second >> 4)],
                alphabet[(second & 0x0f) << 2],
                '=',
            };
            const two_byte_written = try encode(encoded[0..], two_byte_input[0..], padding, variant);
            if (padding) {
                try std.testing.expectEqual(@as(usize, 4), two_byte_written);
                try std.testing.expectEqualSlices(u8, two_byte_expected[0..], encoded[0..two_byte_written]);
            } else {
                try std.testing.expectEqual(@as(usize, 3), two_byte_written);
                try std.testing.expectEqualSlices(u8, two_byte_expected[0..3], encoded[0..two_byte_written]);
            }
            try std.testing.expectEqual(@as(usize, 2), try bytes(encoded[0..two_byte_written], padding, variant));
            const two_byte_decoded_len = try decode(decoded_two_byte[0..], encoded[0..two_byte_written], padding, variant);
            try std.testing.expectEqual(@as(usize, 2), two_byte_decoded_len);
            try std.testing.expectEqualSlices(u8, two_byte_input[0..], decoded_two_byte[0..two_byte_decoded_len]);
        }
    }
}

fn expectLengthSweepRoundTrip(variant: Variant, padding: bool) !void {
    var payload: [257]u8 = undefined;
    for (&payload, 0..) |*byte, idx| {
        byte.* = @as(u8, @intCast((idx * 73 + 19) % 256));
    }

    var encoded: [paddedChars(payload.len)]u8 = undefined;
    var decoded: [payload.len]u8 = undefined;

    for (0..(payload.len + 1)) |len| {
        const written = try encode(encoded[0..], payload[0..len], padding, variant);
        try std.testing.expectEqual(chars(len, padding), written);
        const exact_len = try bytes(encoded[0..written], padding, variant);
        try std.testing.expectEqual(len, exact_len);
        try std.testing.expect(exact_len <= maxDecodedBytes(written));
        try std.testing.expect(maxDecodedBytes(written) - exact_len < 3);

        const decoded_len = try decode(decoded[0..], encoded[0..written], padding, variant);
        try std.testing.expectEqual(len, decoded_len);
        try std.testing.expectEqualSlices(u8, payload[0..len], decoded[0..decoded_len]);
    }
}

fn expectWrapperRoundTripSweep(variant: Variant, padding: bool) !void {
    var payload: [33]u8 = undefined;
    for (&payload, 0..) |*byte, idx| {
        byte.* = @as(u8, @intCast((idx * 91 + 7) % 256));
    }

    var encoded_buf: [paddedChars(payload.len)]u8 = [_]u8{0xaa} ** paddedChars(payload.len);
    var decoded_buf: [payload.len]u8 = [_]u8{0xdd} ** payload.len;

    for (0..(payload.len + 1)) |len| {
        @memset(encoded_buf[0..], 0xaa);
        const encoded = try encodeSlice(encoded_buf[0..], payload[0..len], padding, variant);
        try std.testing.expectEqual(chars(len, padding), encoded.len);
        if (encoded.len < encoded_buf.len) {
            try std.testing.expectEqual(@as(u8, 0xaa), encoded_buf[encoded.len]);
        }

        const alloc_encoded = try encodeAlloc(std.testing.allocator, payload[0..len], padding, variant);
        defer std.testing.allocator.free(alloc_encoded);
        try std.testing.expectEqualSlices(u8, encoded, alloc_encoded);

        @memset(decoded_buf[0..], 0xdd);
        const decoded = try decodeSlice(decoded_buf[0..], encoded, padding, variant);
        try std.testing.expectEqual(len, decoded.len);
        try std.testing.expectEqualSlices(u8, payload[0..len], decoded);
        if (decoded.len < decoded_buf.len) {
            try std.testing.expectEqual(@as(u8, 0xdd), decoded_buf[decoded.len]);
        }

        const alloc_decoded = try decodeAlloc(std.testing.allocator, encoded, padding, variant);
        defer std.testing.allocator.free(alloc_decoded);
        try std.testing.expectEqualSlices(u8, payload[0..len], alloc_decoded);
    }
}

fn expectStdWrapperRoundTripSweep(padding: bool) !void {
    var payload: [33]u8 = undefined;
    for (&payload, 0..) |*byte, idx| {
        byte.* = @as(u8, @intCast((idx * 57 + 29) % 256));
    }

    var direct_encoded_buf: [paddedChars(payload.len)]u8 = [_]u8{0xbb} ** paddedChars(payload.len);
    var slice_encoded_buf: [paddedChars(payload.len)]u8 = [_]u8{0xcc} ** paddedChars(payload.len);
    var direct_decoded_buf: [payload.len]u8 = [_]u8{0xee} ** payload.len;
    var slice_decoded_buf: [payload.len]u8 = [_]u8{0xff} ** payload.len;

    for (0..(payload.len + 1)) |len| {
        @memset(direct_encoded_buf[0..], 0xbb);
        const direct_encoded_len = try encodeStd(direct_encoded_buf[0..], payload[0..len], padding);
        try std.testing.expectEqual(chars(len, padding), direct_encoded_len);
        if (direct_encoded_len < direct_encoded_buf.len) {
            try std.testing.expectEqual(@as(u8, 0xbb), direct_encoded_buf[direct_encoded_len]);
        }

        @memset(slice_encoded_buf[0..], 0xcc);
        const slice_encoded = try encodeStdSlice(slice_encoded_buf[0..], payload[0..len], padding);
        try std.testing.expectEqualSlices(u8, direct_encoded_buf[0..direct_encoded_len], slice_encoded);
        if (slice_encoded.len < slice_encoded_buf.len) {
            try std.testing.expectEqual(@as(u8, 0xcc), slice_encoded_buf[slice_encoded.len]);
        }

        const alloc_encoded = try encodeStdAlloc(std.testing.allocator, payload[0..len], padding);
        defer std.testing.allocator.free(alloc_encoded);
        try std.testing.expectEqualSlices(u8, direct_encoded_buf[0..direct_encoded_len], alloc_encoded);

        @memset(direct_decoded_buf[0..], 0xee);
        const direct_decoded_len = try decodeStd(direct_decoded_buf[0..], slice_encoded, padding);
        try std.testing.expectEqual(len, direct_decoded_len);
        try std.testing.expectEqualSlices(u8, payload[0..len], direct_decoded_buf[0..direct_decoded_len]);
        if (direct_decoded_len < direct_decoded_buf.len) {
            try std.testing.expectEqual(@as(u8, 0xee), direct_decoded_buf[direct_decoded_len]);
        }

        @memset(slice_decoded_buf[0..], 0xff);
        const slice_decoded = try decodeStdSlice(slice_decoded_buf[0..], slice_encoded, padding);
        try std.testing.expectEqualSlices(u8, payload[0..len], slice_decoded);
        if (slice_decoded.len < slice_decoded_buf.len) {
            try std.testing.expectEqual(@as(u8, 0xff), slice_decoded_buf[slice_decoded.len]);
        }

        const alloc_decoded = try decodeStdAlloc(std.testing.allocator, slice_encoded, padding);
        defer std.testing.allocator.free(alloc_decoded);
        try std.testing.expectEqualSlices(u8, payload[0..len], alloc_decoded);
    }
}

fn expectVariantConvenienceWrapperRoundTrip(variant: Variant, padding: bool) !void {
    const payload = [_]u8{ 0xfb, 0xff };
    const expected_encoded = switch (variant) {
        .urlsafe => if (padding) "-_8=" else "-_8",
        .imap => if (padding) "+,8=" else "+,8",
        .std => unreachable,
    };

    var direct_encoded_buf: [8]u8 = [_]u8{0xab} ** 8;
    var slice_encoded_buf: [8]u8 = [_]u8{0xbc} ** 8;
    var direct_decoded_buf: [3]u8 = [_]u8{0xcd} ** 3;
    var slice_decoded_buf: [3]u8 = [_]u8{0xde} ** 3;

    @memset(direct_encoded_buf[0..], 0xab);
    const direct_encoded_len = switch (variant) {
        .urlsafe => try encodeUrlsafe(direct_encoded_buf[0..], payload[0..], padding),
        .imap => try encodeImap(direct_encoded_buf[0..], payload[0..], padding),
        .std => unreachable,
    };
    try std.testing.expectEqualStrings(expected_encoded, direct_encoded_buf[0..direct_encoded_len]);
    try std.testing.expectEqual(@as(usize, expected_encoded.len), direct_encoded_len);
    try std.testing.expectEqual(@as(u8, 0xab), direct_encoded_buf[direct_encoded_len]);

    @memset(slice_encoded_buf[0..], 0xbc);
    const slice_encoded = switch (variant) {
        .urlsafe => try encodeUrlsafeSlice(slice_encoded_buf[0..], payload[0..], padding),
        .imap => try encodeImapSlice(slice_encoded_buf[0..], payload[0..], padding),
        .std => unreachable,
    };
    try std.testing.expectEqualStrings(expected_encoded, slice_encoded);
    try std.testing.expectEqual(@as(u8, 0xbc), slice_encoded_buf[slice_encoded.len]);

    const alloc_encoded = switch (variant) {
        .urlsafe => try encodeUrlsafeAlloc(std.testing.allocator, payload[0..], padding),
        .imap => try encodeImapAlloc(std.testing.allocator, payload[0..], padding),
        .std => unreachable,
    };
    defer std.testing.allocator.free(alloc_encoded);
    try std.testing.expectEqualStrings(expected_encoded, alloc_encoded);

    @memset(direct_decoded_buf[0..], 0xcd);
    const direct_decoded_len = switch (variant) {
        .urlsafe => try decodeUrlsafe(direct_decoded_buf[0..], expected_encoded, padding),
        .imap => try decodeImap(direct_decoded_buf[0..], expected_encoded, padding),
        .std => unreachable,
    };
    try std.testing.expectEqual(@as(usize, payload.len), direct_decoded_len);
    try std.testing.expectEqualSlices(u8, payload[0..], direct_decoded_buf[0..direct_decoded_len]);
    try std.testing.expectEqual(@as(u8, 0xcd), direct_decoded_buf[direct_decoded_len]);

    @memset(slice_decoded_buf[0..], 0xde);
    const slice_decoded = switch (variant) {
        .urlsafe => try decodeUrlsafeSlice(slice_decoded_buf[0..], expected_encoded, padding),
        .imap => try decodeImapSlice(slice_decoded_buf[0..], expected_encoded, padding),
        .std => unreachable,
    };
    try std.testing.expectEqualSlices(u8, payload[0..], slice_decoded);
    try std.testing.expectEqual(@as(u8, 0xde), slice_decoded_buf[slice_decoded.len]);

    const alloc_decoded = switch (variant) {
        .urlsafe => try decodeUrlsafeAlloc(std.testing.allocator, expected_encoded, padding),
        .imap => try decodeImapAlloc(std.testing.allocator, expected_encoded, padding),
        .std => unreachable,
    };
    defer std.testing.allocator.free(alloc_decoded);
    try std.testing.expectEqualSlices(u8, payload[0..], alloc_decoded);
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

test "base64 standard and variant round-trips cover unpadded and binary payloads" {
    const one_byte = [_]u8{0xfb};
    const three_bytes = [_]u8{ 0xfb, 0xff, 0xff };
    const binary = [_]u8{ 0x00, 0xff, 0x10, 0x80 };

    var encoded: [16]u8 = undefined;
    var decoded: [16]u8 = undefined;

    const std_padded = try encode(encoded[0..], one_byte[0..], true, .std);
    try std.testing.expectEqualStrings("+w==", encoded[0..std_padded]);

    const std_unpadded = try encode(encoded[0..], one_byte[0..], false, .std);
    try std.testing.expectEqualStrings("+w", encoded[0..std_unpadded]);
    try std.testing.expectEqual(@as(usize, 1), try bytes(encoded[0..std_unpadded], false, .std));
    const std_decoded = try decode(decoded[0..], encoded[0..std_unpadded], false, .std);
    try std.testing.expectEqualSlices(u8, one_byte[0..], decoded[0..std_decoded]);

    const urlsafe_padded = try encode(encoded[0..], one_byte[0..], true, .urlsafe);
    try std.testing.expectEqualStrings("-w==", encoded[0..urlsafe_padded]);
    const urlsafe_decoded = try decode(decoded[0..], encoded[0..urlsafe_padded], true, .urlsafe);
    try std.testing.expectEqualSlices(u8, one_byte[0..], decoded[0..urlsafe_decoded]);

    const imap_unpadded = try encode(encoded[0..], three_bytes[0..], false, .imap);
    try std.testing.expectEqualStrings("+,,,", encoded[0..imap_unpadded]);
    const imap_decoded = try decode(decoded[0..], encoded[0..imap_unpadded], false, .imap);
    try std.testing.expectEqualSlices(u8, three_bytes[0..], decoded[0..imap_decoded]);

    const binary_unpadded = try encode(encoded[0..], binary[0..], false, .std);
    try std.testing.expectEqual(@as(usize, binary.len), try bytes(encoded[0..binary_unpadded], false, .std));
    const binary_decoded = try decode(decoded[0..], encoded[0..binary_unpadded], false, .std);
    try std.testing.expectEqualSlices(u8, binary[0..], decoded[0..binary_decoded]);
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

test "base64 standard convenience wrappers pin the common variant across direct, slice, and allocator paths" {
    var encoded_buf: [8]u8 = [_]u8{0xaa} ** 8;
    const encoded = try encodeStdSlice(encoded_buf[0..], "hi", true);
    try std.testing.expectEqualStrings("aGk=", encoded);
    try std.testing.expectEqual(@as(u8, 0xaa), encoded_buf[encoded.len]);

    const encoded_alloc = try encodeStdAlloc(std.testing.allocator, "hi", false);
    defer std.testing.allocator.free(encoded_alloc);
    try std.testing.expectEqualStrings("aGk", encoded_alloc);

    var direct_encoded_buf: [8]u8 = [_]u8{0xbb} ** 8;
    const direct_encoded_len = try encodeStd(direct_encoded_buf[0..], "f", true);
    try std.testing.expectEqualStrings("Zg==", direct_encoded_buf[0..direct_encoded_len]);
    try std.testing.expectEqual(@as(u8, 0xbb), direct_encoded_buf[direct_encoded_len]);

    var decoded_buf: [8]u8 = [_]u8{0xdd} ** 8;
    const decoded = try decodeStdSlice(decoded_buf[0..], "aGk=", true);
    try std.testing.expectEqualStrings("hi", decoded);
    try std.testing.expectEqual(@as(u8, 0xdd), decoded_buf[decoded.len]);

    const decoded_alloc = try decodeStdAlloc(std.testing.allocator, "aGk", false);
    defer std.testing.allocator.free(decoded_alloc);
    try std.testing.expectEqualStrings("hi", decoded_alloc);

    var direct_decoded_buf: [8]u8 = [_]u8{0xee} ** 8;
    const direct_decoded_len = try decodeStd(direct_decoded_buf[0..], "Zg==", true);
    try std.testing.expectEqualStrings("f", direct_decoded_buf[0..direct_decoded_len]);
    try std.testing.expectEqual(@as(u8, 0xee), direct_decoded_buf[direct_decoded_len]);
}

test "base64 urlsafe and imap convenience wrappers pin their variant across direct, slice, and allocator paths" {
    try expectVariantConvenienceWrapperRoundTrip(.urlsafe, true);
    try expectVariantConvenienceWrapperRoundTrip(.urlsafe, false);
    try expectVariantConvenienceWrapperRoundTrip(.imap, true);
    try expectVariantConvenienceWrapperRoundTrip(.imap, false);
}

test "base64 generic slice and allocator wrappers sweep exact round-trips across variants and padding modes" {
    try expectWrapperRoundTripSweep(.std, true);
    try expectWrapperRoundTripSweep(.std, false);
    try expectWrapperRoundTripSweep(.urlsafe, true);
    try expectWrapperRoundTripSweep(.urlsafe, false);
    try expectWrapperRoundTripSweep(.imap, true);
    try expectWrapperRoundTripSweep(.imap, false);
}

test "base64 standard wrappers sweep exact round-trips across payload lengths" {
    try expectStdWrapperRoundTripSweep(true);
    try expectStdWrapperRoundTripSweep(false);
}

test "base64 allocator wrappers allocate exact encoded and decoded lengths" {
    const encoded = try encodeAlloc(std.testing.allocator, "hi", true, .std);
    defer std.testing.allocator.free(encoded);
    try std.testing.expectEqualStrings("aGk=", encoded);

    const decoded = try decodeAlloc(std.testing.allocator, "-___", false, .urlsafe);
    defer std.testing.allocator.free(decoded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xfb, 0xff, 0xff }, decoded);
}

test "base64 exact-buffer slice wrappers return the written view" {
    var encoded_buf: [8]u8 = [_]u8{0xaa} ** 8;
    const encoded = try encodeSlice(encoded_buf[0..], "hi", true, .std);
    try std.testing.expectEqualStrings("aGk=", encoded);
    try std.testing.expectEqual(@as(u8, 0xaa), encoded_buf[encoded.len]);

    var decoded_buf: [8]u8 = [_]u8{0xdd} ** 8;
    const decoded = try decodeSlice(decoded_buf[0..], "-___", false, .urlsafe);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xfb, 0xff, 0xff }, decoded);
    try std.testing.expectEqual(@as(u8, 0xdd), decoded_buf[decoded.len]);
}

test "base64 slice wrappers preserve destination-too-small errors" {
    var encoded: [3]u8 = [_]u8{0xaa} ** 3;
    try std.testing.expectError(error.DestinationTooSmall, encodeSlice(encoded[0..], "hi", true, .std));
    try std.testing.expectEqual(@as(u8, 0xaa), encoded[0]);

    var decoded: [1]u8 = [_]u8{0xdd} ** 1;
    try std.testing.expectError(error.DestinationTooSmall, decodeSlice(decoded[0..], "aGk=", true, .std));
    try std.testing.expectEqual(@as(u8, 0xdd), decoded[0]);
}

test "base64 standard convenience wrappers preserve destination-too-small errors" {
    var encoded: [1]u8 = [_]u8{0xaa} ** 1;
    try std.testing.expectError(error.DestinationTooSmall, encodeStd(encoded[0..], "f", true));
    try std.testing.expectEqual(@as(u8, 0xaa), encoded[0]);

    var decoded: [1]u8 = [_]u8{0xdd} ** 1;
    try std.testing.expectError(error.DestinationTooSmall, decodeStd(decoded[0..], "Zm8=", true));
    try std.testing.expectEqual(@as(u8, 0xdd), decoded[0]);
}

test "base64 urlsafe and imap convenience wrappers preserve destination-too-small errors" {
    const payload = [_]u8{ 0xfb, 0xff };

    var urlsafe_encoded: [2]u8 = [_]u8{0xaa} ** 2;
    try std.testing.expectError(error.DestinationTooSmall, encodeUrlsafe(urlsafe_encoded[0..], payload[0..], true));
    try std.testing.expectEqual(@as(u8, 0xaa), urlsafe_encoded[0]);

    var imap_encoded: [2]u8 = [_]u8{0xbb} ** 2;
    try std.testing.expectError(error.DestinationTooSmall, encodeImap(imap_encoded[0..], payload[0..], true));
    try std.testing.expectEqual(@as(u8, 0xbb), imap_encoded[0]);

    var urlsafe_decoded: [1]u8 = [_]u8{0xcc} ** 1;
    try std.testing.expectError(error.DestinationTooSmall, decodeUrlsafe(urlsafe_decoded[0..], "-_8=", true));
    try std.testing.expectEqual(@as(u8, 0xcc), urlsafe_decoded[0]);

    var imap_decoded: [1]u8 = [_]u8{0xdd} ** 1;
    try std.testing.expectError(error.DestinationTooSmall, decodeImap(imap_decoded[0..], "+,8=", true));
    try std.testing.expectEqual(@as(u8, 0xdd), imap_decoded[0]);
}

test "base64 reports exact destination-too-small errors" {
    var encoded: [3]u8 = [_]u8{0xaa} ** 3;
    try std.testing.expectError(error.DestinationTooSmall, encode(encoded[0..], "hi", true, .std));
    try std.testing.expectEqual(@as(u8, 0xaa), encoded[0]);

    var decoded: [1]u8 = [_]u8{0xdd} ** 1;
    try std.testing.expectError(error.DestinationTooSmall, decode(decoded[0..], "aGk=", true, .std));
    try std.testing.expectEqual(@as(u8, 0xdd), decoded[0]);
}

test "base64 rejects non-canonical tail bits for padded and unpadded input" {
    var out: [8]u8 = undefined;

    const one_byte_padded = try decode(out[0..], "AQ==", true, .std);
    try std.testing.expectEqual(@as(usize, 1), one_byte_padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{0x01}, out[0..one_byte_padded]);
    try std.testing.expectEqual(@as(usize, 1), try bytes("AQ==", true, .std));
    try std.testing.expectError(error.InvalidInput, bytes("AR==", true, .std));
    try std.testing.expectError(error.InvalidInput, decode(out[0..], "AR==", true, .std));

    const one_byte_unpadded = try decode(out[0..], "AQ", false, .std);
    try std.testing.expectEqual(@as(usize, 1), one_byte_unpadded);
    try std.testing.expectEqualSlices(u8, &[_]u8{0x01}, out[0..one_byte_unpadded]);
    try std.testing.expectEqual(@as(usize, 1), try bytes("AQ", false, .std));
    try std.testing.expectError(error.InvalidInput, bytes("AR", false, .std));
    try std.testing.expectError(error.InvalidInput, decode(out[0..], "AR", false, .std));

    const two_byte_padded = try decode(out[0..], "aGk=", true, .std);
    try std.testing.expectEqual(@as(usize, 2), two_byte_padded);
    try std.testing.expectEqualStrings("hi", out[0..two_byte_padded]);
    try std.testing.expectEqual(@as(usize, 2), try bytes("aGk=", true, .std));
    try std.testing.expectError(error.InvalidInput, bytes("aGl=", true, .std));
    try std.testing.expectError(error.InvalidInput, decode(out[0..], "aGl=", true, .std));

    const two_byte_unpadded = try decode(out[0..], "aGk", false, .std);
    try std.testing.expectEqual(@as(usize, 2), two_byte_unpadded);
    try std.testing.expectEqualStrings("hi", out[0..two_byte_unpadded]);
    try std.testing.expectEqual(@as(usize, 2), try bytes("aGk", false, .std));
    try std.testing.expectError(error.InvalidInput, bytes("aGl", false, .std));
    try std.testing.expectError(error.InvalidInput, decode(out[0..], "aGl", false, .std));
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

test "base64 decode exhaustively accepts only canonical padded short tails across variants" {
    try expectExhaustivePaddedTailCanonicality(.std);
    try expectExhaustivePaddedTailCanonicality(.urlsafe);
    try expectExhaustivePaddedTailCanonicality(.imap);
}

test "base64 decode exhaustively accepts only canonical unpadded short tails across variants" {
    try expectExhaustiveUnpaddedTailCanonicality(.std);
    try expectExhaustiveUnpaddedTailCanonicality(.urlsafe);
    try expectExhaustiveUnpaddedTailCanonicality(.imap);
}

test "base64 reverse maps exhaustively classify each shipped alphabet" {
    try expectExhaustiveReverseMapClassification(.std);
    try expectExhaustiveReverseMapClassification(.urlsafe);
    try expectExhaustiveReverseMapClassification(.imap);
}

test "base64 encode exhaustively emits canonical padded and unpadded short tails across variants" {
    try expectExhaustiveEncodeShortTailCanonicality(.std, true);
    try expectExhaustiveEncodeShortTailCanonicality(.std, false);
    try expectExhaustiveEncodeShortTailCanonicality(.urlsafe, true);
    try expectExhaustiveEncodeShortTailCanonicality(.urlsafe, false);
    try expectExhaustiveEncodeShortTailCanonicality(.imap, true);
    try expectExhaustiveEncodeShortTailCanonicality(.imap, false);
}

test "base64 length sweep keeps chars encode bytes and decode aligned across variants" {
    try expectLengthSweepRoundTrip(.std, true);
    try expectLengthSweepRoundTrip(.std, false);
    try expectLengthSweepRoundTrip(.urlsafe, true);
    try expectLengthSweepRoundTrip(.urlsafe, false);
    try expectLengthSweepRoundTrip(.imap, true);
    try expectLengthSweepRoundTrip(.imap, false);
}
