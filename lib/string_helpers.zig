const std = @import("std");

pub const STRING_UNITS_10: u32 = 0;
pub const STRING_UNITS_2: u32 = 1;
pub const STRING_UNITS_MASK: u32 = @as(u32, 1) << 0;
pub const STRING_UNITS_NO_SPACE: u32 = @as(u32, 1) << 30;
pub const STRING_UNITS_NO_BYTES: u32 = @as(u32, 1) << 31;

pub const UNESCAPE_SPACE: u32 = @as(u32, 1) << 0;
pub const UNESCAPE_OCTAL: u32 = @as(u32, 1) << 1;
pub const UNESCAPE_HEX: u32 = @as(u32, 1) << 2;
pub const UNESCAPE_SPECIAL: u32 = @as(u32, 1) << 3;
pub const UNESCAPE_ANY: u32 = UNESCAPE_SPACE | UNESCAPE_OCTAL | UNESCAPE_HEX | UNESCAPE_SPECIAL;
pub const UNESCAPE_ALL_MASK: u32 = UNESCAPE_ANY;

pub const ESCAPE_SPACE: u32 = @as(u32, 1) << 0;
pub const ESCAPE_SPECIAL: u32 = @as(u32, 1) << 1;
pub const ESCAPE_NULL: u32 = @as(u32, 1) << 2;
pub const ESCAPE_OCTAL: u32 = @as(u32, 1) << 3;
pub const ESCAPE_ANY: u32 = ESCAPE_SPACE | ESCAPE_OCTAL | ESCAPE_SPECIAL | ESCAPE_NULL;
pub const ESCAPE_NP: u32 = @as(u32, 1) << 4;
pub const ESCAPE_ANY_NP: u32 = ESCAPE_ANY | ESCAPE_NP;
pub const ESCAPE_HEX: u32 = @as(u32, 1) << 5;
pub const ESCAPE_NA: u32 = @as(u32, 1) << 6;
pub const ESCAPE_NAP: u32 = @as(u32, 1) << 7;
pub const ESCAPE_APPEND: u32 = @as(u32, 1) << 8;
pub const ESCAPE_ALL_MASK: u32 = (@as(u32, 1) << 9) - 1;

const string_units_10 = [_][]const u8{ "", "k", "M", "G", "T", "P", "E", "Z", "Y" };
const string_units_2 = [_][]const u8{ "", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi" };
const empty_kasprintf_strarray_null_terminated: []const ?[*:0]const u8 = &.{null};

const UnescapeMatch = struct {
    value: u8,
    consumed: usize,
};

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

    pub fn cArray(self: *const KasprintfStrarrayResult) [*:null]const ?[*:0]const u8 {
        std.debug.assert(self.names_null_terminated.len == self.names.len + 1);
        std.debug.assert(self.names_null_terminated[self.names.len] == null);
        return self.names_null_terminated[0..self.names.len :null].ptr;
    }
};

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

fn isOctDigit(ch: u8) bool {
    return ch >= '0' and ch <= '7';
}

fn isAscii(ch: u8) bool {
    return ch <= 0x7f;
}

fn isPrintable(ch: u8) bool {
    return ch >= 0x20 and ch <= 0x7e;
}

fn hexNibble(ch: u8) ?u8 {
    return switch (ch) {
        '0'...'9' => ch - '0',
        'a'...'f' => ch - 'a' + 10,
        'A'...'F' => ch - 'A' + 10,
        else => null,
    };
}

fn hexUpperNibble(ch: u8) u8 {
    return "0123456789ABCDEF"[ch >> 4];
}

fn hexLowerNibble(ch: u8) u8 {
    return "0123456789ABCDEF"[ch & 0x0f];
}

fn stringUnitsDivisor(units_base: u32) u128 {
    return if (units_base == STRING_UNITS_2) 1024 else 1000;
}

fn stringUnitsLabel(units_base: u32, index: usize) []const u8 {
    if (index >= string_units_2.len) return "UNK";
    return if (units_base == STRING_UNITS_2) string_units_2[index] else string_units_10[index];
}

fn stringGetSizeFractionDigits(value: u128) usize {
    if (value >= 100) return 0;
    if (value >= 10) return 1;
    return 2;
}

