const std = @import("std");
const cmdline = @import("cmdline.zig");

pub const ParseBoolError = error{Invalid};

pub const MemparseResult = cmdline.MemparseResult;

const strscpy_e2big: isize = -7;

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
        'e', 'E', 'y', 'Y', 't', 'T', '1' => return true,
        'd', 'D', 'n', 'N', 'f', 'F', '0' => return false,
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

pub fn strlcat(dest: []u8, src: []const u8) usize {
    const src_len = cStringLen(src);
    if (dest.len == 0) {
        return src_len;
    }

    const dest_len = strnlen(dest, dest.len);
    if (dest_len == dest.len) {
        return dest.len + src_len;
    }

    const copy_len = @min(src_len, dest.len - dest_len - 1);
    if (copy_len != 0) {
        @memcpy(dest[dest_len .. dest_len + copy_len], src[0..copy_len]);
    }
    dest[dest_len + copy_len] = 0;
    return dest_len + src_len;
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

pub fn memcpyAndPad(dest: []u8, src: []const u8, count: usize, pad: u8) void {
    const copy_len = @min(dest.len, @min(count, src.len));
    if (copy_len != 0) {
        @memcpy(dest[0..copy_len], src[0..copy_len]);
    }
    if (copy_len < dest.len) {
        @memset(dest[copy_len..], pad);
    }
}

pub fn memcpy_and_pad(dest: []u8, src: []const u8, count: usize, pad: u8) void {
    memcpyAndPad(dest, src, count, pad);
}

pub fn strtomem(dest: []u8, src: []const u8) void {
    const copy_len = @min(dest.len, cStringLen(src));
    if (copy_len != 0) {
        @memcpy(dest[0..copy_len], src[0..copy_len]);
    }
}

pub fn strtomem_pad(dest: []u8, src: []const u8, pad: u8) void {
    memcpyAndPad(dest, src, @min(dest.len, cStringLen(src)), pad);
}

pub fn memtostr(dest: []u8, src: []const u8) void {
    if (dest.len == 0) {
        return;
    }

    const copy_len = @min(dest.len - 1, strnlen(src, src.len));
    if (copy_len != 0) {
        @memcpy(dest[0..copy_len], src[0..copy_len]);
    }
    dest[copy_len] = 0;
}

pub fn memtostrPad(dest: []u8, src: []const u8) void {
    if (dest.len == 0) {
        return;
    }

    const copy_len = @min(dest.len - 1, strnlen(src, src.len));
    if (copy_len != 0) {
        @memcpy(dest[0..copy_len], src[0..copy_len]);
    }
    @memset(dest[copy_len..], 0);
}

pub fn memtostr_pad(dest: []u8, src: []const u8) void {
    memtostrPad(dest, src);
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

pub fn strHasPrefix(buf: []const u8, prefix: []const u8) usize {
    const buf_len = cStringLen(buf);
    const prefix_len = cStringLen(prefix);
    if (prefix_len > buf_len) {
        return 0;
    }
    if (std.mem.eql(u8, buf[0..prefix_len], prefix[0..prefix_len])) {
        return prefix_len;
    }
    return 0;
}

pub fn str_has_prefix(buf: []const u8, prefix: []const u8) usize {
    return strHasPrefix(buf, prefix);
}

pub fn strstarts(buf: []const u8, prefix: []const u8) bool {
    return strHasPrefix(buf, prefix) != 0;
}

pub fn strHasSuffix(buf: []const u8, suffix: []const u8) usize {
    const buf_len = cStringLen(buf);
    const suffix_len = cStringLen(suffix);
    if (suffix_len > buf_len) {
        return 0;
    }
    if (std.mem.eql(u8, buf[buf_len - suffix_len .. buf_len], suffix[0..suffix_len])) {
        return suffix_len;
    }
    return 0;
}

pub fn str_has_suffix(buf: []const u8, suffix: []const u8) usize {
    return strHasSuffix(buf, suffix);
}

pub fn strEndsWith(buf: []const u8, suffix: []const u8) bool {
    return strHasSuffix(buf, suffix) != 0;
}

pub fn str_ends_with(buf: []const u8, suffix: []const u8) bool {
    return strEndsWith(buf, suffix);
}

pub fn strends(buf: []const u8, suffix: []const u8) bool {
    return strEndsWith(buf, suffix);
}

pub fn kbasename(path: []const u8) []const u8 {
    const len = cStringLen(path);
    var start: usize = 0;
    for (path[0..len], 0..) |ch, idx| {
        if (ch == '/') {
            start = idx + 1;
        }
    }
    return path[start..len];
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
        const prefix = @intFromPtr(buf.ptr) % word_bytes;
        if (prefix != 0) {
            const prefix_len = @min(word_bytes - prefix, buf.len);
            while (idx < prefix_len) : (idx += 1) {
                if (buf[idx] != value) {
                    return idx;
                }
            }
        }

        while (idx + word_bytes <= buf.len) : (idx += word_bytes) {
            const word_bytes_ptr: [*]align(@alignOf(usize)) const u8 = @alignCast(buf[idx .. idx + word_bytes].ptr);
            const word_ptr: *const usize = @ptrCast(word_bytes_ptr);
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

fn asciiLower(ch: u8) u8 {
    return std.ascii.toLower(ch);
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

pub fn __sysfs_match_string(haystack: []const []const u8, count: usize, needle: []const u8) ?usize {
    const limit = @min(count, haystack.len);
    for (haystack[0..limit], 0..) |candidate, idx| {
        if (sysfsStreq(candidate, needle)) {
            return idx;
        }
    }
    return null;
}

pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {
    return __sysfs_match_string(haystack, haystack.len, needle);
}

pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {
    return sysfsMatchString(haystack, needle);
}

pub fn matchString(haystack: []const []const u8, needle: []const u8) ?usize {
    for (haystack, 0..) |candidate, idx| {
        if (strEq(candidate, needle)) {
            return idx;
        }
    }
    return null;
}

pub fn match_string(haystack: []const []const u8, needle: []const u8) ?usize {
    return matchString(haystack, needle);
}

pub fn strcmp(lhs: []const u8, rhs: []const u8) i32 {
    const lhs_len = cStringLen(lhs);
    const rhs_len = cStringLen(rhs);
    const limit = @min(lhs_len, rhs_len);

    var idx: usize = 0;
    while (idx < limit) : (idx += 1) {
        if (lhs[idx] != rhs[idx]) {
            return @as(i32, lhs[idx]) - @as(i32, rhs[idx]);
        }
    }

    if (lhs_len == rhs_len) {
        return 0;
    }

    const lhs_tail: u8 = if (lhs_len > rhs_len) lhs[rhs_len] else 0;
    const rhs_tail: u8 = if (rhs_len > lhs_len) rhs[lhs_len] else 0;
    return @as(i32, lhs_tail) - @as(i32, rhs_tail);
}

pub fn strncmp(lhs: []const u8, rhs: []const u8, count: usize) i32 {
    if (count == 0) {
        return 0;
    }

    const lhs_len = cStringLen(lhs);
    const rhs_len = cStringLen(rhs);
    const limit = @min(count, @min(lhs_len, rhs_len));

    var idx: usize = 0;
    while (idx < limit) : (idx += 1) {
        if (lhs[idx] != rhs[idx]) {
            return @as(i32, lhs[idx]) - @as(i32, rhs[idx]);
        }
    }

    if (idx == count) {
        return 0;
    }

    const lhs_tail: u8 = if (lhs_len > idx) lhs[idx] else 0;
    const rhs_tail: u8 = if (rhs_len > idx) rhs[idx] else 0;
    return @as(i32, lhs_tail) - @as(i32, rhs_tail);
}

pub fn strcasecmp(lhs: []const u8, rhs: []const u8) i32 {
    const lhs_len = cStringLen(lhs);
    const rhs_len = cStringLen(rhs);
    const limit = @min(lhs_len, rhs_len);

    var idx: usize = 0;
    while (idx < limit) : (idx += 1) {
        const lhs_ch = asciiLower(lhs[idx]);
        const rhs_ch = asciiLower(rhs[idx]);
        if (lhs_ch != rhs_ch) {
            return @as(i32, lhs_ch) - @as(i32, rhs_ch);
        }
    }

    if (lhs_len == rhs_len) {
        return 0;
    }

    const lhs_tail: u8 = if (lhs_len > rhs_len) asciiLower(lhs[rhs_len]) else 0;
    const rhs_tail: u8 = if (rhs_len > lhs_len) asciiLower(rhs[lhs_len]) else 0;
    return @as(i32, lhs_tail) - @as(i32, rhs_tail);
}

pub fn strncasecmp(lhs: []const u8, rhs: []const u8, count: usize) i32 {
    if (count == 0) {
        return 0;
    }

    const lhs_len = cStringLen(lhs);
    const rhs_len = cStringLen(rhs);
    const limit = @min(count, @min(lhs_len, rhs_len));

    var idx: usize = 0;
    while (idx < limit) : (idx += 1) {
        const lhs_ch = asciiLower(lhs[idx]);
        const rhs_ch = asciiLower(rhs[idx]);
        if (lhs_ch != rhs_ch) {
            return @as(i32, lhs_ch) - @as(i32, rhs_ch);
        }
    }

    if (limit == count) {
        return 0;
    }

    const lhs_tail: u8 = if (lhs_len > idx) asciiLower(lhs[idx]) else 0;
    const rhs_tail: u8 = if (rhs_len > idx) asciiLower(rhs[idx]) else 0;
    return @as(i32, lhs_tail) - @as(i32, rhs_tail);
}

pub fn strchr(buf: []const u8, needle: u8) ?usize {
    const limit = cStringLen(buf);
    if (needle == 0) {
        return limit;
    }
    for (buf[0..limit], 0..) |ch, idx| {
        if (ch == needle) {
            return idx;
        }
    }
    return null;
}

pub fn strrchr(buf: []const u8, needle: u8) ?usize {
    const limit = cStringLen(buf);
    if (needle == 0) {
        return limit;
    }
    var idx = limit;
    while (idx > 0) {
        idx -= 1;
        if (buf[idx] == needle) {
            return idx;
        }
    }
    return null;
}

pub fn strpbrk(buf: []const u8, accept: []const u8) ?usize {
    const limit = cStringLen(buf);
    const accept_len = cStringLen(accept);
    for (buf[0..limit], 0..) |ch, idx| {
        for (accept[0..accept_len]) |allowed| {
            if (ch == allowed) {
                return idx;
            }
        }
    }
    return null;
}

pub fn strspn(buf: []const u8, accept: []const u8) usize {
    const limit = cStringLen(buf);
    const accept_len = cStringLen(accept);
    for (buf[0..limit], 0..) |ch, idx| {
        var matched = false;
        for (accept[0..accept_len]) |allowed| {
            if (ch == allowed) {
                matched = true;
                break;
            }
        }
        if (!matched) {
            return idx;
        }
    }
    return limit;
}

pub fn strcspn(buf: []const u8, reject: []const u8) usize {
    const limit = cStringLen(buf);
    const reject_len = cStringLen(reject);
    for (buf[0..limit], 0..) |ch, idx| {
        for (reject[0..reject_len]) |blocked| {
            if (ch == blocked) {
                return idx;
            }
        }
    }
    return limit;
}

pub fn strstr(buf: []const u8, needle: []const u8) ?usize {
    return strnstr(buf, needle, cStringLen(buf));
}

pub fn strnstr(buf: []const u8, needle: []const u8, count: usize) ?usize {
    const limit = strnlen(buf, count);
    const needle_len = cStringLen(needle);
    if (needle_len == 0) {
        return 0;
    }
    if (needle_len > limit) {
        return null;
    }

    var idx: usize = 0;
    while (idx + needle_len <= limit) : (idx += 1) {
        if (std.mem.eql(u8, buf[idx .. idx + needle_len], needle[0..needle_len])) {
            return idx;
        }
    }
    return null;
}

pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {
    const limit = strnlen(buf, count);
    if (needle == 0) {
        return if (limit == count) null else limit;
    }
    for (buf[0..limit], 0..) |ch, idx| {
        if (ch == needle) {
            return idx;
        }
    }
    return null;
}

pub fn strlen(buf: []const u8) usize {
    return cStringLen(buf);
}

pub fn strnlen(buf: []const u8, count: usize) usize {
    return @min(cStringLen(buf), @min(count, buf.len));
}

pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {
    return if (strnchr(buf, count, needle)) |idx| idx else strnlen(buf, count);
}

pub fn strnchrnul(buf: []const u8, count: usize, needle: u8) usize {
    return strnchrNul(buf, count, needle);
}

pub fn strchrNul(buf: []const u8, needle: u8) usize {
    return if (strchr(buf, needle)) |idx| idx else cStringLen(buf);
}

pub fn strchrnul(buf: []const u8, needle: u8) usize {
    return strchrNul(buf, needle);
}

fn sysfsStringLen(buf: []const u8) usize {
    const len = cStringLen(buf);
    if (len > 0 and buf[len - 1] == '\n') {
        return len - 1;
    }
    return len;
}

test "strtobool accepts common Linux forms" {
    try std.testing.expect(try strtobool("y") == true);
    try std.testing.expect(try strtobool("enable") == true);
    try std.testing.expect(try strtobool("true") == true);
    try std.testing.expect(try strtobool("off") == false);
    try std.testing.expect(try strtobool("disable") == false);
    try std.testing.expect(try strtobool("false") == false);
    try std.testing.expectError(error.Invalid, strtobool("maybe"));
}

test "strlcpy copies and returns the source length" {
    var buf = [_]u8{ 0, 0, 0, 0 };
    try std.testing.expectEqual(@as(usize, 5), strlcpy(buf[0..], "hello"));
    try std.testing.expectEqualStrings("hel", buf[0..3]);
    try std.testing.expectEqual(@as(u8, 0), buf[3]);
}

test "strlcpy stops at embedded NUL bytes and reports the C-string source length" {
    var buf = [_]u8{ 9, 9, 9, 9, 9 };
    const src = [_]u8{ 'h', 'i', 0, 'x', 'x' };

    try std.testing.expectEqual(@as(usize, 2), strlcpy(buf[0..], &src));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 9, 9 }, buf[0..]);
}

test "strlcat appends only the C-string prefix from embedded-NUL sources" {
    var buf = [_]u8{ 'a', 0, 'x', 'x' };
    const src = [_]u8{ 'b', 'c', 0, 'd' };

    try std.testing.expectEqual(@as(usize, 3), strlcat(buf[0..], &src));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 0 }, buf[0..]);
}

test "strlcat truncates with a terminator and keeps the full attempted length" {
    var buf = [_]u8{ 'a', 'b', 0, 'x' };
    try std.testing.expectEqual(@as(usize, 6), strlcat(buf[0..], "cdef"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 0 }, buf[0..]);
}

test "strlcat treats an unterminated destination as full" {
    var buf = [_]u8{ 'a', 'b', 'c' };
    try std.testing.expectEqual(@as(usize, 6), strlcat(buf[0..], "xyz"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c' }, buf[0..]);
}

test "strlcat handles a zero-length destination buffer" {
    var empty = [_]u8{};
    try std.testing.expectEqual(@as(usize, 3), strlcat(empty[0..], "zig"));
}

test "strscpy keeps NUL termination and reports truncation with -E2BIG" {
    var buf = [_]u8{ 1, 1, 1, 1 };
    try std.testing.expectEqual(strscpy_e2big, strscpy(buf[0..], "hello"));
    try std.testing.expectEqualStrings("hel", buf[0..3]);
    try std.testing.expectEqual(@as(u8, 0), buf[3]);
}

test "strscpyPad zero-pads the tail after a short source" {
    var buf = [_]u8{ 1, 1, 1, 1, 1 };
    try std.testing.expectEqual(@as(isize, 2), strscpyPad(buf[0..], "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0 }, buf[0..]);
}

test "strscpyPad stops at embedded NUL and pads the remaining tail" {
    var buf = [_]u8{ 1, 1, 1, 1, 1, 1 };
    try std.testing.expectEqual(@as(isize, 2), strscpyPad(buf[0..], &[_]u8{ 'h', 'i', 0, 'x', 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0, 0 }, buf[0..]);
}

test "strscpyPad preserves strscpy truncation semantics" {
    var buf = [_]u8{ 9, 9, 9 };
    try std.testing.expectEqual(strscpy_e2big, strscpyPad(buf[0..], "abcd"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0 }, buf[0..]);
}

test "strscpy_pad mirrors strscpyPad padding semantics" {
    var buf = [_]u8{ 1, 1, 1, 1 };
    try std.testing.expectEqual(@as(isize, 2), strscpy_pad(buf[0..], "ok"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0 }, buf[0..]);
}

test "strscpy and strscpyPad keep one-byte destinations terminated" {
    var single_a = [_]u8{7};
    var single_b = [_]u8{8};
    try std.testing.expectEqual(strscpy_e2big, strscpy(single_a[0..], "x"));
    try std.testing.expectEqual(strscpy_e2big, strscpyPad(single_b[0..], "y"));
    try std.testing.expectEqual(@as(u8, 0), single_a[0]);
    try std.testing.expectEqual(@as(u8, 0), single_b[0]);
}

test "memcpyAndPad copies the requested prefix and pads the destination tail" {
    var buf = [_]u8{ 9, 9, 9, 9, 9 };
    memcpyAndPad(buf[0..], "abcxyz", 3, '.');
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', '.', '.' }, buf[0..]);
}

test "memcpy_and_pad mirrors memcpyAndPad padding semantics" {
    var direct = [_]u8{ 9, 9, 9, 9 };
    var alias = [_]u8{ 8, 8, 8, 8 };
    memcpyAndPad(direct[0..], "wxyz", 2, '.');
    memcpy_and_pad(alias[0..], "wxyz", 2, '.');
    try std.testing.expectEqualSlices(u8, direct[0..], alias[0..]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'w', 'x', '.', '.' }, alias[0..]);
}

test "strtomem copies a C-string prefix without adding a terminator or padding" {
    var buf = [_]u8{ 9, 9, 9, 9 };
    strtomem(buf[0..], &[_]u8{ 'o', 'k', 0, 'x' });
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 9, 9 }, buf[0..]);
}

test "strtomem_pad copies through the first NUL and pads the remaining tail" {
    var buf = [_]u8{ 9, 9, 9, 9, 9 };
    strtomem_pad(buf[0..], &[_]u8{ 'h', 'i', 0, 'x' }, '.');
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', '.', '.', '.' }, buf[0..]);
}

test "memtostr copies a bounded non-NUL source and adds one terminator" {
    var buf = [_]u8{ 9, 9, 9, 9, 9 };
    memtostr(buf[0..], &[_]u8{ 'o', 'k' });
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 9, 9 }, buf[0..]);
}

test "memtostr stops at embedded NUL without padding the tail" {
    var buf = [_]u8{ 9, 9, 9, 9, 9 };
    memtostr(buf[0..], &[_]u8{ 'h', 'i', 0, 'x' });
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 9, 9 }, buf[0..]);
}

