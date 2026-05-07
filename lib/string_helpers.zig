// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");
const cmdline = @import("cmdline.zig");

pub const EINVAL: i32 = -22;
pub const STRING_UNITS_10: u32 = 0;
pub const STRING_UNITS_2: u32 = 1;
pub const STRING_UNITS_MASK: u32 = 1 << 0;
pub const STRING_UNITS_NO_SPACE: u32 = 1 << 30;
pub const STRING_UNITS_NO_BYTES: u32 = 1 << 31;
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
const empty_kasprintf_strarray_null_terminated: []const ?[*:0]const u8 = &.{null};

pub const KasprintfStrarrayResult = struct {
    names: [][:0]u8,
    names_null_terminated: []const ?[*:0]const u8,

    pub fn deinit(self: *KasprintfStrarrayResult, allocator: std.mem.Allocator) void {
        for (self.names) |name| {
            allocator.free(name);
        }
        if (self.names_null_terminated.ptr != empty_kasprintf_strarray_null_terminated.ptr) {
            allocator.free(self.names_null_terminated);
        }
        if (self.names.len != 0) {
            allocator.free(self.names);
        }
        self.* = .{
            .names = &.{},
            .names_null_terminated = empty_kasprintf_strarray_null_terminated,
        };
    }

    pub fn cArray(self: *const KasprintfStrarrayResult) [*]const ?[*:0]const u8 {
        return self.names_null_terminated.ptr;
    }
};

pub const ParseIntArrayError = std.mem.Allocator.Error || error{NoEntry};
pub const ParseIntArrayUserError = ParseIntArrayError || error{Fault};

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

pub fn kstrdupAndReplace(
    allocator: std.mem.Allocator,
    src: []const u8,
    old: u8,
    new: u8,
) ![:0]u8 {
    const dup = try allocator.dupeZ(u8, cStringPrefix(src));
    _ = strreplace(dup, old, new);
    return dup;
}

