const std = @import("std");

pub const UNESCAPE_SPACE: u32 = @as(u32, 1) << 0;
pub const UNESCAPE_OCTAL: u32 = @as(u32, 1) << 1;
pub const UNESCAPE_HEX: u32 = @as(u32, 1) << 2;
pub const UNESCAPE_SPECIAL: u32 = @as(u32, 1) << 3;
pub const UNESCAPE_ANY: u32 = UNESCAPE_SPACE | UNESCAPE_OCTAL | UNESCAPE_HEX | UNESCAPE_SPECIAL;
pub const UNESCAPE_ALL_MASK: u32 = UNESCAPE_ANY;

const UnescapeMatch = struct {
    value: u8,
    consumed: usize,
};

fn cStringLen(buf: []const u8) usize {
    for (buf, 0..) |ch, idx| {
        if (ch == 0) return idx;
    }
    return buf.len;
}

fn sysfsStringLen(buf: []const u8) usize {
    const len = cStringLen(buf);
    if (len > 0 and buf[len - 1] == '\n') return len - 1;
    return len;
}

fn isOctDigit(ch: u8) bool {
    return ch >= '0' and ch <= '7';
}

fn hexNibble(ch: u8) ?u8 {
    return switch (ch) {
        '0'...'9' => ch - '0',
        'a'...'f' => ch - 'a' + 10,
        'A'...'F' => ch - 'A' + 10,
        else => null,
    };
}

fn matchUnescapeSpace(src: []const u8) ?UnescapeMatch {
    if (src.len == 0) return null;
    const value: u8 = switch (src[0]) {
        'n' => '\n',
        'r' => '\r',
        't' => '\t',
        'v' => '\x0b',
        'f' => '\x0c',
        else => return null,
    };
    return .{ .value = value, .consumed = 1 };
}

fn matchUnescapeOctal(src: []const u8) ?UnescapeMatch {
    if (src.len == 0 or !isOctDigit(src[0])) return null;

    var value: u8 = src[0] & 7;
    var consumed: usize = 1;

    while (value < 32 and consumed < 3 and consumed < src.len and isOctDigit(src[consumed])) : (consumed += 1) {
        value = (value << 3) + (src[consumed] & 7);
    }

    return .{ .value = value, .consumed = consumed };
}

fn matchUnescapeHex(src: []const u8) ?UnescapeMatch {
    if (src.len < 2 or src[0] != 'x') return null;

    var value = hexNibble(src[1]) orelse return null;
    var consumed: usize = 2;

    if (src.len > 2) {
        if (hexNibble(src[2])) |next| {
            value = (value << 4) | next;
            consumed += 1;
        }
    }

    return .{ .value = value, .consumed = consumed };
}

fn matchUnescapeSpecial(src: []const u8) ?UnescapeMatch {
    if (src.len == 0) return null;
    const value: u8 = switch (src[0]) {
        '"' => '"',
        '\\' => '\\',
        'a' => '\x07',
        'e' => '\x1b',
        else => return null,
    };
    return .{ .value = value, .consumed = 1 };
}

pub fn skipSpaces(text: []const u8) []const u8 {
    var index: usize = 0;
    while (index < text.len) : (index += 1) {
        const ch = text[index];
        if (ch == 0 or !std.ascii.isWhitespace(ch)) break;
    }
    return text[index..];
}

pub fn skip_spaces(text: []const u8) []const u8 {
    return skipSpaces(text);
}

pub fn trimSpaces(buf: []u8) []u8 {
    if (buf.len == 0) return buf[0..0];

    const string_len = cStringLen(buf);
    var start: usize = 0;
    while (start < string_len and std.ascii.isWhitespace(buf[start])) : (start += 1) {}

    if (start == string_len) {
        buf[0] = 0;
        return buf[0..0];
    }

    var end = string_len;
    while (end > start and std.ascii.isWhitespace(buf[end - 1])) : (end -= 1) {}

    if (end < string_len) {
        buf[end] = 0;
    }

    return buf[start..end];
}

pub fn strim(buf: []u8) []u8 {
    return trimSpaces(buf);
}

pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {
    const lhs_len = sysfsStringLen(lhs);
    const rhs_len = sysfsStringLen(rhs);
    if (lhs_len != rhs_len) return false;
    return std.mem.eql(u8, lhs[0..lhs_len], rhs[0..rhs_len]);
}

pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {
    return sysfsStreq(lhs, rhs);
}