fn stringGetSizeFractionFactor(decimals: usize) u128 {
    return switch (decimals) {
        0 => 1,
        1 => 10,
        else => 100,
    };
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

fn allocKasprintfStrarrayNullTerminated(
    allocator: std.mem.Allocator,
    n: usize,
) ![]?[*:0]const u8 {
    const len = try std.math.add(usize, n, 1);
    return allocator.alloc(?[*:0]const u8, len);
}

fn allocKasprintfStrarrayNames(
    allocator: std.mem.Allocator,
    n: usize,
) ![][:0]u8 {
    _ = try std.math.mul(usize, @sizeOf([:0]u8), n);
    return allocator.alloc([:0]u8, n);
}

fn matchUnescapeSpace(src: []const u8) ?UnescapeMatch {
    if (src.len == 0) return null;
    const value: u8 = switch (src[0]) {
        'n' => '\n',
        'r' => '\r',
        't' => '\t',
        'v' => '\x0b',
        'f' => '\x0c',
        else => return null,
    };
    return .{ .value = value, .consumed = 1 };
}

fn matchUnescapeOctal(src: []const u8) ?UnescapeMatch {
    if (src.len == 0 or !isOctDigit(src[0])) return null;

    var value: u8 = src[0] & 7;
    var consumed: usize = 1;

    while (value < 32 and consumed < 3 and consumed < src.len and isOctDigit(src[consumed])) : (consumed += 1) {
        value = (value << 3) + (src[consumed] & 7);
    }

    return .{ .value = value, .consumed = consumed };
}

fn matchUnescapeHex(src: []const u8) ?UnescapeMatch {
    if (src.len < 2 or src[0] != 'x') return null;

    var value = hexNibble(src[1]) orelse return null;
    var consumed: usize = 2;

    if (src.len > 2) {
        if (hexNibble(src[2])) |next| {
            value = (value << 4) | next;
            consumed += 1;
        }
    }

    return .{ .value = value, .consumed = consumed };
}

fn matchUnescapeSpecial(src: []const u8) ?UnescapeMatch {
    if (src.len == 0) return null;
    const value: u8 = switch (src[0]) {
        '"' => '"',
        '\\' => '\\',
        'a' => '\x07',
        'e' => '\x1b',
        else => return null,
    };
    return .{ .value = value, .consumed = 1 };
}

fn emitEscapeByte(dst: []u8, limit: usize, out_index: *usize, value: u8) void {
    if (out_index.* < limit) {
        dst[out_index.*] = value;
    }
    out_index.* += 1;
}

fn escapePassthrough(ch: u8, dst: []u8, limit: usize, out_index: *usize) void {
    emitEscapeByte(dst, limit, out_index, ch);
}

fn escapeSpace(ch: u8, dst: []u8, limit: usize, out_index: *usize) bool {
    const escaped: ?u8 = switch (ch) {
        '\n' => 'n',
        '\r' => 'r',
        '\t' => 't',
        '\x0b' => 'v',
        '\x0c' => 'f',
        else => null,
    };
    const value = escaped orelse return false;
    emitEscapeByte(dst, limit, out_index, '\\');
    emitEscapeByte(dst, limit, out_index, value);
    return true;
}

fn escapeSpecial(ch: u8, dst: []u8, limit: usize, out_index: *usize) bool {
    const escaped: ?u8 = switch (ch) {
        '\\' => '\\',
        '\x07' => 'a',
        '\x1b' => 'e',
        '"' => '"',
        else => null,
    };
    const value = escaped orelse return false;
    emitEscapeByte(dst, limit, out_index, '\\');
    emitEscapeByte(dst, limit, out_index, value);
    return true;
}

fn escapeNull(ch: u8, dst: []u8, limit: usize, out_index: *usize) bool {
    if (ch != 0) return false;
    emitEscapeByte(dst, limit, out_index, '\\');
    emitEscapeByte(dst, limit, out_index, '0');
    return true;
}

fn escapeOctal(ch: u8, dst: []u8, limit: usize, out_index: *usize) void {
    emitEscapeByte(dst, limit, out_index, '\\');
    emitEscapeByte(dst, limit, out_index, ((ch >> 6) & 0x07) + '0');
    emitEscapeByte(dst, limit, out_index, ((ch >> 3) & 0x07) + '0');
    emitEscapeByte(dst, limit, out_index, (ch & 0x07) + '0');
}

fn escapeHex(ch: u8, dst: []u8, limit: usize, out_index: *usize) void {
    emitEscapeByte(dst, limit, out_index, '\\');
    emitEscapeByte(dst, limit, out_index, 'x');
    emitEscapeByte(dst, limit, out_index, hexUpperNibble(ch));
    emitEscapeByte(dst, limit, out_index, hexLowerNibble(ch));
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

fn matchStringLimit(haystack: []const ?[]const u8, count: usize) usize {
    return @min(count, haystack.len);
}

pub fn matchStringBounded(haystack: []const ?[]const u8, count: usize, needle: []const u8) ?usize {
    const limit = matchStringLimit(haystack, count);
    for (haystack[0..limit], 0..) |entry, idx| {
        const value = entry orelse break;
        if (std.mem.eql(u8, value[0..cStringLen(value)], needle[0..cStringLen(needle)])) {
            return idx;
        }
    }
    return null;
}

pub fn match_string_bounded(haystack: []const ?[]const u8, count: usize, needle: []const u8) ?usize {
    return matchStringBounded(haystack, count, needle);
}

pub fn matchString(haystack: []const ?[]const u8, needle: []const u8) ?usize {
    return matchStringBounded(haystack, haystack.len, needle);
}

pub fn match_string(haystack: []const ?[]const u8, needle: []const u8) ?usize {
    return matchString(haystack, needle);
}

pub fn sysfsMatchStringBounded(haystack: []const ?[]const u8, count: usize, needle: []const u8) ?usize {
    const limit = matchStringLimit(haystack, count);
    for (haystack[0..limit], 0..) |entry, idx| {
        const value = entry orelse break;
        if (sysfsStreq(value, needle)) return idx;
    }
    return null;
}

pub fn __sysfs_match_string_bounded(haystack: []const ?[]const u8, count: usize, needle: []const u8) ?usize {
    return sysfsMatchStringBounded(haystack, count, needle);
}

pub fn sysfsMatchString(haystack: []const ?[]const u8, needle: []const u8) ?usize {
    return sysfsMatchStringBounded(haystack, haystack.len, needle);
}

pub fn __sysfs_match_string(haystack: []const ?[]const u8, needle: []const u8) ?usize {
    return sysfsMatchString(haystack, needle);
}

pub fn stringIsTerminated(buf: []const u8, count: usize) bool {
    if (count == 0 or count > buf.len) return false;
    return std.mem.indexOfScalar(u8, buf[0..count], 0) != null;
}

pub fn string_is_terminated(buf: []const u8, count: usize) bool {
    return stringIsTerminated(buf, count);
}

pub fn stringGetSize(size: u64, blk_size: u64, units: u32, buf: []u8, len: usize) usize {
    var scaled: u128 = if (blk_size == 0) 0 else @as(u128, size) * @as(u128, blk_size);
    const units_base = units & STRING_UNITS_MASK;
    const divisor = stringUnitsDivisor(units_base);
    var unit_index: usize = 0;
    var remainder: u128 = 0;

    while (scaled >= divisor and unit_index + 1 < string_units_2.len) {
        remainder = scaled % divisor;
        scaled /= divisor;
        unit_index += 1;
    }

    var decimals = if (scaled == 0) @as(usize, 0) else stringGetSizeFractionDigits(scaled);
    var fraction: u128 = 0;

    if (scaled > 0) {
        const fraction_factor = stringGetSizeFractionFactor(decimals);
        fraction = (remainder * fraction_factor + (divisor / 2)) / divisor;
        if (fraction == fraction_factor) {
            scaled += 1;
            fraction = 0;
            if (decimals > 0 and scaled >= divisor and unit_index + 1 < string_units_2.len) {
                scaled = 1;
                unit_index += 1;
            }
            decimals = if (scaled == 0) 0 else stringGetSizeFractionDigits(scaled);
        }
    }

    const separator = if ((units & STRING_UNITS_NO_SPACE) != 0) "" else " ";
    const bytes_suffix = if ((units & STRING_UNITS_NO_BYTES) != 0) "" else "B";
    const unit = stringUnitsLabel(units_base, unit_index);

    var formatted = [_]u8{0} ** 32;
    const rendered = switch (decimals) {
        0 => std.fmt.bufPrint(&formatted, "{d}{s}{s}{s}", .{ scaled, separator, unit, bytes_suffix }) catch unreachable,
        1 => std.fmt.bufPrint(&formatted, "{d}.{d:0>1}{s}{s}{s}", .{ scaled, fraction, separator, unit, bytes_suffix }) catch unreachable,
        else => std.fmt.bufPrint(&formatted, "{d}.{d:0>2}{s}{s}{s}", .{ scaled, fraction, separator, unit, bytes_suffix }) catch unreachable,
    };

    const limit = if (len == 0) buf.len else @min(len, buf.len);
    if (limit > 0) {
        const copy_len = @min(rendered.len, limit - 1);
        @memcpy(buf[0..copy_len], rendered[0..copy_len]);
        buf[copy_len] = 0;
    }

    return rendered.len;
}

pub fn string_get_size(size: u64, blk_size: u64, units: u32, buf: []u8, len: usize) usize {
    return stringGetSize(size, blk_size, units, buf, len);
}

pub fn stringUnescape(src: []const u8, dst: []u8, size: usize, flags: u32) usize {
    if (dst.len == 0) return 0;

    const limit = if (size == 0) dst.len else @min(size, dst.len);
    if (limit == 0) return 0;

    var src_index: usize = 0;
    var out_index: usize = 0;

    while (src_index < src.len and src[src_index] != 0 and out_index + 1 < limit) {
        const remaining = limit - out_index - 1;
        if (src[src_index] == '\\' and src_index + 1 < src.len and src[src_index + 1] != 0 and remaining > 0) {
            src_index += 1;

            if ((flags & UNESCAPE_SPACE) != 0) {
                if (matchUnescapeSpace(src[src_index..])) |match| {
                    dst[out_index] = match.value;
                    out_index += 1;
                    src_index += match.consumed;
                    continue;
                }
            }

            if ((flags & UNESCAPE_OCTAL) != 0) {
                if (matchUnescapeOctal(src[src_index..])) |match| {
                    dst[out_index] = match.value;
                    out_index += 1;
                    src_index += match.consumed;
                    continue;
                }
            }

            if ((flags & UNESCAPE_HEX) != 0) {
                if (matchUnescapeHex(src[src_index..])) |match| {
                    dst[out_index] = match.value;
                    out_index += 1;
                    src_index += match.consumed;
                    continue;
                }
            }

            if ((flags & UNESCAPE_SPECIAL) != 0) {
                if (matchUnescapeSpecial(src[src_index..])) |match| {
                    dst[out_index] = match.value;
                    out_index += 1;
                    src_index += match.consumed;
                    continue;
                }
            }

            dst[out_index] = '\\';
            out_index += 1;

            if (remaining == 1) break;
        }

        dst[out_index] = src[src_index];
        out_index += 1;
        src_index += 1;
    }

    dst[out_index] = 0;
    return out_index;
}

pub fn string_unescape(src: []const u8, dst: []u8, size: usize, flags: u32) usize {
    return stringUnescape(src, dst, size, flags);
}

pub fn stringUnescapeInplace(buf: []u8, flags: u32) usize {
    return stringUnescape(buf, buf, 0, flags);
}

pub fn string_unescape_inplace(buf: []u8, flags: u32) usize {
    return stringUnescapeInplace(buf, flags);
}

pub fn stringUnescapeAny(src: []const u8, dst: []u8, size: usize) usize {
    return stringUnescape(src, dst, size, UNESCAPE_ANY);
}

pub fn string_unescape_any(src: []const u8, dst: []u8, size: usize) usize {
    return stringUnescapeAny(src, dst, size);
}

pub fn stringUnescapeAnyInplace(buf: []u8) usize {
    return stringUnescapeAny(buf, buf, 0);
}

pub fn string_unescape_any_inplace(buf: []u8) usize {
    return stringUnescapeAnyInplace(buf);
}

pub fn stringEscapeMem(src: []const u8, dst: []u8, size: usize, flags: u32, only: ?[]const u8) usize {
    const limit = if (size == 0) dst.len else @min(size, dst.len);
    const dict = only orelse &[_]u8{};
    const dict_len = cStringLen(dict);
    const is_dict = dict_len > 0;
    const is_append = (flags & ESCAPE_APPEND) != 0;
    var out_index: usize = 0;

    for (src) |ch| {
        const in_dict = is_dict and std.mem.indexOfScalar(u8, dict[0..dict_len], ch) != null;

        if (!(is_append or in_dict) and is_dict) {
            escapePassthrough(ch, dst, limit, &out_index);
            continue;
        }
        if (!(is_append and in_dict) and isAscii(ch) and isPrintable(ch) and (flags & ESCAPE_NAP) != 0) {
            escapePassthrough(ch, dst, limit, &out_index);
            continue;
        }
        if (!(is_append and in_dict) and isPrintable(ch) and (flags & ESCAPE_NP) != 0) {
            escapePassthrough(ch, dst, limit, &out_index);
            continue;
        }
        if (!(is_append and in_dict) and isAscii(ch) and (flags & ESCAPE_NA) != 0) {
            escapePassthrough(ch, dst, limit, &out_index);
            continue;
        }
        if ((flags & ESCAPE_SPACE) != 0 and escapeSpace(ch, dst, limit, &out_index)) continue;
        if ((flags & ESCAPE_SPECIAL) != 0 and escapeSpecial(ch, dst, limit, &out_index)) continue;
        if ((flags & ESCAPE_NULL) != 0 and escapeNull(ch, dst, limit, &out_index)) continue;
        if ((flags & ESCAPE_OCTAL) != 0) {
            escapeOctal(ch, dst, limit, &out_index);
            continue;
        }
        if ((flags & ESCAPE_HEX) != 0) {
            escapeHex(ch, dst, limit, &out_index);
            continue;
        }
        escapePassthrough(ch, dst, limit, &out_index);
    }

    return out_index;
}

pub fn string_escape_mem(src: []const u8, dst: []u8, size: usize, flags: u32, only: ?[]const u8) usize {
    return stringEscapeMem(src, dst, size, flags, only);
}

pub fn stringEscapeMemAnyNp(src: []const u8, dst: []u8, size: usize, only: ?[]const u8) usize {
    return stringEscapeMem(src, dst, size, ESCAPE_ANY_NP, only);
}

pub fn string_escape_mem_any_np(src: []const u8, dst: []u8, size: usize, only: ?[]const u8) usize {
    return stringEscapeMemAnyNp(src, dst, size, only);
}

pub fn stringEscapeStr(src: []const u8, dst: []u8, size: usize, flags: u32, only: ?[]const u8) usize {
    return stringEscapeMem(src[0..cStringLen(src)], dst, size, flags, only);
}

pub fn string_escape_str(src: []const u8, dst: []u8, size: usize, flags: u32, only: ?[]const u8) usize {
    return stringEscapeStr(src, dst, size, flags, only);
}

pub fn stringEscapeStrAnyNp(src: []const u8, dst: []u8, size: usize, only: ?[]const u8) usize {
    return stringEscapeStr(src, dst, size, ESCAPE_ANY_NP, only);
}

pub fn string_escape_str_any_np(src: []const u8, dst: []u8, size: usize, only: ?[]const u8) usize {
    return stringEscapeStrAnyNp(src, dst, size, only);
}

pub fn kasprintfStrarray(
    allocator: std.mem.Allocator,
    prefix: []const u8,
    n: usize,
) !KasprintfStrarrayResult {
    const current = prefix[0..cStringLen(prefix)];
    if (n == 0) {
        return .{
            .names = &.{},
            .names_null_terminated = empty_kasprintf_strarray_null_terminated,
        };
    }

    var names = try allocKasprintfStrarrayNames(allocator, n);
    errdefer allocator.free(names);

    var names_null_terminated = try allocKasprintfStrarrayNullTerminated(allocator, n);
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

pub fn kasprintf_strarray(
    allocator: std.mem.Allocator,
    prefix: []const u8,
    n: usize,
) !KasprintfStrarrayResult {
    return kasprintfStrarray(allocator, prefix, n);
}

pub fn kfreeStrarray(allocator: std.mem.Allocator, result: *KasprintfStrarrayResult) void {
    result.deinit(allocator);
}

pub fn kfree_strarray(allocator: std.mem.Allocator, result: *KasprintfStrarrayResult) void {
    kfreeStrarray(allocator, result);
}

pub fn kstrdupQuotable(allocator: std.mem.Allocator, src: ?[]const u8) !?[:0]u8 {
    const raw = src orelse return null;
    const current = raw[0..cStringLen(raw)];
    const esc = "\x0c\n\r\t\x0b\x07\x1b\\\"";
    const empty = [_]u8{};
    const escaped_len = stringEscapeMem(current, empty[0..], 0, ESCAPE_HEX, esc);
    const duplicated = try allocator.alloc(u8, escaped_len + 1);
    errdefer allocator.free(duplicated);

    std.debug.assert(stringEscapeMem(current, duplicated, escaped_len, ESCAPE_HEX, esc) == escaped_len);
    duplicated[escaped_len] = 0;
    return duplicated[0..escaped_len :0];
}

pub fn kstrdup_quotable(allocator: std.mem.Allocator, src: ?[]const u8) !?[:0]u8 {
    return kstrdupQuotable(allocator, src);
}

pub fn kstrdupQuotableFile(allocator: std.mem.Allocator, src: ?[]const u8) ![:0]u8 {
    const raw = src orelse return allocator.dupeZ(u8, "<unknown>");
    return (try kstrdupQuotable(allocator, raw)).?;
}

pub fn kstrdup_quotable_file(allocator: std.mem.Allocator, src: ?[]const u8) ![:0]u8 {
    return kstrdupQuotableFile(allocator, src);
}

pub fn kstrdupQuotableCmdline(allocator: std.mem.Allocator, src: ?[]const u8) !?[:0]u8 {
    const raw = src orelse return null;

    var end = raw.len;
    while (end > 0 and raw[end - 1] == 0) : (end -= 1) {}

    const normalized = try allocator.dupe(u8, raw[0..end]);
    defer allocator.free(normalized);

    for (normalized) |*ch| {
        if (ch.* == 0) ch.* = ' ';
    }

    return (try kstrdupQuotable(allocator, normalized)).?;
}

pub fn kstrdup_quotable_cmdline(allocator: std.mem.Allocator, src: ?[]const u8) !?[:0]u8 {
    return kstrdupQuotableCmdline(allocator, src);
}

pub const ParseIntArrayError = std.mem.Allocator.Error || error{ NoEntry, Overflow };

fn boundedCountPrefix(buf: []const u8, count: usize) []const u8 {
    return buf[0..@min(cStringLen(buf), count)];
}

fn trimParseIntToken(text: []const u8) []const u8 {
    return std.mem.trim(u8, text, " \t\r\n\x0b\x0c");
}

fn parseAutoI32(text: []const u8) ?i32 {
    return std.fmt.parseInt(i32, text, 0) catch null;
}

fn appendPositiveRange(values: *std.ArrayList(i32), allocator: std.mem.Allocator, start: i32, end: i32) std.mem.Allocator.Error!void {
    if (start < 0 or end < start) return;

    var current = start;
    while (true) {
        try values.append(allocator, current);
        if (current == end) break;
        current += 1;
    }
}

pub fn parseIntArray(allocator: std.mem.Allocator, buf: []const u8, count: usize) ParseIntArrayError![]i32 {
    const current = boundedCountPrefix(buf, count);
    var values = try std.ArrayList(i32).initCapacity(allocator, 0);
    defer values.deinit(allocator);

    var index: usize = 0;
    while (index < current.len) {
        const comma = std.mem.indexOfScalarPos(u8, current, index, ',') orelse current.len;
        const token = trimParseIntToken(current[index..comma]);
        if (token.len == 0) break;

        if (std.mem.indexOfScalarPos(u8, token, 1, '-')) |range_sep| {
            const start = parseAutoI32(trimParseIntToken(token[0..range_sep])) orelse break;
            const end = parseAutoI32(trimParseIntToken(token[range_sep + 1 ..])) orelse break;
            if (start < 0 or end < start) break;
            try appendPositiveRange(&values, allocator, start, end);
        } else {
            const value = parseAutoI32(token) orelse break;
            try values.append(allocator, value);
        }

        if (comma == current.len) break;
        index = comma + 1;
    }

    if (values.items.len == 0) return error.NoEntry;

    const parsed_count = std.math.cast(i32, values.items.len) orelse return error.Overflow;
    var parsed = try allocator.alloc(i32, values.items.len + 1);
    errdefer allocator.free(parsed);

    parsed[0] = parsed_count;
    @memcpy(parsed[1..], values.items);
    return parsed;
}

pub fn parse_int_array(allocator: std.mem.Allocator, buf: []const u8, count: usize) ParseIntArrayError![]i32 {
    return parseIntArray(allocator, buf, count);
}

pub fn kstrdupAndReplace(
    allocator: std.mem.Allocator,
    src: []const u8,
    old: u8,
    new: u8,
) ![:0]u8 {
    var duplicated = try allocator.dupeZ(u8, src[0..cStringLen(src)]);
    _ = strreplace(duplicated[0..duplicated.len], old, new);
    return duplicated;
}

pub fn kstrdup_and_replace(
    allocator: std.mem.Allocator,
    src: []const u8,
    old: u8,
    new: u8,
) ![:0]u8 {
    return kstrdupAndReplace(allocator, src, old, new);
}

pub fn stringUpper(dst: []u8, src: []const u8) void {
    const limit = @min(dst.len, src.len);
    var idx: usize = 0;
    while (idx < limit) : (idx += 1) {
        const ch = src[idx];
        dst[idx] = std.ascii.toUpper(ch);
        if (ch == 0) return;
    }
}

pub fn string_upper(dst: []u8, src: []const u8) void {
    stringUpper(dst, src);
}

pub fn stringLower(dst: []u8, src: []const u8) void {
    const limit = @min(dst.len, src.len);
    var idx: usize = 0;
    while (idx < limit) : (idx += 1) {
        const ch = src[idx];
        dst[idx] = std.ascii.toLower(ch);
        if (ch == 0) return;
    }
}

pub fn string_lower(dst: []u8, src: []const u8) void {
    stringLower(dst, src);
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

fn runKasprintfStrarrayWithFailingAllocator(
    allocator: std.mem.Allocator,
    prefix: []const u8,
    n: usize,
) !void {
    var result = try kasprintfStrarray(allocator, prefix, n);
    defer result.deinit(allocator);
}

fn runKstrdupAndReplaceWithFailingAllocator(
    allocator: std.mem.Allocator,
    src: []const u8,
    old: u8,
    new: u8,
) !void {
    const duplicated = try kstrdupAndReplace(allocator, src, old, new);
    allocator.free(duplicated);
}

fn runKstrdupQuotableWithFailingAllocator(allocator: std.mem.Allocator, src: ?[]const u8) !void {
    if (try kstrdupQuotable(allocator, src)) |quoted| {
        allocator.free(quoted);
    }
}

fn runKstrdupQuotableFileWithFailingAllocator(allocator: std.mem.Allocator, src: ?[]const u8) !void {
    const quoted = try kstrdupQuotableFile(allocator, src);
    allocator.free(quoted);
}

fn runKstrdupQuotableCmdlineWithFailingAllocator(allocator: std.mem.Allocator, src: ?[]const u8) !void {
    if (try kstrdupQuotableCmdline(allocator, src)) |quoted| {
        allocator.free(quoted);
    }
}

fn runParseIntArrayWithFailingAllocator(allocator: std.mem.Allocator, buf: []const u8, count: usize) !void {
    const parsed = try parseIntArray(allocator, buf, count);
    allocator.free(parsed);
}

test "kasprintfStrarray keeps sentinel ownership stable for empty and populated arrays" {
    var empty = try kasprintfStrarray(std.testing.allocator, "dev", 0);
    defer empty.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 0), empty.names.len);
    try std.testing.expectEqual(empty_kasprintf_strarray_null_terminated.ptr, empty.names_null_terminated.ptr);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), empty.cArray()[0]);

    var result = try kasprintfStrarray(std.testing.allocator, "tty\x00ignored", 3);
    try std.testing.expectEqual(@as(usize, 3), result.names.len);
    try std.testing.expectEqual(@as(usize, 4), result.names_null_terminated.len);
    try std.testing.expectEqualStrings("tty-0", result.names[0]);
    try std.testing.expectEqualStrings("tty-1", result.names[1]);
    try std.testing.expectEqualStrings("tty-2", result.names[2]);

    const c_array = result.cArray();
    try std.testing.expectEqualStrings("tty-0", std.mem.span(c_array[0].?));
    try std.testing.expectEqualStrings("tty-1", std.mem.span(c_array[1].?));
    try std.testing.expectEqualStrings("tty-2", std.mem.span(c_array[2].?));
    try std.testing.expectEqual(@as(?[*:0]const u8, null), c_array[3]);

    result.deinit(std.testing.allocator);
    try std.testing.expectEqual(@as(usize, 0), result.names.len);
    try std.testing.expectEqual(empty_kasprintf_strarray_null_terminated.ptr, result.names_null_terminated.ptr);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), result.cArray()[0]);

    kfreeStrarray(std.testing.allocator, &result);
    try std.testing.expectEqual(@as(usize, 0), result.names.len);
    try std.testing.expectEqual(empty_kasprintf_strarray_null_terminated.ptr, result.names_null_terminated.ptr);
}

