// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");
const cmdline = @import("cmdline.zig");

pub const EINVAL: i32 = -22;
pub const UNESCAPE_SPACE: u32 = 1 << 0;
pub const UNESCAPE_OCTAL: u32 = 1 << 1;
pub const UNESCAPE_HEX: u32 = 1 << 2;
pub const UNESCAPE_SPECIAL: u32 = 1 << 3;
pub const UNESCAPE_ANY: u32 = UNESCAPE_SPACE | UNESCAPE_OCTAL | UNESCAPE_HEX | UNESCAPE_SPECIAL;
pub const UNESCAPE_ALL_MASK: u32 = UNESCAPE_ANY;
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
pub const ESCAPE_ALL_MASK: u32 = ESCAPE_ANY | ESCAPE_NP | ESCAPE_HEX | ESCAPE_NA | ESCAPE_NAP | ESCAPE_APPEND;
pub const STRING_UNITS_10: u32 = 0;
pub const STRING_UNITS_2: u32 = 1;
pub const STRING_UNITS_MASK: u32 = 1 << 0;
pub const STRING_UNITS_NO_SPACE: u32 = 1 << 30;
pub const STRING_UNITS_NO_BYTES: u32 = 1 << 31;

pub const ParseIntArrayError = std.mem.Allocator.Error || error{NoEntry};
const empty_kasprintf_strarray_null_terminated: []const ?[*:0]const u8 = &.{null};
const empty_kasprintf_strarray_raw: []const ?[*:0]u8 = &.{null};

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

pub fn kasprintfStrarrayRaw(
    allocator: std.mem.Allocator,
    prefix: []const u8,
    n: usize,
) ![]?[*:0]u8 {
    const current = cStringPrefix(prefix);
    if (n == 0) {
        return try allocator.dupe(?[*:0]u8, empty_kasprintf_strarray_raw);
    }

    const slot_count = try std.math.add(usize, n, 1);
    var names = try allocator.alloc(?[*:0]u8, slot_count);
    @memset(names, null);

    var allocated: usize = 0;
    errdefer kfreeStrarrayRaw(allocator, names, allocated);

    while (allocated < n) : (allocated += 1) {
        names[allocated] = (try allocPrintCString(allocator, "{s}-{d}", .{ current, allocated })).ptr;
    }
    names[n] = null;
    return names;
}

pub fn kfreeStrarrayRaw(allocator: std.mem.Allocator, array: ?[]?[*:0]u8, count: usize) void {
    const values = array orelse return;
    const limit = @min(count, values.len);
    for (values[0..limit]) |item| {
        if (item) |ptr| {
            allocator.free(std.mem.span(ptr));
        }
    }
    allocator.free(values);
}

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

pub fn skipSpaces(str: []const u8) []const u8 {
    const prefix = cStringPrefix(str);
    var start: usize = 0;
    while (start < prefix.len and std.ascii.isWhitespace(prefix[start])) : (start += 1) {}
    return prefix[start..];
}

