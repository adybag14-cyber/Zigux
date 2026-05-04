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

const std_table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
const urlsafe_table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
const imap_table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+,";
const invalid_reverse_value: i8 = -1;

const std_reverse_map = initReverseMap('+', '/');
const urlsafe_reverse_map = initReverseMap('-', '_');
const imap_reverse_map = initReverseMap('+', ',');

pub fn chars(nbytes: usize, padding: bool) usize {
    const full_groups = (nbytes / 3) * 4;
    const remainder = nbytes % 3;

    if (padding) {
        return full_groups + (if (remainder == 0) @as(usize, 0) else @as(usize, 4));
    }

    return full_groups + switch (remainder) {
        0 => @as(usize, 0),
        1 => @as(usize, 2),
        2 => @as(usize, 3),
        else => unreachable,
    };
}

pub fn bytes(src: []const u8, padding: bool, variant: Variant) DecodeError!usize {
    return decodedLength(src, padding, variant);
}

pub fn encode(dst: []u8, src: []const u8, padding: bool, variant: Variant) EncodeError!usize {
    const needed = chars(src.len, padding);
    if (dst.len < needed) {
        return EncodeError.DestinationTooSmall;
    }

    const table = alphabet(variant);
    var out_index: usize = 0;
    var src_index: usize = 0;

    while (src_index + 3 <= src.len) : (src_index += 3) {
        const ac = (@as(u32, src[src_index]) << 16) |
            (@as(u32, src[src_index + 1]) << 8) |
            src[src_index + 2];
        dst[out_index] = table[ac >> 18];
        dst[out_index + 1] = table[(ac >> 12) & 0x3f];
        dst[out_index + 2] = table[(ac >> 6) & 0x3f];
        dst[out_index + 3] = table[ac & 0x3f];
        out_index += 4;
    }

    switch (src.len - src_index) {
        0 => {},
        1 => {
            const ac = @as(u32, src[src_index]) << 16;
            dst[out_index] = table[ac >> 18];
            dst[out_index + 1] = table[(ac >> 12) & 0x3f];
            out_index += 2;
            if (padding) {
                dst[out_index] = '=';
                dst[out_index + 1] = '=';
                out_index += 2;
            }
        },
        2 => {
            const ac = (@as(u32, src[src_index]) << 16) |
                (@as(u32, src[src_index + 1]) << 8);
            dst[out_index] = table[ac >> 18];
            dst[out_index + 1] = table[(ac >> 12) & 0x3f];
            dst[out_index + 2] = table[(ac >> 6) & 0x3f];
            out_index += 3;
            if (padding) {
                dst[out_index] = '=';
                out_index += 1;
            }
        },
        else => unreachable,
    }

    return out_index;
}

pub fn decode(dst: []u8, src: []const u8, padding: bool, variant: Variant) DecodeError!usize {
    const exact_len = try bytes(src, padding, variant);
    if (dst.len < exact_len) {
        return DecodeError.DestinationTooSmall;
    }

    const map = reverseMap(variant);
    var out_index: usize = 0;
    var src_index: usize = 0;

    while (src_index + 4 <= src.len) : (src_index += 4) {
        const a = try decodeValueFromMap(map, src[src_index]);
        const b = try decodeValueFromMap(map, src[src_index + 1]);
        const third_char = src[src_index + 2];
        const fourth_char = src[src_index + 3];

        if (third_char == '=' or fourth_char == '=') {
            const tail_src = if (third_char == '=')
                src[src_index .. src_index + 2]
            else
                src[src_index .. src_index + 3];
            out_index += try decodeTailFromMap(dst[out_index..], tail_src, map);
            return out_index;
        }

        const c = try decodeValueFromMap(map, third_char);
        const d = try decodeValueFromMap(map, fourth_char);

        const value = (@as(u32, a) << 18) |
            (@as(u32, b) << 12) |
            (@as(u32, c) << 6) |
            @as(u32, d);
        dst[out_index] = @truncate(value >> 16);
        dst[out_index + 1] = @truncate(value >> 8);
        dst[out_index + 2] = @truncate(value);
        out_index += 3;
    }

    const tail = src.len - src_index;
    if (tail == 0) {
        return out_index;
    }
    out_index += try decodeTailFromMap(dst[out_index..], src[src_index..], map);
    return out_index;
}