test "kasprintfStrarray frees partially built arrays when allocator failure interrupts setup" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runKasprintfStrarrayWithFailingAllocator,
        .{ "phase7-helper", 4 },
    );
}

test "matchStringBounded and sysfsMatchStringBounded respect explicit counts and null sentinels" {
    const haystack = [_]?[]const u8{ "alpha", "beta", "gamma", null, "delta" };
    try std.testing.expectEqual(@as(?usize, 1), matchStringBounded(&haystack, 2, "beta"));
    try std.testing.expectEqual(@as(?usize, null), matchStringBounded(&haystack, 2, "gamma"));
    try std.testing.expectEqual(@as(?usize, null), matchStringBounded(&haystack, haystack.len, "delta"));
    try std.testing.expectEqual(@as(?usize, 2), matchString(&haystack, "gamma"));
    try std.testing.expectEqual(@as(?usize, 1), match_string_bounded(&haystack, 2, "beta"));

    const sysfs_haystack = [_]?[]const u8{ "off\n", "on", null, "auto\n" };
    try std.testing.expectEqual(@as(?usize, 0), sysfsMatchStringBounded(&sysfs_haystack, 1, "off"));
    try std.testing.expectEqual(@as(?usize, null), sysfsMatchStringBounded(&sysfs_haystack, 1, "on"));
    try std.testing.expectEqual(@as(?usize, 1), __sysfs_match_string_bounded(&sysfs_haystack, 2, "on\n"));
    try std.testing.expectEqual(@as(?usize, null), __sysfs_match_string_bounded(&sysfs_haystack, sysfs_haystack.len, "auto"));
}