pub fn strim(buf: []u8) []u8 {
    const prefix_len = cStringPrefixMutable(buf).len;
    var end = prefix_len;

    while (end > 0 and std.ascii.isWhitespace(buf[end - 1])) : (end -= 1) {}
    if (end < buf.len) {
        buf[end] = 0;
    }

    var start: usize = 0;
    while (start < end and std.ascii.isWhitespace(buf[start])) : (start += 1) {}
    return buf[start..end];
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
    const divisor = [_]u64{ 1000, 1024 };
    const rounding = [_]u32{ 500, 50, 5 };
    const units_10 = [_][]const u8{ "", "k", "M", "G", "T", "P", "E", "Z", "Y" };
    const units_2 = [_][]const u8{ "", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi" };
    const units_base: usize = @intCast(units & STRING_UNITS_MASK);

    var size = size_in;
    var blk_size = blk_size_in;
    var order: usize = 0;
    var remainder: u32 = 0;
    var fraction_buf: [12]u8 = undefined;
    var fraction: []const u8 = "";

    if (blk_size == 0) {
        size = 0;
    }

    if (size != 0) {
        while ((blk_size >> 32) != 0) {
            blk_size = @divFloor(blk_size, divisor[units_base]);
            order += 1;
        }
        while ((size >> 32) != 0) {
            size = @divFloor(size, divisor[units_base]);
            order += 1;
        }

        size *= blk_size;
        while (size >= divisor[units_base]) {
            remainder = @intCast(@mod(size, divisor[units_base]));
            size = @divFloor(size, divisor[units_base]);
            order += 1;
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
            const rendered = std.fmt.bufPrint(&fraction_buf, ".{d:0>3}", .{remainder}) catch unreachable;
            fraction = rendered[0 .. precision_digits + 1];
        }
    }

    const unit = if (order >= units_2.len)
        "UNK"
    else if (units_base == STRING_UNITS_2)
        units_2[order]
    else
        units_10[order];

    var rendered: [32]u8 = undefined;
    const full = std.fmt.bufPrint(
        &rendered,
        "{d}{s}{s}{s}{s}",
        .{
            size,
            fraction,
            if ((units & STRING_UNITS_NO_SPACE) != 0) "" else " ",
            unit,
            if ((units & STRING_UNITS_NO_BYTES) != 0) "" else "B",
        },
    ) catch unreachable;
    return copySnprintfStyle(buf, full);
}

pub fn parseIntArray(allocator: std.mem.Allocator, buf: []const u8) ParseIntArrayError![]i32 {
    const input = cStringPrefix(buf);
    var count_buf = [_]i32{0};
    _ = cmdline.getOptions(input, 0, &count_buf);
    if (count_buf[0] <= 0) {
        return error.NoEntry;
    }

    const count: usize = @intCast(count_buf[0]);
    const ints = try allocator.alloc(i32, try checkedTrailingNulCapacity(count));
    errdefer allocator.free(ints);
    @memset(ints, 0);
    _ = cmdline.getOptions(input, ints.len, ints);
    return ints;
}

pub fn parseIntArrayUser(allocator: std.mem.Allocator, from: []const u8, count: usize) ParseIntArrayError![]i32 {
    const copy_len = @min(count, from.len);
    const buf = try allocator.alloc(u8, try checkedTrailingNulCapacity(copy_len));
    defer allocator.free(buf);

    @memcpy(buf[0..copy_len], from[0..copy_len]);
    buf[copy_len] = 0;
    return parseIntArray(allocator, buf);
}

pub fn kstrdupQuotable(allocator: std.mem.Allocator, src: ?[]const u8) !?[:0]u8 {
    const input = src orelse return null;
    const prefix = cStringPrefix(input);
    const escaped_len = stringEscapeMem(prefix, &.{}, ESCAPE_HEX, "\x0c\n\r\t\x0b\x07\x1b\\\"");
    const dst = try allocator.alloc(u8, try checkedTrailingNulCapacity(escaped_len));
    errdefer allocator.free(dst);

    const actual_len = stringEscapeMem(prefix, dst[0..escaped_len], ESCAPE_HEX, "\x0c\n\r\t\x0b\x07\x1b\\\"");
    std.debug.assert(actual_len == escaped_len);
    dst[escaped_len] = 0;
    return dst[0..escaped_len :0];
}

pub fn kstrdupAndReplace(allocator: std.mem.Allocator, src: ?[]const u8, old: u8, new: u8) !?[:0]u8 {
    const input = src orelse return null;
    const prefix = cStringPrefix(input);
    const dst = try allocator.alloc(u8, try checkedTrailingNulCapacity(prefix.len));
    errdefer allocator.free(dst);

    @memcpy(dst[0..prefix.len], prefix);
    dst[prefix.len] = 0;
    _ = strreplace(dst[0 .. prefix.len + 1], old, new);
    return dst[0..prefix.len :0];
}

pub fn kasprintfStrarray(
    allocator: std.mem.Allocator,
    prefix: []const u8,
    n: usize,
) !KasprintfStrarrayResult {
    if (n == 0) {
        return .{
            .names = &.{},
            .names_null_terminated = empty_kasprintf_strarray_null_terminated,
        };
    }

    const slot_count = try std.math.add(usize, n, 1);
    var names = try allocator.alloc([:0]u8, n);
    errdefer allocator.free(names);

    const raw = try kasprintfStrarrayRaw(allocator, prefix, n);
    defer kfreeStrarrayRaw(allocator, raw, n);

    var names_null_terminated = try allocator.alloc(?[*:0]const u8, slot_count);
    errdefer allocator.free(names_null_terminated);

    var duplicated: usize = 0;
    errdefer {
        for (names[0..duplicated]) |name| {
            allocator.free(name);
        }
    }

    for (raw[0..n], 0..) |item, index| {
        const ptr = item orelse unreachable;
        const name = std.mem.span(ptr);
        names[index] = try allocator.dupeZ(u8, name);
        names_null_terminated[index] = names[index].ptr;
        duplicated += 1;
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

pub fn stringUnescapeInplace(buf: []u8, flags: u32) usize {
    return stringUnescape(buf, buf, 0, flags);
}

pub fn stringUnescapeAny(src: []const u8, dst: []u8, size: usize) usize {
    return stringUnescape(src, dst, size, UNESCAPE_ANY);
}

pub fn stringUnescapeAnyInplace(buf: []u8) usize {
    return stringUnescapeAny(buf, buf, 0);
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

pub fn stringEscapeMemAnyNp(src: []const u8, dst: []u8, only: ?[]const u8) usize {
    return stringEscapeMem(src, dst, ESCAPE_ANY_NP, only);
}

pub fn stringEscapeStr(src: []const u8, dst: []u8, size: usize, flags: u32, only: ?[]const u8) usize {
    const limit = @min(size, dst.len);
    return stringEscapeMem(cStringPrefix(src), dst[0..limit], flags, only);
}

pub fn stringEscapeStrAnyNp(src: []const u8, dst: []u8, size: usize, only: ?[]const u8) usize {
    return stringEscapeStr(src, dst, size, ESCAPE_ANY_NP, only);
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

fn copySnprintfStyle(dest: []u8, src: []const u8) usize {
    if (dest.len == 0) {
        return src.len;
    }

    const copy_len = @min(src.len, dest.len - 1);
    @memcpy(dest[0..copy_len], src[0..copy_len]);
    dest[copy_len] = 0;
    return src.len;
}

fn checkedTrailingNulCapacity(base_len: usize) error{Overflow}!usize {
    return std.math.add(usize, base_len, 1);
}

fn allocPrintCString(
    allocator: std.mem.Allocator,
    comptime fmt: []const u8,
    args: anytype,
) ![:0]u8 {
    const len = std.fmt.count(fmt, args);
    const rendered = try allocator.alloc(u8, try checkedTrailingNulCapacity(len));
    errdefer allocator.free(rendered);
    _ = try std.fmt.bufPrint(rendered[0..len], fmt, args);
    rendered[len] = 0;
    return rendered[0..len :0];
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

test "skipSpaces and strim preserve C-string whitespace semantics" {
    try std.testing.expectEqualStrings("value", skipSpaces(" \t\nvalue\x00tail"));
    try std.testing.expectEqual(skipSpaces(" \t\n\x00tail").len, 0);

    var trimmed = [_]u8{ ' ', '\t', 'o', 'k', '\n', ' ', 0, 'x' };
    const strimmed = strim(&trimmed);
    try std.testing.expectEqualStrings("ok", strimmed);
    try std.testing.expectEqual(@as(u8, 0), trimmed[4]);
    try std.testing.expectEqual(@as(u8, 0), trimmed[6]);
    try std.testing.expectEqual(@as(u8, 'x'), trimmed[7]);

    var all_space = [_]u8{ ' ', '\n', '\t', 0, 'x' };
    const empty = strim(&all_space);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(u8, 0), all_space[0]);
    try std.testing.expectEqual(@as(u8, 'x'), all_space[4]);
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

test "stringGetSize formats bounded SI and binary sizes" {
    var out = [_]u8{0} ** 16;

    try std.testing.expectEqual(@as(usize, 3), stringGetSize(0, 1, STRING_UNITS_10, &out));
    try std.testing.expectEqualStrings("0 B", cStringPrefix(&out));

    try std.testing.expectEqual(@as(usize, 7), stringGetSize(1500, 1, STRING_UNITS_10, &out));
    try std.testing.expectEqualStrings("1.50 kB", cStringPrefix(&out));

    try std.testing.expectEqual(@as(usize, 8), stringGetSize(1536, 1, STRING_UNITS_2, &out));
    try std.testing.expectEqualStrings("1.50 KiB", cStringPrefix(&out));

    try std.testing.expectEqual(@as(usize, 7), stringGetSize(10, 512, STRING_UNITS_10, &out));
    try std.testing.expectEqualStrings("5.12 kB", cStringPrefix(&out));

    try std.testing.expectEqual(@as(usize, 7), stringGetSize(1100, 1, STRING_UNITS_10, &out));
    try std.testing.expectEqualStrings("1.10 kB", cStringPrefix(&out));

    try std.testing.expectEqual(@as(usize, 8), stringGetSize(1100, 1, STRING_UNITS_2, &out));
    try std.testing.expectEqualStrings("1.07 KiB", cStringPrefix(&out));

    try std.testing.expectEqual(@as(usize, 7), stringGetSize(3000, 1900, STRING_UNITS_10, &out));
    try std.testing.expectEqualStrings("5.70 MB", cStringPrefix(&out));

    try std.testing.expectEqual(@as(usize, 8), stringGetSize(3000, 1900, STRING_UNITS_2, &out));
    try std.testing.expectEqualStrings("5.44 MiB", cStringPrefix(&out));

    try std.testing.expectEqual(@as(usize, 7), stringGetSize(std.math.maxInt(u64), 4096, STRING_UNITS_10, &out));
    try std.testing.expectEqualStrings("75.6 ZB", cStringPrefix(&out));

    try std.testing.expectEqual(@as(usize, 8), stringGetSize(std.math.maxInt(u64), 4096, STRING_UNITS_2, &out));
    try std.testing.expectEqualStrings("64.0 ZiB", cStringPrefix(&out));
}

test "stringGetSize honors formatting flags and snprintf-style truncation" {
    var compact = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0 };
    try std.testing.expectEqual(
        @as(usize, 6),
        stringGetSize(1536, 1, STRING_UNITS_2 | STRING_UNITS_NO_SPACE | STRING_UNITS_NO_BYTES, &compact),
    );
    try std.testing.expectEqualStrings("1.50Ki", cStringPrefix(&compact));

    var truncated = [_]u8{ '!', '!', '!', '!', '!' };
    try std.testing.expectEqual(@as(usize, 7), stringGetSize(1500, 1, STRING_UNITS_10, &truncated));
    try std.testing.expectEqualSlices(u8, &[_]u8{ '1', '.', '5', '0', 0 }, &truncated);

    try std.testing.expectEqual(@as(usize, 7), stringGetSize(1500, 1, STRING_UNITS_10, &.{}));
}

test "stringEscapeStr treats zero-sized destinations as length-only requests" {
    var out = [_]u8{ '?', '?', '?', '?' };
    const len = stringEscapeStr("A\n\x00tail", &out, 0, ESCAPE_HEX, null);

    try std.testing.expectEqual(@as(usize, 8), len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '?', '?', '?', '?' }, &out);

    const any_np_len = stringEscapeStrAnyNp("A\n\x00tail", &out, 0, null);
    try std.testing.expectEqual(@as(usize, 3), any_np_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '?', '?', '?', '?' }, &out);
}

test "allocation-backed trailing-NUL helpers reject usize overflow before allocation" {
    try std.testing.expectEqual(@as(usize, 1), try checkedTrailingNulCapacity(0));
    try std.testing.expectError(error.Overflow, checkedTrailingNulCapacity(std.math.maxInt(usize)));
}

test "parseIntArray returns a counted Linux-style integer array" {
    const ints = try parseIntArray(std.testing.allocator, "1-3,5");
    defer std.testing.allocator.free(ints);

    try std.testing.expectEqual(@as(usize, 5), ints.len);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 1, 2, 3, 5 }, ints);
}

test "parseIntArray reuses cmdline parsing semantics for bases and negatives" {
    const ints = try parseIntArray(std.testing.allocator, "0x10,07,-2");
    defer std.testing.allocator.free(ints);

    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 16, 7, -2 }, ints);
}

