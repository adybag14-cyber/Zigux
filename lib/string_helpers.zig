// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub const EINVAL: i32 = -22;
pub const UNESCAPE_SPACE: u32 = 1 << 0;
pub const UNESCAPE_OCTAL: u32 = 1 << 1;
pub const UNESCAPE_HEX: u32 = 1 << 2;
pub const UNESCAPE_SPECIAL: u32 = 1 << 3;
pub const UNESCAPE_ANY: u32 = UNESCAPE_SPACE | UNESCAPE_OCTAL | UNESCAPE_HEX | UNESCAPE_SPECIAL;

pub fn sysfsStreq(s1: []const u8, s2: []const u8) bool {
    return std.mem.eql(u8, sysfsComparablePrefix(s1), sysfsComparablePrefix(s2));
}

pub fn matchString(array: []const ?[]const u8, n: usize, needle: []const u8) i32 {
    const limit = @min(n, array.len);
    for (array[0..limit], 0..) |item, index| {
        const value = item orelse break;
        if (std.mem.eql(u8, cStringPrefix(value), cStringPrefix(needle))) {
            return @intCast(index);
        }
    }
    return EINVAL;
}

pub fn sysfsMatchString(array: []const ?[]const u8, n: usize, needle: []const u8) i32 {
    const limit = @min(n, array.len);
    for (array[0..limit], 0..) |item, index| {
        const value = item orelse break;
        if (sysfsStreq(value, needle)) {
            return @intCast(index);
        }
    }
    return EINVAL;
}

pub fn strreplace(buf: []u8, old: u8, new: u8) []u8 {
    for (cStringPrefixMutable(buf)) |*ch| {
        if (ch.* == old) {
            ch.* = new;
        }
    }
    return buf;
}

pub fn memcpyAndPad(dest: []u8, src: []const u8, count: usize, pad: u8) void {
    std.debug.assert(src.len >= count);

    if (dest.len > count) {
        @memcpy(dest[0..count], src[0..count]);
        @memset(dest[count..], pad);
    } else {
        @memcpy(dest, src[0..dest.len]);
    }
}

pub fn stringIsTerminated(s: []const u8, len: usize) bool {
    return std.mem.indexOfScalar(u8, s[0..@min(len, s.len)], 0) != null;
}

pub fn stringUpper(dest: []u8, src: []const u8) void {
    copyCStringMapped(dest, src, std.ascii.toUpper);
}

pub fn stringLower(dest: []u8, src: []const u8) void {
    copyCStringMapped(dest, src, std.ascii.toLower);
}

pub fn stringUnescape(src: []const u8, dst: []u8, size: usize, flags: u32) usize {
    const limit = if (size == 0) dst.len else @min(size, dst.len);
    if (limit == 0) {
        return 0;
    }

    var src_index: usize = 0;
    var dst_index: usize = 0;
    var remaining = limit;

    while (src_index < src.len and src[src_index] != 0 and remaining > 1) {
        if (src[src_index] == '\\' and src_index + 1 < src.len and src[src_index + 1] != 0 and remaining > 2) {
            src_index += 1;

            if ((flags & UNESCAPE_SPACE) != 0) {
                if (unescapeSpace(src, &src_index, dst, &dst_index)) {
                    remaining -= 1;
                    continue;
                }
            }

            if ((flags & UNESCAPE_OCTAL) != 0) {
                if (unescapeOctal(src, &src_index, dst, &dst_index)) {
                    remaining -= 1;
                    continue;
                }
            }

            if ((flags & UNESCAPE_HEX) != 0) {
                if (unescapeHex(src, &src_index, dst, &dst_index)) {
                    remaining -= 1;
                    continue;
                }
            }

            if ((flags & UNESCAPE_SPECIAL) != 0) {
                if (unescapeSpecial(src, &src_index, dst, &dst_index)) {
                    remaining -= 1;
                    continue;
                }
            }

            dst[dst_index] = '\\';
            dst_index += 1;
            remaining -= 1;
        }

        dst[dst_index] = src[src_index];
        dst_index += 1;
        src_index += 1;
        remaining -= 1;
    }

    dst[dst_index] = 0;
    return dst_index;
}

fn cStringPrefix(s: []const u8) []const u8 {
    return s[0 .. std.mem.indexOfScalar(u8, s, 0) orelse s.len];
}

fn cStringPrefixMutable(s: []u8) []u8 {
    return s[0 .. std.mem.indexOfScalar(u8, s, 0) orelse s.len];
}