fn alphabet(variant: Variant) []const u8 {
    return switch (variant) {
        .std => std_table,
        .urlsafe => urlsafe_table,
        .imap => imap_table,
    };
}

fn reverseMap(variant: Variant) *const [256]i8 {
    return switch (variant) {
        .std => &std_reverse_map,
        .urlsafe => &urlsafe_reverse_map,
        .imap => &imap_reverse_map,
    };
}

fn initReverseMap(comptime ch_62: u8, comptime ch_63: u8) [256]i8 {
    var map = [_]i8{invalid_reverse_value} ** 256;

    for ('A'..'Z' + 1) |value| {
        map[value] = @intCast(value - 'A');
    }
    for ('a'..'z' + 1) |value| {
        map[value] = @intCast(value - 'a' + 26);
    }
    for ('0'..'9' + 1) |value| {
        map[value] = @intCast(value - '0' + 52);
    }

    map[ch_62] = 62;
    map[ch_63] = 63;
    return map;
}

fn decodedLength(src: []const u8, padding: bool, variant: Variant) DecodeError!usize {
    const map = reverseMap(variant);
    var out_len: usize = 0;
    var src_index: usize = 0;

    while (src_index + 4 <= src.len) : (src_index += 4) {
        const quartet = src[src_index .. src_index + 4];
        const a = decodeValueFromMap(map, quartet[0]) catch return DecodeError.InvalidInput;
        const b = decodeValueFromMap(map, quartet[1]) catch return DecodeError.InvalidInput;
        _ = a;
        _ = b;

        const c = quartet[2];
        const d = quartet[3];

        if (c == '=' or d == '=') {
            if (!padding or src_index + 4 != src.len or d != '=') {
                return DecodeError.InvalidInput;
            }

            if (c == '=') {
                out_len += try validateTailFromMap(src[src_index .. src_index + 2], map);
            } else {
                _ = decodeValueFromMap(map, c) catch return DecodeError.InvalidInput;
                out_len += try validateTailFromMap(src[src_index .. src_index + 3], map);
            }
            return out_len;
        }

        _ = decodeValueFromMap(map, c) catch return DecodeError.InvalidInput;
        _ = decodeValueFromMap(map, d) catch return DecodeError.InvalidInput;
        out_len += 3;
    }

    const tail = src.len - src_index;
    if (tail == 0) {
        return out_len;
    }
    if (padding or tail == 1) {
        return DecodeError.InvalidInput;
    }
    return out_len + try validateTailFromMap(src[src_index..], map);
}

fn decodeTail(dst: []u8, src: []const u8, variant: Variant) DecodeError!usize {
    return decodeTailFromMap(dst, src, reverseMap(variant));
}

fn decodeTailFromMap(dst: []u8, src: []const u8, map: *const [256]i8) DecodeError!usize {
    if (src.len < 2 or src.len > 3) {
        return DecodeError.InvalidInput;
    }

    const needed: usize = if (src.len == 2) 1 else 2;
    if (dst.len < needed) {
        return DecodeError.DestinationTooSmall;
    }

    const a = try decodeValueFromMap(map, src[0]);
    const b = try decodeValueFromMap(map, src[1]);
    var value = (@as(u32, a) << 12) | (@as(u32, b) << 6);

    if (src.len == 2) {
        if ((value & 0x3ff) != 0) {
            return DecodeError.InvalidInput;
        }
        dst[0] = @truncate(value >> 10);
        return 1;
    }

    const c = try decodeValueFromMap(map, src[2]);
    value |= @as(u32, c);
    if ((value & 0x3) != 0) {
        return DecodeError.InvalidInput;
    }
    dst[0] = @truncate(value >> 10);
    dst[1] = @truncate(value >> 2);
    return 2;
}

fn validateTail(src: []const u8, variant: Variant) DecodeError!usize {
    return validateTailFromMap(src, reverseMap(variant));
}

fn validateTailFromMap(src: []const u8, map: *const [256]i8) DecodeError!usize {
    var scratch: [2]u8 = undefined;
    return decodeTailFromMap(scratch[0..], src, map);
}

fn decodeValueFromMap(map: *const [256]i8, ch: u8) DecodeError!u8 {
    const value = map[ch];
    if (value < 0) {
        return DecodeError.InvalidInput;
    }
    return @intCast(value);
}

fn decodeValue(ch: u8, variant: Variant) DecodeError!u8 {
    return decodeValueFromMap(reverseMap(variant), ch);
}