test "parseIntArray truncates wide values and stops at the first NUL" {
    const ints = try parseIntArray(std.testing.allocator, "4294967297\x00,3");
    defer std.testing.allocator.free(ints);

    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 1 }, ints);
}

test "parseIntArray returns NoEntry when nothing parseable is present" {
    try std.testing.expectError(error.NoEntry, parseIntArray(std.testing.allocator, ""));
    try std.testing.expectError(error.NoEntry, parseIntArray(std.testing.allocator, "+,7"));
}

test "parseIntArrayUser copies a bounded input window before parsing" {
    const ints = try parseIntArrayUser(std.testing.allocator, "1-3,5", 3);
    defer std.testing.allocator.free(ints);

    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 1, 2, 3 }, ints);
}

test "parseIntArrayUser keeps count-bounded NUL insertion and empty-input behavior" {
    const counted = try parseIntArrayUser(std.testing.allocator, "7,9tail", 3);
    defer std.testing.allocator.free(counted);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, 7, 9 }, counted);

    try std.testing.expectError(error.NoEntry, parseIntArrayUser(std.testing.allocator, "1,2", 0));
}

test "kstrdupQuotable allocates an escaped printable C string" {
    const quoted = (try kstrdupQuotable(std.testing.allocator, "A\n\t\\\"\x00tail")).?;
    defer std.testing.allocator.free(quoted);

    try std.testing.expectEqualStrings("A\\x0a\\x09\\x5c\\x22", quoted);
    try std.testing.expectEqual(@as(u8, 0), quoted[quoted.len]);

    try std.testing.expectEqual(@as(?[:0]u8, null), try kstrdupQuotable(std.testing.allocator, null));
}