pub fn kstrdupQuotable(allocator: std.mem.Allocator, src: ?[]const u8) !?[:0]u8 {
    const current = src orelse return null;
    const prefix = cStringPrefix(current);
    const quotable_only = "\x0c\n\r\t\x0b\x07\x1b\\\"";
    var empty: [0]u8 = .{};
    const escaped_len = stringEscapeMem(prefix, empty[0..], ESCAPE_HEX, quotable_only);
    const dup_len = try std.math.add(usize, escaped_len, 1);
    const dup = try allocator.alloc(u8, dup_len);
    errdefer allocator.free(dup);
    const written = stringEscapeMem(prefix, dup[0..escaped_len], ESCAPE_HEX, quotable_only);
    std.debug.assert(written == escaped_len);
    dup[escaped_len] = 0;
    return dup[0..escaped_len :0];
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
    const units_10 = [_][]const u8{ "", "k", "M", "G", "T", "P", "E", "Z", "Y" };
    const units_2 = [_][]const u8{ "", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi" };
    const rounding = [_]u32{ 500, 50, 5 };

    const units_base = units & STRING_UNITS_MASK;
    const divisor: u64 = if (units_base == STRING_UNITS_2) 1024 else 1000;
    const unit_table = if (units_base == STRING_UNITS_2) units_2[0..] else units_10[0..];

    var size = size_in;
    var blk_size = blk_size_in;
    var remainder: u32 = 0;
    var scale_index: usize = 0;
    var fraction: []const u8 = "";
    var fraction_buf: [5]u8 = undefined;
    var rendered_buf: [24]u8 = undefined;

    if (blk_size == 0) {
        size = 0;
    }

    if (size != 0) {
        while ((blk_size >> 32) != 0) {
            blk_size /= divisor;
            scale_index += 1;
        }

        while ((size >> 32) != 0) {
            size /= divisor;
            scale_index += 1;
        }

        size *= blk_size;

        while (size >= divisor) {
            remainder = @intCast(size % divisor);
            size /= divisor;
            scale_index += 1;
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
            const digits = std.fmt.bufPrint(&fraction_buf, ".{d:0>3}", .{remainder}) catch unreachable;
            fraction = digits[0 .. precision_digits + 1];
        }
    }

    const unit = if (scale_index >= unit_table.len) "UNK" else unit_table[scale_index];
    const rendered = std.fmt.bufPrint(
        &rendered_buf,
        "{d}{s}{s}{s}{s}",
        .{
            size,
            fraction,
            if ((units & STRING_UNITS_NO_SPACE) != 0) "" else " ",
            unit,
            if ((units & STRING_UNITS_NO_BYTES) != 0) "" else "B",
        },
    ) catch unreachable;

    copyRenderedCString(buf, rendered);
    return rendered.len;
}

pub fn parseIntArray(allocator: std.mem.Allocator, buf: []const u8) ParseIntArrayError![]i32 {
    const current = cStringPrefix(buf);
    var count_only = [_]i32{0};
    _ = cmdline.getOptions(current, 0, &count_only);

    if (count_only[0] <= 0) {
        return error.NoEntry;
    }

    const nints: usize = @intCast(count_only[0]);
    const ints = try allocator.alloc(i32, nints + 1);
    errdefer allocator.free(ints);

    _ = cmdline.getOptions(current, ints.len, ints);
    return ints;
}

pub fn parseIntArrayUser(
    allocator: std.mem.Allocator,
    from: []const u8,
    count: usize,
) ParseIntArrayUserError![]i32 {
    if (count > from.len) {
        return error.Fault;
    }

    const buf = try allocator.alloc(u8, count + 1);
    defer allocator.free(buf);

    @memcpy(buf[0..count], from[0..count]);
    buf[count] = 0;
    return parseIntArray(allocator, buf);
}

pub fn freeIntArray(allocator: std.mem.Allocator, ints: []i32) void {
    allocator.free(ints);
}

pub fn kasprintfStrarray(
    allocator: std.mem.Allocator,
    prefix: []const u8,
    n: usize,
) !KasprintfStrarrayResult {
    const current = cStringPrefix(prefix);
    if (n == 0) {
        return .{
            .names = &.{},
            .names_null_terminated = empty_kasprintf_strarray_null_terminated,
        };
    }

    var names = try allocator.alloc([:0]u8, n);
    errdefer allocator.free(names);

    var names_null_terminated = try allocator.alloc(?[*:0]const u8, n + 1);
    errdefer allocator.free(names_null_terminated);

    var allocated: usize = 0;
    errdefer {
        for (names[0..allocated]) |name| {
            allocator.free(name);
        }
    }

    while (allocated < n) : (allocated += 1) {
        names[allocated] = try allocPrintCString(allocator, "{s}-{d}", .{ current, allocated });
        names_null_terminated[allocated] = names[allocated].ptr;
    }
    names_null_terminated[n] = null;

    return .{
        .names = names,
        .names_null_terminated = names_null_terminated,
    };
}

pub fn kfreeStrarray(allocator: std.mem.Allocator, result: *KasprintfStrarrayResult) void {
    result.deinit(allocator);
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

pub fn skipSpaces(s: []const u8) []const u8 {
    const prefix = cStringPrefix(s);
    var start: usize = 0;
    while (start < prefix.len and std.ascii.isWhitespace(prefix[start])) : (start += 1) {}
    return prefix[start..];
}

pub fn strim(s: []u8) []u8 {
    const prefix = cStringPrefixMutable(s);
    var end = prefix.len;

    while (end > 0 and std.ascii.isWhitespace(prefix[end - 1])) : (end -= 1) {}

    if (end < prefix.len) {
        prefix[end] = 0;
    }

    var start: usize = 0;
    while (start < end and std.ascii.isWhitespace(prefix[start])) : (start += 1) {}
    return prefix[start..end];
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

fn copyRenderedCString(dest: []u8, rendered: []const u8) void {
    if (dest.len == 0) {
        return;
    }

    const copy_len = @min(rendered.len, dest.len - 1);
    @memcpy(dest[0..copy_len], rendered[0..copy_len]);
    dest[copy_len] = 0;
}

fn allocPrintCString(
    allocator: std.mem.Allocator,
    comptime fmt: []const u8,
    args: anytype,
) ![:0]u8 {
    const len = std.fmt.count(fmt, args);
    const rendered = try allocator.alloc(u8, len + 1);
    errdefer allocator.free(rendered);
    _ = try std.fmt.bufPrint(rendered[0..len], fmt, args);
    rendered[len] = 0;
    return rendered[0..len :0];
}

fn runKasprintfStrarrayWithFailingAllocator(allocator: std.mem.Allocator, prefix: []const u8, n: usize) !void {
    var names = try kasprintfStrarray(allocator, prefix, n);
    defer names.deinit(allocator);
}

fn runKstrdupQuotableWithFailingAllocator(allocator: std.mem.Allocator, input: ?[]const u8) !void {
    if (try kstrdupQuotable(allocator, input)) |dup| {
        allocator.free(dup);
    }
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

test "kstrdupAndReplace duplicates the first-NUL prefix before replacing bytes" {
    const duplicated = try kstrdupAndReplace(std.testing.allocator, "tty-0\x00ignored-tail", '-', '_');
    defer std.testing.allocator.free(duplicated);

    try std.testing.expectEqualStrings("tty_0", duplicated);
    try std.testing.expectEqual(@as(u8, 0), duplicated[5]);
}

test "kstrdupQuotable hex-escapes special log bytes while preserving ordinary characters" {
    const duplicated = (try kstrdupQuotable(std.testing.allocator, "line\n\"tab\"\x1b\\tail")) orelse return error.TestUnexpectedResult;
    defer std.testing.allocator.free(duplicated);

    try std.testing.expectEqualStrings("line\\x0a\\x22tab\\x22\\x1b\\x5ctail", duplicated);
    try std.testing.expectEqual(@as(u8, 0), duplicated[duplicated.len]);
}

test "kstrdupQuotable returns null for null input, keeps empty results owned, and stops at the first NUL" {
    try std.testing.expectEqual(@as(?[:0]u8, null), try kstrdupQuotable(std.testing.allocator, null));

    const empty = (try kstrdupQuotable(std.testing.allocator, "")) orelse return error.TestUnexpectedResult;
    defer std.testing.allocator.free(empty);

    try std.testing.expectEqualStrings("", empty);
    try std.testing.expectEqual(@as(u8, 0), empty[0]);

    const duplicated = (try kstrdupQuotable(std.testing.allocator, "tty\tname\x00ignored")) orelse return error.TestUnexpectedResult;
    defer std.testing.allocator.free(duplicated);

    try std.testing.expectEqualStrings("tty\\x09name", duplicated);
}

test "kstrdupQuotable frees the owned copy when allocation fails" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runKstrdupQuotableWithFailingAllocator,
        .{"alpha\nbeta"},
    );
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

test "stringGetSize formats decimal and binary units with Linux-style rounding" {
    var out = [_]u8{0} ** 16;

    try std.testing.expectEqual(@as(usize, 7), stringGetSize(1500, 1, STRING_UNITS_10, &out));
    try std.testing.expectEqualStrings("1.50 kB", std.mem.sliceTo(&out, 0));

    try std.testing.expectEqual(@as(usize, 8), stringGetSize(1536, 1, STRING_UNITS_2, &out));
    try std.testing.expectEqualStrings("1.50 KiB", std.mem.sliceTo(&out, 0));
}

test "stringGetSize respects no-space and no-bytes modifiers" {
    var out = [_]u8{0} ** 16;

    try std.testing.expectEqual(@as(usize, 6), stringGetSize(4096, 1, STRING_UNITS_2 | STRING_UNITS_NO_SPACE | STRING_UNITS_NO_BYTES, &out));
    try std.testing.expectEqualStrings("4.00Ki", std.mem.sliceTo(&out, 0));

    try std.testing.expectEqual(@as(usize, 4), stringGetSize(500, 1, STRING_UNITS_10 | STRING_UNITS_NO_SPACE, &out));
    try std.testing.expectEqualStrings("500B", std.mem.sliceTo(&out, 0));
}

test "stringGetSize reports truncated output length without losing termination" {
    var out = [_]u8{ '!', '!', '!', '!' };
    const len = stringGetSize(1500, 1, STRING_UNITS_10, &out);

    try std.testing.expectEqual(@as(usize, 7), len);
    try std.testing.expectEqual(@as(u8, '1'), out[0]);
    try std.testing.expectEqual(@as(u8, '.'), out[1]);
    try std.testing.expectEqual(@as(u8, '5'), out[2]);
    try std.testing.expectEqual(@as(u8, 0), out[3]);
}

test "stringGetSize handles zero block size and zero-length outputs safely" {
    var out = [_]u8{ '?', '?', '?', '?', '?' };

    try std.testing.expectEqual(@as(usize, 3), stringGetSize(99, 0, STRING_UNITS_10, &out));
    try std.testing.expectEqualStrings("0 B", std.mem.sliceTo(&out, 0));
    try std.testing.expectEqual(@as(usize, 7), stringGetSize(1500, 1, STRING_UNITS_10, out[0..0]));
}

test "parseIntArray keeps mixed-base and negative-number semantics explicit" {
    const ints = try parseIntArray(std.testing.allocator, "0x10,07,-2");
    defer freeIntArray(std.testing.allocator, ints);

    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 16, 7, -2 }, ints);
}

test "parseIntArray respects the first NUL and count-bounded parsing" {
    const ints = try parseIntArray(std.testing.allocator, "1-3,9\x00ignored");
    defer freeIntArray(std.testing.allocator, ints);

    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 1, 2, 3, 9 }, ints);
}