fn expectedDecodeValueForTest(ch: u8, variant: Variant) ?u8 {
    return switch (ch) {
        'A'...'Z' => ch - 'A',
        'a'...'z' => ch - 'a' + 26,
        '0'...'9' => ch - '0' + 52,
        '+' => switch (variant) {
            .std, .imap => 62,
            .urlsafe => null,
        },
        '/' => switch (variant) {
            .std => 63,
            .urlsafe, .imap => null,
        },
        '-' => switch (variant) {
            .urlsafe => 62,
            .std, .imap => null,
        },
        '_' => switch (variant) {
            .urlsafe => 63,
            .std, .imap => null,
        },
        ',' => switch (variant) {
            .imap => 63,
            .std, .urlsafe => null,
        },
        else => null,
    };
}

fn expectTailHelperRoundTrip(
    variant: Variant,
    tail: []const u8,
    padded_tail: []const u8,
    expected: []const u8,
) !void {
    var tail_out: [2]u8 = undefined;

    try std.testing.expectEqual(expected.len, try validateTail(tail, variant));
    try std.testing.expectEqual(expected.len, try decodeTail(tail_out[0..], tail, variant));
    try std.testing.expectEqualSlices(u8, expected, tail_out[0..expected.len]);

    try std.testing.expectEqual(expected.len, try bytes(padded_tail, true, variant));
}

fn expectPublicShortRoundTrip(variant: Variant, payload: []const u8, padding: bool) !void {
    var encoded: [4]u8 = undefined;
    var decoded: [2]u8 = undefined;

    const encoded_len = try encode(encoded[0..], payload, padding, variant);
    try std.testing.expectEqual(chars(payload.len, padding), encoded_len);
    try std.testing.expectEqual(payload.len, try bytes(encoded[0..encoded_len], padding, variant));

    const decoded_len = try decode(decoded[0..], encoded[0..encoded_len], padding, variant);
    try std.testing.expectEqual(payload.len, decoded_len);
    try std.testing.expectEqualSlices(u8, payload, decoded[0..decoded_len]);
}

fn expectExhaustiveTailCanonicality(variant: Variant) !void {
    const table = alphabet(variant);
    var two_char_tail: [2]u8 = undefined;
    var three_char_tail: [3]u8 = undefined;
    var one_byte_out: [1]u8 = undefined;
    var two_byte_out: [2]u8 = undefined;

    for (0..64) |raw_a| {
        const a: u8 = @intCast(raw_a);
        for (0..64) |raw_b| {
            const b: u8 = @intCast(raw_b);
            two_char_tail[0] = table[a];
            two_char_tail[1] = table[b];

            if ((b & 0x0f) == 0) {
                const expected = @as(u8, @intCast((@as(u16, a) << 2) | (@as(u16, b) >> 4)));
                try std.testing.expectEqual(@as(usize, 1), try validateTail(two_char_tail[0..], variant));
                try std.testing.expectEqual(@as(usize, 1), try bytes(two_char_tail[0..], false, variant));
                try std.testing.expectEqual(@as(usize, 1), try decodeTail(one_byte_out[0..], two_char_tail[0..], variant));
                try std.testing.expectEqual(expected, one_byte_out[0]);
                try std.testing.expectEqual(@as(usize, 1), try decode(one_byte_out[0..], two_char_tail[0..], false, variant));
                try std.testing.expectEqual(expected, one_byte_out[0]);
            } else {
                try std.testing.expectError(DecodeError.InvalidInput, validateTail(two_char_tail[0..], variant));
                try std.testing.expectError(DecodeError.InvalidInput, bytes(two_char_tail[0..], false, variant));
                try std.testing.expectError(DecodeError.InvalidInput, decodeTail(one_byte_out[0..], two_char_tail[0..], variant));
                try std.testing.expectError(DecodeError.InvalidInput, decode(one_byte_out[0..], two_char_tail[0..], false, variant));
            }

            for (0..64) |raw_c| {
                const c: u8 = @intCast(raw_c);
                three_char_tail[0] = table[a];
                three_char_tail[1] = table[b];
                three_char_tail[2] = table[c];

                if ((c & 0x03) == 0) {
                    const expected = [_]u8{
                        @as(u8, @intCast((@as(u16, a) << 2) | (@as(u16, b) >> 4))),
                        @as(u8, @intCast(((@as(u16, b) & 0x0f) << 4) | (@as(u16, c) >> 2))),
                    };
                    try std.testing.expectEqual(@as(usize, 2), try validateTail(three_char_tail[0..], variant));
                    try std.testing.expectEqual(@as(usize, 2), try bytes(three_char_tail[0..], false, variant));
                    try std.testing.expectEqual(@as(usize, 2), try decodeTail(two_byte_out[0..], three_char_tail[0..], variant));
                    try std.testing.expectEqualSlices(u8, &expected, two_byte_out[0..]);
                    try std.testing.expectEqual(@as(usize, 2), try decode(two_byte_out[0..], three_char_tail[0..], false, variant));
                    try std.testing.expectEqualSlices(u8, &expected, two_byte_out[0..]);
                } else {
                    try std.testing.expectError(DecodeError.InvalidInput, validateTail(three_char_tail[0..], variant));
                    try std.testing.expectError(DecodeError.InvalidInput, bytes(three_char_tail[0..], false, variant));
                    try std.testing.expectError(DecodeError.InvalidInput, decodeTail(two_byte_out[0..], three_char_tail[0..], variant));
                    try std.testing.expectError(DecodeError.InvalidInput, decode(two_byte_out[0..], three_char_tail[0..], false, variant));
                }
            }
        }
    }
}