test "stringGetSize reports rounded units and truncates destination buffers safely" {
    var rendered = [_]u8{0} ** 32;
    const rendered_len = stringGetSize(1024, 1024, STRING_UNITS_2, rendered[0..], 0);
    try std.testing.expectEqual(@as(usize, 8), rendered_len);
    try std.testing.expectEqualStrings("1.00 MiB", rendered[0..cStringLen(rendered[0..])]);

    var truncated = [_]u8{ 'x', 'x', 'x', 'x', 'x' };
    const truncated_len = stringGetSize(1536, 1, STRING_UNITS_2 | STRING_UNITS_NO_BYTES, truncated[0..], truncated.len);
    try std.testing.expectEqual(@as(usize, 7), truncated_len);
    try std.testing.expectEqualStrings("1.50", truncated[0..cStringLen(truncated[0..])]);
    try std.testing.expectEqual(@as(u8, 0), truncated[4]);
}

test "stringGetSize reports the rendered length even when the caller provides no writable storage" {
    const empty = [_]u8{};
    const rendered_len = stringGetSize(1536, 1, STRING_UNITS_2, empty[0..], 0);
    try std.testing.expectEqual(@as(usize, 8), rendered_len);
}

test "string escape and unescape preserve bounded output and invalid escape fallbacks" {
    var escaped = [_]u8{0} ** 16;
    const escaped_len = stringEscapeMem("A\n\x1b", escaped[0..], 0, ESCAPE_SPACE | ESCAPE_SPECIAL, null);
    try std.testing.expectEqual(@as(usize, 5), escaped_len);
    try std.testing.expectEqualStrings("A\\n\\e", escaped[0..escaped_len]);

    var unescaped = [_]u8{0} ** 16;
    const unescaped_len = stringUnescape("A\\n\\e", unescaped[0..], 0, UNESCAPE_ALL_MASK);
    try std.testing.expectEqual(@as(usize, 3), unescaped_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'A', '\n', '\x1b' }, unescaped[0..unescaped_len]);
    try std.testing.expectEqual(@as(u8, 0), unescaped[unescaped_len]);

    var invalid = [_]u8{ 'x', 'x' };
    const invalid_len = stringUnescape("\\q", invalid[0..], invalid.len, UNESCAPE_ALL_MASK);
    try std.testing.expectEqual(@as(usize, 1), invalid_len);
    try std.testing.expectEqualStrings("\\", invalid[0..cStringLen(invalid[0..])]);
}

