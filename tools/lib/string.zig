const std = @import("std");

pub const ParseBoolError = error{Invalid};

pub fn memdup(allocator: std.mem.Allocator, src: []const u8) ![]u8 {
    return allocator.dupe(u8, src);
}

pub fn strtobool(s: ?[]const u8) ParseBoolError!bool {
    const text = s orelse return error.Invalid;
    if (text.len == 0) {
        return error.Invalid;
    }

    switch (text[0]) {
        'y', 'Y', '1' => return true,
        'n', 'N', '0' => return false,
        'o', 'O' => {
            if (text.len < 2) {
                return error.Invalid;
            }

            switch (text[1]) {
                'n', 'N' => return true,
                'f', 'F' => return false,
                else => {},
            }
        },
        else => {},
    }

    return error.Invalid;
}

pub fn strlcpy(dest: []u8, src: []const u8) usize {
    const ret = src.len;
    if (dest.len == 0) {
        return ret;
    }

    const len = if (ret >= dest.len) dest.len - 1 else ret;
    @memcpy(dest[0..len], src[0..len]);
    dest[len] = 0;
    return ret;
}

pub fn skipSpaces(str: []const u8) []const u8 {
    var idx: usize = 0;
    while (idx < str.len and std.ascii.isWhitespace(str[idx])) : (idx += 1) {}
    return str[idx..];
}

pub fn trimSpaces(buf: []u8) []u8 {
    if (buf.len == 0) {
        return buf[0..0];
    }

    var start: usize = 0;
    while (start < buf.len and std.ascii.isWhitespace(buf[start])) : (start += 1) {}
    if (start == buf.len) {
        buf[0] = 0;
        return buf[0..0];
    }

    var end = buf.len;
    while (end > start and std.ascii.isWhitespace(buf[end - 1])) : (end -= 1) {}
    if (end < buf.len) {
        buf[end] = 0;
    }

    return buf[start..end];
}

pub fn removeSpaces(buf: []u8) []u8 {
    var write_idx: usize = 0;
    for (buf, 0..) |ch, read_idx| {
        if (ch != ' ') {
            buf[write_idx] = buf[read_idx];
            write_idx += 1;
        }
    }

    if (write_idx < buf.len) {
        buf[write_idx] = 0;
    }

    return buf[0..write_idx];
}

pub fn replaceChar(buf: []u8, old: u8, new: u8) usize {
    for (buf, 0..) |*ch, idx| {
        if (ch.* == 0) {
            return idx;
        }
        if (ch.* == old) {
            ch.* = new;
        }
    }
    return buf.len;
}

pub fn memchrInv(buf: []const u8, value: u8) ?usize {
    for (buf, 0..) |ch, idx| {
        if (ch != value) {
            return idx;
        }
    }
    return null;
}

fn cStringLen(buf: []const u8) usize {
    for (buf, 0..) |ch, idx| {
        if (ch == 0) {
            return idx;
        }
    }
    return buf.len;
}

pub fn strHasPrefix(str: []const u8, prefix: []const u8) bool {
    const prefix_len = cStringLen(prefix);
    const str_len = cStringLen(str);
    if (prefix_len > str_len) {
        return false;
    }

    return std.mem.eql(u8, str[0..prefix_len], prefix[0..prefix_len]);
}

pub fn str_has_prefix(str: []const u8, prefix: []const u8) bool {
    return strHasPrefix(str, prefix);
}

test "strtobool accepts common Linux forms" {
    try std.testing.expect(try strtobool("y"));
    try std.testing.expect(try strtobool("On"));
    try std.testing.expect(!(try strtobool("0")));
    try std.testing.expect(!(try strtobool("of")));
    try std.testing.expectError(error.Invalid, strtobool("maybe"));
}

test "strlcpy copies and returns the source length" {
    var dst = [_]u8{ 0, 0, 0, 0 };
    try std.testing.expectEqual(@as(usize, 5), strlcpy(&dst, "hello"));
    try std.testing.expectEqualSlices(u8, "hel", dst[0..3]);
    try std.testing.expectEqual(@as(u8, 0), dst[3]);
}

test "skip trim remove and replace spaces work in place" {
    try std.testing.expectEqualStrings("hello", skipSpaces("   hello"));

    var trim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };
    try std.testing.expectEqualStrings("hi", trimSpaces(&trim_buf));

    var remove_buf = [_]u8{ 'a', ' ', 'b', ' ', 'c' };
    try std.testing.expectEqualStrings("abc", removeSpaces(&remove_buf));

    var replace_buf = [_]u8{ 'a', '-', 'b' };
    try std.testing.expectEqual(@as(usize, 3), replaceChar(&replace_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, "a_b", &replace_buf);

    var replace_cstr_buf = [_]u8{ 'a', '-', 0, '-' };
    try std.testing.expectEqual(@as(usize, 2), replaceChar(&replace_cstr_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 0, '-' }, &replace_cstr_buf);
}

test "strHasPrefix honors C-string boundaries" {
    try std.testing.expect(strHasPrefix("prefix", "pre"));
    try std.testing.expect(str_has_prefix("prefix", "prefix"));
    try std.testing.expect(!strHasPrefix("prefix", "suffix"));
    try std.testing.expect(!strHasPrefix("pre", "prefix"));

    const cstr = [_]u8{ 'a', 'b', 0, 'x' };
    const embedded_prefix = [_]u8{ 'a', 'b', 0, 'y' };
    try std.testing.expect(strHasPrefix(&cstr, &embedded_prefix));
}

test "memdup and memchrInv preserve byte content" {
    const allocator = std.testing.allocator;
    const duplicated = try memdup(allocator, "zigux");
    defer allocator.free(duplicated);

    try std.testing.expectEqualStrings("zigux", duplicated);
    try std.testing.expectEqual(@as(?usize, 4), memchrInv("aaaaXaaa", 'a'));
    try std.testing.expectEqual(@as(?usize, null), memchrInv("bbbb", 'b'));
}