test "memtostrPad zero-pads the remaining tail after copying" {
    var buf = [_]u8{ 9, 9, 9, 9, 9 };
    memtostrPad(buf[0..], &[_]u8{ 'a', 'b', 'c' });
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 0, 0 }, buf[0..]);
}

test "memtostr helpers keep one-byte destinations terminated" {
    var direct = [_]u8{7};
    var alias = [_]u8{8};
    memtostr(direct[0..], &[_]u8{ 'x' });
    memtostr_pad(alias[0..], &[_]u8{ 'y' });
    try std.testing.expectEqual(@as(u8, 0), direct[0]);
    try std.testing.expectEqual(@as(u8, 0), alias[0]);
}

test "streq matches C-string equality semantics" {
    try std.testing.expect(streq(&[_]u8{ 'a', 0, 'x' }, &[_]u8{ 'a', 0, 'y' }));
    try std.testing.expect(!streq("abc", "abd"));
}

test "skip trim remove and replace spaces work in place" {
    var trim_buf = [_]u8{ ' ', 'a', ' ', 'b', ' ', 0, 'x' };
    const trimmed = trimSpaces(trim_buf[0..]);
    try std.testing.expectEqualStrings("a b", trimmed);

    var remove_buf = [_]u8{ 'a', ' ', 'b', ' ', 0, 'x' };
    const removed = removeSpaces(remove_buf[0..]);
    try std.testing.expectEqualStrings("ab", removed);

    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), replaceChar(replace_buf[0..], '-', '+'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '+', 'b', 0, '-' }, replace_buf[0..]);
    try std.testing.expectEqualStrings("lead", skipSpaces("  \tlead"));
}