fn sysfsComparablePrefix(s: []const u8) []const u8 {
    const prefix = cStringPrefix(s);
    if (prefix.len != 0 and prefix[prefix.len - 1] == '\n') {
        return prefix[0 .. prefix.len - 1];
    }
    return prefix;
}

fn copyCStringMapped(dest: []u8, src: []const u8, comptime mapper: fn (u8) u8) void {
    const limit = @min(dest.len, src.len);
    var index: usize = 0;

    while (index < limit) : (index += 1) {
        const ch = src[index];
        dest[index] = mapper(ch);
        if (ch == 0) {
            break;
        }
    }
}

fn unescapeSpace(src: []const u8, src_index: *usize, dst: []u8, dst_index: *usize) bool {
    const value: u8 = switch (src[src_index.*]) {
        'n' => '\n',
        'r' => '\r',
        't' => '\t',
        'v' => 0x0b,
        'f' => 0x0c,
        else => return false,
    };
    dst[dst_index.*] = value;
    dst_index.* += 1;
    src_index.* += 1;
    return true;
}

fn unescapeOctal(src: []const u8, src_index: *usize, dst: []u8, dst_index: *usize) bool {
    if (!isOctalDigit(src[src_index.*])) {
        return false;
    }

    const start = src_index.*;
    var num: u8 = src[src_index.*] - '0';
    src_index.* += 1;

    while (num < 32 and src_index.* < src.len and isOctalDigit(src[src_index.*]) and src_index.* - start < 3) {
        num = (num << 3) + (src[src_index.*] - '0');
        src_index.* += 1;
    }

    dst[dst_index.*] = num;
    dst_index.* += 1;
    return true;
}

fn unescapeHex(src: []const u8, src_index: *usize, dst: []u8, dst_index: *usize) bool {
    if (src[src_index.*] != 'x') {
        return false;
    }
    if (src_index.* + 1 >= src.len) {
        return false;
    }

    var index = src_index.* + 1;
    const hi = std.fmt.charToDigit(src[index], 16) catch return false;
    var num: u8 = @intCast(hi);
    index += 1;

    if (index < src.len) {
        if (std.fmt.charToDigit(src[index], 16)) |lo| {
            num = (num << 4) | @as(u8, @intCast(lo));
            index += 1;
        } else |_| {}
    }

    dst[dst_index.*] = num;
    dst_index.* += 1;
    src_index.* = index;
    return true;
}

fn unescapeSpecial(src: []const u8, src_index: *usize, dst: []u8, dst_index: *usize) bool {
    const value: u8 = switch (src[src_index.*]) {
        '"' => '"',
        '\\' => '\\',
        'a' => 0x07,
        'e' => 0x1b,
        else => return false,
    };
    dst[dst_index.*] = value;
    dst_index.* += 1;
    src_index.* += 1;
    return true;
}

fn isOctalDigit(ch: u8) bool {
    return ch >= '0' and ch <= '7';
}

test "sysfsStreq accepts optional trailing newline" {
    try std.testing.expect(sysfsStreq("enabled", "enabled\n"));
    try std.testing.expect(sysfsStreq("enabled\n", "enabled"));
    try std.testing.expect(sysfsStreq("enabled\x00ignored", "enabled\n"));
    try std.testing.expect(!sysfsStreq("enabled", "disabled"));
    try std.testing.expect(!sysfsStreq("enabled\nlater", "enabled"));
}

test "matchString stops at null sentinels and returns -EINVAL on miss" {
    const choices = [_]?[]const u8{ "alpha", "beta", null, "gamma" };

    try std.testing.expectEqual(@as(i32, 0), matchString(&choices, choices.len, "alpha"));
    try std.testing.expectEqual(@as(i32, 1), matchString(&choices, choices.len, "beta\x00ignored"));
    try std.testing.expectEqual(EINVAL, matchString(&choices, choices.len, "gamma"));
    try std.testing.expectEqual(EINVAL, matchString(&choices, 2, "gamma"));
}

test "sysfsMatchString reuses sysfs newline semantics" {
    const choices = [_]?[]const u8{ "offline", "online", "standby", null };

    try std.testing.expectEqual(@as(i32, 1), sysfsMatchString(&choices, choices.len, "online\n"));
    try std.testing.expectEqual(@as(i32, 2), sysfsMatchString(&choices, choices.len, "standby"));
    try std.testing.expectEqual(EINVAL, sysfsMatchString(&choices, choices.len, "missing\n"));
}