fn expectExhaustivePaddedTailCanonicality(variant: Variant) !void {
    const table = alphabet(variant);
    var padded_two_char_tail: [4]u8 = undefined;
    var padded_three_char_tail: [4]u8 = undefined;
    var one_byte_out: [1]u8 = undefined;
    var two_byte_out: [2]u8 = undefined;

    for (0..64) |raw_a| {
        const a: u8 = @intCast(raw_a);
        for (0..64) |raw_b| {
            const b: u8 = @intCast(raw_b);
            padded_two_char_tail[0] = table[a];
            padded_two_char_tail[1] = table[b];
            padded_two_char_tail[2] = '=';
            padded_two_char_tail[3] = '=';

            if ((b & 0x0f) == 0) {
                const expected = @as(u8, @intCast((@as(u16, a) << 2) | (@as(u16, b) >> 4)));
                try std.testing.expectEqual(@as(usize, 1), try bytes(padded_two_char_tail[0..], true, variant));
                try std.testing.expectEqual(@as(usize, 1), try decode(one_byte_out[0..], padded_two_char_tail[0..], true, variant));
                try std.testing.expectEqual(expected, one_byte_out[0]);
            } else {
                try std.testing.expectError(DecodeError.InvalidInput, bytes(padded_two_char_tail[0..], true, variant));
                try std.testing.expectError(DecodeError.InvalidInput, decode(one_byte_out[0..], padded_two_char_tail[0..], true, variant));
            }

            for (0..64) |raw_c| {
                const c: u8 = @intCast(raw_c);
                padded_three_char_tail[0] = table[a];
                padded_three_char_tail[1] = table[b];
                padded_three_char_tail[2] = table[c];
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
                    try std.testing.expectError(DecodeError.InvalidInput, bytes(padded_three_char_tail[0..], true, variant));
                    try std.testing.expectError(DecodeError.InvalidInput, decode(two_byte_out[0..], padded_three_char_tail[0..], true, variant));
                }
            }
        }
    }
}

test "chars matches padded and unpadded output sizes" {
    try std.testing.expectEqual(@as(usize, 0), chars(0, true));
    try std.testing.expectEqual(@as(usize, 4), chars(1, true));
    try std.testing.expectEqual(@as(usize, 4), chars(2, true));
    try std.testing.expectEqual(@as(usize, 4), chars(3, true));
    try std.testing.expectEqual(@as(usize, 8), chars(4, true));

    try std.testing.expectEqual(@as(usize, 0), chars(0, false));
    try std.testing.expectEqual(@as(usize, 2), chars(1, false));
    try std.testing.expectEqual(@as(usize, 3), chars(2, false));
    try std.testing.expectEqual(@as(usize, 4), chars(3, false));
    try std.testing.expectEqual(@as(usize, 6), chars(4, false));
}