test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace" {
    var buf = [_]u8{ ' ', 'o', 'k', 0, ' ', ' ', 0 };
    try std.testing.expectEqualStrings("ok", strim(buf[0..]));
    try std.testing.expectEqualStrings("ok", strstrip(buf[0..]));
}

test "strreplace mirrors replaceChar C-string semantics" {
    var buf = [_]u8{ 'a', 'b', 'a', 0, 'a' };
    try std.testing.expectEqual(@as(usize, 3), strreplace(buf[0..], 'a', 'z'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'b', 'z', 0, 'a' }, buf[0..]);
}

test "strHasPrefix returns the matched prefix length with C-string semantics" {
    try std.testing.expectEqual(@as(usize, 3), strHasPrefix(&[_]u8{ 'a', 'b', 'c', 0, 'x' }, "abc"));
    try std.testing.expectEqual(@as(usize, 3), str_has_prefix("abcdef", "abc"));
    try std.testing.expectEqual(@as(usize, 0), strHasPrefix("abcdef", "abd"));
}

test "strHasSuffix returns the matched suffix length with C-string semantics" {
    try std.testing.expectEqual(@as(usize, 3), strHasSuffix(&[_]u8{ 'a', 'b', 'c', 0, 'x' }, "abc"));
    try std.testing.expectEqual(@as(usize, 3), str_has_suffix("abcdef", "def"));
    try std.testing.expectEqual(@as(usize, 0), strHasSuffix("abcdef", "deg"));
}

