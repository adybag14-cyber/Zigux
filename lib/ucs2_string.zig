// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub const E2BIG: isize = 7;

pub fn ucs2_strnlen(s: [*]const u16, maxlength: usize) usize {
    var length: usize = 0;
    while (length < maxlength and s[length] != 0) : (length += 1) {}
    return length;
}

pub fn ucs2_strlen(s: [*:0]const u16) usize {
    var length: usize = 0;
    while (s[length] != 0) : (length += 1) {}
    return length;
}

pub fn ucs2_strsize(data: [*]const u16, maxlength: usize) usize {
    return ucs2_strnlen(data, maxlength / @sizeOf(u16)) * @sizeOf(u16);
}

pub fn ucs2_strscpy(dst: [*]u16, src: [*]const u16, count: usize) isize {
    const max_count: usize = @intCast(std.math.maxInt(isize));
    if (count == 0 or count > max_count) return -E2BIG;

    var copied: usize = 0;
    while (copied < count) : (copied += 1) {
        const c = src[copied];
        dst[copied] = c;
        if (c == 0) return @intCast(copied);
    }

    dst[count - 1] = 0;
    return -E2BIG;
}

pub fn ucs2_strncmp(a: [*]const u16, b: [*]const u16, len: usize) i32 {
    var i: usize = 0;
    while (true) : (i += 1) {
        if (i == len) return 0;
        if (a[i] < b[i]) return -1;
        if (a[i] > b[i]) return 1;
        if (a[i] == 0) return 0;
    }
}

pub fn ucs2_utf8size(src: [*:0]const u16) usize {
    var i: usize = 0;
    var bytes: usize = 0;
    while (src[i] != 0) : (i += 1) {
        const c = src[i];
        if (c >= 0x800) {
            bytes += 3;
        } else if (c >= 0x80) {
            bytes += 2;
        } else {
            bytes += 1;
        }
    }
    return bytes;
}

pub fn ucs2_as_utf8(dest: [*]u8, src: [*:0]const u16, maxlength: usize) usize {
    var remaining = maxlength;
    var written: usize = 0;
    const limit = ucs2_strnlen(src, maxlength);

    var i: usize = 0;
    while (remaining != 0 and i < limit) : (i += 1) {
        const c = src[i];
        if (c >= 0x800) {
            if (remaining < 3) break;
            remaining -= 3;
            dest[written] = @intCast(0xe0 | ((c & 0xf000) >> 12));
            dest[written + 1] = @intCast(0x80 | ((c & 0x0fc0) >> 6));
            dest[written + 2] = @intCast(0x80 | (c & 0x003f));
            written += 3;
        } else if (c >= 0x80) {
            if (remaining < 2) break;
            remaining -= 2;
            dest[written] = @intCast(0xc0 | ((c & 0x07c0) >> 6));
            dest[written + 1] = @intCast(0x80 | (c & 0x003f));
            written += 2;
        } else {
            remaining -= 1;
            dest[written] = @intCast(c & 0x007f);
            written += 1;
        }
    }

    if (remaining != 0) dest[written] = 0;
    return written;
}

test "ucs2 length helpers stop at nul or maximum" {
    const s = [_]u16{ 'a', 'b', 0, 'c' };
    try std.testing.expectEqual(@as(usize, 2), ucs2_strnlen(&s, 4));
    try std.testing.expectEqual(@as(usize, 1), ucs2_strnlen(&s, 1));
    try std.testing.expectEqual(@as(usize, 0), ucs2_strnlen(&s, 0));

    const sentinel = [_:0]u16{ 'x', 'y' };
    try std.testing.expectEqual(@as(usize, 2), ucs2_strlen(&sentinel));
}

test "ucs2 string size uses byte limit rounded down to whole code units" {
    const s = [_]u16{ 'a', 'b', 'c', 0 };
    try std.testing.expectEqual(@as(usize, 2), ucs2_strsize(&s, 3));
    try std.testing.expectEqual(@as(usize, 4), ucs2_strsize(&s, 5));
}

test "ucs2 strscpy copies nul and reports copied characters" {
    const src = [_]u16{ 'a', 'b', 0 };
    var dst = [_]u16{ 9, 9, 9 };
    try std.testing.expectEqual(@as(isize, 2), ucs2_strscpy(&dst, &src, dst.len));
    try std.testing.expectEqualSlices(u16, &.{ 'a', 'b', 0 }, &dst);
}

test "ucs2 strscpy truncates and leaves nul termination" {
    const src = [_]u16{ 'a', 'b', 'c', 0 };
    var dst = [_]u16{ 9, 9, 9 };
    try std.testing.expectEqual(@as(isize, -E2BIG), ucs2_strscpy(&dst, &src, dst.len));
    try std.testing.expectEqualSlices(u16, &.{ 'a', 'b', 0 }, &dst);
}

test "ucs2 strscpy rejects zero count without writing" {
    const src = [_]u16{ 'a', 0 };
    var dst = [_]u16{9};
    try std.testing.expectEqual(@as(isize, -E2BIG), ucs2_strscpy(&dst, &src, 0));
    try std.testing.expectEqual(@as(u16, 9), dst[0]);
}

test "ucs2 strncmp is lexicographic and nul aware" {
    try std.testing.expectEqual(@as(i32, 0), ucs2_strncmp(&[_]u16{ 'a', 0 }, &[_]u16{ 'a', 0 }, 2));
    try std.testing.expectEqual(@as(i32, -1), ucs2_strncmp(&[_]u16{ 'a', 0 }, &[_]u16{ 'a', 'b' }, 2));
    try std.testing.expectEqual(@as(i32, 1), ucs2_strncmp(&[_]u16{ 'b', 0 }, &[_]u16{ 'a', 0 }, 2));
    try std.testing.expectEqual(@as(i32, 0), ucs2_strncmp(&[_]u16{'a'}, &[_]u16{'b'}, 0));
}

test "ucs2 utf8 size counts each u16 independently" {
    const s = [_:0]u16{ 0x007f, 0x0080, 0x07ff, 0x0800 };
    try std.testing.expectEqual(@as(usize, 8), ucs2_utf8size(&s));
}

test "ucs2 utf8 conversion writes whole characters and optional nul" {
    const src = [_:0]u16{ 0x24, 0x00a2, 0x20ac };
    var dst = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0 };

    try std.testing.expectEqual(@as(usize, 3), ucs2_as_utf8(&dst, &src, 3));
    try std.testing.expectEqualSlices(u8, &.{ 0x24, 0xc2, 0xa2 }, dst[0..3]);

    @memset(dst[0..], 0xaa);
    try std.testing.expectEqual(@as(usize, 3), ucs2_as_utf8(&dst, &src, 4));
    try std.testing.expectEqual(@as(u8, 0), dst[3]);

    @memset(dst[0..], 0xaa);
    try std.testing.expectEqual(@as(usize, 0), ucs2_as_utf8(&dst, &src, 0));
    try std.testing.expectEqual(@as(u8, 0xaa), dst[0]);
}
