const std = @import("std");

pub const MemparseResult = struct {
    value: u64,
    rest: []const u8,
};

pub const NextArgResult = struct {
    param: []const u8,
    value: ?[]const u8,
    rest: []const u8,
    remaining: []const u8,
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

fn skipLeadingSpaces(text: []const u8, start: usize) usize {
    var idx = start;
    while (idx < text.len and std.ascii.isWhitespace(text[idx])) : (idx += 1) {}
    return idx;
}

fn cStringPrefix(text: []const u8) []const u8 {
    return text[0 .. std.mem.indexOfScalar(u8, text, 0) orelse text.len];
}

fn clearOptionOut(pint: ?*i32) void {
    if (pint) |out| {
        out.* = 0;
    }
}

fn wrapUnsignedToI32(value: u64) i32 {
    return @bitCast(@as(u32, @truncate(value)));
}

fn wrapNegativeUnsignedToI32(value: u64) i32 {
    return @bitCast(@as(u32, @truncate(@as(u64, 0) -% value)));
}

fn parseOptionBase(text: []const u8, start: usize) struct {
    base: u8,
    digits_start: usize,
} {
    if (start < text.len and text[start] == '0') {
        if (start + 2 < text.len and (text[start + 1] == 'x' or text[start + 1] == 'X') and digitValue(text[start + 2], 16) != null) {
            return .{ .base = 16, .digits_start = start + 2 };
        }
        return .{ .base = 8, .digits_start = start };
    }

    return .{ .base = 10, .digits_start = start };
}

fn parseUnsignedOption(text: []const u8) struct {
    parsed_any: bool,
    consumed: usize,
    value: u64,
} {
    const base_info = parseOptionBase(text, 0);

    var idx = base_info.digits_start;
    var parsed_any = false;
    var value: u64 = 0;

    while (idx < text.len) : (idx += 1) {
        const digit = digitValue(text[idx], base_info.base) orelse break;
        parsed_any = true;
        value = saturatingMulAdd(value, base_info.base, digit);
    }

    return .{
        .parsed_any = parsed_any,
        .consumed = idx,
        .value = value,
    };
}

fn parseSignedOption(text: []const u8) struct {
    parsed_any: bool,
    value: i32,
} {
    if (text.len == 0) {
        return .{ .parsed_any = false, .value = 0 };
    }

    var offset: usize = 0;
    var negative = false;
    switch (text[0]) {
        '-' => {
            negative = true;
            offset = 1;
        },
        '+' => {
            offset = 1;
        },
        else => {},
    }

    const parsed = parseUnsignedOption(text[offset..]);
    if (!parsed.parsed_any) {
        return .{ .parsed_any = false, .value = 0 };
    }

    return .{
        .parsed_any = true,
        .value = if (negative) wrapNegativeUnsignedToI32(parsed.value) else wrapUnsignedToI32(parsed.value),
    };
}

fn getRange(str: *[]const u8, first_value: i32, dest: []i32) i64 {
    if (str.*.len == 0 or str.*[0] != '-') {
        return -1;
    }

    str.* = str.*[1..];
    const parsed_upper = parseSignedOption(str.*);
    if (!parsed_upper.parsed_any) {
        return -1;
    }

    var x = first_value;
    var write_index: usize = 0;
    while (write_index < dest.len and x < parsed_upper.value) : ({
        write_index += 1;
        x +%= 1;
    }) {
        dest[write_index] = x;
    }

    return @as(i64, parsed_upper.value) - @as(i64, first_value);
}

pub fn getOption(str: *[]const u8, pint: ?*i32) u8 {
    if (str.*.len == 0) {
        clearOptionOut(pint);
        return 0;
    }

    if (str.*[0] == '+') {
        clearOptionOut(pint);
        return 0;
    }

    if (str.*[0] == '-') {
        const parsed_negative = parseUnsignedOption(str.*[1..]);
        if (!parsed_negative.parsed_any) {
            str.* = str.*[1..];
            clearOptionOut(pint);
            return 0;
        }

        str.* = str.*[1 + parsed_negative.consumed ..];
        if (pint) |out| {
            out.* = wrapNegativeUnsignedToI32(parsed_negative.value);
        }
    } else {
        const parsed_positive = parseUnsignedOption(str.*);
        if (!parsed_positive.parsed_any) {
            clearOptionOut(pint);
            return 0;
        }

        str.* = str.*[parsed_positive.consumed..];
        if (pint) |out| {
            out.* = wrapUnsignedToI32(parsed_positive.value);
        }
    }

    if (str.*.len != 0 and str.*[0] == ',') {
        str.* = str.*[1..];
        return 2;
    }

    if (str.*.len != 0 and str.*[0] == '-') {
        return 3;
    }

    return 1;
}

pub const get_option = getOption;

pub fn getOptions(str: []const u8, nints: usize, ints: []i32) []const u8 {
    const validate = nints == 0;
    var current = str;
    var i: isize = 1;
    var ignored = [_]i32{};

    while (i < @as(isize, @intCast(nints)) or validate) {
        const pint = if (validate) &ints[0] else &ints[@intCast(i)];
        const res = getOption(&current, pint);
        if (res == 0) {
            break;
        }

        if (res == 3) {
            const range_nums = getRange(&current, pint.*, if (validate) ignored[0..] else ints[@intCast(i)..nints]);
            if (range_nums < 0) {
                break;
            }
            i += @intCast(range_nums - 1);
        }

        i += 1;
        if (res == 1) {
            break;
        }
    }

    ints[0] = @intCast(i - 1);
    return current;
}

pub const get_options = getOptions;

pub fn nextArg(args: []const u8) NextArgResult {
    const current = cStringPrefix(args);
    if (current.len == 0) {
        return .{
            .param = current[0..0],
            .value = null,
            .rest = current[0..0],
            .remaining = current[0..0],
        };
    }

    if (std.ascii.isWhitespace(current[0])) {
        const rest = current[skipLeadingSpaces(current, 1)..];
        return .{
            .param = current[0..0],
            .value = null,
            .rest = rest,
            .remaining = rest,
        };
    }

    const quoted_prefix = current[0] == '"';
    const token_start: usize = if (quoted_prefix) 1 else 0;

    var idx = token_start;
    var equals_idx: ?usize = null;
    var in_quote = quoted_prefix;

    while (idx < current.len) : (idx += 1) {
        const ch = current[idx];
        if (std.ascii.isWhitespace(ch) and !in_quote) {
            break;
        }
        if (equals_idx == null and ch == '=' and idx != token_start) {
            equals_idx = idx;
        }
        if (ch == '"') {
            in_quote = !in_quote;
        }
    }

    const token_end = if (quoted_prefix and idx > token_start and current[idx - 1] == '"') idx - 1 else idx;
    const rest = if (idx < current.len and std.ascii.isWhitespace(current[idx]))
        current[skipLeadingSpaces(current, idx + 1)..]
    else
        current[idx..];

    if (equals_idx) |eq| {
        var value_start = eq + 1;
        var value_end = token_end;
        if (value_start < value_end and current[value_start] == '"') {
            value_start += 1;
            if (value_end > value_start and current[value_end - 1] == '"') {
                value_end -= 1;
            }
        }

        return .{
            .param = current[token_start..eq],
            .value = current[value_start..value_end],
            .rest = rest,
            .remaining = rest,
        };
    }

    return .{
        .param = current[token_start..token_end],
        .value = null,
        .rest = rest,
        .remaining = rest,
    };
}

pub const next_arg = nextArg;

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

test "getOption and getOptions preserve Linux-style range parsing" {
    var option_rest: []const u8 = "3-5";
    var option_value: i32 = 0;

    try std.testing.expectEqual(@as(u8, 3), getOption(&option_rest, &option_value));
    try std.testing.expectEqual(@as(i32, 3), option_value);
    try std.testing.expectEqualStrings("-5", option_rest);

    var values = [_]i32{ 0, 0, 0, 0, 0 };
    const rest = getOptions("3-5,8", values.len, &values);
    try std.testing.expectEqualStrings("", rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 3, 4, 5, 8 }, &values);

    var single_validate = [_]i32{0};
    const single_validate_rest = getOptions("1-1", 0, &single_validate);
    try std.testing.expectEqualStrings("", single_validate_rest);
    try std.testing.expectEqual(@as(i32, 1), single_validate[0]);
}

