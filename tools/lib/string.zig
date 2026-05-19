const std = @import("std");
const cmdline = @import("cmdline.zig");

pub const ParseBoolError = error{Invalid};

pub const MemparseResult = cmdline.MemparseResult;

const strscpy_e2big: isize = -7;

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
    const ret = cStringLen(src);
    if (dest.len == 0) {
        return ret;
    }

    const len = if (ret >= dest.len) dest.len - 1 else ret;
    @memcpy(dest[0..len], src[0..len]);
    dest[len] = 0;
    return ret;
}

pub fn strscpy(dest: []u8, src: []const u8) isize {
    if (dest.len == 0) {
        return strscpy_e2big;
    }

    const src_len = cStringLen(src);
    const copy_len = @min(src_len, dest.len - 1);
    if (copy_len != 0) {
        @memcpy(dest[0..copy_len], src[0..copy_len]);
    }
    dest[copy_len] = 0;

    if (copy_len != src_len) {
        return strscpy_e2big;
    }

    return @intCast(copy_len);
}

pub fn strscpyPad(dest: []u8, src: []const u8) isize {
    const copied = strscpy(dest, src);
    if (copied >= 0) {
        const copied_len: usize = @intCast(copied);
        const pad_start = copied_len + 1;
        if (pad_start < dest.len) {
            @memset(dest[pad_start..], 0);
        }
    }
    return copied;
}

pub fn strscpy_pad(dest: []u8, src: []const u8) isize {
    return strscpyPad(dest, src);
}

pub fn skipSpaces(str: []const u8) []const u8 {
    var idx: usize = 0;
    while (idx < str.len and std.ascii.isWhitespace(str[idx])) : (idx += 1) {}
    return str[idx..];
}

pub fn skip_spaces(str: []const u8) []const u8 {
    return skipSpaces(str);
}

pub fn strEq(lhs: []const u8, rhs: []const u8) bool {
    const lhs_len = cStringLen(lhs);
    const rhs_len = cStringLen(rhs);
    if (lhs_len != rhs_len) {
        return false;
    }

    return std.mem.eql(u8, lhs[0..lhs_len], rhs[0..rhs_len]);
}

pub fn streq(lhs: []const u8, rhs: []const u8) bool {
    return strEq(lhs, rhs);
}

