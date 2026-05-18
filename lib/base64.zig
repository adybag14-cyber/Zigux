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

pub fn bytesStd(src: []const u8, padding: bool) DecodeError!usize {
    return bytes(src, padding, .std);
}

pub fn bytesUrlsafe(src: []const u8, padding: bool) DecodeError!usize {
    return bytes(src, padding, .urlsafe);
}

pub fn bytesImap(src: []const u8, padding: bool) DecodeError!usize {
    return bytes(src, padding, .imap);
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

pub fn encodeStd(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {
    return encode(dst, src, padding, .std);
}

pub fn encodeUrlsafe(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {
    return encode(dst, src, padding, .urlsafe);
}

pub fn encodeImap(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {
    return encode(dst, src, padding, .imap);
}

pub fn encodeSlice(dst: []u8, src: []const u8, padding: bool, variant: Variant) EncodeError![]u8 {
    const written = try encode(dst, src, padding, variant);
    return dst[0..written];
}

pub fn encodeAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool, variant: Variant) EncodeAllocError![]u8 {
    const needed = chars(src.len, padding);
    const dst = try allocator.alloc(u8, needed);
    errdefer allocator.free(dst);

    const written = try encode(dst, src, padding, variant);
    return dst[0..written];
}

pub fn encodeStdSlice(dst: []u8, src: []const u8, padding: bool) EncodeError![]u8 {
    return encodeSlice(dst, src, padding, .std);
}

pub fn encodeStdAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool) EncodeAllocError![]u8 {
    return encodeAlloc(allocator, src, padding, .std);
}

pub fn encodeUrlsafeSlice(dst: []u8, src: []const u8, padding: bool) EncodeError![]u8 {
    return encodeSlice(dst, src, padding, .urlsafe);
}

pub fn encodeUrlsafeAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool) EncodeAllocError![]u8 {
    return encodeAlloc(allocator, src, padding, .urlsafe);
}

pub fn encodeImapSlice(dst: []u8, src: []const u8, padding: bool) EncodeError![]u8 {
    return encodeSlice(dst, src, padding, .imap);
}

pub fn encodeImapAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool) EncodeAllocError![]u8 {
    return encodeAlloc(allocator, src, padding, .imap);
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

pub fn decodeStd(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {
    return decode(dst, src, padding, .std);
}

pub fn decodeUrlsafe(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {
    return decode(dst, src, padding, .urlsafe);
}

pub fn decodeImap(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {
    return decode(dst, src, padding, .imap);
}

pub fn decodeSlice(dst: []u8, src: []const u8, padding: bool, variant: Variant) DecodeError![]u8 {
    const written = try decode(dst, src, padding, variant);
    return dst[0..written];
}

pub fn decodeAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool, variant: Variant) DecodeAllocError![]u8 {
    const exact_len = try bytes(src, padding, variant);
    const dst = try allocator.alloc(u8, exact_len);
    errdefer allocator.free(dst);

    const written = try decode(dst, src, padding, variant);
    return dst[0..written];
}

pub fn decodeStdSlice(dst: []u8, src: []const u8, padding: bool) DecodeError![]u8 {
    return decodeSlice(dst, src, padding, .std);
}

pub fn decodeStdAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool) DecodeAllocError![]u8 {
    return decodeAlloc(allocator, src, padding, .std);
}

pub fn decodeUrlsafeSlice(dst: []u8, src: []const u8, padding: bool) DecodeError![]u8 {
    return decodeSlice(dst, src, padding, .urlsafe);
}

pub fn decodeUrlsafeAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool) DecodeAllocError![]u8 {
    return decodeAlloc(allocator, src, padding, .urlsafe);
}

pub fn decodeImapSlice(dst: []u8, src: []const u8, padding: bool) DecodeError![]u8 {
    return decodeSlice(dst, src, padding, .imap);
}

pub fn decodeImapAlloc(allocator: std.mem.Allocator, src: []const u8, padding: bool) DecodeAllocError![]u8 {
    return decodeAlloc(allocator, src, padding, .imap);
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

fn decodeTailFromMap(dst: []u8, src: []const u8, map: *const [256]i8) DecodeError!usize {
    if (src.len < 2 or src.len > 3) {
        return DecodeError.InvalidInput;
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

fn expectShortTailRoundTripCase(payload: []const u8, padding: bool, variant: Variant) !void {
    var encoded_buf: [5]u8 = [_]u8{0xaa} ** 5;
    const encoded_len = try encode(encoded_buf[0..], payload, padding, variant);
    try std.testing.expectEqual(chars(payload.len, padding), encoded_len);

    if (payload.len == 1) {
        try std.testing.expectEqual(@as(usize, if (padding) 4 else 2), encoded_len);
        if (padding) {
            try std.testing.expectEqual(@as(u8, '='), encoded_buf[2]);
            try std.testing.expectEqual(@as(u8, '='), encoded_buf[3]);
        }
    } else {
        try std.testing.expectEqual(@as(usize, if (padding) 4 else 3), encoded_len);
        if (padding) {
            try std.testing.expectEqual(@as(u8, '='), encoded_buf[3]);
        }
    }
    try std.testing.expectEqual(@as(u8, 0xaa), encoded_buf[encoded_len]);

    const encoded = encoded_buf[0..encoded_len];
    try std.testing.expectEqual(payload.len, try bytes(encoded, padding, variant));

    var decoded_buf: [3]u8 = [_]u8{0xbb} ** 3;
    const decoded_len = try decode(decoded_buf[0..], encoded, padding, variant);
    try std.testing.expectEqual(payload.len, decoded_len);
    try std.testing.expectEqualSlices(u8, payload, decoded_buf[0..decoded_len]);
    try std.testing.expectEqual(@as(u8, 0xbb), decoded_buf[decoded_len]);
}

fn expectShortTailRoundTripSweep(variant: Variant, padding: bool) !void {
    for (0..256) |first_raw| {
        const first: u8 = @intCast(first_raw);
        const one = [_]u8{first};
        try expectShortTailRoundTripCase(one[0..], padding, variant);

        for (0..256) |second_raw| {
            const second: u8 = @intCast(second_raw);
            const two = [_]u8{ first, second };
            try expectShortTailRoundTripCase(two[0..], padding, variant);
        }
    }
}

fn expectNonCanonicalTailMutationRejectionCase(payload: []const u8, padding: bool, variant: Variant) !void {
    var encoded_buf: [5]u8 = undefined;
    const encoded_len = try encode(encoded_buf[0..], payload, padding, variant);
    const mutated_index: usize = if (payload.len == 1) 1 else 2;
    const canonical_value = try decodeValue(encoded_buf[mutated_index], variant);
    const mutated_value: u8 = canonical_value | 0x1;
    try std.testing.expect(mutated_value != canonical_value);

    var mutated_buf = encoded_buf;
    mutated_buf[mutated_index] = alphabet(variant)[mutated_value];
    const mutated = mutated_buf[0..encoded_len];

    try std.testing.expectError(DecodeError.InvalidInput, bytes(mutated, padding, variant));

    var decoded_buf: [3]u8 = undefined;
    try std.testing.expectError(DecodeError.InvalidInput, decode(decoded_buf[0..], mutated, padding, variant));
}

fn expectNonCanonicalTailMutationRejectionSweep(variant: Variant, padding: bool) !void {
    for (0..256) |first_raw| {
        const first: u8 = @intCast(first_raw);
        const one = [_]u8{first};
        try expectNonCanonicalTailMutationRejectionCase(one[0..], padding, variant);

        for (0..256) |second_raw| {
            const second: u8 = @intCast(second_raw);
            const two = [_]u8{ first, second };
            try expectNonCanonicalTailMutationRejectionCase(two[0..], padding, variant);
        }
    }
}

fn expectVariantPinnedConvenienceParity(input: []const u8, expected: []const u8, padding: bool, variant: Variant) !void {
    var generic_buf: [16]u8 = undefined;
    var pinned_buf: [16]u8 = undefined;
    const generic_written = try encode(generic_buf[0..], input, padding, variant);
    const pinned_written = switch (variant) {
        .std => try encodeStd(pinned_buf[0..], input, padding),
        .urlsafe => try encodeUrlsafe(pinned_buf[0..], input, padding),
        .imap => try encodeImap(pinned_buf[0..], input, padding),
    };
    try std.testing.expectEqual(generic_written, pinned_written);
    try std.testing.expectEqualStrings(expected, generic_buf[0..generic_written]);
    try std.testing.expectEqualStrings(expected, pinned_buf[0..pinned_written]);

    const generic_len = try bytes(expected, padding, variant);
    const pinned_len = switch (variant) {
        .std => try bytesStd(expected, padding),
        .urlsafe => try bytesUrlsafe(expected, padding),
        .imap => try bytesImap(expected, padding),
    };
    try std.testing.expectEqual(generic_len, pinned_len);

    var generic_decoded: [8]u8 = undefined;
    var pinned_decoded: [8]u8 = undefined;
    const generic_decoded_len = try decode(generic_decoded[0..], expected, padding, variant);
    const pinned_decoded_len = switch (variant) {
        .std => try decodeStd(pinned_decoded[0..], expected, padding),
        .urlsafe => try decodeUrlsafe(pinned_decoded[0..], expected, padding),
        .imap => try decodeImap(pinned_decoded[0..], expected, padding),
    };
    try std.testing.expectEqual(generic_decoded_len, pinned_decoded_len);
    try std.testing.expectEqualSlices(u8, input, generic_decoded[0..generic_decoded_len]);
    try std.testing.expectEqualSlices(u8, input, pinned_decoded[0..pinned_decoded_len]);

    var generic_slice_buf: [16]u8 = [_]u8{0xaa} ** 16;
    var pinned_slice_buf: [16]u8 = [_]u8{0xbb} ** 16;
    const generic_slice = try encodeSlice(generic_slice_buf[0..generic_written], input, padding, variant);
    const pinned_slice = switch (variant) {
        .std => try encodeStdSlice(pinned_slice_buf[0..pinned_written], input, padding),
        .urlsafe => try encodeUrlsafeSlice(pinned_slice_buf[0..pinned_written], input, padding),
        .imap => try encodeImapSlice(pinned_slice_buf[0..pinned_written], input, padding),
    };
    try std.testing.expectEqualStrings(expected, generic_slice);
    try std.testing.expectEqualStrings(expected, pinned_slice);
    try std.testing.expectEqual(@as(u8, 0xaa), generic_slice_buf[generic_slice.len]);
    try std.testing.expectEqual(@as(u8, 0xbb), pinned_slice_buf[pinned_slice.len]);

    const generic_alloc = try encodeAlloc(std.testing.allocator, input, padding, variant);
    defer std.testing.allocator.free(generic_alloc);
    const pinned_alloc = switch (variant) {
        .std => try encodeStdAlloc(std.testing.allocator, input, padding),
        .urlsafe => try encodeUrlsafeAlloc(std.testing.allocator, input, padding),
        .imap => try encodeImapAlloc(std.testing.allocator, input, padding),
    };
    defer std.testing.allocator.free(pinned_alloc);
    try std.testing.expectEqualStrings(generic_alloc, pinned_alloc);

    var generic_decode_slice_buf: [8]u8 = [_]u8{0xcc} ** 8;
    var pinned_decode_slice_buf: [8]u8 = [_]u8{0xdd} ** 8;
    const generic_decode_slice = try decodeSlice(generic_decode_slice_buf[0..generic_len], expected, padding, variant);
    const pinned_decode_slice = switch (variant) {
        .std => try decodeStdSlice(pinned_decode_slice_buf[0..pinned_len], expected, padding),
        .urlsafe => try decodeUrlsafeSlice(pinned_decode_slice_buf[0..pinned_len], expected, padding),
        .imap => try decodeImapSlice(pinned_decode_slice_buf[0..pinned_len], expected, padding),
    };
    try std.testing.expectEqualSlices(u8, input, generic_decode_slice);
    try std.testing.expectEqualSlices(u8, generic_decode_slice, pinned_decode_slice);
    try std.testing.expectEqual(@as(u8, 0xcc), generic_decode_slice_buf[generic_decode_slice.len]);
    try std.testing.expectEqual(@as(u8, 0xdd), pinned_decode_slice_buf[pinned_decode_slice.len]);

    const generic_decode_alloc = try decodeAlloc(std.testing.allocator, expected, padding, variant);
    defer std.testing.allocator.free(generic_decode_alloc);
    const pinned_decode_alloc = switch (variant) {
        .std => try decodeStdAlloc(std.testing.allocator, expected, padding),
        .urlsafe => try decodeUrlsafeAlloc(std.testing.allocator, expected, padding),
        .imap => try decodeImapAlloc(std.testing.allocator, expected, padding),
    };
    defer std.testing.allocator.free(pinned_decode_alloc);
    try std.testing.expectEqualSlices(u8, generic_decode_alloc, pinned_decode_alloc);
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

test "variant-pinned convenience helpers mirror the generic api" {
    const sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };
    const one_byte = [_]u8{0xfb};
    const two_byte = [_]u8{ 0xff, 0xf0 };
    try expectVariantPinnedConvenienceParity(&sample, "APv/f4A", false, .std);
    try expectVariantPinnedConvenienceParity(&sample, "APv/f4A=", true, .std);
    try expectVariantPinnedConvenienceParity(&sample, "APv_f4A", false, .urlsafe);
    try expectVariantPinnedConvenienceParity(&sample, "APv_f4A=", true, .urlsafe);
    try expectVariantPinnedConvenienceParity(&sample, "APv,f4A", false, .imap);
    try expectVariantPinnedConvenienceParity(&sample, "APv,f4A=", true, .imap);

    try expectVariantPinnedConvenienceParity(&one_byte, "+w", false, .std);
    try expectVariantPinnedConvenienceParity(&one_byte, "-w", false, .urlsafe);
    try expectVariantPinnedConvenienceParity(&one_byte, "+w", false, .imap);
    try expectVariantPinnedConvenienceParity(&two_byte, "//A=", true, .std);
    try expectVariantPinnedConvenienceParity(&two_byte, "__A=", true, .urlsafe);
    try expectVariantPinnedConvenienceParity(&two_byte, ",,A=", true, .imap);
}

test "standard slice and allocator helpers pin the common variant across exact-span ownership paths" {
    const sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };
    var generic_encoded_buf: [9]u8 = [_]u8{0xaa} ** 9;
    var std_encoded_buf: [9]u8 = [_]u8{0xbb} ** 9;

    const generic_encoded = try encodeSlice(generic_encoded_buf[0..8], &sample, true, .std);
    const std_encoded = try encodeStdSlice(std_encoded_buf[0..8], &sample, true);
    try std.testing.expectEqualStrings("APv/f4A=", generic_encoded);
    try std.testing.expectEqualStrings(generic_encoded, std_encoded);
    try std.testing.expectEqual(@as(u8, 0xaa), generic_encoded_buf[generic_encoded.len]);
    try std.testing.expectEqual(@as(u8, 0xbb), std_encoded_buf[std_encoded.len]);

    const generic_alloc = try encodeAlloc(std.testing.allocator, &sample, true, .std);
    defer std.testing.allocator.free(generic_alloc);
    const std_alloc = try encodeStdAlloc(std.testing.allocator, &sample, true);
    defer std.testing.allocator.free(std_alloc);
    try std.testing.expectEqualStrings(generic_alloc, std_alloc);

    var generic_decoded_buf: [6]u8 = [_]u8{0xcc} ** 6;
    var std_decoded_buf: [6]u8 = [_]u8{0xdd} ** 6;
    const generic_decoded = try decodeSlice(generic_decoded_buf[0..5], "APv/f4A=", true, .std);
    const std_decoded = try decodeStdSlice(std_decoded_buf[0..5], "APv/f4A=", true);
    try std.testing.expectEqualSlices(u8, &sample, generic_decoded);
    try std.testing.expectEqualSlices(u8, generic_decoded, std_decoded);
    try std.testing.expectEqual(@as(u8, 0xcc), generic_decoded_buf[generic_decoded.len]);
    try std.testing.expectEqual(@as(u8, 0xdd), std_decoded_buf[std_decoded.len]);

    const generic_decoded_alloc = try decodeAlloc(std.testing.allocator, "APv/f4A=", true, .std);
    defer std.testing.allocator.free(generic_decoded_alloc);
    const std_decoded_alloc = try decodeStdAlloc(std.testing.allocator, "APv/f4A=", true);
    defer std.testing.allocator.free(std_decoded_alloc);
    try std.testing.expectEqualSlices(u8, generic_decoded_alloc, std_decoded_alloc);
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

test "encode slice and allocator companions return exact written spans" {
    const sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };
    var slice_buf: [8]u8 = undefined;

    const url_slice = try encodeSlice(slice_buf[0..], &sample, false, .urlsafe);
    try std.testing.expectEqual(@as(usize, 7), url_slice.len);
    try std.testing.expectEqualStrings("APv_f4A", url_slice);

    const imap_alloc = try encodeAlloc(std.testing.allocator, &sample, true, .imap);
    defer std.testing.allocator.free(imap_alloc);
    try std.testing.expectEqual(@as(usize, 8), imap_alloc.len);
    try std.testing.expectEqualStrings("APv,f4A=", imap_alloc);
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

test "decode slice and allocator companions return exact written spans" {
    var slice_buf: [8]u8 = undefined;

    const url_slice = try decodeSlice(slice_buf[0..], "APv_f4A", false, .urlsafe);
    try std.testing.expectEqual(@as(usize, 5), url_slice.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 }, url_slice);

    const imap_alloc = try decodeAlloc(std.testing.allocator, "APv,f4A=", true, .imap);
    defer std.testing.allocator.free(imap_alloc);
    try std.testing.expectEqual(@as(usize, 5), imap_alloc.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 }, imap_alloc);
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

test "encode and decode sweep every one-byte and two-byte tail across variants and padding modes" {
    inline for ([_]Variant{ .std, .urlsafe, .imap }) |variant| {
        inline for ([_]bool{ false, true }) |padding| {
            try expectShortTailRoundTripSweep(variant, padding);
        }
    }
}

test "decode and bytes reject non-canonical mutated tail bits across every variant tail shape" {
    inline for ([_]Variant{ .std, .urlsafe, .imap }) |variant| {
        inline for ([_]bool{ false, true }) |padding| {
            try expectNonCanonicalTailMutationRejectionSweep(variant, padding);
        }
    }
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