test "strstarts mirrors the header-level prefix helper" {
    try std.testing.expect(strstarts("kernel", "ker"));
    try std.testing.expect(!strstarts("kernel", "ern"));
}

test "strEndsWith honors C-string boundaries" {
    try std.testing.expect(strEndsWith(&[_]u8{ 'a', 'b', 'c', 0, 'd' }, "bc"));
    try std.testing.expect(str_ends_with("abcdef", "def"));
    try std.testing.expect(strends("abcdef", "def"));
    try std.testing.expect(!strEndsWith("abcdef", "deg"));
}

test "prefix and suffix Linux-style aliases mirror the primary helpers" {
    const prefix_cstr = [_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'x' };
    const suffix_cstr = [_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'y' };

    try std.testing.expectEqual(strHasPrefix(&prefix_cstr, "ker"), str_has_prefix(&prefix_cstr, "ker"));
    try std.testing.expectEqual(strHasPrefix("kernel", "xyz"), str_has_prefix("kernel", "xyz"));
    try std.testing.expectEqual(strHasSuffix(&suffix_cstr, "nel"), str_has_suffix(&suffix_cstr, "nel"));
    try std.testing.expectEqual(strHasSuffix("kernel", "xyz"), str_has_suffix("kernel", "xyz"));
    try std.testing.expectEqual(strEndsWith(&suffix_cstr, "nel"), str_ends_with(&suffix_cstr, "nel"));
    try std.testing.expectEqual(strEndsWith(&suffix_cstr, "nel"), strends(&suffix_cstr, "nel"));
    try std.testing.expectEqual(strEndsWith("kernel", "xyz"), str_ends_with("kernel", "xyz"));
    try std.testing.expectEqual(strEndsWith("kernel", "xyz"), strends("kernel", "xyz"));
}