pub fn trimSpaces(buf: []u8) []u8 {
    if (buf.len == 0) {
        return buf[0..0];
    }

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

pub fn strstrip(buf: []u8) []u8 {
    return trimSpaces(buf);
}

pub fn removeSpaces(buf: []u8) []u8 {
    var read_idx: usize = 0;
    var write_idx: usize = 0;
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

pub fn remove_spaces(buf: []u8) []u8 {
    return removeSpaces(buf);
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

pub fn strreplace(buf: []u8, old: u8, new: u8) usize {
    return replaceChar(buf, old, new);
}

fn repeatByte(value: u8) usize {
    var repeated: usize = 0;
    var idx: usize = 0;
    while (idx < @sizeOf(usize)) : (idx += 1) {
        repeated = (repeated << 8) | @as(usize, value);
    }
    return repeated;
}

fn firstDirtyByteIndex(diff: usize) usize {
    return switch (@import("builtin").cpu.arch.endian()) {
        .little => @ctz(diff) / 8,
        .big => @clz(diff) / 8,
    };
}

pub fn memchrInv(buf: []const u8, value: u8) ?usize {
    const word_bytes = @sizeOf(usize);
    var idx: usize = 0;

    if (buf.len >= word_bytes * 2) {
        const repeated = repeatByte(value);

        while (idx + word_bytes <= buf.len) : (idx += word_bytes) {
            const word_ptr: *align(1) const usize = @ptrCast(buf[idx .. idx + word_bytes].ptr);
            const diff = word_ptr.* ^ repeated;
            if (diff != 0) {
                return idx + firstDirtyByteIndex(diff);
            }
        }
    }

    while (idx < buf.len) : (idx += 1) {
        if (buf[idx] != value) {
            return idx;
        }
    }
    return null;
}

pub fn memchr_inv(buf: []const u8, value: u8) ?usize {
    return memchrInv(buf, value);
}

fn cStringLen(buf: []const u8) usize {
    for (buf, 0..) |ch, idx| {
        if (ch == 0) {
            return idx;
        }
    }
    return buf.len;
}

pub fn strnlen(buf: []const u8, count: usize) usize {
    return @min(cStringLen(buf), @min(count, buf.len));
}

fn sysfsStringLen(buf: []const u8) usize {
    const len = cStringLen(buf);
    if (len > 0 and buf[len - 1] == '\n') {
        return len - 1;
    }
    return len;
}

pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {
    const lhs_len = sysfsStringLen(lhs);
    const rhs_len = sysfsStringLen(rhs);
    if (lhs_len != rhs_len) {
        return false;
    }

    return std.mem.eql(u8, lhs[0..lhs_len], rhs[0..rhs_len]);
}

pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {
    return sysfsStreq(lhs, rhs);
}

pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {
    for (haystack, 0..) |entry, idx| {
        if (sysfsStreq(entry, needle)) {
            return idx;
        }
    }
    return null;
}

pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {
    return sysfsMatchString(haystack, needle);
}

pub fn matchString(haystack: []const []const u8, needle: []const u8) ?usize {
    for (haystack, 0..) |entry, idx| {
        if (streq(entry, needle)) {
            return idx;
        }
    }
    return null;
}

pub fn match_string(haystack: []const []const u8, needle: []const u8) ?usize {
    return matchString(haystack, needle);
}

pub fn memparse(text: []const u8) MemparseResult {
    return cmdline.memparse(text);
}

pub fn strHasPrefix(str: []const u8, prefix: []const u8) usize {
    const prefix_len = cStringLen(prefix);
    const str_len = cStringLen(str);
    if (prefix_len > str_len) {
        return 0;
    }

    if (!std.mem.eql(u8, str[0..prefix_len], prefix[0..prefix_len])) {
        return 0;
    }

    return prefix_len;
}

pub fn str_has_prefix(str: []const u8, prefix: []const u8) usize {
    return strHasPrefix(str, prefix);
}

pub fn strstarts(str: []const u8, prefix: []const u8) bool {
    return strHasPrefix(str, prefix) == cStringLen(prefix);
}

pub fn strHasSuffix(str: []const u8, suffix: []const u8) usize {
    const suffix_len = cStringLen(suffix);
    if (suffix_len == 0) {
        return 0;
    }

    const str_len = cStringLen(str);
    if (suffix_len > str_len) {
        return 0;
    }

    const start = str_len - suffix_len;
    if (!std.mem.eql(u8, str[start..str_len], suffix[0..suffix_len])) {
        return 0;
    }

    return suffix_len;
}

pub fn str_has_suffix(str: []const u8, suffix: []const u8) usize {
    return strHasSuffix(str, suffix);
}

pub fn strEndsWith(str: []const u8, suffix: []const u8) bool {
    return strHasSuffix(str, suffix) == cStringLen(suffix);
}

pub fn str_ends_with(str: []const u8, suffix: []const u8) bool {
    return strEndsWith(str, suffix);
}

pub fn strends(str: []const u8, suffix: []const u8) bool {
    return strEndsWith(str, suffix);
}

pub fn kbasename(path: []const u8) []const u8 {
    const path_len = cStringLen(path);
    const visible = path[0..path_len];
    const slash_idx = std.mem.lastIndexOfScalar(u8, visible, '/') orelse return visible;
    return visible[slash_idx + 1 ..];
}

pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {
    const scan_len = @min(count, buf.len);
    var idx: usize = 0;
    while (idx < scan_len) : (idx += 1) {
        const ch = buf[idx];
        if (ch == needle) {
            return idx;
        }
        if (ch == 0) {
            return null;
        }
    }
    return null;
}

pub fn strchr(buf: []const u8, needle: u8) ?usize {
    return strnchr(buf, buf.len, needle);
}

pub fn strrchr(buf: []const u8, needle: u8) ?usize {
    const string_len = cStringLen(buf);
    if (needle == 0) {
        if (string_len < buf.len) {
            return string_len;
        }
        return null;
    }

    var idx = string_len;
    while (idx > 0) {
        idx -= 1;
        if (buf[idx] == needle) {
            return idx;
        }
    }
    return null;
}

pub fn strpbrk(buf: []const u8, accept: []const u8) ?usize {
    const string_len = cStringLen(buf);
    const accept_len = cStringLen(accept);

    var idx: usize = 0;
    while (idx < string_len) : (idx += 1) {
        if (std.mem.indexOfScalar(u8, accept[0..accept_len], buf[idx]) != null) {
            return idx;
        }
    }

    return null;
}

pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {
    const scan_len = @min(count, buf.len);
    var idx: usize = 0;
    while (idx < scan_len) : (idx += 1) {
        const ch = buf[idx];
        if (ch == needle or ch == 0) {
            return idx;
        }
    }
    return scan_len;
}

pub fn strnchrnul(buf: []const u8, count: usize, needle: u8) usize {
    return strnchrNul(buf, count, needle);
}

pub fn strchrNul(buf: []const u8, needle: u8) usize {
    return strnchrNul(buf, buf.len, needle);
}

pub fn strchrnul(buf: []const u8, needle: u8) usize {
    return strchrNul(buf, needle);
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

    const src_cstr = [_]u8{ 'o', 'k', 0, 'x', 'y' };
    var cstr_dst = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(usize, 2), strlcpy(&cstr_dst, &src_cstr));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0xaa }, &cstr_dst);

    var tiny_cstr_dst = [_]u8{ 0xaa, 0xaa };
    try std.testing.expectEqual(@as(usize, 2), strlcpy(&tiny_cstr_dst, &src_cstr));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 0 }, &tiny_cstr_dst);
}