test "getOptions expands negative ranges and negative upper bounds" {
    var negative_values = [_]i32{ 0, 0, 0, 0, 0 };
    const negative_rest = getOptions("-2-1", negative_values.len, &negative_values);
    try std.testing.expectEqualStrings("", negative_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, -2, -1, 0, 1 }, &negative_values);

    var negative_upper_values = [_]i32{ 0, 0, 0, 0 };
    const negative_upper_rest = getOptions("-3--1", negative_upper_values.len, &negative_upper_values);
    try std.testing.expectEqualStrings("", negative_upper_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, -3, -2, -1 }, &negative_upper_values);
}

test "getOption clears caller output on malformed signed and unsigned input" {
    var hyphen_only: []const u8 = "-";
    var hyphen_only_value: i32 = 99;
    try std.testing.expectEqual(@as(u8, 0), getOption(&hyphen_only, &hyphen_only_value));
    try std.testing.expectEqual(@as(i32, 0), hyphen_only_value);
    try std.testing.expectEqualStrings("", hyphen_only);

    var malformed_negative: []const u8 = "-x";
    var malformed_negative_value: i32 = 99;
    try std.testing.expectEqual(@as(u8, 0), getOption(&malformed_negative, &malformed_negative_value));
    try std.testing.expectEqual(@as(i32, 0), malformed_negative_value);
    try std.testing.expectEqualStrings("x", malformed_negative);

    var malformed_unsigned: []const u8 = "x";
    var malformed_unsigned_value: i32 = 99;
    try std.testing.expectEqual(@as(u8, 0), getOption(&malformed_unsigned, &malformed_unsigned_value));
    try std.testing.expectEqual(@as(i32, 0), malformed_unsigned_value);
    try std.testing.expectEqualStrings("x", malformed_unsigned);

    var plus: []const u8 = "+9,tail";
    try std.testing.expectEqual(@as(u8, 0), getOption(&plus, null));
    try std.testing.expectEqualStrings("+9,tail", plus);
}

