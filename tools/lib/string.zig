const std = @import("std");
const cmdline = @import("cmdline.zig");

pub const ParseBoolError = error{Invalid};

pub const MemparseResult = cmdline.MemparseResult;

pub fn memdup(allocator: std.mem.Allocator, src: []const u8) ![]u8 {
    return allocator.dupe(u8, src);
}

pub fn memparse(text: []const u8) MemparseResult {
    return cmdline.memparse(text);
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

fn cStringLen(src: []const u8) usize {
    var len: usize = 0;
    while (len < src.len and src[len] != 0) : (len += 1) {}
    return len;
}

fn cStringByte(src: []const u8, idx: usize) u8 {
    if (idx >= src.len) {
        return 0;
    }
    return src[idx];
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

const strscpy_e2big: isize = -7;

pub fn strscpy(dest: []u8, src: []const u8) isize {
    if (dest.len == 0) {
        return strscpy_e2big;
    }

    const src_len = cStringLen(src);
    const copy_len = @min(src_len, dest.len - 1);
    @memcpy(dest[0..copy_len], src[0..copy_len]);
    dest[copy_len] = 0;

    if (copy_len != src_len) {
        return strscpy_e2big;
    }

    return @as(isize, @intCast(copy_len));
}

pub fn strscpyPad(dest: []u8, src: []const u8) isize {
    const written = strscpy(dest, src);
    if (written >= 0) {
        const len: usize = @intCast(written);
        if (len + 1 < dest.len) {
            @memset(dest[len + 1 ..], 0);
        }
    }
    return written;
}

pub fn strscpy_pad(dest: []u8, src: []const u8) isize {
    return strscpyPad(dest, src);
}

pub fn skipSpaces(str: []const u8) []const u8 {
    const limit = cStringLen(str);
    var idx: usize = 0;
    while (idx < limit and std.ascii.isWhitespace(str[idx])) : (idx += 1) {}
    return str[idx..limit];
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

pub fn strStarts(str: []const u8, prefix: []const u8) bool {
    const prefix_len = cStringLen(prefix);
    const str_len = cStringLen(str);
    if (str_len < prefix_len) {
        return false;
    }

    return std.mem.eql(u8, str[0..prefix_len], prefix[0..prefix_len]);
}

pub fn strstarts(str: []const u8, prefix: []const u8) bool {
    return strStarts(str, prefix);
}

pub fn strHasPrefix(str: []const u8, prefix: []const u8) usize {
    const prefix_len = cStringLen(prefix);
    const str_len = cStringLen(str);
    if (str_len < prefix_len) {
        return 0;
    }

    return if (std.mem.eql(u8, str[0..prefix_len], prefix[0..prefix_len])) prefix_len else 0;
}

pub fn str_has_prefix(str: []const u8, prefix: []const u8) usize {
    return strHasPrefix(str, prefix);
}

pub fn strEndsWith(str: []const u8, suffix: []const u8) bool {
    const suffix_len = cStringLen(suffix);
    const str_len = cStringLen(str);
    if (suffix_len > str_len) {
        return false;
    }

    return std.mem.eql(u8, str[str_len - suffix_len .. str_len], suffix[0..suffix_len]);
}

pub fn str_ends_with(str: []const u8, suffix: []const u8) bool {
    return strEndsWith(str, suffix);
}

pub fn strends(str: []const u8, suffix: []const u8) bool {
    return strEndsWith(str, suffix);
}

pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {
    var idx: usize = 0;
    while (true) : (idx += 1) {
        const lhs_ch = cStringByte(lhs, idx);
        const rhs_ch = cStringByte(rhs, idx);
        if (lhs_ch == 0 or lhs_ch != rhs_ch) {
            if (lhs_ch == rhs_ch) {
                return true;
            }
            if (lhs_ch == '\n' and cStringByte(lhs, idx + 1) == 0 and rhs_ch == 0) {
                return true;
            }
            if (lhs_ch == 0 and rhs_ch == '\n' and cStringByte(rhs, idx + 1) == 0) {
                return true;
            }
            return false;
        }
    }
}

pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {
    return sysfsStreq(lhs, rhs);
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

pub fn strstrip(buf: []u8) []u8 {
    return strim(buf);
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

// Phase 1 validator anchor: pub fn strreplace(buf: []u8, old: u8, new: u8) []u8 {
pub fn strreplace(buf: []u8, old: u8, new: u8) [*]u8 {
    const end = replaceChar(buf, old, new);
    return buf.ptr + end;
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
            const diff = word ^ repeated;
            return word_start + @as(usize, @intCast(@ctz(diff) >> 3));
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
    try std.testing.expectError(error.Invalid, strtobool(""));
    try std.testing.expectError(error.Invalid, strtobool(null));
}

test "strlcpy copies and returns the source length" {
    var dst = [_]u8{ 0, 0, 0, 0 };
    try std.testing.expectEqual(@as(usize, 5), strlcpy(&dst, "hello"));
    try std.testing.expectEqualSlices(u8, "hel", dst[0..3]);
    try std.testing.expectEqual(@as(u8, 0), dst[3]);

    var untouched = [_]u8{0xaa};
    try std.testing.expectEqual(@as(usize, 5), strlcpy(untouched[0..0], "hello"));
    try std.testing.expectEqual(@as(u8, 0xaa), untouched[0]);
}

test "strscpy mirrors bounded kernel copy semantics" {
    var dst = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 3), strscpy(&dst, "cat"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'c', 'a', 't', 0 }, &dst);

    var truncated = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(strscpy_e2big, strscpy(&truncated, "hello"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'e', 'l', 0 }, &truncated);

    const embedded = [_]u8{ 'o', 'k', 0, 'x' };
    var embedded_dst = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 2), strscpy(&embedded_dst, &embedded));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0xaa }, &embedded_dst);

    var zero_sized = [_]u8{0xaa};
    try std.testing.expectEqual(strscpy_e2big, strscpy(zero_sized[0..0], "x"));
    try std.testing.expectEqual(@as(u8, 0xaa), zero_sized[0]);
}