test "strscpy keeps NUL termination and reports truncation with -E2BIG" {
    var copied = [_]u8{0xaa} ** 5;
    try std.testing.expectEqual(@as(isize, 2), strscpy(&copied, "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0xaa, 0xaa }, &copied);

    var truncated = [_]u8{0xaa} ** 4;
    try std.testing.expectEqual(strscpy_e2big, strscpy(&truncated, "hello"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'e', 'l', 0 }, &truncated);

    var zero_sized = [_]u8{};
    try std.testing.expectEqual(strscpy_e2big, strscpy(&zero_sized, "hello"));

    const src_cstr = [_]u8{ 'o', 'k', 0, 'x', 'y' };
    var cstr_dst = [_]u8{0xaa} ** 6;
    try std.testing.expectEqual(@as(isize, 2), strscpy(&cstr_dst, &src_cstr));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0xaa, 0xaa, 0xaa }, &cstr_dst);
}

test "strscpyPad zero-pads the tail after a short source" {
    var padded = [_]u8{0xaa} ** 6;
    try std.testing.expectEqual(@as(isize, 2), strscpyPad(&padded, "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0, 0 }, &padded);
}

test "strscpyPad stops at embedded NUL and pads the remaining tail" {
    const src_cstr = [_]u8{ 'o', 'k', 0, 'x', 'y' };
    var padded = [_]u8{0xaa} ** 6;
    try std.testing.expectEqual(@as(isize, 2), strscpyPad(&padded, &src_cstr));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &padded);
}

test "strscpyPad preserves strscpy truncation semantics" {
    var truncated = [_]u8{0xaa} ** 4;
    try std.testing.expectEqual(strscpy_e2big, strscpyPad(&truncated, "hello"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'e', 'l', 0 }, &truncated);

    var zero_sized = [_]u8{};
    try std.testing.expectEqual(strscpy_e2big, strscpyPad(&zero_sized, "hello"));
}

test "strscpy_pad mirrors strscpyPad padding semantics" {
    var padded = [_]u8{0xaa} ** 5;
    try std.testing.expectEqual(@as(isize, 2), strscpy_pad(&padded, "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0 }, &padded);
}

test "strscpy and strscpyPad keep one-byte destinations terminated" {
    var strscpy_empty = [_]u8{0xaa};
    try std.testing.expectEqual(@as(isize, 0), strscpy(&strscpy_empty, ""));
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, &strscpy_empty);

    var strscpy_truncated = [_]u8{0xaa};
    try std.testing.expectEqual(strscpy_e2big, strscpy(&strscpy_truncated, "x"));
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, &strscpy_truncated);

    var strscpy_pad_empty = [_]u8{0xaa};
    try std.testing.expectEqual(@as(isize, 0), strscpyPad(&strscpy_pad_empty, ""));
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, &strscpy_pad_empty);

    var strscpy_pad_truncated = [_]u8{0xaa};
    try std.testing.expectEqual(strscpy_e2big, strscpyPad(&strscpy_pad_truncated, "x"));
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, &strscpy_pad_truncated);

    var alias_truncated = [_]u8{0xaa};
    try std.testing.expectEqual(strscpy_e2big, strscpy_pad(&alias_truncated, "x"));
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, &alias_truncated);
}

test "streq matches C-string equality semantics" {
    try std.testing.expect(strEq("zigux", "zigux"));
    try std.testing.expect(streq("zigux", "zigux"));
    try std.testing.expect(streq("", ""));
    try std.testing.expect(!streq("zigux", "zig"));
    try std.testing.expect(!streq("zigux", "Zigux"));

    const source = [_]u8{ 'z', 'i', 'g', 0, 'x' };
    const embedded_match = [_]u8{ 'z', 'i', 'g', 0, 'u', 'x' };
    const embedded_miss = [_]u8{ 'z', 'i', 'p', 0, 'u', 'x' };
    try std.testing.expect(streq(&source, &embedded_match));
    try std.testing.expect(!streq(&source, &embedded_miss));
}