test "kbasename returns the final path component with C-string semantics" {
    try std.testing.expectEqualStrings("file.txt", kbasename("/tmp/file.txt"));
    try std.testing.expectEqualStrings("node", kbasename(&[_]u8{ '/', 'a', '/', 'n', 'o', 'd', 'e', 0, '/', 'x' }));
}

test "sysfsStreq treats trailing newline and NUL as equivalent" {
    try std.testing.expect(sysfsStreq("alpha\n", "alpha"));
    try std.testing.expect(!sysfsStreq("alpha\n", "beta"));
}

test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence" {
    try std.testing.expect(sysfs_streq("mode\n", "mode"));
    try std.testing.expect(!sysfs_streq("mode\n", "modes"));
}

test "sysfsMatchString finds newline-aware matches and preserves first-match order" {
    const haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), __sysfs_match_string(haystack[0..], 3, "auto"));
    try std.testing.expectEqual(@as(?usize, null), __sysfs_match_string(haystack[0..], 1, "auto"));
    try std.testing.expectEqual(@as(?usize, null), sysfsMatchString(haystack[0..], "missing"));
}

test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists" {
    const haystack = [_][]const u8{ "a\n", "b" };
    const empty = [_][]const u8{};
    try std.testing.expectEqual(@as(?usize, 0), sysfs_match_string(haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 1), __sysfs_match_string(haystack[0..], 99, "b"));
    try std.testing.expectEqual(@as(?usize, null), sysfs_match_string(empty[0..], "a"));
}

test "matchString finds C-string matches and preserves first-match order" {
    const haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };
    try std.testing.expectEqual(@as(?usize, 0), matchString(haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, null), matchString(haystack[0..], "gamma"));
}

test "match_string mirrors matchString for empty and matched lists" {
    const haystack = [_][]const u8{ "blue", "green" };
    const empty = [_][]const u8{};
    try std.testing.expectEqual(@as(?usize, 1), match_string(haystack[0..], "green"));
    try std.testing.expectEqual(@as(?usize, null), match_string(empty[0..], "green"));
}