test "string escape and unescape keep exact-fit, truncated, and zero-capacity buffer edges explicit" {
    var exact_fit_escape = [_]u8{ '!', '!', '!', '!' };
    const exact_fit_escape_len = stringEscapeMem(&[_]u8{'\n'}, exact_fit_escape[0..], exact_fit_escape.len, ESCAPE_HEX, null);
    try std.testing.expectEqual(@as(usize, 4), exact_fit_escape_len);
    try std.testing.expectEqualSlices(u8, "\\x0A", exact_fit_escape[0..]);

    var truncated_escape = [_]u8{ '!', '!', '!' };
    const truncated_escape_len = stringEscapeMem(&[_]u8{'\n'}, truncated_escape[0..], 2, ESCAPE_HEX, null);
    try std.testing.expectEqual(@as(usize, 4), truncated_escape_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '\\', 'x', '!' }, truncated_escape[0..]);

    const zero_capacity_escape = [_]u8{};
    const zero_capacity_escape_len = stringEscapeMem(&[_]u8{'\n'}, zero_capacity_escape[0..], 0, ESCAPE_HEX, null);
    try std.testing.expectEqual(@as(usize, 4), zero_capacity_escape_len);

    var exact_fit_unescape = [_]u8{ '!', '!', '!' };
    const exact_fit_unescape_len = stringUnescape("\\n\\r", exact_fit_unescape[0..], exact_fit_unescape.len, UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 2), exact_fit_unescape_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '\n', '\r', 0 }, exact_fit_unescape[0 .. exact_fit_unescape_len + 1]);

    var terminator_only_unescape = [_]u8{ '!', '!' };
    const terminator_only_unescape_len = stringUnescape("\\n\\r", terminator_only_unescape[0..], 1, UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 0), terminator_only_unescape_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, '!' }, terminator_only_unescape[0..]);

    const zero_capacity_unescape = [_]u8{};
    const zero_capacity_unescape_len = stringUnescape("\\n", zero_capacity_unescape[0..], 0, UNESCAPE_SPACE);
    try std.testing.expectEqual(@as(usize, 0), zero_capacity_unescape_len);
}