test "skip trim remove and replace spaces work in place" {
    try std.testing.expectEqualStrings("hello", skipSpaces("   hello"));
    try std.testing.expectEqualStrings("hello", skip_spaces("   hello"));

    var trim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };
    try std.testing.expectEqualStrings("hi", trimSpaces(&trim_buf));

    var strim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };
    try std.testing.expectEqualStrings("hi", strim(&strim_buf));

    var strstrip_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };
    try std.testing.expectEqualStrings("hi", strstrip(&strstrip_buf));

    var trim_cstr_buf = [_]u8{ ' ', 'h', 'i', ' ', '\n', 0, 'x', 'y' };
    try std.testing.expectEqualStrings("hi", trimSpaces(&trim_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'h', 'i', 0, '\n', 0, 'x', 'y' }, &trim_cstr_buf);

    var strim_cstr_buf = [_]u8{ ' ', 'h', 'i', ' ', '\n', 0, 'x', 'y' };
    try std.testing.expectEqualStrings("hi", strim(&strim_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'h', 'i', 0, '\n', 0, 'x', 'y' }, &strim_cstr_buf);

    var remove_buf = [_]u8{ 'a', ' ', 'b', ' ', 'c' };
    try std.testing.expectEqualStrings("abc", removeSpaces(&remove_buf));

    var remove_cstr_buf = [_]u8{ 'a', ' ', 0, 'b', ' ', 'c' };
    try std.testing.expectEqualStrings("a", removeSpaces(&remove_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 0, 0, 'b', ' ', 'c' }, &remove_cstr_buf);

    var remove_alias_buf = [_]u8{ ' ', 'a', ' ', 'b', 0, 'x' };
    try std.testing.expectEqualStrings("ab", remove_spaces(&remove_alias_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0, 'b', 0, 'x' }, &remove_alias_buf);

    var replace_buf = [_]u8{ 'a', '-', 'b' };
    try std.testing.expectEqual(@as(usize, 3), replaceChar(&replace_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, "a_b", &replace_buf);

    var replace_cstr_buf = [_]u8{ 'a', '-', 0, '-' };
    try std.testing.expectEqual(@as(usize, 2), replaceChar(&replace_cstr_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 0, '-' }, &replace_cstr_buf);
}

test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace" {
    var trim_buf = [_]u8{ ' ', 'a', 'b', 0, ' ', '\t', 'x' };
    try std.testing.expectEqualStrings("ab", trimSpaces(&trim_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'a', 'b', 0, ' ', '\t', 'x' }, &trim_buf);

    var strim_buf = [_]u8{ ' ', 'a', 'b', 0, ' ', '\n', 'y' };
    try std.testing.expectEqualStrings("ab", strim(&strim_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'a', 'b', 0, ' ', '\n', 'y' }, &strim_buf);

    var strstrip_buf = [_]u8{ ' ', 'a', 'b', 0, ' ', '\n', 'z' };
    try std.testing.expectEqualStrings("ab", strstrip(&strstrip_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'a', 'b', 0, ' ', '\n', 'z' }, &strstrip_buf);
}

test "phase 1 string replaceChar stops at embedded NUL" {
    var replace_cstr_buf = [_]u8{ 'a', '-', 0, '-', 'z' };
    try std.testing.expectEqual(@as(usize, 2), replaceChar(&replace_cstr_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 0, '-', 'z' }, &replace_cstr_buf);
}