test "strcmp mirrors C-string lexical ordering" {
    try std.testing.expect(strcmp("abc", "abc") == 0);
    try std.testing.expect(strcmp("abd", "abc") > 0);
    try std.testing.expect(strcmp("abc", "abd") < 0);
}

test "strcmp stops at embedded NULs and length mismatches" {
    try std.testing.expect(strcmp(&[_]u8{ 'a', 0, 'z' }, &[_]u8{ 'a', 0, 'x' }) == 0);
    try std.testing.expect(strcmp(&[_]u8{ 'a', 0, 'z' }, "ab") < 0);
    try std.testing.expect(strcmp("ab", &[_]u8{ 'a', 0, 'z' }) > 0);
}

test "strncmp honors the count limit before later mismatches" {
    try std.testing.expect(strncmp("abcdef", "abcxyz", 3) == 0);
    try std.testing.expect(strncmp("abcdef", "abcxyz", 4) < 0);
    try std.testing.expect(strncmp("abcxyz", "abcdef", 4) > 0);
    try std.testing.expect(strncmp("abcdef", "abcxyz", 0) == 0);
}

test "strncmp stops at embedded NULs and shorter prefixes" {
    try std.testing.expect(strncmp(&[_]u8{ 'a', 0, 'z' }, &[_]u8{ 'a', 0, 'x' }, 3) == 0);
    try std.testing.expect(strncmp(&[_]u8{ 'a', 0, 'z' }, "ab", 3) < 0);
    try std.testing.expect(strncmp("ab", &[_]u8{ 'a', 0, 'z' }, 3) > 0);
    try std.testing.expect(strncmp("ab", "abc", 2) == 0);
}

test "strcasecmp ignores ASCII case and preserves lexical ordering" {
    try std.testing.expect(strcasecmp("Kernel", "kernel") == 0);
    try std.testing.expect(strcasecmp("abd", "ABC") > 0);
    try std.testing.expect(strcasecmp("ABC", "abd") < 0);
}

test "strcasecmp stops at embedded NULs and length mismatches" {
    try std.testing.expect(strcasecmp(&[_]u8{ 'A', 0, 'z' }, &[_]u8{ 'a', 0, 'x' }) == 0);
    try std.testing.expect(strcasecmp(&[_]u8{ 'A', 0, 'z' }, "ab") < 0);
    try std.testing.expect(strcasecmp("ab", &[_]u8{ 'A', 0, 'z' }) > 0);
}

test "strncasecmp honors the count limit before later mismatches" {
    try std.testing.expect(strncasecmp("AbCdEf", "aBcXEf", 3) == 0);
    try std.testing.expect(strncasecmp("AbCdEf", "aBcXEf", 4) < 0);
    try std.testing.expect(strncasecmp("aBcXEf", "AbCdEf", 4) > 0);
    try std.testing.expect(strncasecmp("abcdef", "ABCXYZ", 0) == 0);
}

test "strncasecmp stops at embedded NULs and shorter prefixes" {
    try std.testing.expect(strncasecmp(&[_]u8{ 'A', 0, 'z' }, &[_]u8{ 'a', 0, 'x' }, 3) == 0);
    try std.testing.expect(strncasecmp(&[_]u8{ 'A', 0, 'z' }, "ab", 3) < 0);
    try std.testing.expect(strncasecmp("ab", &[_]u8{ 'A', 0, 'z' }, 3) > 0);
    try std.testing.expect(strncasecmp("ab", "ABC", 2) == 0);
}

test "memdup and memchrInv preserve byte content" {
    var dup = try memdup(std.testing.allocator, "abc");
    defer std.testing.allocator.free(dup);
    try std.testing.expectEqualStrings("abc", dup);
    dup[0] = 'z';
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'b', 'c' }, dup);
    try std.testing.expectEqual(@as(?usize, 2), memchrInv(&[_]u8{ 'x', 'x', 'y' }, 'x'));
}

test "memchr_inv mirrors memchrInv byte-search semantics" {
    try std.testing.expectEqual(memchrInv(&[_]u8{ 0, 0, 1 }, 0), memchr_inv(&[_]u8{ 0, 0, 1 }, 0));
}

test "memchrInv keeps long-buffer first-dirty-byte results stable" {
    var buf = [_]u8{0} ** 32;
    buf[19] = 1;
    try std.testing.expectEqual(@as(?usize, 19), memchrInv(buf[0..], 0));
}

test "memchrInv follows the earliest dirty byte as long buffers change" {
    var buf = [_]u8{0} ** 32;
    buf[21] = 1;
    try std.testing.expectEqual(@as(?usize, 21), memchrInv(buf[0..], 0));
    buf[7] = 1;
    try std.testing.expectEqual(@as(?usize, 7), memchrInv(buf[0..], 0));
}

test "memchrInv dirty-word shortcut handles zero-value scans at word boundaries" {
    var buf = [_]u8{0} ** 24;
    buf[@sizeOf(usize)] = 9;
    try std.testing.expectEqual(@as(?usize, @sizeOf(usize)), memchrInv(buf[0..], 0));
}

test "memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment" {
    for (0..@sizeOf(usize)) |offset| {
        var backing = [_]u8{0} ** 40;
        backing[offset + 9] = 2;
        try std.testing.expectEqual(@as(?usize, 9), memchrInv(backing[offset..], 0));
    }
}

