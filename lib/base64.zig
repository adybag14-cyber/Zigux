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

    var out_index: usize = 0;
    var src_index: usize = 0;

    while (src_index + 4 <= src.len) : (src_index += 4) {
        const a = try decodeValue(src[src_index], variant);
        const b = try decodeValue(src[src_index + 1], variant);
        const third_char = src[src_index + 2];
        const fourth_char = src[src_index + 3];

        if (third_char == '=' or fourth_char == '=') {
            var value = (@as(u32, a) << 12) | (@as(u32, b) << 6);
            dst[out_index] = @truncate(value >> 10);
            out_index += 1;

            if (third_char != '=') {
                const c = try decodeValue(third_char, variant);
                value |= @as(u32, c);
                dst[out_index] = @truncate(value >> 2);
                out_index += 1;
            }

            return out_index;
        }

        const c = try decodeValue(third_char, variant);
        const d = try decodeValue(fourth_char, variant);

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

    const a = try decodeValue(src[src_index], variant);
    const b = try decodeValue(src[src_index + 1], variant);
    var value = (@as(u32, a) << 12) | (@as(u32, b) << 6);
    dst[out_index] = @truncate(value >> 10);
    out_index += 1;

    if (tail == 2) {
        return out_index;
    }

    const c = try decodeValue(src[src_index + 2], variant);
    value |= @as(u32, c);
    dst[out_index] = @truncate(value >> 2);
    out_index += 1;
    return out_index;
}

fn alphabet(variant: Variant) []const u8 {
    return switch (variant) {
        .std => std_table,
        .urlsafe => urlsafe_table,
        .imap => imap_table,
    };
}

fn decodedLength(src: []const u8, padding: bool, variant: Variant) DecodeError!usize {
    var out_len: usize = 0;
    var src_index: usize = 0;

    while (src_index + 4 <= src.len) : (src_index += 4) {
        const quartet = src[src_index .. src_index + 4];
        const a = decodeValue(quartet[0], variant) catch return DecodeError.InvalidInput;
        const b = decodeValue(quartet[1], variant) catch return DecodeError.InvalidInput;
        _ = a;
        _ = b;

        const c = quartet[2];
        const d = quartet[3];

        if (c == '=' or d == '=') {
            if (!padding or src_index + 4 != src.len or d != '=') {
                return DecodeError.InvalidInput;
            }

            if (c == '=') {
                out_len += try validateTail(src[src_index .. src_index + 2], variant);
            } else {
                _ = decodeValue(c, variant) catch return DecodeError.InvalidInput;
                out_len += try validateTail(src[src_index .. src_index + 3], variant);
            }
            return out_len;
        }

        _ = decodeValue(c, variant) catch return DecodeError.InvalidInput;
        _ = decodeValue(d, variant) catch return DecodeError.InvalidInput;
        out_len += 3;
    }

    const tail = src.len - src_index;
    if (tail == 0) {
        return out_len;
    }
    if (padding or tail == 1) {
        return DecodeError.InvalidInput;
    }
    return out_len + try validateTail(src[src_index..], variant);
}

fn validateTail(src: []const u8, variant: Variant) DecodeError!usize {
    if (src.len < 2 or src.len > 3) {
        return DecodeError.InvalidInput;
    }

    const a = try decodeValue(src[0], variant);
    const b = try decodeValue(src[1], variant);
    var value = (@as(u32, a) << 12) | (@as(u32, b) << 6);

    if (src.len == 2) {
        if ((value & 0x3ff) != 0) {
            return DecodeError.InvalidInput;
        }
        return 1;
    }

    const c = try decodeValue(src[2], variant);
    value |= @as(u32, c);
    if ((value & 0x3) != 0) {
        return DecodeError.InvalidInput;
    }
    return 2;
}

fn decodeValue(ch: u8, variant: Variant) DecodeError!u8 {
    return switch (ch) {
        'A'...'Z' => ch - 'A',
        'a'...'z' => ch - 'a' + 26,
        '0'...'9' => ch - '0' + 52,
        '+' => switch (variant) {
            .std, .imap => 62,
            .urlsafe => DecodeError.InvalidInput,
        },
        '/' => switch (variant) {
            .std => 63,
            .urlsafe, .imap => DecodeError.InvalidInput,
        },
        '-' => switch (variant) {
            .urlsafe => 62,
            .std, .imap => DecodeError.InvalidInput,
        },
        '_' => switch (variant) {
            .urlsafe => 63,
            .std, .imap => DecodeError.InvalidInput,
        },
        ',' => switch (variant) {
            .imap => 63,
            .std, .urlsafe => DecodeError.InvalidInput,
        },
        else => DecodeError.InvalidInput,
    };
}