test "kstrdupAndReplace duplicates the prefix before replacing bytes in place" {
    const replaced = (try kstrdupAndReplace(std.testing.allocator, "a-b-a\x00tail", '-', '_')).?;
    defer std.testing.allocator.free(replaced);

    try std.testing.expectEqualStrings("a_b_a", replaced);
    try std.testing.expectEqual(@as(u8, 0), replaced[replaced.len]);

    var original = [_]u8{ 'a', '-', 'b', 0, '-', 'x' };
    const duplicate = (try kstrdupAndReplace(std.testing.allocator, &original, '-', '_')).?;
    defer std.testing.allocator.free(duplicate);
    try std.testing.expectEqualStrings("a_b", duplicate);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '-', 'b', 0, '-', 'x' }, &original);

    try std.testing.expectEqual(@as(?[:0]u8, null), try kstrdupAndReplace(std.testing.allocator, null, '-', '_'));
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

fn expectKasprintfStrarrayAllocFailure(allocator: std.mem.Allocator) !void {
    var names = try kasprintfStrarray(allocator, "cpu", 3);
    defer names.deinit(allocator);
}

test "kasprintfStrarray frees partially duplicated names on allocation failure" {
    try std.testing.checkAllAllocationFailures(std.testing.allocator, expectKasprintfStrarrayAllocFailure, .{});
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

test "kasprintfStrarray rejects usize overflow before wrapper allocation" {
    try std.testing.expectError(error.Overflow, kasprintfStrarray(std.testing.allocator, "cpu", std.math.maxInt(usize)));
}

test "kasprintfStrarrayRaw keeps zero-count ownership and teardown semantics explicit" {
    const empty_a = try kasprintfStrarrayRaw(std.testing.allocator, "cpu", 0);
    const empty_b = try kasprintfStrarrayRaw(std.testing.allocator, "cpu", 0);
    try std.testing.expectEqual(@as(usize, 1), empty_a.len);
    try std.testing.expectEqual(@as(?[*:0]u8, null), empty_a[0]);
    try std.testing.expect(empty_a.ptr != empty_kasprintf_strarray_raw.ptr);
    try std.testing.expect(empty_b.ptr != empty_kasprintf_strarray_raw.ptr);
    try std.testing.expect(empty_a.ptr != empty_b.ptr);
    kfreeStrarrayRaw(std.testing.allocator, empty_a, 0);
    kfreeStrarrayRaw(std.testing.allocator, empty_b, 0);

    const partial = try std.testing.allocator.alloc(?[*:0]u8, 2);
    @memset(partial, null);
    partial[0] = (try std.testing.allocator.dupeZ(u8, "tty-0")).ptr;
    kfreeStrarrayRaw(std.testing.allocator, partial, 99);

    kfreeStrarrayRaw(std.testing.allocator, null, 7);
}

test "kasprintfStrarrayRaw rejects usize overflow before allocation" {
    try std.testing.expectError(error.Overflow, kasprintfStrarrayRaw(std.testing.allocator, "cpu", std.math.maxInt(usize)));
}

test "escape flag masks stay aligned with the Linux public helper surface" {
    try std.testing.expectEqual(
        UNESCAPE_SPACE | UNESCAPE_OCTAL | UNESCAPE_HEX | UNESCAPE_SPECIAL,
        UNESCAPE_ALL_MASK,
    );
    try std.testing.expectEqual(
        ESCAPE_SPACE | ESCAPE_SPECIAL | ESCAPE_NULL | ESCAPE_OCTAL | ESCAPE_NP | ESCAPE_HEX | ESCAPE_NA | ESCAPE_NAP | ESCAPE_APPEND,
        ESCAPE_ALL_MASK,
    );
}