test "parseIntArray fails closed when no integers are present" {
    try std.testing.expectError(error.NoEntry, parseIntArray(std.testing.allocator, ""));
    try std.testing.expectError(error.NoEntry, parseIntArray(std.testing.allocator, "noints"));
}

test "parseIntArrayUser copies a bounded user buffer before parsing" {
    const ints = try parseIntArrayUser(std.testing.allocator, "1-3,9 trailing", 5);
    defer freeIntArray(std.testing.allocator, ints);

    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 1, 2, 3, 9 }, ints);

    const nul_bounded = try parseIntArrayUser(std.testing.allocator, "7,8\x00ignored,9", 11);
    defer freeIntArray(std.testing.allocator, nul_bounded);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, 7, 8 }, nul_bounded);
}

test "parseIntArrayUser fails closed on short buffers and empty copied input" {
    try std.testing.expectError(error.Fault, parseIntArrayUser(std.testing.allocator, "12", 3));
    try std.testing.expectError(error.NoEntry, parseIntArrayUser(std.testing.allocator, "none", 4));
}

test "kasprintfStrarray returns sequential owned strings with a trailing null pointer" {
    var names = try kasprintfStrarray(std.testing.allocator, "cpu", 3);
    defer names.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 3), names.names.len);
    try std.testing.expectEqualStrings("cpu-0", names.names[0]);
    try std.testing.expectEqualStrings("cpu-1", names.names[1]);
    try std.testing.expectEqualStrings("cpu-2", names.names[2]);
    try std.testing.expectEqualStrings("cpu-0", std.mem.span(names.cArray()[0].?));
    try std.testing.expectEqual(@as(?[*:0]const u8, null), names.cArray()[3]);
}

