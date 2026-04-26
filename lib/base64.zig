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

fn alphabet(variant: Variant) []const u8 {
    return switch (variant) {
        .std => std_table,
        .urlsafe => urlsafe_table,
        .imap => imap_table,
    };
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