fn expectDecodeRejectsWithoutWrites(decoded: []u8, tail: []const u8, padding: bool, variant: Variant) !void {
    @memset(decoded, 0xee);
    try std.testing.expectError(DecodeError.InvalidInput, decode(decoded, tail, padding, variant));
    for (decoded) |byte| {
        try std.testing.expectEqual(@as(u8, 0xee), byte);
    }
}

fn expectExhaustiveTailCanonicality(padding: bool, variant: Variant) !void {
    const table = alphabet(variant);
    var encoded: [4]u8 = undefined;
    var decoded: [2]u8 = undefined;

    for (0..64) |a| {
        for (0..64) |b| {
            encoded[0] = table[a];
            encoded[1] = table[b];
            if (padding) {
                encoded[2] = '=';
                encoded[3] = '=';
            }

            const tail = if (padding) encoded[0..4] else encoded[0..2];
            if ((b & 0x0f) == 0) {
                const exact_len = try bytes(tail, padding, variant);
                try std.testing.expectEqual(@as(usize, 1), exact_len);
                const written = try decode(decoded[0..], tail, padding, variant);
                try std.testing.expectEqual(@as(usize, 1), written);
                try std.testing.expectEqual(@as(u8, @intCast((a << 2) | (b >> 4))), decoded[0]);
            } else {
                try std.testing.expectError(DecodeError.InvalidInput, bytes(tail, padding, variant));
                try expectDecodeRejectsWithoutWrites(decoded[0..], tail, padding, variant);
            }
        }
    }

    for (0..64) |a| {
        for (0..64) |b| {
            for (0..64) |c| {
                encoded[0] = table[a];
                encoded[1] = table[b];
                encoded[2] = table[c];
                if (padding) {
                    encoded[3] = '=';
                }

                const tail = if (padding) encoded[0..4] else encoded[0..3];
                if ((c & 0x03) == 0) {
                    const exact_len = try bytes(tail, padding, variant);
                    try std.testing.expectEqual(@as(usize, 2), exact_len);
                    const written = try decode(decoded[0..], tail, padding, variant);
                    try std.testing.expectEqual(@as(usize, 2), written);
                    try std.testing.expectEqual(@as(u8, @intCast((a << 2) | (b >> 4))), decoded[0]);
                    try std.testing.expectEqual(@as(u8, @intCast(((b & 0x0f) << 4) | (c >> 2))), decoded[1]);
                } else {
                    try std.testing.expectError(DecodeError.InvalidInput, bytes(tail, padding, variant));
                    try expectDecodeRejectsWithoutWrites(decoded[0..], tail, padding, variant);
                }
            }
        }
    }
}