test "bytes reports decoded output sizes and rejects malformed input" {
    try std.testing.expectEqual(@as(usize, 0), try bytes("", true, .std));
    try std.testing.expectEqual(@as(usize, 1), try bytes("Zg==", true, .std));
    try std.testing.expectEqual(@as(usize, 2), try bytes("Zm8", false, .std));
    try std.testing.expectEqual(@as(usize, 5), try bytes("APv_f4A", false, .urlsafe));
    try std.testing.expectEqual(@as(usize, 5), try bytes("APv,f4A", false, .imap));

    try std.testing.expectError(DecodeError.InvalidInput, bytes("Zg", true, .std));
    try std.testing.expectError(DecodeError.InvalidInput, bytes("Zm9v====", true, .std));
    try std.testing.expectError(DecodeError.InvalidInput, bytes("Zg==", false, .urlsafe));
}

test "encode covers standard and variant alphabets" {
    var std_buf: [16]u8 = undefined;
    var std_padded_buf: [16]u8 = undefined;
    var url_buf: [16]u8 = undefined;
    var url_padded_buf: [16]u8 = undefined;
    var imap_buf: [16]u8 = undefined;
    var imap_padded_buf: [16]u8 = undefined;
    const sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };

    const std_len = try encode(std_buf[0..], &sample, false, .std);
    const std_padded_len = try encode(std_padded_buf[0..], &sample, true, .std);
    const url_len = try encode(url_buf[0..], &sample, false, .urlsafe);
    const url_padded_len = try encode(url_padded_buf[0..], &sample, true, .urlsafe);
    const imap_len = try encode(imap_buf[0..], &sample, false, .imap);
    const imap_padded_len = try encode(imap_padded_buf[0..], &sample, true, .imap);

    try std.testing.expectEqualStrings("APv/f4A", std_buf[0..std_len]);
    try std.testing.expectEqualStrings("APv/f4A=", std_padded_buf[0..std_padded_len]);
    try std.testing.expectEqualStrings("APv_f4A", url_buf[0..url_len]);
    try std.testing.expectEqualStrings("APv_f4A=", url_padded_buf[0..url_padded_len]);
    try std.testing.expectEqualStrings("APv,f4A", imap_buf[0..imap_len]);
    try std.testing.expectEqualStrings("APv,f4A=", imap_padded_buf[0..imap_padded_len]);
}

test "encode accepts exact-fit buffers and rejects one-byte-short buffers" {
    const sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };
    const exact_len = chars(sample.len, true);

    var exact_buf: [8]u8 = undefined;
    const written = try encode(exact_buf[0..exact_len], &sample, true, .std);
    try std.testing.expectEqual(exact_len, written);
    try std.testing.expectEqualStrings("APv/f4A=", exact_buf[0..written]);

    var short_buf: [7]u8 = undefined;
    try std.testing.expectError(EncodeError.DestinationTooSmall, encode(short_buf[0..], &sample, true, .std));
}

test "decode covers padded, unpadded, and variant inputs" {
    var out: [16]u8 = undefined;
    var variant_out: [8]u8 = undefined;

    const padded_len = try decode(out[0..], "SGVsbG8sIHdvcmxkIQ==", true, .std);
    try std.testing.expectEqualStrings("Hello, world!", out[0..padded_len]);

    const unpadded_len = try decode(out[0..], "Zm9vYmFy", false, .std);
    try std.testing.expectEqualStrings("foobar", out[0..unpadded_len]);

    const sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };
    const url_len = try decode(variant_out[0..], "APv_f4A", false, .urlsafe);
    try std.testing.expectEqualSlices(u8, &sample, variant_out[0..url_len]);

    const url_padded_len = try decode(variant_out[0..], "APv_f4A=", true, .urlsafe);
    try std.testing.expectEqualSlices(u8, &sample, variant_out[0..url_padded_len]);

    const imap_len = try decode(variant_out[0..], "APv,f4A", false, .imap);
    try std.testing.expectEqualSlices(u8, &sample, variant_out[0..imap_len]);

    const imap_padded_len = try decode(variant_out[0..], "APv,f4A=", true, .imap);
    try std.testing.expectEqualSlices(u8, &sample, variant_out[0..imap_padded_len]);
}

