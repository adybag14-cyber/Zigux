const std = @import("std");

pub const MemparseResult = struct {
    value: u64,
    rest: []const u8,
};

pub fn parseOptionStr(optionstr: []const u8, option: []const u8) bool {
    if (optionstr.len == 0) {
        return false;
    }

    var idx: usize = 0;
    while (idx < optionstr.len) {
        const start = idx;
        while (idx < optionstr.len and optionstr[idx] != ',' and optionstr[idx] != 0) : (idx += 1) {}

        const entry = optionstr[start..idx];
        const terminated_by_comma = idx < optionstr.len and optionstr[idx] == ',';
        const terminated_by_nul = idx < optionstr.len and optionstr[idx] == 0;

        if ((entry.len != 0 or terminated_by_comma) and std.mem.eql(u8, entry, option)) {
            return true;
        }

        if (terminated_by_nul or !terminated_by_comma) {
            break;
        }

        idx += 1;
    }

    return false;
}

pub const parse_option_str = parseOptionStr;

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

    if (idx < text.len and signed_input) {
        magnitude = applySuffix(magnitude, text[idx]);
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

test "memparse reports no-conversion via unchanged rest" {
    const invalid = memparse("xyz");
    try std.testing.expectEqual(@as(u64, 0), invalid.value);
    try std.testing.expectEqualStrings("xyz", invalid.rest);
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

test "memparse applies suffixes before signed clamping" {
    const negative = memparse("-2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative.value);
    try std.testing.expectEqualStrings("tail", negative.rest);

    const positive = memparse("+3Mmore");
    try std.testing.expectEqual(@as(u64, 3 << 20), positive.value);
    try std.testing.expectEqualStrings("more", positive.rest);
}

test "parseOptionStr matches only exact bare options" {
    try std.testing.expect(parseOptionStr("quiet,debug,nohlt", "debug"));
    try std.testing.expect(parseOptionStr("quiet,debug\x00,nohlt", "debug"));
    try std.testing.expect(!parseOptionStr("quiet,debug=1,nohlt", "debug"));
    try std.testing.expect(!parseOptionStr("quiet,debug\x00,nohlt", "nohlt"));
    try std.testing.expect(parseOptionStr(",debug", ""));
    try std.testing.expect(parseOptionStr("debug,,quiet", ""));
    try std.testing.expect(!parseOptionStr("debug,", ""));
    try std.testing.expect(!parseOptionStr("", ""));
    try std.testing.expect(parse_option_str("quiet,debug,nohlt", "quiet"));
}
