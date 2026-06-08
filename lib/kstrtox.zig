// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub const EINVAL: i32 = 22;
pub const ERANGE: i32 = 34;
pub const KSTRTOX_OVERFLOW: u32 = 1 << 31;
const COUNT_MASK: u32 = KSTRTOX_OVERFLOW - 1;

pub fn _parse_integer_fixup_radix(s: []const u8, base: *u32) []const u8 {
    const offset = parseIntegerFixupRadix(s, base);
    return s[offset..];
}

fn parseIntegerFixupRadix(s: []const u8, base: *u32) usize {
    if (base.* == 0) {
        if (s.len > 0 and s[0] == '0') {
            if (s.len > 2 and lower(s[1]) == 'x' and digitValue(s[2]) != null) {
                base.* = 16;
            } else {
                base.* = 8;
            }
        } else {
            base.* = 10;
        }
    }

    if (base.* == 16 and s.len >= 2 and s[0] == '0' and lower(s[1]) == 'x') {
        return 2;
    }
    return 0;
}

pub fn _parse_integer_limit(s: []const u8, base: u32, p: *u64, max_chars: usize) u32 {
    var res: u64 = 0;
    var consumed: u32 = 0;
    var overflow = false;
    var idx: usize = 0;

    if (base < 2 or base > 16) {
        p.* = 0;
        return 0;
    }

    while (idx < s.len and idx < max_chars) : (idx += 1) {
        const val = digitValue(s[idx]) orelse break;
        if (val >= base) break;

        const val64: u64 = val;
        const base64: u64 = base;
        if (res > (std.math.maxInt(u64) - val64) / base64) overflow = true;
        res = res *% base64 +% val64;
        consumed += 1;
    }

    p.* = res;
    return consumed | (if (overflow) KSTRTOX_OVERFLOW else 0);
}

pub fn _parse_integer(s: []const u8, base: u32, p: *u64) u32 {
    return _parse_integer_limit(s, base, p, std.math.maxInt(usize));
}

fn parseUnsignedNoSign(s: []const u8, base_in: u32, res: *u64) i32 {
    if (!validBase(base_in)) return -EINVAL;

    var base = base_in;
    const offset = parseIntegerFixupRadix(s, &base);
    var tmp: u64 = 0;
    const rv = _parse_integer(s[offset..], base, &tmp);
    if ((rv & KSTRTOX_OVERFLOW) != 0) return -ERANGE;

    const consumed = rv & COUNT_MASK;
    if (consumed == 0) return -EINVAL;

    var rest = s[offset + consumed ..];
    if (rest.len > 0 and rest[0] == '\n') rest = rest[1..];
    if (rest.len != 0) return -EINVAL;

    res.* = tmp;
    return 0;
}

pub fn kstrtoull(s: []const u8, base: u32, res: *u64) i32 {
    if (s.len > 0 and s[0] == '+') {
        return parseUnsignedNoSign(s[1..], base, res);
    }
    return parseUnsignedNoSign(s, base, res);
}

pub fn kstrtoll(s: []const u8, base: u32, res: *i64) i32 {
    if (s.len > 0 and s[0] == '-') {
        var tmp: u64 = 0;
        const rv = parseUnsignedNoSign(s[1..], base, &tmp);
        if (rv < 0) return rv;

        const min_magnitude: u64 = @as(u64, 1) << 63;
        if (tmp > min_magnitude) return -ERANGE;
        res.* = if (tmp == min_magnitude) std.math.minInt(i64) else -@as(i64, @intCast(tmp));
        return 0;
    }

    var tmp: u64 = 0;
    const rv = kstrtoull(s, base, &tmp);
    if (rv < 0) return rv;
    if (tmp > @as(u64, @intCast(std.math.maxInt(i64)))) return -ERANGE;
    res.* = @intCast(tmp);
    return 0;
}

pub fn kstrtoul(s: []const u8, base: u32, res: *usize) i32 {
    return parseUnsignedTo(usize, s, base, res);
}

pub fn kstrtol(s: []const u8, base: u32, res: *isize) i32 {
    return parseSignedTo(isize, s, base, res);
}

pub fn kstrtouint(s: []const u8, base: u32, res: *u32) i32 {
    return parseUnsignedTo(u32, s, base, res);
}

pub fn kstrtoint(s: []const u8, base: u32, res: *i32) i32 {
    return parseSignedTo(i32, s, base, res);
}

pub const kstrtou32 = kstrtouint;
pub const kstrtos32 = kstrtoint;

pub fn kstrtou16(s: []const u8, base: u32, res: *u16) i32 {
    return parseUnsignedTo(u16, s, base, res);
}

pub fn kstrtos16(s: []const u8, base: u32, res: *i16) i32 {
    return parseSignedTo(i16, s, base, res);
}

pub fn kstrtou8(s: []const u8, base: u32, res: *u8) i32 {
    return parseUnsignedTo(u8, s, base, res);
}

pub fn kstrtos8(s: []const u8, base: u32, res: *i8) i32 {
    return parseSignedTo(i8, s, base, res);
}

pub fn kstrtobool(s: []const u8, res: *bool) i32 {
    if (s.len == 0) return -EINVAL;

    switch (s[0]) {
        'e', 'E', 'y', 'Y', 't', 'T', '1' => {
            res.* = true;
            return 0;
        },
        'd', 'D', 'n', 'N', 'f', 'F', '0' => {
            res.* = false;
            return 0;
        },
        'o', 'O' => {
            if (s.len < 2) return -EINVAL;
            switch (s[1]) {
                'n', 'N' => {
                    res.* = true;
                    return 0;
                },
                'f', 'F' => {
                    res.* = false;
                    return 0;
                },
                else => return -EINVAL,
            }
        },
        else => return -EINVAL,
    }
}

