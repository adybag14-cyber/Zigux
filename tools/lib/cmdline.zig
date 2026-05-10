const std = @import("std");

pub const MemparseResult = struct {
    value: u64,
    rest: []const u8,
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
        result = applySuffix(result, text[idx]);
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
