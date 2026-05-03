const std = @import("std");

pub const MemparseResult = struct {
    value: u64,
    rest: []const u8,
};

const ParseMagnitudeResult = struct {
    value: u64,
    overflowed: bool,
    next_index: usize,
    parsed_any: bool,
};

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
        if ((next == 'x' or next == 'X') and start + 2 < text.len and digitValue(text[start + 2], 16) != null) {
            return .{ .base = 16, .digits_start = start + 2 };
        }
        return .{ .base = 8, .digits_start = start };
    }

    return .{ .base = 10, .digits_start = start };
}

fn parseMagnitude(text: []const u8, start: usize, base: u8, limit: u64) ParseMagnitudeResult {
    var idx = start;
    var parsed_any = false;
    var overflowed = false;
    var magnitude: u64 = 0;

    while (idx < text.len) : (idx += 1) {
        const digit = digitValue(text[idx], base) orelse break;
        parsed_any = true;

        if (!overflowed) {
            const base_u64 = @as(u64, base);
            const digit_u64 = @as(u64, digit);
            if (magnitude > (limit - digit_u64) / base_u64) {
                magnitude = limit;
                overflowed = true;
            } else {
                magnitude = magnitude * base_u64 + digit_u64;
            }
        }
    }

    return .{
        .value = magnitude,
        .overflowed = overflowed,
        .next_index = idx,
        .parsed_any = parsed_any,
    };
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
    const signed_limit = @as(u64, std.math.maxInt(i64)) + @intFromBool(prefix.negative);
    const parsed = parseMagnitude(text, base_info.digits_start, base_info.base, signed_limit);

    if (!parsed.parsed_any) {
        return .{ .value = 0, .rest = text };
    }

    const signed_value: i64 = if (prefix.negative)
        if (parsed.value == @as(u64, 1) << 63)
            std.math.minInt(i64)
        else
            -@as(i64, @intCast(parsed.value))
    else
        @as(i64, @intCast(parsed.value));

    var idx = parsed.next_index;
    var result: u64 = @bitCast(signed_value);
    if (idx < text.len) {
        result = applySuffix(result, text[idx]);
        switch (text[idx]) {
            'E', 'e', 'P', 'p', 'T', 't', 'G', 'g', 'M', 'm', 'K', 'k' => {
                idx += 1;
                consumeOptionalUnitTail(text, &idx);
            },
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

test "memparse accepts optional binary unit tails" {
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
    try std.testing.expectEqual(@as(u64, 3 << 10), lowercase_kib.value);
    try std.testing.expectEqualStrings(".", lowercase_kib.rest);
}

test "memparse handles signed and explicit positive prefixes" {
    const negative = memparse("-4K tail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -4096))), negative.value);
    try std.testing.expectEqualStrings(" tail", negative.rest);

    const positive = memparse("+0X10M done");
    try std.testing.expectEqual(@as(u64, 0x10 << 20), positive.value);
    try std.testing.expectEqualStrings(" done", positive.rest);
}

test "memparse keeps bare hex prefixes aligned with C parsing" {
    const bare = memparse("0x");
    try std.testing.expectEqual(@as(u64, 0), bare.value);
    try std.testing.expectEqualStrings("x", bare.rest);

    const signed_bare = memparse("-0x");
    try std.testing.expectEqual(@as(u64, 0), signed_bare.value);
    try std.testing.expectEqualStrings("x", signed_bare.rest);

    const invalid_hex_digit = memparse("0xG");
    try std.testing.expectEqual(@as(u64, 0), invalid_hex_digit.value);
    try std.testing.expectEqualStrings("xG", invalid_hex_digit.rest);
}

test "memparse keeps the original rest when sign-prefixed input has no digits" {
    const negative = memparse("-xyz");
    try std.testing.expectEqual(@as(u64, 0), negative.value);
    try std.testing.expectEqualStrings("-xyz", negative.rest);

    const positive = memparse("+nope");
    try std.testing.expectEqual(@as(u64, 0), positive.value);
    try std.testing.expectEqualStrings("+nope", positive.rest);
}

test "memparse reports no-conversion via unchanged rest" {
    const invalid = memparse("xyz");
    try std.testing.expectEqual(@as(u64, 0), invalid.value);
    try std.testing.expectEqualStrings("xyz", invalid.rest);
}

test "memparse saturates signed overflow instead of trapping" {
    const positive = memparse("9223372036854775808");
    try std.testing.expectEqual(@as(u64, std.math.maxInt(i64)), positive.value);
    try std.testing.expectEqualStrings("", positive.rest);

    const negative = memparse("-9223372036854775809");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, std.math.minInt(i64)))), negative.value);
    try std.testing.expectEqualStrings("", negative.rest);
}

test "memparse applies suffix shifts after signed saturation" {
    const saturated = memparse("18446744073709551615K");
    try std.testing.expectEqual(@as(u64, 18446744073709550592), saturated.value);
    try std.testing.expectEqualStrings("", saturated.rest);
}