test "strscpyPad zero-fills the remaining destination tail on success" {
    var dst = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 2), strscpyPad(&dst, "ok"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &dst);
}

test "strscpyPad preserves embedded-NUL C-string semantics and zero-fills after the terminator" {
    const src = [_]u8{ 'o', 'k', 0, 'x' };
    var dst = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 2), strscpyPad(&dst, &src));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0 }, &dst);
}

test "strscpy_pad alias matches the padded copy semantics" {
    var dst = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 1), strscpy_pad(&dst, "z"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 0, 0, 0 }, &dst);
}

test "strscpyPad keeps truncation behavior unchanged" {
    var dst = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(strscpy_e2big, strscpyPad(&dst, "hello"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'e', 'l', 0 }, &dst);

    var zero_sized = [_]u8{0xaa};
    try std.testing.expectEqual(strscpy_e2big, strscpyPad(zero_sized[0..0], "x"));
    try std.testing.expectEqual(@as(u8, 0xaa), zero_sized[0]);
}

test "strlcpy stops at the first embedded NUL in the source" {
    const src = [_]u8{ 'h', 'i', 0, 'x', 'y' };

    var dst = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(usize, 2), strlcpy(&dst, &src));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0xaa, 0xaa }, &dst);

    var truncated = [_]u8{ 0xaa, 0xaa };
    try std.testing.expectEqual(@as(usize, 2), strlcpy(&truncated, &src));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 0 }, &truncated);

    var zero_sized = [_]u8{0xaa};
    try std.testing.expectEqual(@as(usize, 2), strlcpy(zero_sized[0..0], &src));
    try std.testing.expectEqual(@as(u8, 0xaa), zero_sized[0]);
}