test "kfreeStrarray keeps first-NUL prefixes, zero-count reuse, and repeated teardown safe" {
    var prefixed = try kasprintfStrarray(std.testing.allocator, "tty\x00ignored", 2);
    try std.testing.expectEqualStrings("tty-0", prefixed.names[0]);
    try std.testing.expectEqualStrings("tty-1", prefixed.names[1]);
    kfreeStrarray(std.testing.allocator, &prefixed);
    try std.testing.expectEqual(@as(usize, 0), prefixed.names.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), prefixed.cArray()[0]);
    kfreeStrarray(std.testing.allocator, &prefixed);

    var empty = try kasprintfStrarray(std.testing.allocator, "cpu", 0);
    try std.testing.expectEqual(@as(usize, 0), empty.names.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), empty.cArray()[0]);
    kfreeStrarray(std.testing.allocator, &empty);
    kfreeStrarray(std.testing.allocator, &empty);
}

test "kasprintfStrarray frees intermediate allocations when setup fails" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runKasprintfStrarrayWithFailingAllocator,
        .{ "cpu", @as(usize, 3) },
    );
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

test "stringUnescape keeps terminator-only and zero-capacity destinations bounded" {
    var terminator_only = [_]u8{'!'};
    const terminator_only_len = stringUnescape("\\n", &terminator_only, terminator_only.len, UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 0), terminator_only_len);
    try std.testing.expectEqual(@as(u8, 0), terminator_only[0]);

    var empty: [0]u8 = .{};
    const empty_len = stringUnescape("abc", empty[0..], 0, UNESCAPE_ANY);
    try std.testing.expectEqual(@as(usize, 0), empty_len);
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

test "stringEscapeMem zero-capacity destinations still report the full escaped length" {
    var empty: [0]u8 = .{};
    const empty_len = stringEscapeMem("\n", empty[0..], ESCAPE_HEX, null);
    try std.testing.expectEqual(@as(usize, 4), empty_len);

    var single = [_]u8{'?'};
    const single_len = stringEscapeMem("\n", &single, ESCAPE_HEX, null);
    try std.testing.expectEqual(@as(usize, 4), single_len);
    try std.testing.expectEqual(@as(u8, '\\'), single[0]);
}

test "skipSpaces returns the first non-whitespace byte before the first NUL" {
    try std.testing.expectEqualStrings("alpha", skipSpaces(" \t\nalpha\x00tail"));
    try std.testing.expectEqual(@as(usize, 0), skipSpaces("\x00tail").len);
}

test "strim trims in place without touching bytes after the first NUL" {
    var padded = [_]u8{ ' ', '\t', 'o', 'k', ' ', '\n', 0, 'x', ' ' };
    const trimmed = strim(&padded);
    try std.testing.expectEqualStrings("ok", trimmed);
    try std.testing.expectEqual(@as(u8, 0), padded[4]);
    try std.testing.expectEqual(@as(u8, 'x'), padded[7]);

    var spaces_only = [_]u8{ ' ', '\t', '\n', 0, 'x' };
    const empty = strim(&spaces_only);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(u8, 0), spaces_only[0]);
    try std.testing.expectEqual(@as(u8, 'x'), spaces_only[4]);
}