test "kstrdupAndReplace duplicates only the exported c-string prefix" {
    const source = [_]u8{ 'p', 'a', 't', 'h', '/', 'n', 'a', 'm', 'e', 0, '/', 't', 'a', 'i', 'l' };
    const duplicated = try kstrdupAndReplace(std.testing.allocator, &source, '/', '_');
    defer std.testing.allocator.free(duplicated);

    try std.testing.expectEqualStrings("path_name", duplicated);
    try std.testing.expectEqual(@as(u8, 0), duplicated[duplicated.len]);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 'p', 'a', 't', 'h', '/', 'n', 'a', 'm', 'e', 0, '/', 't', 'a', 'i', 'l' },
        &source,
    );

    const unchanged = try kstrdupAndReplace(std.testing.allocator, "phase7", '/', '_');
    defer std.testing.allocator.free(unchanged);
    try std.testing.expectEqualStrings("phase7", unchanged);

    const alias = try kstrdup_and_replace(std.testing.allocator, "", 'x', 'y');
    defer std.testing.allocator.free(alias);
    try std.testing.expectEqualStrings("", alias);
}

test "kstrdupAndReplace reports allocation failure cleanly" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runKstrdupAndReplaceWithFailingAllocator,
        .{ "phase7/helper", '/', '_' },
    );
}