test "getOption preserves incomplete hex-prefix and descending-range behavior" {
    var incomplete_hex: []const u8 = "0x";
    var incomplete_hex_value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 1), getOption(&incomplete_hex, &incomplete_hex_value));
    try std.testing.expectEqual(@as(i32, 0), incomplete_hex_value);
    try std.testing.expectEqualStrings("x", incomplete_hex);

    var plus_hex_rest: []const u8 = "+0x";
    var plus_hex_value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 0), getOption(&plus_hex_rest, &plus_hex_value));
    try std.testing.expectEqual(@as(i32, 0), plus_hex_value);
    try std.testing.expectEqualStrings("+0x", plus_hex_rest);

    var descending = [_]i32{ 0, 0, 0, 0 };
    const descending_rest = getOptions("4-2,9", descending.len, &descending);
    try std.testing.expectEqualStrings("2,9", descending_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 0, 4, 0, 0 }, &descending);
}

test "getOption and getOptions preserve oversized wrap semantics" {
    var positive: []const u8 = "2147483648";
    var positive_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 1), getOption(&positive, &positive_value));
    try std.testing.expectEqual(@as(i32, -2147483648), positive_value);
    try std.testing.expectEqualStrings("", positive);

    var negative: []const u8 = "-2147483649";
    var negative_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 1), getOption(&negative, &negative_value));
    try std.testing.expectEqual(@as(i32, 2147483647), negative_value);
    try std.testing.expectEqualStrings("", negative);

    var full_values = [_]i32{ 0, 0, 0 };
    const full_rest = getOptions("18446744073709551615,-18446744073709551615", full_values.len, &full_values);
    try std.testing.expectEqualStrings("", full_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, -1, 1 }, &full_values);

    var overflow_validate_only = [_]i32{0};
    const overflow_validate_rest = getOptions("18446744073709551616,-18446744073709551616", 0, &overflow_validate_only);
    try std.testing.expectEqualStrings("", overflow_validate_rest);
    try std.testing.expectEqual(@as(i32, 2), overflow_validate_only[0]);
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

    const leading_plus = memparse("+3Mmore");
    try std.testing.expectEqual(@as(u64, 0), leading_plus.value);
    try std.testing.expectEqualStrings("+3Mmore", leading_plus.rest);

    const leading_plus_decimal = memparse("+7tail");
    try std.testing.expectEqual(@as(u64, 0), leading_plus_decimal.value);
    try std.testing.expectEqualStrings("+7tail", leading_plus_decimal.rest);
}