pub fn matchString(haystack: []const ?[]const u8, needle: []const u8) ?usize {
    for (haystack, 0..) |entry, idx| {
        const value = entry orelse break;
        if (std.mem.eql(u8, value[0..cStringLen(value)], needle[0..cStringLen(needle)])) {
            return idx;
        }
    }
    return null;
}

pub fn match_string(haystack: []const ?[]const u8, needle: []const u8) ?usize {
    return matchString(haystack, needle);
}

pub fn sysfsMatchString(haystack: []const ?[]const u8, needle: []const u8) ?usize {
    for (haystack, 0..) |entry, idx| {
        const value = entry orelse break;
        if (sysfsStreq(value, needle)) return idx;
    }
    return null;
}

pub fn __sysfs_match_string(haystack: []const ?[]const u8, needle: []const u8) ?usize {
    return sysfsMatchString(haystack, needle);
}

pub fn stringUnescape(src: []const u8, dst: []u8, size: usize, flags: u32) usize {
    if (dst.len == 0) return 0;

    const limit = if (size == 0) dst.len else @min(size, dst.len);
    if (limit == 0) return 0;

    var src_index: usize = 0;
    var out_index: usize = 0;

    while (src_index < src.len and src[src_index] != 0 and out_index + 1 < limit) {
        const remaining = limit - out_index - 1;
        if (src[src_index] == '\\' and src_index + 1 < src.len and src[src_index + 1] != 0 and remaining > 1) {
            src_index += 1;

            if ((flags & UNESCAPE_SPACE) != 0) {
                if (matchUnescapeSpace(src[src_index..])) |match| {
                    dst[out_index] = match.value;
                    out_index += 1;
                    src_index += match.consumed;
                    continue;
                }
            }

            if ((flags & UNESCAPE_OCTAL) != 0) {
                if (matchUnescapeOctal(src[src_index..])) |match| {
                    dst[out_index] = match.value;
                    out_index += 1;
                    src_index += match.consumed;
                    continue;
                }
            }

            if ((flags & UNESCAPE_HEX) != 0) {
                if (matchUnescapeHex(src[src_index..])) |match| {
                    dst[out_index] = match.value;
                    out_index += 1;
                    src_index += match.consumed;
                    continue;
                }
            }

            if ((flags & UNESCAPE_SPECIAL) != 0) {
                if (matchUnescapeSpecial(src[src_index..])) |match| {
                    dst[out_index] = match.value;
                    out_index += 1;
                    src_index += match.consumed;
                    continue;
                }
            }

            dst[out_index] = '\\';
            out_index += 1;
        }

        dst[out_index] = src[src_index];
        out_index += 1;
        src_index += 1;
    }

    dst[out_index] = 0;
    return out_index;
}

pub fn string_unescape(src: []const u8, dst: []u8, size: usize, flags: u32) usize {
    return stringUnescape(src, dst, size, flags);
}

pub fn stringUnescapeInplace(buf: []u8, flags: u32) usize {
    return stringUnescape(buf, buf, 0, flags);
}

pub fn string_unescape_inplace(buf: []u8, flags: u32) usize {
    return stringUnescapeInplace(buf, flags);
}

pub fn stringUnescapeAny(src: []const u8, dst: []u8, size: usize) usize {
    return stringUnescape(src, dst, size, UNESCAPE_ANY);
}

pub fn string_unescape_any(src: []const u8, dst: []u8, size: usize) usize {
    return stringUnescapeAny(src, dst, size);
}

pub fn stringUnescapeAnyInplace(buf: []u8) usize {
    return stringUnescapeAny(buf, buf, 0);
}

pub fn string_unescape_any_inplace(buf: []u8) usize {
    return stringUnescapeAnyInplace(buf);
}

pub fn memcpyAndPad(dest: []u8, src: []const u8, count: usize, pad: u8) void {
    const bounded_count = @min(count, src.len);
    const copy_len = @min(dest.len, bounded_count);
    @memcpy(dest[0..copy_len], src[0..copy_len]);

    if (dest.len > copy_len) {
        @memset(dest[copy_len..], pad);
    }
}

pub fn memcpy_and_pad(dest: []u8, src: []const u8, count: usize, pad: u8) void {
    memcpyAndPad(dest, src, count, pad);
}

pub fn strreplace(buf: []u8, old: u8, new: u8) usize {
    for (buf, 0..) |*ch, idx| {
        if (ch.* == 0) return idx;
        if (ch.* == old) ch.* = new;
    }
    return buf.len;
}
