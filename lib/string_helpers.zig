const std = @import("std");

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