test "memparse keeps signed non-decimal prefixes aligned with suffix handling" {
    const negative_hex = memparse("-0x2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative_hex.value);
    try std.testing.expectEqualStrings("tail", negative_hex.rest);

    const unsigned_octal = memparse("010Mmore");
    try std.testing.expectEqual(@as(u64, 8 << 20), unsigned_octal.value);
    try std.testing.expectEqualStrings("more", unsigned_octal.rest);
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

test "nextArg keeps empty input borrowed from the caller slice" {
    var empty = [_]u8{};
    const empty_args = empty[0..];
    const parsed = nextArg(empty_args);

    try std.testing.expectEqualStrings("", parsed.param);
    try std.testing.expect(parsed.value == null);
    try std.testing.expectEqualStrings("", parsed.rest);
    try std.testing.expectEqual(@as(usize, @intFromPtr(empty_args.ptr)), @as(usize, @intFromPtr(parsed.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(empty_args.ptr)), @as(usize, @intFromPtr(parsed.rest.ptr)));
}

test "nextArg keeps the Linux-style empty sentinel token for leading whitespace" {
    var leading_whitespace = [_]u8{ ' ', '\t', 'f', 'o', 'o', '=', '1', 0 };
    const parsed = nextArg(&leading_whitespace);

    try std.testing.expectEqualStrings("", parsed.param);
    try std.testing.expect(parsed.value == null);
    try std.testing.expectEqualStrings("foo=1", parsed.rest);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&leading_whitespace[0])), @as(usize, @intFromPtr(parsed.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&leading_whitespace[2])), @as(usize, @intFromPtr(parsed.rest.ptr)));
}

test "nextArg keeps whitespace-only input as an empty sentinel before the first NUL" {
    const parsed = nextArg(" \t\n\x00ignored tail");
    try std.testing.expectEqualStrings("", parsed.param);
    try std.testing.expect(parsed.value == null);
    try std.testing.expectEqualStrings("", parsed.rest);
}

test "nextArg parses bare parameters and keeps the remaining text" {
    const first = nextArg("debug nohlt");
    try std.testing.expectEqualStrings("debug", first.param);
    try std.testing.expect(first.value == null);
    try std.testing.expectEqualStrings("nohlt", first.remaining);
}

test "nextArg stays inside the first NUL for bare and key value tokens" {
    const bare = nextArg("debug\x00 nohlt");
    try std.testing.expectEqualStrings("debug", bare.param);
    try std.testing.expect(bare.value == null);
    try std.testing.expectEqualStrings("", bare.remaining);

    const keyed = nextArg("console=ttyS0\x00 root=/dev/vda");
    try std.testing.expectEqualStrings("console", keyed.param);
    try std.testing.expectEqualStrings("ttyS0", keyed.value.?);
    try std.testing.expectEqualStrings("", keyed.remaining);
}

test "nextArg keeps leading equals tokens as bare parameters" {
    const parsed = nextArg("=ttyS0 tail");
    try std.testing.expectEqualStrings("=ttyS0", parsed.param);
    try std.testing.expect(parsed.value == null);
    try std.testing.expectEqualStrings("tail", parsed.remaining);
}

test "nextArg keeps quoted leading equals tokens as bare parameters" {
    const parsed = nextArg("\"=ttyS0\" tail");
    try std.testing.expectEqualStrings("=ttyS0", parsed.param);
    try std.testing.expect(parsed.value == null);
    try std.testing.expectEqualStrings("tail", parsed.remaining);
}

test "nextArg parses key value pairs and quoted values" {
    const parsed = nextArg("console=ttyS0,115200 root=\"/dev/sda1 quiet\" panic=-1");
    try std.testing.expectEqualStrings("console", parsed.param);
    try std.testing.expectEqualStrings("ttyS0,115200", parsed.value.?);
    try std.testing.expectEqualStrings("root=\"/dev/sda1 quiet\" panic=-1", parsed.remaining);

    const second = nextArg(parsed.remaining);
    try std.testing.expectEqualStrings("root", second.param);
    try std.testing.expectEqualStrings("/dev/sda1 quiet", second.value.?);
    try std.testing.expectEqualStrings("panic=-1", second.remaining);
}

test "nextArg handles a quoted full token that contains a key value pair" {
    const parsed = next_arg("\"mode=fast path\" tail");
    try std.testing.expectEqualStrings("mode", parsed.param);
    try std.testing.expectEqualStrings("fast path", parsed.value.?);
    try std.testing.expectEqualStrings("tail", parsed.remaining);
}

test "nextArg keeps quoted bare tokens together and preserves the following remainder" {
    const parsed = nextArg("\"two words\" tail");
    try std.testing.expectEqualStrings("two words", parsed.param);
    try std.testing.expect(parsed.value == null);
    try std.testing.expectEqualStrings("tail", parsed.remaining);
}

test "nextArg keeps quoted empty values explicit without swallowing the next token" {
    const parsed = nextArg("flag=\"\" next");
    try std.testing.expectEqualStrings("flag", parsed.param);
    try std.testing.expectEqualStrings("", parsed.value.?);
    try std.testing.expectEqualStrings("next", parsed.remaining);
}