test "kstrdupQuotable hex-escapes special log hazards without widening past the exported prefix" {
    try std.testing.expect((try kstrdupQuotable(std.testing.allocator, null)) == null);

    const source = [_]u8{ 'a', '\n', '"', '\\', '\x1b', 0, 'x' };
    const quoted = (try kstrdupQuotable(std.testing.allocator, &source)).?;
    defer std.testing.allocator.free(quoted);
    try std.testing.expectEqualStrings("a\\x0A\\x22\\x5C\\x1B", quoted);

    const alias = (try kstrdup_quotable(std.testing.allocator, "tab\tquote\"")).?;
    defer std.testing.allocator.free(alias);
    try std.testing.expectEqualStrings("tab\\x09quote\\x22", alias);

    const nul_prefixed = [_]u8{ 'p', 'a', 't', 'h', 0, '"', '\\' };
    const bounded = (try kstrdupQuotable(std.testing.allocator, &nul_prefixed)).?;
    defer std.testing.allocator.free(bounded);
    try std.testing.expectEqualStrings("path", bounded);
}

test "kstrdupQuotable reports allocation failure cleanly" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runKstrdupQuotableWithFailingAllocator,
        .{
            "phase7\nquote\"",
        },
    );
}

test "kstrdupQuotableFile quotes already-materialized paths and falls back to unknown for missing files" {
    const missing = try kstrdupQuotableFile(std.testing.allocator, null);
    defer std.testing.allocator.free(missing);
    try std.testing.expectEqualStrings("<unknown>", missing);

    const source = [_]u8{ '/', 't', 'm', 'p', '/', 'f', 'o', 'o', '\n', '"', 0, 'x' };
    const quoted = try kstrdupQuotableFile(std.testing.allocator, &source);
    defer std.testing.allocator.free(quoted);
    try std.testing.expectEqualStrings("/tmp/foo\\x0A\\x22", quoted);

    const alias = try kstrdup_quotable_file(std.testing.allocator, "trace\\\"path");
    defer std.testing.allocator.free(alias);
    try std.testing.expectEqualStrings("trace\\x5C\\x22path", alias);
}