test "strreplace mirrors replaceChar C-string semantics" {
    var replace_buf = [_]u8{ 'a', '-', 'b' };
    try std.testing.expectEqual(@as(usize, 3), strreplace(&replace_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, "a_b", &replace_buf);

    var replace_cstr_buf = [_]u8{ 'a', '-', 0, '-', 'z' };
    try std.testing.expectEqual(@as(usize, 2), strreplace(&replace_cstr_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 0, '-', 'z' }, &replace_cstr_buf);
}

test "strHasPrefix returns the matched prefix length with C-string semantics" {
    try std.testing.expectEqual(@as(usize, 3), strHasPrefix("prefix", "pre"));
    try std.testing.expectEqual(@as(usize, 6), strHasPrefix("prefix", "prefix"));
    try std.testing.expectEqual(@as(usize, 0), strHasPrefix("prefix", "suffix"));
    try std.testing.expectEqual(@as(usize, 0), strHasPrefix("pre", "prefix"));
    try std.testing.expectEqual(@as(usize, 0), strHasPrefix("prefix", ""));
    try std.testing.expectEqual(@as(usize, 3), str_has_prefix("prefix", "pre"));

    const cstr = [_]u8{ 'a', 'b', 0, 'x' };
    const embedded_prefix = [_]u8{ 'a', 'b', 0, 'y' };
    try std.testing.expectEqual(@as(usize, 2), strHasPrefix(&cstr, &embedded_prefix));
}

test "strHasSuffix returns the matched suffix length with C-string semantics" {
    try std.testing.expectEqual(@as(usize, 3), strHasSuffix("prefix", "fix"));
    try std.testing.expectEqual(@as(usize, 6), strHasSuffix("prefix", "prefix"));
    try std.testing.expectEqual(@as(usize, 0), strHasSuffix("prefix", "suffix"));
    try std.testing.expectEqual(@as(usize, 0), strHasSuffix("pre", "prefix"));
    try std.testing.expectEqual(@as(usize, 0), strHasSuffix("prefix", ""));
    try std.testing.expectEqual(@as(usize, 3), str_has_suffix("prefix", "fix"));

    const cstr = [_]u8{ 'a', 'b', 0, 'x' };
    const embedded_suffix = [_]u8{ 'a', 'b', 0, 'y' };
    try std.testing.expectEqual(@as(usize, 2), strHasSuffix(&cstr, &embedded_suffix));
}

test "strstarts mirrors the header-level prefix helper" {
    try std.testing.expect(strstarts("prefix", "pre"));
    try std.testing.expect(strstarts("prefix", "prefix"));
    try std.testing.expect(strstarts("prefix", ""));
    try std.testing.expect(!strstarts("prefix", "suffix"));
    try std.testing.expect(!strstarts("pre", "prefix"));

    const cstr = [_]u8{ 'a', 'b', 0, 'x' };
    const prefix = [_]u8{ 'a', 'b', 0, 'y' };
    try std.testing.expect(strstarts(&cstr, &prefix));
}

test "strEndsWith honors C-string boundaries" {
    try std.testing.expect(strEndsWith("prefix", "fix"));
    try std.testing.expect(str_ends_with("prefix", "prefix"));
    try std.testing.expect(strends("prefix", "fix"));
    try std.testing.expect(strEndsWith("prefix", ""));
    try std.testing.expect(!strEndsWith("prefix", "suffix"));
    try std.testing.expect(!strEndsWith("pre", "prefix"));

    const cstr = [_]u8{ 'a', 'b', 0, 'x' };
    const embedded_suffix = [_]u8{ 'a', 'b', 0, 'y' };
    const trailing_miss = [_]u8{ 'x', 0, 'y' };
    try std.testing.expect(strEndsWith(&cstr, &embedded_suffix));
    try std.testing.expect(strends(&cstr, &embedded_suffix));
    try std.testing.expect(!strEndsWith(&cstr, &trailing_miss));
    try std.testing.expect(!strends(&cstr, &trailing_miss));
}

test "kbasename returns the final path component with C-string semantics" {
    try std.testing.expectEqualStrings("file.txt", kbasename("dir/file.txt"));
    try std.testing.expectEqualStrings("file.txt", kbasename("file.txt"));
    try std.testing.expectEqualStrings("", kbasename("/"));
    try std.testing.expectEqualStrings("", kbasename("dir/"));

    const embedded_nul = [_]u8{ '/', 't', 'm', 'p', '/', 'o', 'k', 0, '/', 'b', 'a', 'd' };
    try std.testing.expectEqualStrings("ok", kbasename(&embedded_nul));
}

test "sysfsStreq treats trailing newline and NUL as equivalent" {
    try std.testing.expect(sysfsStreq("zigux\n", "zigux"));
    try std.testing.expect(sysfsStreq("zigux", "zigux\n"));
    try std.testing.expect(sysfsStreq("zigux\n", "zigux\n"));
    try std.testing.expect(!sysfsStreq("zig\nux", "zigux"));
    try std.testing.expect(!sysfsStreq("zigux\nmore", "zigux"));

    const newline = [_]u8{ 'o', 'k', '\n', 0, 'x' };
    const nul = [_]u8{ 'o', 'k', 0, 'y' };
    try std.testing.expect(sysfsStreq(&newline, &nul));
}

test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence" {
    try std.testing.expect(sysfs_streq("zigux\n", "zigux"));
    try std.testing.expect(sysfs_streq("zigux", "zigux\n"));
    try std.testing.expect(!sysfs_streq("zigux\nmore", "zigux"));
}

test "sysfsMatchString finds newline-aware matches and preserves first-match order" {
    const haystack = [_][]const u8{
        "disabled",
        "auto\n",
        "manual",
        "auto",
    };
    try std.testing.expectEqual(@as(?usize, 1), sysfsMatchString(&haystack, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), sysfsMatchString(&haystack, "auto\n"));

    const nul_terminated = [_]u8{ 'm', 'a', 'n', 'u', 'a', 'l', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, 2), sysfsMatchString(&haystack, &nul_terminated));
    try std.testing.expectEqual(@as(?usize, null), sysfsMatchString(&haystack, "missing"));
}

test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists" {
    const haystack = [_][]const u8{
        "first",
        "second\n",
    };
    const empty = [_][]const u8{};

    try std.testing.expectEqual(@as(?usize, 1), sysfs_match_string(&haystack, "second"));
    try std.testing.expectEqual(@as(?usize, null), sysfs_match_string(&empty, "second"));
}

test "matchString finds C-string matches and preserves first-match order" {
    const haystack = [_][]const u8{
        "disabled",
        "manual",
        "manual",
        "auto",
    };
    try std.testing.expectEqual(@as(?usize, 1), matchString(&haystack, "manual"));

    const nul_terminated = [_]u8{ 'a', 'u', 't', 'o', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, 3), matchString(&haystack, &nul_terminated));
    try std.testing.expectEqual(@as(?usize, null), matchString(&haystack, "missing"));
}

test "match_string mirrors matchString for empty and matched lists" {
    const haystack = [_][]const u8{
        "first",
        "second",
    };
    const empty = [_][]const u8{};

    try std.testing.expectEqual(@as(?usize, 1), match_string(&haystack, "second"));
    try std.testing.expectEqual(@as(?usize, null), match_string(&empty, "second"));
}