fn expectExhaustiveShortRoundtrip(padding: bool, variant: Variant) !void {
    var encoded: [4]u8 = undefined;
    var decoded: [2]u8 = undefined;

    for (0..256) |a| {
        const input = [_]u8{@intCast(a)};
        const encoded_len = try encode(encoded[0..], input[0..], padding, variant);
        try std.testing.expectEqual(chars(input.len, padding), encoded_len);
        try std.testing.expectEqual(@as(usize, input.len), try bytes(encoded[0..encoded_len], padding, variant));

        const decoded_len = try decode(decoded[0..], encoded[0..encoded_len], padding, variant);
        try std.testing.expectEqual(@as(usize, 1), decoded_len);
        try std.testing.expectEqualSlices(u8, input[0..], decoded[0..decoded_len]);
    }

    for (0..256) |a| {
        for (0..256) |b| {
            const input = [_]u8{ @intCast(a), @intCast(b) };
            const encoded_len = try encode(encoded[0..], input[0..], padding, variant);
            try std.testing.expectEqual(chars(input.len, padding), encoded_len);
            try std.testing.expectEqual(@as(usize, input.len), try bytes(encoded[0..encoded_len], padding, variant));

            const decoded_len = try decode(decoded[0..], encoded[0..encoded_len], padding, variant);
            try std.testing.expectEqual(@as(usize, 2), decoded_len);
            try std.testing.expectEqualSlices(u8, input[0..], decoded[0..decoded_len]);
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

test "bytes matches canonical padded and unpadded decode sizes" {
    try std.testing.expectEqual(@as(usize, 13), try bytes("SGVsbG8sIHdvcmxkIQ==", true, .std));
    try std.testing.expectEqual(@as(usize, 6), try bytes("Zm9vYmFy", false, .std));
    try std.testing.expectEqual(@as(usize, 5), try bytes("APv_f4A", false, .urlsafe));
    try std.testing.expectEqual(@as(usize, 5), try bytes("APv,f4A=", true, .imap));
}

test "bytes rejects malformed input and non-canonical tails" {
    try std.testing.expectError(DecodeError.InvalidInput, bytes("Zg", true, .std));
    try std.testing.expectError(DecodeError.InvalidInput, bytes("Zg=!", true, .std));
    try std.testing.expectError(DecodeError.InvalidInput, bytes("Zm9v====", false, .std));
    try std.testing.expectError(DecodeError.InvalidInput, bytes("Zg==", false, .urlsafe));
    try std.testing.expectError(DecodeError.InvalidInput, bytes("Zh==", true, .std));
    try std.testing.expectError(DecodeError.InvalidInput, bytes("Zm9", false, .std));
}

test "encode covers standard and variant alphabets" {
    var std_buf: [16]u8 = undefined;
    var url_buf: [16]u8 = undefined;
    var imap_buf: [16]u8 = undefined;
    const sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };

    const std_len = try encode(std_buf[0..], &sample, false, .std);
    const url_len = try encode(url_buf[0..], &sample, false, .urlsafe);
    const imap_len = try encode(imap_buf[0..], &sample, false, .imap);

    try std.testing.expectEqualStrings("APv/f4A", std_buf[0..std_len]);
    try std.testing.expectEqualStrings("APv_f4A", url_buf[0..url_len]);
    try std.testing.expectEqualStrings("APv,f4A", imap_buf[0..imap_len]);
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

    const imap_len = try decode(variant_out[0..], "APv,f4A", false, .imap);
    try std.testing.expectEqualSlices(u8, &sample, variant_out[0..imap_len]);
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

test "decode leaves caller bytes past the returned payload untouched" {
    const sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };
    const cases = [_]struct {
        input: []const u8,
        expected: []const u8,
        padding: bool,
        variant: Variant,
    }{
        .{ .input = "Zg==", .expected = "f", .padding = true, .variant = .std },
        .{ .input = "Zg", .expected = "f", .padding = false, .variant = .std },
        .{ .input = "Zm8=", .expected = "fo", .padding = true, .variant = .std },
        .{ .input = "Zm8", .expected = "fo", .padding = false, .variant = .std },
        .{ .input = "APv_f4A", .expected = sample[0..], .padding = false, .variant = .urlsafe },
        .{ .input = "APv,f4A=", .expected = sample[0..], .padding = true, .variant = .imap },
    };

    for (cases) |case| {
        var decoded = [_]u8{0xaa} ** 8;
        try std.testing.expectEqual(case.expected.len, try bytes(case.input, case.padding, case.variant));
        const written = try decode(decoded[0..], case.input, case.padding, case.variant);
        try std.testing.expectEqual(case.expected.len, written);
        try std.testing.expectEqualSlices(u8, case.expected, decoded[0..written]);
        for (decoded[written..]) |byte| {
            try std.testing.expectEqual(@as(u8, 0xaa), byte);
        }
    }
}

test "decode exhaustively accepts only canonical padded tails" {
    try expectExhaustiveTailCanonicality(true, .std);
    try expectExhaustiveTailCanonicality(true, .urlsafe);
    try expectExhaustiveTailCanonicality(true, .imap);
}

test "decode exhaustively accepts only canonical unpadded tails" {
    try expectExhaustiveTailCanonicality(false, .std);
    try expectExhaustiveTailCanonicality(false, .urlsafe);
    try expectExhaustiveTailCanonicality(false, .imap);
}

test "encode and decode roundtrip every short payload across variants" {
    inline for (.{ Variant.std, Variant.urlsafe, Variant.imap }) |variant| {
        try expectExhaustiveShortRoundtrip(true, variant);
        try expectExhaustiveShortRoundtrip(false, variant);
    }
}