test "skip trim remove and replace spaces work in place" {
    try std.testing.expectEqualStrings("hello", skipSpaces("   hello"));
    try std.testing.expectEqualStrings("hello", skip_spaces("   hello"));

    const skip_empty_cstr = [_]u8{ ' ', '\t', 0, 'x' };
    try std.testing.expectEqual(@as(usize, 0), skipSpaces(&skip_empty_cstr).len);
    try std.testing.expectEqual(@as(usize, 0), skip_spaces(&skip_empty_cstr).len);

    const skip_text_cstr = [_]u8{ ' ', '\t', 'o', 'k', 0, 'x' };
    try std.testing.expectEqualStrings("ok", skipSpaces(&skip_text_cstr));
    try std.testing.expectEqualStrings("ok", skip_spaces(&skip_text_cstr));

    var trim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };
    try std.testing.expectEqualStrings("hi", trimSpaces(&trim_buf));

    var whitespace_only_buf = [_]u8{ ' ', '\t', '\n' };
    try std.testing.expectEqualStrings("", trimSpaces(&whitespace_only_buf));
    try std.testing.expectEqual(@as(u8, 0), whitespace_only_buf[0]);

    var strim_buf = [_]u8{ ' ', 'o', 'k', ' ', '\n', 0 };
    try std.testing.expectEqualStrings("ok", strim(&strim_buf));

    var strim_cstr_buf = [_]u8{ ' ', 'o', 'k', 0, ' ', 'x' };
    try std.testing.expectEqualStrings("ok", strim(&strim_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'o', 'k', 0, ' ', 'x' }, &strim_cstr_buf);

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
    const replaced_end = strreplace(strreplace_buf[0 .. strreplace_buf.len - 1], '-', '_');
    try std.testing.expectEqual(@intFromPtr(strreplace_buf[0..].ptr) + 3, @intFromPtr(replaced_end));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 'b', 0, '-' }, &strreplace_buf);
}

test "strstrip aliases strim with the same C-string trimming semantics" {
    var strip_buf = [_]u8{ ' ', '\t', 'o', 'k', ' ', '\n', 0, 'x' };
    try std.testing.expectEqualStrings("ok", strstrip(&strip_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', '\t', 'o', 'k', 0, '\n', 0, 'x' }, &strip_buf);

    var whitespace_only = [_]u8{ ' ', '\n', 0, 'x' };
    try std.testing.expectEqualStrings("", strstrip(&whitespace_only));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, '\n', 0, 'x' }, &whitespace_only);
}

test "trimSpaces and strim stop at the first embedded NUL" {
    var trim_cstr_buf = [_]u8{ ' ', 'a', 0, 'x', '\n' };
    try std.testing.expectEqualStrings("a", trimSpaces(&trim_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'a', 0, 'x', '\n' }, &trim_cstr_buf);

    var strim_cstr_buf = [_]u8{ '\t', 'o', 'k', 0, 'x', '\n' };
    try std.testing.expectEqualStrings("ok", strim(&strim_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ '\t', 'o', 'k', 0, 'x', '\n' }, &strim_cstr_buf);
}

test "trimSpaces and strim trim trailing whitespace before an embedded NUL" {
    var trim_trailing_cstr_buf = [_]u8{ ' ', 'a', ' ', '\t', 0, 'x' };
    try std.testing.expectEqualStrings("a", trimSpaces(&trim_trailing_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'a', 0, '\t', 0, 'x' }, &trim_trailing_cstr_buf);

    var strim_trailing_cstr_buf = [_]u8{ ' ', 'o', 'k', ' ', '\t', 0, 'x' };
    try std.testing.expectEqualStrings("ok", strim(&strim_trailing_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'o', 'k', 0, '\t', 0, 'x' }, &strim_trailing_cstr_buf);
}