test "memdup and memchrInv preserve byte content" {
    const allocator = std.testing.allocator;
    const duplicated = try memdup(allocator, "zigux");
    defer allocator.free(duplicated);

    try std.testing.expectEqualStrings("zigux", duplicated);
    try std.testing.expectEqual(@as(?usize, 4), memchrInv("aaaaXaaa", 'a'));
    try std.testing.expectEqual(@as(?usize, null), memchrInv("bbbb", 'b'));

    const fully_dirty = [_]u8{'b'} ** (@sizeOf(usize) * 2);
    try std.testing.expectEqual(@as(?usize, 0), memchrInv(&fully_dirty, 'a'));
}

test "memchr_inv mirrors memchrInv byte-search semantics" {
    try std.testing.expectEqual(memchrInv("aaaaXaaa", 'a'), memchr_inv("aaaaXaaa", 'a'));
    try std.testing.expectEqual(memchrInv("bbbb", 'b'), memchr_inv("bbbb", 'b'));
}

test "memchrInv keeps long-buffer first-dirty-byte results stable" {
    var middle_dirty = [_]u8{'a'} ** 129;
    middle_dirty[64] = 'X';
    try std.testing.expectEqual(@as(?usize, 64), memchrInv(&middle_dirty, 'a'));

    var tail_dirty = [_]u8{'a'} ** 129;
    tail_dirty[128] = 'X';
    try std.testing.expectEqual(@as(?usize, 128), memchrInv(&tail_dirty, 'a'));

    var head_dirty = [_]u8{'a'} ** 129;
    head_dirty[0] = 'X';
    try std.testing.expectEqual(@as(?usize, 0), memchrInv(&head_dirty, 'a'));

    const clean = [_]u8{'a'} ** 192;
    try std.testing.expectEqual(@as(?usize, null), memchrInv(&clean, 'a'));
}

test "memchrInv follows the earliest dirty byte as long buffers change" {
    var moving_dirty = [_]u8{'a'} ** 160;

    moving_dirty[64] = 'X';
    moving_dirty[96] = 'Y';
    try std.testing.expectEqual(@as(?usize, 64), memchrInv(&moving_dirty, 'a'));

    moving_dirty[64] = 'a';
    try std.testing.expectEqual(@as(?usize, 96), memchrInv(&moving_dirty, 'a'));

    moving_dirty[96] = 'a';
    try std.testing.expectEqual(@as(?usize, null), memchrInv(&moving_dirty, 'a'));
}

test "memchrInv dirty-word shortcut handles zero-value scans at word boundaries" {
    var word_aligned = [_]u8{0} ** 80;
    word_aligned[64] = 0x7f;
    try std.testing.expectEqual(@as(?usize, 64), memchrInv(&word_aligned, 0));
}

test "memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment" {
    var backing = [_]u8{0} ** 96;
    for (0..8) |prefix| {
        @memset(backing[0..], 0);
        const slice = backing[prefix .. prefix + 33];
        slice[17] = 0x7f;
        slice[25] = 0x33;
        try std.testing.expectEqual(@as(?usize, 17), memchrInv(slice, 0));
    }
}

test "memchrInv keeps the earliest dirty byte for long non-zero scans across alignments" {
    const word_bytes = @sizeOf(usize);
    var backing = [_]u8{0xaa} ** (word_bytes * 5);

    for (0..word_bytes) |prefix| {
        const slice = backing[prefix .. prefix + (word_bytes * 2) + 1];
        for (0..slice.len) |dirty_idx| {
            @memset(backing[0..], 0xaa);
            slice[dirty_idx] = 0x11;
            slice[slice.len - 1] = 0x33;
            try std.testing.expectEqual(@as(?usize, dirty_idx), memchrInv(slice, 0xaa));
        }
    }
}

test "memchrInv keeps the earliest dirty byte for long zero-value scans across alignments" {
    const word_bytes = @sizeOf(usize);
    var backing = [_]u8{0} ** (word_bytes * 5);

    for (0..word_bytes) |prefix| {
        const slice = backing[prefix .. prefix + (word_bytes * 2) + 1];
        for (0..slice.len) |dirty_idx| {
            @memset(backing[0..], 0);
            slice[dirty_idx] = 0x7f;
            slice[slice.len - 1] = 0x33;
            try std.testing.expectEqual(@as(?usize, dirty_idx), memchrInv(slice, 0));
        }
    }
}

test "memchrInv short zero-value scans stay byte-accurate" {
    var short_zero_scan = [_]u8{ 0, 0, 0x7f, 0 };
    try std.testing.expectEqual(@as(?usize, 2), memchrInv(&short_zero_scan, 0));
    short_zero_scan[2] = 0;
    try std.testing.expectEqual(@as(?usize, null), memchrInv(&short_zero_scan, 0));
}