test "kstrdupQuotableFile reports allocation failure cleanly" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runKstrdupQuotableFileWithFailingAllocator,
        .{"/tmp/phase7\nquote\""},
    );
}

test "kstrdupQuotableCmdline collapses trailing nulls and replaces inter-argument separators before quoting" {
    const cmdline = [_]u8{ 'z', 'i', 'g', 0, 'b', 'u', 'i', 'l', 'd', '\n', '"', 0, 0 };
    const quoted = (try kstrdupQuotableCmdline(std.testing.allocator, &cmdline)).?;
    defer std.testing.allocator.free(quoted);
    try std.testing.expectEqualStrings("zig build\\x0A\\x22", quoted);

    const blank = [_]u8{ 0, 0, 0 };
    const quoted_blank = (try kstrdupQuotableCmdline(std.testing.allocator, &blank)).?;
    defer std.testing.allocator.free(quoted_blank);
    try std.testing.expectEqualStrings("", quoted_blank);

    try std.testing.expect((try kstrdupQuotableCmdline(std.testing.allocator, null)) == null);
}

test "kstrdupQuotableCmdline reports allocation failure cleanly" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runKstrdupQuotableCmdlineWithFailingAllocator,
        .{"zig\x00test\x00\x00"},
    );
}

test "parseIntArray parses bounded comma lists and positive ranges" {
    const source = [_]u8{ '1', ',', '3', '-', '5', ',', '0', 'x', '7', ',', '0', '1', 0, '9' };
    const parsed = try parseIntArray(std.testing.allocator, &source, source.len);
    defer std.testing.allocator.free(parsed);

    try std.testing.expectEqual(@as(i32, 6), parsed[0]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 3, 4, 5, 7, 1 }, parsed[1..]);

    const alias = try parse_int_array(std.testing.allocator, "2-4", 3);
    defer std.testing.allocator.free(alias);
    try std.testing.expectEqual(@as(i32, 3), alias[0]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, 3, 4 }, alias[1..]);
}

test "parseIntArray stops at invalid trailing tokens while respecting count and first NUL" {
    const partial = try parseIntArray(std.testing.allocator, "9,11,broken,15", "9,11,broken,15".len);
    defer std.testing.allocator.free(partial);
    try std.testing.expectEqual(@as(i32, 2), partial[0]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 9, 11 }, partial[1..]);

    const nul_bounded = [_]u8{ '7', ',', '8', 0, ',', '9' };
    const bounded = try parse_int_array(std.testing.allocator, &nul_bounded, nul_bounded.len);
    defer std.testing.allocator.free(bounded);
    try std.testing.expectEqual(@as(i32, 2), bounded[0]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 7, 8 }, bounded[1..]);

    const count_limited = try parseIntArray(std.testing.allocator, "4,6,8", 3);
    defer std.testing.allocator.free(count_limited);
    try std.testing.expectEqual(@as(i32, 2), count_limited[0]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 6 }, count_limited[1..]);
}

test "parseIntArray reports NoEntry when no integers are available" {
    try std.testing.expectError(error.NoEntry, parseIntArray(std.testing.allocator, "broken", "broken".len));
    try std.testing.expectError(error.NoEntry, parse_int_array(std.testing.allocator, "", 0));
}

test "parseIntArray reports allocation failure cleanly" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runParseIntArrayWithFailingAllocator,
        .{ "1-4,0x8", 7 },
    );
}

test "memcpyAndPad and strreplace respect logical bounds" {
    var padded = [_]u8{ '#', '#', '#', '#', '#' };
    memcpyAndPad(padded[0..], "zig", 5, '.');
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', '.', '.' }, padded[0..]);

    var text = [_]u8{ 'a', '-', 'b', 0, '-' };
    const logical_len = strreplace(text[0..], '-', '_');
    try std.testing.expectEqual(@as(usize, 3), logical_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 'b', 0, '-' }, text[0..]);
}