test "trimSpaces and strim empty whitespace-only C strings without touching tail bytes" {
    var trim_whitespace_cstr_buf = [_]u8{ ' ', '\t', 0, 'x', '\n' };
    try std.testing.expectEqualStrings("", trimSpaces(&trim_whitespace_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, '\t', 0, 'x', '\n' }, &trim_whitespace_cstr_buf);

    var strim_whitespace_cstr_buf = [_]u8{ ' ', '\n', 0, 'x', '\t' };
    try std.testing.expectEqualStrings("", strim(&strim_whitespace_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, '\n', 0, 'x', '\t' }, &strim_whitespace_cstr_buf);
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

test "strstarts matches kernel prefix semantics" {
    try std.testing.expect(strStarts("zigux", "zig"));
    try std.testing.expect(strstarts("zigux", "zig"));
    try std.testing.expect(strstarts("zigux", ""));
    try std.testing.expect(strstarts("", ""));
    try std.testing.expect(!strstarts("zig", "zigux"));
    try std.testing.expect(!strstarts("zigux", "Zig"));

    const source = [_]u8{ 'z', 'i', 'g', 0, 'x' };
    const embedded_prefix = [_]u8{ 'z', 'i', 'g', 0, 'u', 'x' };
    try std.testing.expect(strstarts(&source, &embedded_prefix));
}

test "strHasPrefix returns the matched prefix length with C-string semantics" {
    try std.testing.expectEqual(@as(usize, 3), strHasPrefix("zigux", "zig"));
    try std.testing.expectEqual(@as(usize, 3), str_has_prefix("zigux", "zig"));
    try std.testing.expectEqual(@as(usize, 0), strHasPrefix("zigux", "zug"));
    try std.testing.expectEqual(@as(usize, 0), strHasPrefix("zig", "zigux"));

    const source = [_]u8{ 'a', 'l', 'p', 'h', 'a', 0, 'b', 'e', 't', 'a' };
    const embedded_prefix = [_]u8{ 'a', 'l', 'p', 'h', 'a', 0, 'x' };
    try std.testing.expectEqual(@as(usize, 5), strHasPrefix(&source, &embedded_prefix));
}

test "str_ends_with matches kernel suffix semantics" {
    try std.testing.expect(strEndsWith("zigux", "gux"));
    try std.testing.expect(str_ends_with("zigux", "gux"));
    try std.testing.expect(strends("zigux", "gux"));
    try std.testing.expect(str_ends_with("zigux", ""));
    try std.testing.expect(strends("zigux", ""));
    try std.testing.expect(str_ends_with("", ""));
    try std.testing.expect(strends("", ""));
    try std.testing.expect(!str_ends_with("zig", "zigux"));
    try std.testing.expect(!strends("zig", "zigux"));
    try std.testing.expect(!str_ends_with("zigux", "GUX"));
    try std.testing.expect(!strends("zigux", "GUX"));

    const source = [_]u8{ 'z', 'i', 'g', 0, 'x' };
    const embedded_suffix = [_]u8{ 'i', 'g', 0, 'u', 'x' };
    try std.testing.expect(str_ends_with(&source, &embedded_suffix));
    try std.testing.expect(strends(&source, &embedded_suffix));
}

test "sysfsStreq treats a trailing newline as equivalent to C-string termination" {
    try std.testing.expect(sysfsStreq("enabled", "enabled"));
    try std.testing.expect(sysfs_streq("enabled", "enabled\n"));
    try std.testing.expect(sysfs_streq("enabled\n", "enabled"));
    try std.testing.expect(sysfs_streq("", "\n"));
    try std.testing.expect(!sysfs_streq("enabled", "enabled\nx"));
    try std.testing.expect(!sysfs_streq("enabled\nx", "enabled"));
    try std.testing.expect(!sysfs_streq("enabled", "disable"));

    const embedded = [_]u8{ 'o', 'n', 0, 'x' };
    try std.testing.expect(sysfs_streq(&embedded, "on\n"));

    const newline_terminated = [_]u8{ 'o', 'n', '\n', 0, 'x' };
    const nul_terminated = [_]u8{ 'o', 'n', 0, 'y' };
    try std.testing.expect(sysfs_streq(&newline_terminated, &nul_terminated));

    const non_terminal_newline = [_]u8{ 'o', 'n', '\n', 'x', 0 };
    try std.testing.expect(!sysfs_streq(&non_terminal_newline, &nul_terminated));
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

test "memchrInv keeps the short and long cutoff paths aligned" {
    var short_exact = [_]u8{'a'} ** 16;
    short_exact[15] = 'X';
    try std.testing.expectEqual(@as(?usize, 15), memchrInv(&short_exact, 'a'));

    var long_exact = [_]u8{'a'} ** 17;
    long_exact[16] = 'X';
    try std.testing.expectEqual(@as(?usize, 16), memchrInv(&long_exact, 'a'));

    var all_equal = [_]u8{'a'} ** 17;
    try std.testing.expectEqual(@as(?usize, null), memchrInv(&all_equal, 'a'));
}

test "memparse preserves the header-level string helper contract" {
    const decimal = memparse("64K rest");
    try std.testing.expectEqual(@as(u64, 64 << 10), decimal.value);
    try std.testing.expectEqualStrings(" rest", decimal.rest);

    const hexadecimal = memparse("0x20M");
    try std.testing.expectEqual(@as(u64, 0x20 << 20), hexadecimal.value);
    try std.testing.expectEqualStrings("", hexadecimal.rest);

    const octal = memparse("010K");
    try std.testing.expectEqual(@as(u64, 8 << 10), octal.value);
    try std.testing.expectEqualStrings("", octal.rest);

    const positive = memparse("+32");
    try std.testing.expectEqual(@as(u64, 32), positive.value);
    try std.testing.expectEqualStrings("", positive.rest);

    const negative = memparse("-4K tail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -4096))), negative.value);
    try std.testing.expectEqualStrings(" tail", negative.rest);

    const explicit_hex = memparse("+0X10M done");
    try std.testing.expectEqual(@as(u64, 0x10 << 20), explicit_hex.value);
    try std.testing.expectEqualStrings(" done", explicit_hex.rest);

    const kib = memparse("64KiB rest");
    try std.testing.expectEqual(@as(u64, 64 << 10), kib.value);
    try std.testing.expectEqualStrings(" rest", kib.rest);

    const mb = memparse("2MB!");
    try std.testing.expectEqual(@as(u64, 2 << 20), mb.value);
    try std.testing.expectEqualStrings("!", mb.rest);

    const gib = memparse("1GiB trailing");
    try std.testing.expectEqual(@as(u64, 1) << 30, gib.value);
    try std.testing.expectEqualStrings(" trailing", gib.rest);

    const lowercase_kib = memparse("3kib.");
    try std.testing.expectEqual(@as(u64, 3) << 10, lowercase_kib.value);
    try std.testing.expectEqualStrings(".", lowercase_kib.rest);

    const bare_hex = memparse("0x");
    try std.testing.expectEqual(@as(u64, 0), bare_hex.value);
    try std.testing.expectEqualStrings("x", bare_hex.rest);

    const signed_bare_hex = memparse("-0x");
    try std.testing.expectEqual(@as(u64, 0), signed_bare_hex.value);
    try std.testing.expectEqualStrings("x", signed_bare_hex.rest);

    const invalid_hex_digit = memparse("0xG");
    try std.testing.expectEqual(@as(u64, 0), invalid_hex_digit.value);
    try std.testing.expectEqualStrings("xG", invalid_hex_digit.rest);

    const sign_only_invalid = memparse("-xyz");
    try std.testing.expectEqual(@as(u64, 0), sign_only_invalid.value);
    try std.testing.expectEqualStrings("-xyz", sign_only_invalid.rest);

    const plus_invalid = memparse("+nope");
    try std.testing.expectEqual(@as(u64, 0), plus_invalid.value);
    try std.testing.expectEqualStrings("+nope", plus_invalid.rest);

    const invalid = memparse("xyz");
    try std.testing.expectEqual(@as(u64, 0), invalid.value);
    try std.testing.expectEqualStrings("xyz", invalid.rest);

    const positive_overflow = memparse("9223372036854775808");
    try std.testing.expectEqual(@as(u64, std.math.maxInt(i64)), positive_overflow.value);
    try std.testing.expectEqualStrings("", positive_overflow.rest);

    const negative_overflow = memparse("-9223372036854775809");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, std.math.minInt(i64)))), negative_overflow.value);
    try std.testing.expectEqualStrings("", negative_overflow.rest);

    const saturated_suffix = memparse("18446744073709551615K");
    try std.testing.expectEqual(@as(u64, 18446744073709550592), saturated_suffix.value);
    try std.testing.expectEqualStrings("", saturated_suffix.rest);
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