test "memchrInv keeps the earliest dirty byte across the fast-path cutoff" {
    const word_bytes = @sizeOf(usize);
    const cutoff = word_bytes * 2;

    var non_zero_backing = [_]u8{0xaa} ** (word_bytes * 2);
    for (0..2) |extra| {
        const len = (cutoff - 1) + extra;

        @memset(non_zero_backing[0..], 0xaa);
        try std.testing.expectEqual(@as(?usize, null), memchrInv(non_zero_backing[0..len], 0xaa));

        for (0..len) |dirty_idx| {
            @memset(non_zero_backing[0..], 0xaa);
            non_zero_backing[dirty_idx] = 0x11;
            try std.testing.expectEqual(@as(?usize, dirty_idx), memchrInv(non_zero_backing[0..len], 0xaa));
        }
    }

    var zero_backing = [_]u8{0} ** (word_bytes * 2);
    for (0..2) |extra| {
        const len = (cutoff - 1) + extra;

        @memset(zero_backing[0..], 0);
        try std.testing.expectEqual(@as(?usize, null), memchrInv(zero_backing[0..len], 0));

        for (0..len) |dirty_idx| {
            @memset(zero_backing[0..], 0);
            zero_backing[dirty_idx] = 0x7f;
            try std.testing.expectEqual(@as(?usize, dirty_idx), memchrInv(zero_backing[0..len], 0));
        }
    }
}

test "memparse handles decimal hexadecimal octal and suffixes" {
    const decimal = memparse("64K rest");
    try std.testing.expectEqual(@as(u64, 64 << 10), decimal.value);
    try std.testing.expectEqualStrings(" rest", decimal.rest);

    const hexadecimal = memparse("0x20M");
    try std.testing.expectEqual(@as(u64, 0x20 << 20), hexadecimal.value);
    try std.testing.expectEqualStrings("", hexadecimal.rest);

    const octal = memparse("010K");
    try std.testing.expectEqual(@as(u64, 8 << 10), octal.value);
    try std.testing.expectEqualStrings("", octal.rest);

    const binary_unit = memparse("64KiB rest");
    const cmdline_binary_unit = cmdline.memparse("64KiB rest");
    try std.testing.expectEqual(cmdline_binary_unit.value, binary_unit.value);
    try std.testing.expectEqualStrings(cmdline_binary_unit.rest, binary_unit.rest);
}

test "memparse keeps original rest when sign is not followed by digits" {
    const negative_invalid = memparse("-xyz");
    try std.testing.expectEqual(@as(u64, 0), negative_invalid.value);
    try std.testing.expectEqualStrings("-xyz", negative_invalid.rest);

    const positive_invalid = memparse("+nope");
    try std.testing.expectEqual(@as(u64, 0), positive_invalid.value);
    try std.testing.expectEqualStrings("+nope", positive_invalid.rest);
}

test "memparse saturates signed overflow instead of trapping" {
    const positive = memparse("9223372036854775808");
    try std.testing.expectEqual(@as(u64, std.math.maxInt(i64)), positive.value);
    try std.testing.expectEqualStrings("", positive.rest);

    const negative = memparse("-9223372036854775809");
    try std.testing.expectEqual(@as(u64, 0x8000000000000000), negative.value);
    try std.testing.expectEqualStrings("", negative.rest);
}

test "memparse clamps explicit positive signed overflow" {
    const positive = memparse("+9223372036854775808");
    try std.testing.expectEqual(@as(u64, std.math.maxInt(i64)), positive.value);
    try std.testing.expectEqualStrings("", positive.rest);

    const suffixed = memparse("+9223372036854775808Ktail");
    try std.testing.expectEqual(@as(u64, std.math.maxInt(i64)), suffixed.value);
    try std.testing.expectEqualStrings("tail", suffixed.rest);

    const cmdline_suffixed = cmdline.memparse("+9223372036854775808Ktail");
    try std.testing.expectEqual(cmdline_suffixed.value, suffixed.value);
    try std.testing.expectEqualStrings(cmdline_suffixed.rest, suffixed.rest);
}

