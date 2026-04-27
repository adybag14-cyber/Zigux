// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub const EINVAL: i32 = -22;
pub const UNESCAPE_SPACE: u32 = 1 << 0;
pub const UNESCAPE_OCTAL: u32 = 1 << 1;
pub const UNESCAPE_HEX: u32 = 1 << 2;
pub const UNESCAPE_SPECIAL: u32 = 1 << 3;
pub const UNESCAPE_ANY: u32 = UNESCAPE_SPACE | UNESCAPE_OCTAL | UNESCAPE_HEX | UNESCAPE_SPECIAL;
pub const ESCAPE_SPACE: u32 = 1 << 0;
pub const ESCAPE_SPECIAL: u32 = 1 << 1;
pub const ESCAPE_NULL: u32 = 1 << 2;
pub const ESCAPE_OCTAL: u32 = 1 << 3;
pub const ESCAPE_ANY: u32 = ESCAPE_SPACE | ESCAPE_OCTAL | ESCAPE_SPECIAL | ESCAPE_NULL;
pub const ESCAPE_NP: u32 = 1 << 4;
pub const ESCAPE_ANY_NP: u32 = ESCAPE_ANY | ESCAPE_NP;
pub const ESCAPE_HEX: u32 = 1 << 5;
pub const ESCAPE_NA: u32 = 1 << 6;
pub const ESCAPE_NAP: u32 = 1 << 7;
pub const ESCAPE_APPEND: u32 = 1 << 8;
pub const STRING_UNITS_10: u32 = 0;
pub const STRING_UNITS_2: u32 = 1;
pub const STRING_UNITS_MASK: u32 = 1 << 0;
pub const STRING_UNITS_NO_SPACE: u32 = 1 << 30;
pub const STRING_UNITS_NO_BYTES: u32 = 1 << 31;

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

