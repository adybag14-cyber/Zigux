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

const UnescapeMatch = struct {
    value: u8,
    consumed: usize,
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

pub fn matchString(haystack: []const ?[]const u8, needle: []const u8) ?usize {
    for (haystack, 0..) |entry, idx| {
        const value = entry orelse break;
        if (std.mem.eql(u8, value[0..cStringLen(value)], needle[0..cStringLen(needle)])) {
            return idx;
        }
    }
    return null;
}

pub fn match_string(haystack: []const ?[]const u8, needle: []const u8) ?usize {
    return matchString(haystack, needle);
}

pub fn sysfsMatchString(haystack: []const ?[]const u8, needle: []const u8) ?usize {
    for (haystack, 0..) |entry, idx| {
        const value = entry orelse break;
        if (sysfsStreq(value, needle)) return idx;
    }
    return null;
}

pub fn __sysfs_match_string(haystack: []const ?[]const u8, needle: []const u8) ?usize {
    return sysfsMatchString(haystack, needle);
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
    const fraction_factor = stringGetSizeFractionFactor(decimals);
    var fraction: u128 = 0;

    if (decimals > 0 and scaled > 0) {
        fraction = (remainder * fraction_factor + (divisor / 2)) / divisor;
        if (fraction == fraction_factor) {
            scaled += 1;
            fraction = 0;
            if (scaled >= divisor and unit_index + 1 < string_units_2.len) {
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
        if (src[src_index] == '\\' and src_index + 1 < src.len and src[src_index + 1] != 0 and remaining > 1) {
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