test "memchrInv keeps the earliest dirty byte for long non-zero scans across alignments" {
    for (0..@sizeOf(usize)) |offset| {
        var backing = [_]u8{7} ** 40;
        backing[offset + 11] = 5;
        try std.testing.expectEqual(@as(?usize, 11), memchrInv(backing[offset .. offset + 32], 7));
    }
}

test "memchrInv keeps the earliest dirty byte for long zero-value scans across alignments" {
    for (0..@sizeOf(usize)) |offset| {
        var backing = [_]u8{0} ** 40;
        backing[offset + 13] = 4;
        try std.testing.expectEqual(@as(?usize, 13), memchrInv(backing[offset .. offset + 32], 0));
    }
}

test "memchrInv finds a dirty byte in the unaligned prefix before the word fast path" {
    for (1..@sizeOf(usize)) |offset| {
        var backing = [_]u8{0} ** 40;
        backing[offset + 2] = 9;
        try std.testing.expectEqual(@as(?usize, 2), memchrInv(backing[offset..], 0));
    }
}

test "memchrInv keeps aligned word hits stable after consuming an unaligned prefix" {
    for (1..@sizeOf(usize)) |offset| {
        var backing = [_]u8{7} ** 48;
        const aligned_index = @sizeOf(usize) - offset;
        backing[offset + aligned_index + @sizeOf(usize)] = 1;
        try std.testing.expectEqual(
            @as(?usize, aligned_index + @sizeOf(usize)),
            memchrInv(backing[offset .. offset + 32], 7),
        );
    }
}

test "memchrInv short zero-value scans stay byte-accurate" {
    try std.testing.expectEqual(@as(?usize, 3), memchrInv(&[_]u8{ 0, 0, 0, 1 }, 0));
}

test "memchrInv keeps the earliest dirty byte across the fast-path cutoff" {
    var short = [_]u8{0} ** (@sizeOf(usize) * 2 - 1);
    short[short.len - 1] = 1;
    try std.testing.expectEqual(@as(?usize, short.len - 1), memchrInv(short[0..], 0));

    var long = [_]u8{0} ** (@sizeOf(usize) * 2);
    long[long.len - 1] = 1;
    try std.testing.expectEqual(@as(?usize, long.len - 1), memchrInv(long[0..], 0));
}

test "memchrInv keeps non-zero scans stable across the fast-path cutoff" {
    var short = [_]u8{7} ** (@sizeOf(usize) * 2 - 1);
    short[short.len - 1] = 9;
    try std.testing.expectEqual(@as(?usize, short.len - 1), memchrInv(short[0..], 7));

    var long = [_]u8{7} ** (@sizeOf(usize) * 2);
    long[long.len - 1] = 9;
    try std.testing.expectEqual(@as(?usize, long.len - 1), memchrInv(long[0..], 7));
}

test "memparse handles decimal hexadecimal octal and suffixes" {
    try std.testing.expectEqual(@as(u64, 16), memparse("16").value);
    try std.testing.expectEqual(@as(u64, 16), memparse("0x10").value);
    try std.testing.expectEqual(@as(u64, 8), memparse("010").value);
    try std.testing.expectEqual(@as(u64, 2 << 10), memparse("2K").value);
}

test "memparse keeps original rest when sign is not followed by digits" {
    const parsed = memparse("-abc");
    try std.testing.expectEqual(@as(u64, 0), parsed.value);
    try std.testing.expectEqualStrings("-abc", parsed.rest);
}

test "memparse saturates signed overflow instead of trapping" {
    const parsed = memparse("-9223372036854775809");
    const min_signed: i64 = std.math.minInt(i64);
    try std.testing.expectEqual(@as(u64, @bitCast(min_signed)), parsed.value);
}

test "memparse clamps explicit positive signed overflow" {
    const parsed = memparse("+9223372036854775808");
    try std.testing.expectEqual(@as(u64, @intCast(std.math.maxInt(i64))), parsed.value);
}

test "memparse keeps signed values and their trailing rest aligned" {
    const parsed = memparse("-16 trailing");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -16))), parsed.value);
    try std.testing.expectEqualStrings(" trailing", parsed.rest);
}

test "memparse consumes suffix after saturation" {
    const parsed = memparse("18446744073709551615Ktail");
    try std.testing.expectEqual(std.math.maxInt(u64), parsed.value);
    try std.testing.expectEqualStrings("tail", parsed.rest);
}

test "memparse applies suffixes before signed clamping" {
    const parsed = memparse("-9000000000000K");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -9216000000000000))), parsed.value);
}

test "strstr mirrors full-length C-string substring searches" {
    try std.testing.expectEqual(@as(?usize, 1), strstr("abc", "bc"));
    try std.testing.expectEqual(@as(?usize, null), strstr(&[_]u8{ 'a', 0, 'b', 'c' }, "bc"));
    try std.testing.expectEqual(@as(?usize, 1), strstr("abc", &[_]u8{ 'b', 0, 'x' }));
    try std.testing.expectEqual(@as(?usize, 0), strstr("abc", ""));
}