test "strreplace mutates in place without touching bytes after NUL" {
    var buffer = [_]u8{ 'a', '-', 'b', 0, '-', 'x' };
    const returned = strreplace(&buffer, '-', '_');

    try std.testing.expectEqualStrings("a_b", cStringPrefix(returned));
    try std.testing.expectEqual(@as(u8, '-'), buffer[4]);
}

test "memcpyAndPad matches the bounded copy-and-pad contract" {
    var padded = [_]u8{ 0, 0, 0, 0, 0, 0 };
    memcpyAndPad(&padded, "zig", 3, '.');
    try std.testing.expectEqualSlices(u8, "zig...", &padded);

    var truncated = [_]u8{ 0, 0, 0, 0 };
    memcpyAndPad(&truncated, "zigux", 5, '.');
    try std.testing.expectEqualSlices(u8, "zigu", &truncated);
}

test "stringIsTerminated reports whether a bounded window contains NUL" {
    try std.testing.expect(stringIsTerminated("ok\x00tail", 3));
    try std.testing.expect(stringIsTerminated("ok\x00tail", 32));
    try std.testing.expect(!stringIsTerminated("ok\x00tail", 2));
    try std.testing.expect(!stringIsTerminated("plain", 5));
}

test "stringUpper and stringLower perform bounded ASCII case conversion" {
    var upper = [_]u8{ '?', '?', '?', '?', '?', '?', '?', '?' };
    stringUpper(&upper, "abC9!\x00tail");
    try std.testing.expectEqualSlices(u8, "ABC9!\x00", upper[0..6]);
    try std.testing.expectEqual(@as(u8, '?'), upper[6]);

    var lower = [_]u8{ '?', '?', '?', '?', '?' };
    stringLower(&lower, "AbCDe");
    try std.testing.expectEqualSlices(u8, "abcde", &lower);
}

test "stringUnescape applies Linux-style escape classes deterministically" {
    var out = [_]u8{0} ** 64;

    try std.testing.expectEqual(@as(usize, 7), stringUnescape("\\f\\ \\n\\r\\t\\v", &out, out.len, UNESCAPE_SPACE));
    try std.testing.expectEqualSlices(u8, "\x0c\\ \n\r\t\x0b", out[0..7]);

    try std.testing.expectEqual(@as(usize, 15), stringUnescape("\\40\\1\\387\\0064\\05\\040\\8a\\110\\777", &out, out.len, UNESCAPE_OCTAL));
    try std.testing.expectEqualSlices(u8, " \x01\x0387\x064\x05 \\8aH?7", out[0..15]);

    try std.testing.expectEqual(@as(usize, 8), stringUnescape("\\xv\\xa\\x2c\\xD\\x6f2", &out, out.len, UNESCAPE_HEX));
    try std.testing.expectEqualSlices(u8, "\\xv\n,\ro2", out[0..8]);

    try std.testing.expectEqual(@as(usize, 7), stringUnescape("\\h\\\\\\\"\\a\\e\\", &out, out.len, UNESCAPE_SPECIAL));
    try std.testing.expectEqualSlices(u8, "\\h\\\"\x07\x1b\\", out[0..7]);
}

test "stringUnescape supports combined flags, in-place use, and bounded output" {
    var combined = [_]u8{0} ** 32;
    const combined_len = stringUnescape("\\n\\x41\\040\\e", &combined, 0, UNESCAPE_ANY);
    try std.testing.expectEqual(@as(usize, 4), combined_len);
    try std.testing.expectEqualSlices(u8, "\nA \x1b", combined[0..combined_len]);

    var inplace = [_]u8{ '\\', 'n', '\\', 'x', '4', '1', 0, '?', '?' };
    const inplace_len = stringUnescape(inplace[0..], inplace[0..], 0, UNESCAPE_ANY);
    try std.testing.expectEqual(@as(usize, 2), inplace_len);
    try std.testing.expectEqualSlices(u8, "\nA", inplace[0..2]);
    try std.testing.expectEqual(@as(u8, 0), inplace[2]);

    var bounded = [_]u8{ '!', '!', '!', '!' };
    const bounded_len = stringUnescape("\\n\\r", &bounded, bounded.len, UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 2), bounded_len);
    try std.testing.expectEqualSlices(u8, "\n\r", bounded[0..2]);
    try std.testing.expectEqual(@as(u8, 0), bounded[2]);
    try std.testing.expectEqual(@as(u8, '!'), bounded[3]);
}
