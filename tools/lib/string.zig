const std = @import("std");

pub const ParseBoolError = error{Invalid};

pub const MemparseResult = struct {
    value: u64,
    rest: []const u8,
};

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

fn hasZeroByte(word: usize) bool {
    const ones = repeatByte(0x01);
    const high_bits = repeatByte(0x80);
    return ((word -% ones) & ~word & high_bits) != 0;
}

pub fn memchrInv(buf: []const u8, value: u8) ?usize {
    const word_bytes = @sizeOf(usize);
    var idx: usize = 0;

    if (buf.len >= word_bytes * 2) {
        const repeated = repeatByte(value);

        while (idx + word_bytes <= buf.len) : (idx += word_bytes) {
            const word_ptr: *align(1) const usize = @ptrCast(buf[idx .. idx + word_bytes].ptr);
            if (hasZeroByte(word_ptr.* ^ repeated)) {
                for (0..word_bytes) |byte_idx| {
                    if (buf[idx + byte_idx] != value) {
                        return idx + byte_idx;
                    }
                }
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

fn saturatingMulAdd(value: u64, base: u8, digit: u8) u64 {
    const mul = std.math.mul(u64, value, base) catch return std.math.maxInt(u64);
    return std.math.add(u64, mul, digit) catch return std.math.maxInt(u64);
}

fn applySuffix(value: u64, suffix: u8) u64 {
    const shift: u6 = switch (suffix) {
        'E', 'e' => 60,
        'P', 'p' => 50,
        'T', 't' => 40,
        'G', 'g' => 30,
        'M', 'm' => 20,
        'K', 'k' => 10,
        else => return value,
    };
    const max_value: u64 = std.math.maxInt(u64);
    if (value > (max_value >> shift)) {
        return std.math.maxInt(u64);
    }
    return value << shift;
}

fn clampSignedMagnitude(magnitude: u64, negative: bool) u64 {
    const max_positive = std.math.maxInt(i64);
    const min_magnitude = (@as(u64, 1) << 63);
    const min_signed: i64 = std.math.minInt(i64);

    if (negative) {
        if (magnitude >= min_magnitude) {
            return @bitCast(min_signed);
        }

        const signed: i64 = -@as(i64, @intCast(magnitude));
        return @bitCast(signed);
    }

    if (magnitude > @as(u64, @intCast(max_positive))) {
        return @as(u64, @intCast(max_positive));
    }

    return magnitude;
}

pub fn memparse(text: []const u8) MemparseResult {
    const prefix = parseSignedPrefix(text);
    const base_info = parseBase(text, prefix.start);
    const signed_input = prefix.start != 0;

    var idx = base_info.digits_start;
    var parsed_any = false;
    var magnitude: u64 = 0;

    while (idx < text.len) : (idx += 1) {
        const digit = digitValue(text[idx], base_info.base) orelse break;
        parsed_any = true;
        magnitude = saturatingMulAdd(magnitude, base_info.base, digit);
    }

    if (!parsed_any) {
        return .{ .value = 0, .rest = text };
    }

    if (idx < text.len) {
        if (signed_input) {
            magnitude = applySuffix(magnitude, text[idx]);
        }
    }

    var result = clampSignedMagnitude(magnitude, prefix.negative);
    if (idx < text.len) {
        if (!signed_input) {
            result = applySuffix(result, text[idx]);
        }
        switch (text[idx]) {
            'E', 'e', 'P', 'p', 'T', 't', 'G', 'g', 'M', 'm', 'K', 'k' => idx += 1,
            else => {},
        }
    }

    return .{ .value = result, .rest = text[idx..] };
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

pub fn strEndsWith(str: []const u8, suffix: []const u8) bool {
    const suffix_len = cStringLen(suffix);
    const str_len = cStringLen(str);
    if (suffix_len > str_len) {
        return false;
    }

    const start = str_len - suffix_len;
    return std.mem.eql(u8, str[start..str_len], suffix[0..suffix_len]);
}

pub fn str_ends_with(str: []const u8, suffix: []const u8) bool {
    return strEndsWith(str, suffix);
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
    try std.testing.expect(strEndsWith("prefix", ""));
    try std.testing.expect(!strEndsWith("prefix", "suffix"));
    try std.testing.expect(!strEndsWith("pre", "prefix"));

    const cstr = [_]u8{ 'a', 'b', 0, 'x' };
    const embedded_suffix = [_]u8{ 'a', 'b', 0, 'y' };
    const trailing_miss = [_]u8{ 'x', 0, 'y' };
    try std.testing.expect(strEndsWith(&cstr, &embedded_suffix));
    try std.testing.expect(!strEndsWith(&cstr, &trailing_miss));
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

test "strnchr honors count and C-string boundaries" {
    try std.testing.expectEqual(@as(?usize, 1), strnchr("abcd", 4, 'b'));
    try std.testing.expectEqual(@as(?usize, null), strnchr("abcd", 1, 'b'));

    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'b' };
    try std.testing.expectEqual(@as(?usize, 1), strnchr(&cstr, cstr.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), strnchr(&cstr, cstr.len, 'c'));
    try std.testing.expectEqual(@as(?usize, 2), strnchr(&cstr, cstr.len, 0));
    try std.testing.expectEqual(@as(?usize, null), strnchr(&cstr, 2, 0));
}
