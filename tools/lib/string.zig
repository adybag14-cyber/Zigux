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

pub fn skip_spaces(str: []const u8) []const u8 {
    return skipSpaces(str);
}

pub fn trimSpaces(buf: []u8) []u8 {
    if (buf.len == 0) {
        return buf[0..0];
    }

    var limit: usize = 0;
    while (limit < buf.len and buf[limit] != 0) : (limit += 1) {}

    var start: usize = 0;
    while (start < limit and std.ascii.isWhitespace(buf[start])) : (start += 1) {}
    if (start == limit) {
        buf[0] = 0;
        return buf[0..0];
    }

    var end = limit;
    while (end > start and std.ascii.isWhitespace(buf[end - 1])) : (end -= 1) {}
    if (end < limit) {
        buf[end] = 0;
    }

    return buf[start..end];
}

pub fn strim(buf: []u8) []u8 {
    var end: usize = 0;
    while (end < buf.len and buf[end] != 0) : (end += 1) {}
    return trimSpaces(buf[0..end]);
}

pub fn removeSpaces(buf: []u8) []u8 {
    var write_idx: usize = 0;
    var read_idx: usize = 0;
    while (read_idx < buf.len) : (read_idx += 1) {
        const ch = buf[read_idx];
        if (ch == 0) {
            break;
        }
        if (ch != ' ') {
            buf[write_idx] = ch;
            write_idx += 1;
        }
    }

    if (write_idx < buf.len) {
        buf[write_idx] = 0;
    }

    return buf[0..write_idx];
}

pub fn remove_spaces(buf: []u8) void {
    _ = removeSpaces(buf);
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

pub fn strreplace(buf: []u8, old: u8, new: u8) []u8 {
    const end = replaceChar(buf, old, new);
    return buf[0..end];
}

fn repeatedByteWord(value: u8) u64 {
    var repeated = @as(u64, value);
    repeated |= repeated << 8;
    repeated |= repeated << 16;
    repeated |= repeated << 32;
    return repeated;
}

fn checkBytes8(buf: []const u8, value: u8) ?usize {
    for (buf, 0..) |ch, idx| {
        if (ch != value) {
            return idx;
        }
    }
    return null;
}

pub fn memchrInv(buf: []const u8, value: u8) ?usize {
    if (buf.len <= 16) {
        return checkBytes8(buf, value);
    }

    const prefix = (@intFromPtr(buf.ptr) & 7);
    var start: usize = 0;
    if (prefix != 0) {
        const prefix_bytes = @min(buf.len, 8 - prefix);
        if (checkBytes8(buf[0..prefix_bytes], value)) |idx| {
            return idx;
        }
        start = prefix_bytes;
    }

    const repeated = repeatedByteWord(value);
    var word_start = start;
    while (word_start + 8 <= buf.len) : (word_start += 8) {
        const word = std.mem.readInt(u64, buf[word_start .. word_start + 8][0..8], .little);
        if (word != repeated) {
            return word_start + checkBytes8(buf[word_start .. word_start + 8], value).?;
        }
    }

    if (word_start < buf.len) {
        if (checkBytes8(buf[word_start..], value)) |idx| {
            return word_start + idx;
        }
    }
    return null;
}

pub fn memchr_inv(buf: []const u8, value: u8) ?usize {
    return memchrInv(buf, value);
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
    try std.testing.expectEqualStrings("hello", skip_spaces("   hello"));

    var trim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };
    try std.testing.expectEqualStrings("hi", trimSpaces(&trim_buf));

    var strim_buf = [_]u8{ ' ', 'o', 'k', ' ', '\n', 0 };
    try std.testing.expectEqualStrings("ok", strim(&strim_buf));

    var remove_buf = [_]u8{ 'a', ' ', 'b', ' ', 'c' };
    try std.testing.expectEqualStrings("abc", removeSpaces(&remove_buf));

    var remove_cstr_buf = [_]u8{ 'a', ' ', 'b', 0, ' ', 'x' };
    try std.testing.expectEqualStrings("ab", removeSpaces(&remove_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0, 0, ' ', 'x' }, &remove_cstr_buf);

    var remove_spaces_buf = [_]u8{ 'a', ' ', 'b', 0, ' ', 'x' };
    remove_spaces(&remove_spaces_buf);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0, 0, ' ', 'x' }, &remove_spaces_buf);

    var replace_buf = [_]u8{ 'a', '-', 'b' };
    try std.testing.expectEqual(@as(usize, 3), replaceChar(&replace_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, "a_b", &replace_buf);

    var replace_cstr_buf = [_]u8{ 'a', '-', 0, '-' };
    try std.testing.expectEqual(@as(usize, 2), replaceChar(&replace_cstr_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 0, '-' }, &replace_cstr_buf);

    var strreplace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqualStrings("a_b", strreplace(strreplace_buf[0 .. strreplace_buf.len - 1], '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 'b', 0, '-' }, &strreplace_buf);
}

test "trimSpaces and strim stop at the first embedded NUL" {
    var trim_cstr_buf = [_]u8{ ' ', 'a', 0, 'x', '\n' };
    try std.testing.expectEqualStrings("a", trimSpaces(&trim_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'a', 0, 'x', '\n' }, &trim_cstr_buf);

    var strim_cstr_buf = [_]u8{ '\t', 'o', 'k', 0, 'x', '\n' };
    try std.testing.expectEqualStrings("ok", strim(&strim_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ '\t', 'o', 'k', 0, 'x', '\n' }, &strim_cstr_buf);
}

test "memdup and memchrInv preserve byte content" {
    const allocator = std.testing.allocator;
    const duplicated = try memdup(allocator, "zigux");
    defer allocator.free(duplicated);

    try std.testing.expectEqualStrings("zigux", duplicated);
    try std.testing.expectEqual(@as(?usize, 4), memchrInv("aaaaXaaa", 'a'));
    try std.testing.expectEqual(@as(?usize, 4), memchr_inv("aaaaXaaa", 'a'));
    try std.testing.expectEqual(@as(?usize, null), memchrInv("bbbb", 'b'));
}

test "memchrInv scans aligned and misaligned long buffers" {
    var aligned = [_]u8{'a'} ** 24;
    aligned[17] = 'X';
    try std.testing.expectEqual(@as(?usize, 17), memchrInv(&aligned, 'a'));

    var misaligned_storage = [_]u8{'a'} ** 25;
    misaligned_storage[18] = 'X';
    try std.testing.expectEqual(@as(?usize, 17), memchrInv(misaligned_storage[1..], 'a'));
}

test "memchrInv catches prefix and trailing remainder mismatches" {
    var prefix_storage = [_]u8{'a'} ** 25;
    prefix_storage[3] = 'X';
    try std.testing.expectEqual(@as(?usize, 2), memchrInv(prefix_storage[1..], 'a'));

    var trailing_storage = [_]u8{'a'} ** 26;
    trailing_storage[25] = 'X';
    try std.testing.expectEqual(@as(?usize, 24), memchrInv(trailing_storage[1..], 'a'));
}