test "memchrInv returns the earliest mismatch inside a dirty word" {
    var aligned = [_]u8{'a'} ** 24;
    aligned[10] = 'X';
    aligned[12] = 'Y';
    try std.testing.expectEqual(@as(?usize, 10), memchrInv(&aligned, 'a'));

    var misaligned_storage = [_]u8{'a'} ** 25;
    misaligned_storage[11] = 'X';
    misaligned_storage[14] = 'Y';
    try std.testing.expectEqual(@as(?usize, 10), memchrInv(misaligned_storage[1..], 'a'));
}

test "memchrInv dirty-word shortcut handles high-bit byte values" {
    var aligned = [_]u8{0xff} ** 24;
    aligned[9] = 0x7f;
    aligned[13] = 0x01;
    try std.testing.expectEqual(@as(?usize, 9), memchrInv(&aligned, 0xff));

    var misaligned_storage = [_]u8{0x80} ** 25;
    misaligned_storage[10] = 0x00;
    misaligned_storage[15] = 0x7f;
    try std.testing.expectEqual(@as(?usize, 9), memchrInv(misaligned_storage[1..], 0x80));
}

test "memchrInv dirty-word shortcut handles zero-value scans at word boundaries" {
    var aligned = [_]u8{0} ** 24;
    aligned[8] = 1;
    aligned[15] = 2;
    try std.testing.expectEqual(@as(?usize, 8), memchrInv(&aligned, 0));

    var misaligned_storage = [_]u8{0} ** 32;
    const start = (1 -% (@as(usize, @intCast(@intFromPtr(misaligned_storage[0..].ptr) & 7)))) & 7;
    const misaligned = misaligned_storage[start .. start + 24];
    try std.testing.expect((@intFromPtr(misaligned.ptr) & 7) == 1);
    misaligned[8] = 1;
    misaligned[15] = 2;
    try std.testing.expectEqual(@as(?usize, 8), memchrInv(misaligned, 0));
}

test "memchrInv finds a last-byte mismatch in the first aligned dirty word" {
    var aligned = [_]u8{'a'} ** 24;
    aligned[15] = 'X';
    aligned[23] = 'Y';
    try std.testing.expectEqual(@as(?usize, 15), memchrInv(&aligned, 'a'));

    var misaligned_storage = [_]u8{'a'} ** 32;
    const start = (1 -% (@as(usize, @intCast(@intFromPtr(misaligned_storage[0..].ptr) & 7)))) & 7;
    const misaligned = misaligned_storage[start .. start + 24];
    try std.testing.expect((@intFromPtr(misaligned.ptr) & 7) == 1);
    misaligned[14] = 'X';
    misaligned[22] = 'Y';
    try std.testing.expectEqual(@as(?usize, 14), memchrInv(misaligned, 'a'));
}
