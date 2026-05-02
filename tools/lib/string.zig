const std = @import("std");

pub const ParseBoolError = error{Invalid};
pub const MemparseResult = struct {
    value: u64,
    rest: []const u8,
};

pub fn memdup(allocator: std.mem.Allocator, src: []const u8) ![]u8 {
    return allocator.dupe(u8, src);
}

fn digitValue(ch: u8, base: u8) ?u8 {
    const value = std.fmt.charToDigit(ch, base) catch return null;
    return @intCast(value);
}

fn parseSignedPrefix(text: []const u8) struct {
    negative: bool,
    start: usize,
} {
    if (text.len == 0) {
        return .{ .negative = false, .start = 0 };
    }

    return switch (text[0]) {
        '-' => .{ .negative = true, .start = 1 },
        '+' => .{ .negative = false, .start = 1 },
        else => .{ .negative = false, .start = 0 },
    };
}

fn parseBase(text: []const u8, start: usize) struct {
    base: u8,
    digits_start: usize,
} {
    if (start + 1 < text.len and text[start] == '0') {
        const next = text[start + 1];
        if (next == 'x' or next == 'X') {
            return .{ .base = 16, .digits_start = start + 2 };
        }
        return .{ .base = 8, .digits_start = start };
    }

    return .{ .base = 10, .digits_start = start };
}

fn applySuffix(value: u64, suffix: u8) u64 {
    return switch (suffix) {
        'E', 'e' => value << 60,
        'P', 'p' => value << 50,
        'T', 't' => value << 40,
        'G', 'g' => value << 30,
        'M', 'm' => value << 20,
        'K', 'k' => value << 10,
        else => value,
    };
}

fn consumeOptionalUnitTail(text: []const u8, idx: *usize) void {
    if (idx.* >= text.len) {
        return;
    }

    if ((text[idx.*] == 'i' or text[idx.*] == 'I') and idx.* + 1 < text.len and
        (text[idx.* + 1] == 'B' or text[idx.* + 1] == 'b'))
    {
        idx.* += 2;
        return;
    }

    if (text[idx.*] == 'B' or text[idx.*] == 'b') {
        idx.* += 1;
    }
}

pub fn memparse(text: []const u8) MemparseResult {
    const prefix = parseSignedPrefix(text);
    const base_info = parseBase(text, prefix.start);

    var idx = base_info.digits_start;
    var parsed_any = false;
    var magnitude: u64 = 0;

    while (idx < text.len) : (idx += 1) {
        const digit = digitValue(text[idx], base_info.base) orelse break;
        parsed_any = true;
        magnitude = magnitude * base_info.base + digit;
    }

    if (!parsed_any) {
        return .{ .value = 0, .rest = text };
    }

    var signed_value: i64 = @bitCast(magnitude);
    if (prefix.negative) {
        signed_value = -signed_value;
    }

    var result: u64 = @bitCast(signed_value);
    if (idx < text.len) {
        switch (text[idx]) {
            'E', 'e', 'P', 'p', 'T', 't', 'G', 'g', 'M', 'm', 'K', 'k' => {
                result = applySuffix(result, text[idx]);
                idx += 1;
                consumeOptionalUnitTail(text, &idx);
            },
            else => {},
        }
    }

    return .{ .value = result, .rest = text[idx..] };
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
            if (lhs_ch == 0 and rhs_ch == '\n' and cStringByte(rhs, idx + 1) == 0) {
                return true;
            }
            if (lhs_ch == '\n' and cStringByte(lhs, idx + 1) == 0 and rhs_ch == 0) {
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

fn firstMismatchingWordByte(word: u64, repeated: u64) usize {
    const diff = word ^ repeated;
    const ones = repeatedByteWord(0x01);
    const high_bits = repeatedByteWord(0x80);
    const zero_byte_high_bits = (diff -% ones) & ~diff & high_bits;
    const mismatch_high_bits = ~zero_byte_high_bits & high_bits;
    return @as(usize, @intCast(@ctz(mismatch_high_bits) >> 3));
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
            return word_start + firstMismatchingWordByte(word, repeated);
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

test "memparse forwards the header-level string helper surface" {
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

    const kib = memparse("64KiB rest");
    try std.testing.expectEqual(@as(u64, 64 << 10), kib.value);
    try std.testing.expectEqualStrings(" rest", kib.rest);

    const mb = memparse("2MB!");
    try std.testing.expectEqual(@as(u64, 2 << 20), mb.value);
    try std.testing.expectEqualStrings("!", mb.rest);

    const invalid = memparse("xyz");
    try std.testing.expectEqual(@as(u64, 0), invalid.value);
    try std.testing.expectEqualStrings("xyz", invalid.rest);
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