test "decode and bytes cover one-byte and two-byte variant tails" {
    const urlsafe_one = [_]u8{0xfb};
    const urlsafe_two = [_]u8{ 0xff, 0xf0 };
    var out: [4]u8 = undefined;

    try std.testing.expectEqual(@as(usize, 1), try bytes("-w", false, .urlsafe));
    try std.testing.expectEqual(@as(usize, 1), try bytes("-w==", true, .urlsafe));
    try std.testing.expectEqual(@as(usize, 1), try decode(out[0..], "-w", false, .urlsafe));
    try std.testing.expectEqualSlices(u8, &urlsafe_one, out[0..1]);
    try std.testing.expectEqual(@as(usize, 1), try decode(out[0..], "-w==", true, .urlsafe));
    try std.testing.expectEqualSlices(u8, &urlsafe_one, out[0..1]);

    try std.testing.expectEqual(@as(usize, 2), try bytes("__A", false, .urlsafe));
    try std.testing.expectEqual(@as(usize, 2), try bytes("__A=", true, .urlsafe));
    try std.testing.expectEqual(@as(usize, 2), try decode(out[0..], "__A", false, .urlsafe));
    try std.testing.expectEqualSlices(u8, &urlsafe_two, out[0..2]);
    try std.testing.expectEqual(@as(usize, 2), try decode(out[0..], "__A=", true, .urlsafe));
    try std.testing.expectEqualSlices(u8, &urlsafe_two, out[0..2]);

    try std.testing.expectEqual(@as(usize, 2), try bytes(",,A", false, .imap));
    try std.testing.expectEqual(@as(usize, 2), try bytes(",,A=", true, .imap));
    try std.testing.expectEqual(@as(usize, 2), try decode(out[0..], ",,A", false, .imap));
    try std.testing.expectEqualSlices(u8, &urlsafe_two, out[0..2]);
    try std.testing.expectEqual(@as(usize, 2), try decode(out[0..], ",,A=", true, .imap));
    try std.testing.expectEqualSlices(u8, &urlsafe_two, out[0..2]);
}

test "decodeTail and validateTail preserve canonical tail semantics across variants" {
    var invalid_std_tail_buf: [2]u8 = undefined;
    var invalid_urlsafe_tail_buf: [2]u8 = undefined;
    var invalid_imap_tail_buf: [2]u8 = undefined;

    try expectTailHelperRoundTrip(.std, "Zg", "Zg==", "f");
    try expectTailHelperRoundTrip(.std, "Zm8", "Zm8=", "fo");
    try expectTailHelperRoundTrip(.urlsafe, "-w", "-w==", &[_]u8{0xfb});
    try expectTailHelperRoundTrip(.urlsafe, "__A", "__A=", &[_]u8{ 0xff, 0xf0 });
    try expectTailHelperRoundTrip(.imap, "+w", "+w==", &[_]u8{0xfb});
    try expectTailHelperRoundTrip(.imap, ",,A", ",,A=", &[_]u8{ 0xff, 0xf0 });

    try std.testing.expectError(DecodeError.InvalidInput, validateTail("Z=", .std));
    try std.testing.expectError(DecodeError.InvalidInput, validateTail("=m8", .std));
    try std.testing.expectError(DecodeError.InvalidInput, decodeTail(invalid_std_tail_buf[0..], "Z=", .std));
    try std.testing.expectError(DecodeError.InvalidInput, decodeTail(invalid_urlsafe_tail_buf[0..], "__B", .urlsafe));
    try std.testing.expectError(DecodeError.InvalidInput, decodeTail(invalid_imap_tail_buf[0..], ",,B", .imap));
}

test "decodeTail reports destination bounds for short tails across variants" {
    var empty: [0]u8 = .{};
    var one: [1]u8 = undefined;

    try std.testing.expectError(DecodeError.DestinationTooSmall, decodeTail(empty[0..], "Zg", .std));
    try std.testing.expectError(DecodeError.DestinationTooSmall, decodeTail(one[0..], "Zm8", .std));
    try std.testing.expectError(DecodeError.DestinationTooSmall, decodeTail(empty[0..], "-w", .urlsafe));
    try std.testing.expectError(DecodeError.DestinationTooSmall, decodeTail(one[0..], "__A", .urlsafe));
    try std.testing.expectError(DecodeError.DestinationTooSmall, decodeTail(empty[0..], "+w", .imap));
    try std.testing.expectError(DecodeError.DestinationTooSmall, decodeTail(one[0..], ",,A", .imap));
}