test "strnstr honors count and C-string boundaries" {
    try std.testing.expectEqual(@as(?usize, 1), strnstr("abc", "bc", 3));
    try std.testing.expectEqual(@as(?usize, null), strnstr("abc", "bc", 1));
    try std.testing.expectEqual(@as(?usize, null), strnstr(&[_]u8{ 'a', 0, 'b', 'c' }, "bc", 4));
    try std.testing.expectEqual(@as(?usize, 1), strnstr("abc", &[_]u8{ 'b', 0, 'x' }, 3));
    try std.testing.expectEqual(@as(?usize, 0), strnstr("abc", "", 0));
}

test "strchr mirrors full-length C-string searches" {
    try std.testing.expectEqual(@as(?usize, 1), strchr("abc", 'b'));
    try std.testing.expectEqual(@as(?usize, null), strchr(&[_]u8{ 'a', 0, 'b' }, 'b'));
}

test "strrchr finds the last in-range match with C-string semantics" {
    try std.testing.expectEqual(@as(?usize, 3), strrchr("abca", 'a'));
    try std.testing.expectEqual(@as(?usize, 0), strrchr(&[_]u8{ 'a', 0, 'a' }, 'a'));
}

test "strchr and strrchr return the terminator index when searching for NUL" {
    try std.testing.expectEqual(@as(?usize, 3), strchr("abc", 0));
    try std.testing.expectEqual(@as(?usize, 1), strchr(&[_]u8{ 'a', 0, 'b' }, 0));
    try std.testing.expectEqual(@as(?usize, 3), strrchr("abc", 0));
    try std.testing.expectEqual(@as(?usize, 1), strrchr(&[_]u8{ 'a', 0, 'b' }, 0));
}

test "strpbrk finds the first accepted byte with C-string semantics" {
    try std.testing.expectEqual(@as(?usize, 1), strpbrk("kernel", "xyre"));
    try std.testing.expectEqual(@as(?usize, null), strpbrk(&[_]u8{ 'a', 0, 'b' }, "b"));
}

test "strspn counts the accepted prefix with C-string semantics" {
    try std.testing.expectEqual(@as(usize, 4), strspn("abba!", "ab"));
    try std.testing.expectEqual(@as(usize, 0), strspn("abba!", "xyz"));
    try std.testing.expectEqual(@as(usize, 0), strspn("abba!", ""));

    const cstr = [_]u8{ 'a', 'b', 'a', 0, 'b' };
    try std.testing.expectEqual(@as(usize, 3), strspn(&cstr, "ab"));

    const accept_cstr = [_]u8{ 'a', 0, 'z' };
    try std.testing.expectEqual(@as(usize, 1), strspn("abca", &accept_cstr));
}

test "strcspn counts until the first rejected byte with C-string semantics" {
    try std.testing.expectEqual(@as(usize, 4), strcspn("path=/tmp", "="));
    try std.testing.expectEqual(@as(usize, 4), strcspn("keep", ""));

    const cstr = [_]u8{ 'a', 'b', 'c', 0, 'x' };
    try std.testing.expectEqual(@as(usize, 3), strcspn(&cstr, "xyz"));

    const reject_cstr = [_]u8{ 'x', 0, 'y' };
    try std.testing.expectEqual(@as(usize, 2), strcspn("abxc", &reject_cstr));
}

test "strnchr honors count and C-string boundaries" {
    try std.testing.expectEqual(@as(?usize, 1), strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), strnchr("abc", 1, 'b'));
    try std.testing.expectEqual(@as(?usize, null), strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 'b'));
}

test "strnchr treats the NUL terminator as searchable within the count window" {
    try std.testing.expectEqual(@as(?usize, 1), strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 0));
    try std.testing.expectEqual(@as(?usize, 3), strnchr("abc", 4, 0));
    try std.testing.expectEqual(@as(?usize, null), strnchr("abc", 3, 0));
}

test "strlen honors C-string boundaries" {
    try std.testing.expectEqual(@as(usize, 3), strlen("abc"));
    try std.testing.expectEqual(@as(usize, 1), strlen(&[_]u8{ 'a', 0, 'b' }));
}

test "strnlen honors count and C-string boundaries" {
    try std.testing.expectEqual(@as(usize, 2), strnlen("abc", 2));
    try std.testing.expectEqual(@as(usize, 1), strnlen(&[_]u8{ 'a', 0, 'b' }, 3));
}

test "strnchrNul returns the first match, NUL, or count boundary" {
    try std.testing.expectEqual(@as(usize, 1), strnchrNul("abc", 3, 'b'));
    try std.testing.expectEqual(@as(usize, 3), strnchrNul("abc", 3, 'z'));
    try std.testing.expectEqual(@as(usize, 1), strnchrNul(&[_]u8{ 'a', 0, 'b' }, 3, 'z'));
    try std.testing.expectEqual(@as(usize, 1), strnchrnul(&[_]u8{ 'a', 'b', 0 }, 3, 'b'));
}

test "strchrNul and strchrnul return the first match or terminator boundary" {
    try std.testing.expectEqual(@as(usize, 1), strchrNul("abc", 'b'));
    try std.testing.expectEqual(@as(usize, 3), strchrNul("abc", 'z'));
    try std.testing.expectEqual(@as(usize, 1), strchrNul(&[_]u8{ 'a', 0, 'b' }, 'z'));
    try std.testing.expectEqual(@as(usize, 1), strchrnul(&[_]u8{ 'a', 'b', 0 }, 'b'));
}