fn parseUnsignedTo(comptime T: type, s: []const u8, base: u32, res: *T) i32 {
    var tmp: u64 = 0;
    const rv = kstrtoull(s, base, &tmp);
    if (rv < 0) return rv;

    const max: u64 = std.math.maxInt(T);
    if (tmp > max) return -ERANGE;
    res.* = @intCast(tmp);
    return 0;
}

fn parseSignedTo(comptime T: type, s: []const u8, base: u32, res: *T) i32 {
    var tmp: i64 = 0;
    const rv = kstrtoll(s, base, &tmp);
    if (rv < 0) return rv;

    const min: i64 = std.math.minInt(T);
    const max: i64 = std.math.maxInt(T);
    if (tmp < min or tmp > max) return -ERANGE;
    res.* = @intCast(tmp);
    return 0;
}

fn validBase(base: u32) bool {
    return base == 0 or (base >= 2 and base <= 16);
}

fn lower(ch: u8) u8 {
    return if (ch >= 'A' and ch <= 'Z') ch + ('a' - 'A') else ch;
}

fn digitValue(ch: u8) ?u32 {
    if (ch >= '0' and ch <= '9') return ch - '0';
    const lc = lower(ch);
    if (lc >= 'a' and lc <= 'f') return lc - 'a' + 10;
    return null;
}

test "kstrtox unsigned parsing handles sign base detection and newline" {
    var out: u64 = 0;

    try std.testing.expectEqual(@as(i32, 0), kstrtoull("123", 0, &out));
    try std.testing.expectEqual(@as(u64, 123), out);
    try std.testing.expectEqual(@as(i32, 0), kstrtoull("+123", 0, &out));
    try std.testing.expectEqual(@as(u64, 123), out);
    try std.testing.expectEqual(@as(i32, 0), kstrtoull("012", 0, &out));
    try std.testing.expectEqual(@as(u64, 10), out);
    try std.testing.expectEqual(@as(i32, 0), kstrtoull("0x10\n", 0, &out));
    try std.testing.expectEqual(@as(u64, 16), out);
    try std.testing.expectEqual(@as(i32, -EINVAL), kstrtoull("-123", 0, &out));
    try std.testing.expectEqual(@as(i32, -EINVAL), kstrtoull("123 ", 0, &out));
    try std.testing.expectEqual(@as(i32, -EINVAL), kstrtoull("09", 0, &out));
}

test "kstrtox unsigned detects overflow" {
    var out: u64 = 1;

    try std.testing.expectEqual(@as(i32, 0), kstrtoull("18446744073709551615", 0, &out));
    try std.testing.expectEqual(std.math.maxInt(u64), out);
    try std.testing.expectEqual(@as(i32, -ERANGE), kstrtoull("18446744073709551616", 0, &out));
    try std.testing.expectEqual(std.math.maxInt(u64), out);
}

test "kstrtox signed parsing range checks" {
    var out: i64 = 0;

    try std.testing.expectEqual(@as(i32, 0), kstrtoll("9223372036854775807", 0, &out));
    try std.testing.expectEqual(std.math.maxInt(i64), out);
    try std.testing.expectEqual(@as(i32, 0), kstrtoll("-9223372036854775808", 0, &out));
    try std.testing.expectEqual(std.math.minInt(i64), out);
    try std.testing.expectEqual(@as(i32, -ERANGE), kstrtoll("9223372036854775808", 0, &out));
    try std.testing.expectEqual(@as(i32, -ERANGE), kstrtoll("-9223372036854775809", 0, &out));
    try std.testing.expectEqual(@as(i32, -EINVAL), kstrtoll("--1", 0, &out));
}

test "kstrtox narrow wrappers range check" {
    var u8_out: u8 = 0;
    var i8_out: i8 = 0;

    try std.testing.expectEqual(@as(i32, 0), kstrtou8("255", 0, &u8_out));
    try std.testing.expectEqual(@as(u8, 255), u8_out);
    try std.testing.expectEqual(@as(i32, -ERANGE), kstrtou8("256", 0, &u8_out));
    try std.testing.expectEqual(@as(i32, 0), kstrtos8("-128", 0, &i8_out));
    try std.testing.expectEqual(@as(i8, -128), i8_out);
    try std.testing.expectEqual(@as(i32, -ERANGE), kstrtos8("128", 0, &i8_out));
}

test "kstrtox bool parser follows Linux first-character rules" {
    var value = false;

    try std.testing.expectEqual(@as(i32, 0), kstrtobool("y", &value));
    try std.testing.expect(value);
    try std.testing.expectEqual(@as(i32, 0), kstrtobool("Enabled", &value));
    try std.testing.expect(value);
    try std.testing.expectEqual(@as(i32, 0), kstrtobool("off", &value));
    try std.testing.expect(!value);
    try std.testing.expectEqual(@as(i32, 0), kstrtobool("disabled", &value));
    try std.testing.expect(!value);
    try std.testing.expectEqual(@as(i32, -EINVAL), kstrtobool("o", &value));
    try std.testing.expectEqual(@as(i32, -EINVAL), kstrtobool("", &value));
}