pub fn stringGetSize(size_in: u64, blk_size_in: u64, units: u32, buf: []u8) usize {
    const divisor = [_]u64{ 1000, 1024 };
    const rounding = [_]u32{ 500, 50, 5 };
    const units_10 = [_][]const u8{ "", "k", "M", "G", "T", "P", "E", "Z", "Y" };
    const units_2 = [_][]const u8{ "", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi" };
    const units_base: usize = @intCast(units & STRING_UNITS_MASK);

    var size = size_in;
    var blk_size = blk_size_in;
    var order: usize = 0;
    var remainder: u32 = 0;
    var fraction_buf: [12]u8 = undefined;
    var fraction: []const u8 = "";

    if (blk_size == 0) {
        size = 0;
    }

    if (size != 0) {
        while ((blk_size >> 32) != 0) {
            blk_size = @divFloor(blk_size, divisor[units_base]);
            order += 1;
        }
        while ((size >> 32) != 0) {
            size = @divFloor(size, divisor[units_base]);
            order += 1;
        }

        size *= blk_size;
        while (size >= divisor[units_base]) {
            remainder = @intCast(@mod(size, divisor[units_base]));
            size = @divFloor(size, divisor[units_base]);
            order += 1;
        }

        var sf_cap = size;
        var precision_digits: usize = 0;
        while (sf_cap * 10 < 1000) : (precision_digits += 1) {
            sf_cap *= 10;
        }

        if (units_base == STRING_UNITS_2) {
            remainder = @intCast((@as(u64, remainder) * 1000) >> 10);
        }

        remainder += rounding[precision_digits];
        if (remainder >= 1000) {
            remainder -= 1000;
            size += 1;
        }

        if (precision_digits != 0) {
            const rendered = std.fmt.bufPrint(&fraction_buf, ".{d:0>3}", .{remainder}) catch unreachable;
            fraction = rendered[0 .. precision_digits + 1];
        }
    }

    const unit = if (order >= units_2.len)
        "UNK"
    else if (units_base == STRING_UNITS_2)
        units_2[order]
    else
        units_10[order];

    var rendered: [32]u8 = undefined;
    const full = std.fmt.bufPrint(
        &rendered,
        "{d}{s}{s}{s}{s}",
        .{
            size,
            fraction,
            if ((units & STRING_UNITS_NO_SPACE) != 0) "" else " ",
            unit,
            if ((units & STRING_UNITS_NO_BYTES) != 0) "" else "B",
        },
    ) catch unreachable;
    return copySnprintfStyle(buf, full);
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
        if (src[src_index] == '\\' and src_index + 1 < src.len and src[src_index + 1] != 0 and remaining > 1) {
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

pub fn stringEscapeMem(src: []const u8, dst: []u8, flags: u32, only: ?[]const u8) usize {
    var dst_index: usize = 0;
    const dict = only orelse "";
    const has_dict = dict.len != 0;
    const is_append = (flags & ESCAPE_APPEND) != 0;

    for (src) |ch| {
        const in_dict = has_dict and std.mem.indexOfScalar(u8, dict, ch) != null;

        if (!is_append and has_dict and !in_dict) {
            escapePassthrough(ch, dst, &dst_index);
            continue;
        }

        if (!(is_append and in_dict) and isAscii(ch) and isPrint(ch) and (flags & ESCAPE_NAP) != 0) {
            escapePassthrough(ch, dst, &dst_index);
            continue;
        }

        if (!(is_append and in_dict) and isPrint(ch) and (flags & ESCAPE_NP) != 0) {
            escapePassthrough(ch, dst, &dst_index);
            continue;
        }

        if (!(is_append and in_dict) and isAscii(ch) and (flags & ESCAPE_NA) != 0) {
            escapePassthrough(ch, dst, &dst_index);
            continue;
        }

        if ((flags & ESCAPE_SPACE) != 0 and escapeSpace(ch, dst, &dst_index)) {
            continue;
        }

        if ((flags & ESCAPE_SPECIAL) != 0 and escapeSpecial(ch, dst, &dst_index)) {
            continue;
        }

        if ((flags & ESCAPE_NULL) != 0 and escapeNull(ch, dst, &dst_index)) {
            continue;
        }

        if ((flags & ESCAPE_OCTAL) != 0) {
            escapeOctal(ch, dst, &dst_index);
            continue;
        }

        if ((flags & ESCAPE_HEX) != 0) {
            escapeHex(ch, dst, &dst_index);
            continue;
        }

        escapePassthrough(ch, dst, &dst_index);
    }

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

fn copySnprintfStyle(dest: []u8, src: []const u8) usize {
    if (dest.len == 0) {
        return src.len;
    }

    const copy_len = @min(src.len, dest.len - 1);
    @memcpy(dest[0..copy_len], src[0..copy_len]);
    dest[copy_len] = 0;
    return src.len;
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

fn escapePassthrough(ch: u8, dst: []u8, dst_index: *usize) void {
    if (dst_index.* < dst.len) {
        dst[dst_index.*] = ch;
    }
    dst_index.* += 1;
}

fn escapeSpace(ch: u8, dst: []u8, dst_index: *usize) bool {
    const escaped: u8 = switch (ch) {
        '\n' => 'n',
        '\r' => 'r',
        '\t' => 't',
        0x0b => 'v',
        0x0c => 'f',
        else => return false,
    };
    escapePassthrough('\\', dst, dst_index);
    escapePassthrough(escaped, dst, dst_index);
    return true;
}

fn escapeSpecial(ch: u8, dst: []u8, dst_index: *usize) bool {
    const escaped: u8 = switch (ch) {
        '\\' => '\\',
        0x07 => 'a',
        0x1b => 'e',
        '"' => '"',
        else => return false,
    };
    escapePassthrough('\\', dst, dst_index);
    escapePassthrough(escaped, dst, dst_index);
    return true;
}

fn escapeNull(ch: u8, dst: []u8, dst_index: *usize) bool {
    if (ch != 0) {
        return false;
    }
    escapePassthrough('\\', dst, dst_index);
    escapePassthrough('0', dst, dst_index);
    return true;
}

fn escapeOctal(ch: u8, dst: []u8, dst_index: *usize) void {
    escapePassthrough('\\', dst, dst_index);
    escapePassthrough(((ch >> 6) & 0x07) + '0', dst, dst_index);
    escapePassthrough(((ch >> 3) & 0x07) + '0', dst, dst_index);
    escapePassthrough((ch & 0x07) + '0', dst, dst_index);
}

fn escapeHex(ch: u8, dst: []u8, dst_index: *usize) void {
    escapePassthrough('\\', dst, dst_index);
    escapePassthrough('x', dst, dst_index);
    escapePassthrough(std.fmt.digitToChar((ch >> 4) & 0x0f, .lower), dst, dst_index);
    escapePassthrough(std.fmt.digitToChar(ch & 0x0f, .lower), dst, dst_index);
}

fn isAscii(ch: u8) bool {
    return ch <= 0x7f;
}

fn isPrint(ch: u8) bool {
    return ch >= 0x20 and ch <= 0x7e;
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

test "stringGetSize formats bounded SI and binary sizes" {
    var out = [_]u8{0} ** 16;

    try std.testing.expectEqual(@as(usize, 3), stringGetSize(0, 1, STRING_UNITS_10, &out));
    try std.testing.expectEqualStrings("0 B", cStringPrefix(&out));

    try std.testing.expectEqual(@as(usize, 7), stringGetSize(1500, 1, STRING_UNITS_10, &out));
    try std.testing.expectEqualStrings("1.50 kB", cStringPrefix(&out));

    try std.testing.expectEqual(@as(usize, 8), stringGetSize(1536, 1, STRING_UNITS_2, &out));
    try std.testing.expectEqualStrings("1.50 KiB", cStringPrefix(&out));

    try std.testing.expectEqual(@as(usize, 7), stringGetSize(10, 512, STRING_UNITS_10, &out));
    try std.testing.expectEqualStrings("5.12 kB", cStringPrefix(&out));
}

test "stringGetSize honors formatting flags and snprintf-style truncation" {
    var compact = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0 };
    try std.testing.expectEqual(
        @as(usize, 6),
        stringGetSize(1536, 1, STRING_UNITS_2 | STRING_UNITS_NO_SPACE | STRING_UNITS_NO_BYTES, &compact),
    );
    try std.testing.expectEqualStrings("1.50Ki", cStringPrefix(&compact));

    var truncated = [_]u8{ '!', '!', '!', '!', '!' };
    try std.testing.expectEqual(@as(usize, 7), stringGetSize(1500, 1, STRING_UNITS_10, &truncated));
    try std.testing.expectEqualSlices(u8, &[_]u8{ '1', '.', '5', '0', 0 }, &truncated);

    try std.testing.expectEqual(@as(usize, 7), stringGetSize(1500, 1, STRING_UNITS_10, &.{}));
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

test "stringUnescape exact-fit destination still decodes an escape" {
    var out = [_]u8{ '!', '!' };
    const len = stringUnescape("\\n", &out, out.len, UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 1), len);
    try std.testing.expectEqual(@as(u8, '\n'), out[0]);
    try std.testing.expectEqual(@as(u8, 0), out[1]);
}

test "stringEscapeMem covers the bounded Linux escape classes" {
    var out = [_]u8{0} ** 64;

    try std.testing.expectEqual(@as(usize, 11), stringEscapeMem("\x0c \n\r\t\x0b", &out, ESCAPE_SPACE, null));
    try std.testing.expectEqualSlices(u8, "\\f \\n\\r\\t\\v", out[0..11]);

    try std.testing.expectEqual(@as(usize, 8), stringEscapeMem("\\\"\x07\x1b", &out, ESCAPE_SPECIAL, null));
    try std.testing.expectEqualSlices(u8, "\\\\\\\"\\a\\e", out[0..8]);

    try std.testing.expectEqual(@as(usize, 2), stringEscapeMem("\x00", &out, ESCAPE_NULL, null));
    try std.testing.expectEqualSlices(u8, "\\0", out[0..2]);

    try std.testing.expectEqual(@as(usize, 12), stringEscapeMem("A\x00\x1b", &out, ESCAPE_HEX, null));
    try std.testing.expectEqualSlices(u8, "\\x41\\x00\\x1b", out[0..12]);

    try std.testing.expectEqual(@as(usize, 12), stringEscapeMem("A\x00\x1b", &out, ESCAPE_OCTAL, null));
    try std.testing.expectEqualSlices(u8, "\\101\\000\\033", out[0..12]);
}

test "stringEscapeMem honors only and append selection rules" {
    var out = [_]u8{0} ** 64;

    try std.testing.expectEqual(@as(usize, 5), stringEscapeMem("A\n\tZ", &out, ESCAPE_SPACE, "\n"));
    try std.testing.expectEqualSlices(u8, "A\\n\tZ", out[0..5]);

    try std.testing.expectEqual(@as(usize, 6), stringEscapeMem("A\nZ", &out, ESCAPE_NAP | ESCAPE_HEX | ESCAPE_APPEND, "\n"));
    try std.testing.expectEqualSlices(u8, "A\\x0aZ", out[0..6]);
}

test "stringEscapeMem supports printable and ascii passthrough filters" {
    var out = [_]u8{0} ** 64;

    try std.testing.expectEqual(@as(usize, 6), stringEscapeMem("A\x01z", &out, ESCAPE_NP | ESCAPE_HEX, null));
    try std.testing.expectEqualSlices(u8, "A\\x01z", out[0..6]);

    try std.testing.expectEqual(@as(usize, 6), stringEscapeMem("A\x80z", &out, ESCAPE_NA | ESCAPE_HEX, null));
    try std.testing.expectEqualSlices(u8, "A\\x80z", out[0..6]);

    try std.testing.expectEqual(@as(usize, 10), stringEscapeMem("A\x01\x80z", &out, ESCAPE_NAP | ESCAPE_HEX, null));
    try std.testing.expectEqualSlices(u8, "A\\x01\\x80z", out[0..10]);
}

test "stringEscapeMem reports truncated output length without forcing a terminator" {
    var out = [_]u8{ '?', '?', '?', '?', '?' };
    const len = stringEscapeMem("\n", &out, ESCAPE_HEX, null);
    try std.testing.expectEqual(@as(usize, 4), len);
    try std.testing.expectEqualSlices(u8, "\\x0a?", &out);
}