test "memparse keeps signed values and their trailing rest aligned" {
    const negative = memparse("-17 tail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -17))), negative.value);
    try std.testing.expectEqualStrings(" tail", negative.rest);

    const positive = memparse("+42done");
    try std.testing.expectEqual(@as(u64, 42), positive.value);
    try std.testing.expectEqualStrings("done", positive.rest);
}

test "memparse consumes suffix after saturation" {
    const saturated = memparse("18446744073709551615Ktail");
    try std.testing.expectEqual(std.math.maxInt(u64), saturated.value);
    try std.testing.expectEqualStrings("tail", saturated.rest);
}

test "memparse applies suffixes before signed clamping" {
    const negative = memparse("-2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative.value);
    try std.testing.expectEqualStrings("tail", negative.rest);

    const positive = memparse("+3Mmore");
    try std.testing.expectEqual(@as(u64, 3 << 20), positive.value);
    try std.testing.expectEqualStrings("more", positive.rest);
}

test "strchr mirrors full-length C-string searches" {
    try std.testing.expectEqual(@as(?usize, 1), strchr("abcd", 'b'));
    try std.testing.expectEqual(@as(?usize, null), strchr("abcd", 'z'));

    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'b' };
    try std.testing.expectEqual(@as(?usize, 1), strchr(&cstr, 'b'));
    try std.testing.expectEqual(@as(?usize, null), strchr(&cstr, 'c'));
    try std.testing.expectEqual(@as(?usize, 2), strchr(&cstr, 0));
}

test "strrchr finds the last in-range match with C-string semantics" {
    try std.testing.expectEqual(@as(?usize, 3), strrchr("abca", 'a'));
    try std.testing.expectEqual(@as(?usize, 1), strrchr("abcd", 'b'));
    try std.testing.expectEqual(@as(?usize, null), strrchr("abcd", 'z'));
    try std.testing.expectEqual(@as(?usize, null), strrchr("abcd", 0));

    const cstr = [_]u8{ 'a', 'b', 'a', 0, 'c', 'a' };
    try std.testing.expectEqual(@as(?usize, 2), strrchr(&cstr, 'a'));
    try std.testing.expectEqual(@as(?usize, 3), strrchr(&cstr, 0));

    const past_nul = [_]u8{ 'a', 0, 'b', 'a' };
    try std.testing.expectEqual(@as(?usize, 0), strrchr(&past_nul, 'a'));
    try std.testing.expectEqual(@as(?usize, null), strrchr(&past_nul, 'b'));
}

test "strpbrk finds the first accepted byte with C-string semantics" {
    try std.testing.expectEqual(@as(?usize, 1), strpbrk("abcd", "xzbc"));
    try std.testing.expectEqual(@as(?usize, 0), strpbrk("abcd", "da"));
    try std.testing.expectEqual(@as(?usize, null), strpbrk("abcd", "xyz"));
    try std.testing.expectEqual(@as(?usize, null), strpbrk("abcd", ""));

    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, 0), strpbrk(&cstr, "ax"));
    try std.testing.expectEqual(@as(?usize, 1), strpbrk(&cstr, "xb"));
    try std.testing.expectEqual(@as(?usize, null), strpbrk(&cstr, "cd"));

    const accept_cstr = [_]u8{ 'x', 'b', 0, 'a' };
    try std.testing.expectEqual(@as(?usize, 1), strpbrk("abcd", &accept_cstr));
}

test "strnchr honors count and C-string boundaries" {
    try std.testing.expectEqual(@as(?usize, 1), strnchr("abcd", 4, 'b'));
    try std.testing.expectEqual(@as(?usize, null), strnchr("abcd", 1, 'b'));

    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'b' };
    try std.testing.expectEqual(@as(?usize, 1), strnchr(&cstr, cstr.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), strnchr(&cstr, cstr.len, 'c'));
    try std.testing.expectEqual(@as(?usize, 2), strnchr(&cstr, cstr.len, 0));
    try std.testing.expectEqual(@as(?usize, null), strnchr(&cstr, 2, 0));
}

test "strnlen honors count and C-string boundaries" {
    try std.testing.expectEqual(@as(usize, 4), strnlen("abcd", 7));
    try std.testing.expectEqual(@as(usize, 2), strnlen("abcd", 2));
    try std.testing.expectEqual(@as(usize, 0), strnlen("abcd", 0));

    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(usize, 2), strnlen(&cstr, cstr.len));
    try std.testing.expectEqual(@as(usize, 2), strnlen(&cstr, 4));
    try std.testing.expectEqual(@as(usize, 1), strnlen(&cstr, 1));
}

test "strnchrNul returns the first match, NUL, or count boundary" {
    try std.testing.expectEqual(@as(usize, 1), strnchrNul("abcd", 4, 'b'));
    try std.testing.expectEqual(@as(usize, 4), strnchrNul("abcd", 4, 'z'));
    try std.testing.expectEqual(@as(usize, 2), strnchrNul("abcd", 2, 'z'));
    try std.testing.expectEqual(@as(usize, 1), strchrNul("abcd", 'b'));
    try std.testing.expectEqual(@as(usize, 4), strchrNul("abcd", 'z'));
    try std.testing.expectEqual(@as(usize, 4), strchrnul("abcd", 'z'));

    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'b' };
    try std.testing.expectEqual(@as(usize, 1), strnchrNul(&cstr, cstr.len, 'b'));
    try std.testing.expectEqual(@as(usize, 2), strnchrNul(&cstr, cstr.len, 'c'));
    try std.testing.expectEqual(@as(usize, 2), strnchrNul(&cstr, cstr.len, 0));
    try std.testing.expectEqual(@as(usize, 2), strnchrnul(&cstr, cstr.len, 'z'));
    try std.testing.expectEqual(@as(usize, 2), strchrNul(&cstr, 'c'));
    try std.testing.expectEqual(@as(usize, 2), strchrNul(&cstr, 0));
    try std.testing.expectEqual(@as(usize, 2), strchrnul(&cstr, 'z'));
}