test "decode accepts exact-fit buffers and rejects one-byte-short buffers" {
    const encoded = "APv_f4A";
    const exact_len = try bytes(encoded, false, .urlsafe);
    const expected = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };

    var exact_buf: [5]u8 = undefined;
    const written = try decode(exact_buf[0..exact_len], encoded, false, .urlsafe);
    try std.testing.expectEqual(exact_len, written);
    try std.testing.expectEqualSlices(u8, &expected, exact_buf[0..written]);

    var short_buf: [4]u8 = undefined;
    try std.testing.expectError(DecodeError.DestinationTooSmall, decode(short_buf[0..], encoded, false, .urlsafe));
}

test "decode rejects malformed input and reports destination bounds" {
    var small: [2]u8 = undefined;
    var buf: [16]u8 = undefined;

    try std.testing.expectError(DecodeError.DestinationTooSmall, decode(small[0..], "Zm9v", false, .std));
    try std.testing.expectError(DecodeError.InvalidInput, decode(buf[0..], "Zg", true, .std));
    try std.testing.expectError(DecodeError.InvalidInput, decode(buf[0..], "Zg=!", true, .std));
    try std.testing.expectError(DecodeError.InvalidInput, decode(buf[0..], "Zm9v====", false, .std));
    try std.testing.expectError(DecodeError.InvalidInput, decode(buf[0..], "Zg==", false, .urlsafe));
}

test "decode and bytes reject non-canonical tail bits across variants" {
    var buf: [4]u8 = undefined;

    try std.testing.expectError(DecodeError.InvalidInput, bytes("Zh", false, .std));
    try std.testing.expectError(DecodeError.InvalidInput, decode(buf[0..], "Zh", false, .std));
    try std.testing.expectError(DecodeError.InvalidInput, bytes("-x", false, .urlsafe));
    try std.testing.expectError(DecodeError.InvalidInput, decode(buf[0..], "-x", false, .urlsafe));
    try std.testing.expectError(DecodeError.InvalidInput, bytes("+x", false, .imap));
    try std.testing.expectError(DecodeError.InvalidInput, decode(buf[0..], "+x", false, .imap));

    try std.testing.expectError(DecodeError.InvalidInput, bytes("//B", false, .std));
    try std.testing.expectError(DecodeError.InvalidInput, decode(buf[0..], "//B", false, .std));
    try std.testing.expectError(DecodeError.InvalidInput, bytes("__B", false, .urlsafe));
    try std.testing.expectError(DecodeError.InvalidInput, decode(buf[0..], "__B", false, .urlsafe));
    try std.testing.expectError(DecodeError.InvalidInput, bytes(",,B", false, .imap));
    try std.testing.expectError(DecodeError.InvalidInput, decode(buf[0..], ",,B", false, .imap));
}

test "public encode and decode exhaustively round-trip short payloads across variants" {
    const variants = [_]Variant{ .std, .urlsafe, .imap };
    const paddings = [_]bool{ false, true };
    var one_byte = [_]u8{0};
    var two_bytes = [_]u8{ 0, 0 };

    inline for (variants) |variant| {
        inline for (paddings) |padding| {
            try expectPublicShortRoundTrip(variant, "", padding);

            for (0..256) |first| {
                one_byte[0] = @intCast(first);
                try expectPublicShortRoundTrip(variant, one_byte[0..], padding);
            }

            for (0..256) |first| {
                two_bytes[0] = @intCast(first);
                for (0..256) |second| {
                    two_bytes[1] = @intCast(second);
                    try expectPublicShortRoundTrip(variant, two_bytes[0..], padding);
                }
            }
        }
    }
}

test "decodeTail exhaustively accepts only canonical short tails across variants" {
    try expectExhaustiveTailCanonicality(.std);
    try expectExhaustiveTailCanonicality(.urlsafe);
    try expectExhaustiveTailCanonicality(.imap);
}

test "decode exhaustively accepts only canonical padded short tails across variants" {
    try expectExhaustivePaddedTailCanonicality(.std);
    try expectExhaustivePaddedTailCanonicality(.urlsafe);
    try expectExhaustivePaddedTailCanonicality(.imap);
}

test "decode reverse maps classify every byte across all variants" {
    const variants = [_]Variant{ .std, .urlsafe, .imap };

    inline for (variants) |variant| {
        for (0..256) |raw| {
            const ch: u8 = @intCast(raw);
            if (expectedDecodeValueForTest(ch, variant)) |value| {
                try std.testing.expectEqual(value, try decodeValue(ch, variant));
            } else {
                try std.testing.expectError(DecodeError.InvalidInput, decodeValue(ch, variant));
            }
        }
    }
}
