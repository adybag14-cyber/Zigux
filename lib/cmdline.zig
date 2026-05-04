// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub fn getOption(str: *[]const u8, pint: ?*i32) u8 {
    const current = str.*;
    if (current.len == 0) {
        return 0;
    }

    var parsed_bits: u64 = 0;
    var negative = false;
    var consumed: usize = 0;

    if (current[0] == '-') {
        if (current.len == 1) {
            if (pint) |out| {
                out.* = 0;
            }
            str.* = current[1..];
            return 0;
        }

        const parsed = parseUnsignedPrefix(current[1..]) orelse {
            if (pint) |out| {
                out.* = 0;
            }
            str.* = current[1..];
            return 0;
        };
        parsed_bits = parsed.value;
        negative = true;
        consumed = 1 + parsed.len;
    } else {
        const parsed = parseUnsignedPrefix(current) orelse {
            if (pint) |out| {
                out.* = 0;
            }
            return 0;
        };
        parsed_bits = parsed.value;
        consumed = parsed.len;
    }

    const value = wrapU64ToI32(parsed_bits, negative);
    if (pint) |out| {
        out.* = value;
    }

    const rest = current[consumed..];
    if (rest.len != 0 and rest[0] == ',') {
        str.* = rest[1..];
        return 2;
    }
    if (rest.len != 0 and rest[0] == '-') {
        str.* = rest;
        return 3;
    }

    str.* = rest;
    return 1;
}

pub fn getOptions(str: []const u8, nints: usize, ints: []i32) []const u8 {
    std.debug.assert(ints.len > 0);
    if (nints != 0) {
        std.debug.assert(ints.len >= nints);
    }

    const validate = nints == 0;
    var remaining = str;
    var i: usize = 1;

    while (i < nints or validate) {
        var value: i32 = 0;
        const res = getOption(&remaining, &value);
        if (res == 0) {
            break;
        }

        if (!validate) {
            ints[i] = value;
        }

        if (res == 3) {
            const range_count = getRange(&remaining, value, if (validate) ints[0..0] else ints[i..nints]);
            if (range_count == null) {
                break;
            }
            i += range_count.? -| 1;
        }

        i += 1;
        if (res == 1) {
            break;
        }
    }

    ints[0] = @intCast(i - 1);
    return remaining;
}

pub fn memparse(ptr: []const u8, ret_index: ?*usize) u64 {
    const parsed = parseUnsignedPrefix(ptr);
    var value: u64 = 0;
    var index: usize = 0;

    if (parsed) |result| {
        value = result.value;
        index = result.len;
    } else if (ptr.len != 0 and memSuffixShift(ptr[0]) != 0) {
        // `memparse()` in `lib/cmdline.c` still consumes a leading size suffix
        // even when `simple_strtoull()` did not parse any digits.
        index = 1;
    } else {
        if (ret_index) |out| {
            out.* = 0;
        }
        return 0;
    }

    if (parsed != null and index < ptr.len) {
        const shift_blocks = memSuffixShift(ptr[index]);
        if (shift_blocks != 0) {
            value <<= shift_blocks * 10;
            index += 1;
        }
    }

    if (ret_index) |out| {
        out.* = index;
    }
    return value;
}

pub fn parseOptionStr(str: []const u8, option: []const u8) bool {
    var remaining = cStringPrefix(str);
    const needle = cStringPrefix(option);
    while (remaining.len != 0) {
        if (remaining.len >= needle.len and std.mem.eql(u8, remaining[0..needle.len], needle)) {
            if (remaining.len == needle.len or remaining[needle.len] == ',') {
                return true;
            }
        }

        const comma = std.mem.indexOfScalar(u8, remaining, ',') orelse return false;
        remaining = remaining[comma + 1 ..];
    }

    return false;
}

pub const NextArgResult = struct {
    rest: []u8,
    param: []const u8,
    value: ?[]const u8,
};

pub fn nextArg(args: []u8) NextArgResult {
    if (args.len == 0) {
        return .{ .rest = args, .param = "", .value = null };
    }

    var start: usize = 0;
    var quoted = false;
    var in_quote = false;
    if (args[0] == '"') {
        start = 1;
        quoted = true;
        in_quote = true;
    }

    const current = args[start..];
    // Mirror Linux's sentinel behavior: '=' at offset 0 does not split
    // the token into param/value parts.
    var equals_index: usize = 0;
    var index: usize = 0;
    while (index < current.len and current[index] != 0) : (index += 1) {
        if (!in_quote and std.ascii.isWhitespace(current[index])) {
            break;
        }
        if (equals_index == 0 and current[index] == '=') {
            equals_index = index;
        }
        if (current[index] == '"') {
            in_quote = !in_quote;
        }
    }

    var value_start: ?usize = null;
    if (equals_index != 0) {
        current[equals_index] = 0;
        var value_index = equals_index + 1;
        if (value_index < current.len and current[value_index] == '"') {
            value_index += 1;
            if (index > 0 and current[index - 1] == '"') {
                current[index - 1] = 0;
            }
        }
        value_start = value_index;
    }

    if (quoted and index > 0 and current[index - 1] == '"') {
        current[index - 1] = 0;
    }

    const rest_start = start + index;
    if (rest_start < args.len and args[rest_start] != 0) {
        args[rest_start] = 0;
        return .{
            .rest = skipSpaces(args[rest_start + 1 ..]),
            .param = cStringPrefix(current),
            .value = if (value_start) |value_offset| cStringPrefix(current[value_offset..]) else null,
        };
    }

    return .{
        .rest = skipSpaces(args[rest_start..]),
        .param = cStringPrefix(current),
        .value = if (value_start) |value_offset| cStringPrefix(current[value_offset..]) else null,
    };
}

fn getRange(str: *[]const u8, lower: i32, out: []i32) ?usize {
    if (str.*.len == 0 or str.*[0] != '-') {
        return null;
    }

    str.* = str.*[1..];
    const parsed = parseSignedPrefix(str.*) orelse return null;
    const upper = std.math.cast(i32, parsed.value) orelse return null;

    const lower_wide: i64 = lower;
    const upper_wide: i64 = upper;
    const delta = std.math.sub(i64, upper_wide, lower_wide) catch return null;
    if (delta < 0) {
        return null;
    }

    var written: usize = 0;
    var current_value = lower_wide;
    while (written < out.len and current_value < upper_wide) : (written += 1) {
        out[written] = @intCast(current_value);
        current_value += 1;
    }

    return std.math.cast(usize, delta);
}

fn cStringPrefix(s: []const u8) []const u8 {
    return s[0 .. std.mem.indexOfScalar(u8, s, 0) orelse s.len];
}

fn parseUnsignedPrefix(s: []const u8) ?struct { value: u64, len: usize } {
    if (s.len == 0) {
        return null;
    }

    // `lib/cmdline.c` routes unsigned parsing through `simple_strtoull()`,
    // which does not accept an explicit leading '+' in this tree.
    if (s[0] == '+') {
        return null;
    }

    var base: u8 = 10;
    var start: usize = 0;

    if (s.len >= 3 and s[0] == '0' and (s[1] == 'x' or s[1] == 'X') and isDigitForBase(s[2], 16)) {
        base = 16;
        start = 2;
    } else if (s[0] == '0') {
        base = 8;
        start = 1;
    }

    var index = start;
    while (index < s.len and isDigitForBase(s[index], base)) : (index += 1) {}

    if (index == start) {
        if (start == 1) {
            return .{ .value = 0, .len = 1 };
        }
        return null;
    }

    return .{
        .value = std.fmt.parseUnsigned(u64, s[start..index], base) catch return null,
        .len = index,
    };
}

fn parseSignedPrefix(s: []const u8) ?struct { value: i64, len: usize } {
    if (s.len == 0) {
        return null;
    }

    if (s[0] == '-') {
        const parsed = parseUnsignedPrefix(s[1..]) orelse return null;
        return .{
            .value = wrapUnsignedToI64(parsed.value, true),
            .len = 1 + parsed.len,
        };
    }

    const parsed = parseUnsignedPrefix(s) orelse return null;
    return .{
        .value = wrapUnsignedToI64(parsed.value, false),
        .len = parsed.len,
    };
}

fn isDigitForBase(ch: u8, base: u8) bool {
    const value = switch (ch) {
        '0'...'9' => ch - '0',
        'a'...'z' => ch - 'a' + 10,
        'A'...'Z' => ch - 'A' + 10,
        else => return false,
    };
    return value < base;
}

fn memSuffixShift(ch: u8) u6 {
    return switch (ch) {
        'E', 'e' => 6,
        'P', 'p' => 5,
        'T', 't' => 4,
        'G', 'g' => 3,
        'M', 'm' => 2,
        'K', 'k' => 1,
        else => 0,
    };
}

fn wrapUnsignedToI64(value: u64, negative: bool) i64 {
    const bits = if (negative) (0 -% value) else value;
    return @bitCast(bits);
}

fn wrapU64ToI32(value: u64, negative: bool) i32 {
    const bits = if (negative) (0 -% value) else value;
    const truncated: u32 = @truncate(bits);
    return @bitCast(truncated);
}

fn skipSpaces(s: []u8) []u8 {
    var index: usize = 0;
    while (index < s.len and s[index] != 0 and std.ascii.isWhitespace(s[index])) : (index += 1) {}
    return s[index..];
}

const GetOptionCase = struct {
    input: []const u8,
    expected_rc: u8,
    expected_rest: []const u8,
};

const GetOptionsCase = struct {
    input: []const u8,
    expected: []const i32,
};

const NextArgCase = struct {
    name: []const u8,
    input: []const u8,
    expected_param: []const u8,
    expected_value: ?[]const u8,
    expected_rest: []const u8,
};

const next_arg_cases = [_]NextArgCase{
    .{
        .name = "quoted value with trailing token",
        .input = "root=\"/dev/sda 1\" ro",
        .expected_param = "root",
        .expected_value = "/dev/sda 1",
        .expected_rest = "ro",
    },
    .{
        .name = "quoted bare token with trailing token",
        .input = "\"noparam value\" next",
        .expected_param = "noparam value",
        .expected_value = null,
        .expected_rest = "next",
    },
    .{
        .name = "unquoted value keeps punctuation until whitespace",
        .input = "console=ttyS0,115200n8 panic=-1",
        .expected_param = "console",
        .expected_value = "ttyS0,115200n8",
        .expected_rest = "panic=-1",
    },
    .{
        .name = "empty quoted value becomes empty string",
        .input = "rdinit=\"\" quiet",
        .expected_param = "rdinit",
        .expected_value = "",
        .expected_rest = "quiet",
    },
    .{
        .name = "first equals wins inside the value",
        .input = "key=alpha=beta tail",
        .expected_param = "key",
        .expected_value = "alpha=beta",
        .expected_rest = "tail",
    },
    .{
        .name = "quoted value without trailing token leaves empty rest",
        .input = "mode=\"fast boot\"",
        .expected_param = "mode",
        .expected_value = "fast boot",
        .expected_rest = "",
    },
    .{
        .name = "unterminated quoted value consumes the token tail",
        .input = "mode=\"fast boot",
        .expected_param = "mode",
        .expected_value = "fast boot",
        .expected_rest = "",
    },
    .{
        .name = "leading equals sign stays in the parameter token",
        .input = "=bad next",
        .expected_param = "=bad",
        .expected_value = null,
        .expected_rest = "next",
    },
    .{
        .name = "trailing spaces after key=value trim to empty rest",
        .input = "mode=fast   ",
        .expected_param = "mode",
        .expected_value = "fast",
        .expected_rest = "",
    },
};

fn expectNextArgFixture(case: NextArgCase) !void {
    var buffer = [_]u8{0} ** 128;
    try std.testing.expect(case.input.len <= buffer.len);
    @memcpy(buffer[0..case.input.len], case.input);

    const parsed = nextArg(buffer[0..case.input.len]);
    try std.testing.expectEqualStrings(case.expected_param, parsed.param);
    if (case.expected_value) |expected| {
        try std.testing.expect(parsed.value != null);
        try std.testing.expectEqualStrings(expected, parsed.value.?);
    } else {
        try std.testing.expectEqual(@as(?[]const u8, null), parsed.value);
    }
    try std.testing.expectEqualStrings(case.expected_rest, cStringPrefix(parsed.rest));
}

fn expectGetOptionCase(case: GetOptionCase) !void {
    var rest = case.input;
    var value: i32 = -1;
    try std.testing.expectEqual(case.expected_rc, getOption(&rest, &value));
    try std.testing.expectEqualStrings(case.expected_rest, rest);
}

fn expectGetOptionsCase(case: GetOptionsCase) !void {
    var parsed = [_]i32{0} ** 16;
    _ = getOptions(case.input, parsed.len, &parsed);
    try std.testing.expectEqualSlices(i32, case.expected, parsed[0..case.expected.len]);
    for (parsed[case.expected.len..]) |value| {
        try std.testing.expectEqual(@as(i32, 0), value);
    }

    var validate = [_]i32{0} ** 16;
    _ = getOptions(case.input, 0, &validate);
    try std.testing.expectEqual(case.expected[0], validate[0]);
    for (validate[1..]) |value| {
        try std.testing.expectEqual(@as(i32, 0), value);
    }
}

test "getOption parses signed integers and updates the remaining slice" {
    var rest: []const u8 = "-5,tail";
    var value: i32 = 0;

    try std.testing.expectEqual(@as(u8, 2), getOption(&rest, &value));
    try std.testing.expectEqual(@as(i32, -5), value);
    try std.testing.expectEqualStrings("tail", rest);
}

test "getOption reports ranges and consumes a standalone leading hyphen" {
    var range_rest: []const u8 = "1-3";
    var range_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 3), getOption(&range_rest, &range_value));
    try std.testing.expectEqual(@as(i32, 1), range_value);
    try std.testing.expectEqualStrings("-3", range_rest);

    var hyphen_only: []const u8 = "-";
    try std.testing.expectEqual(@as(u8, 0), getOption(&hyphen_only, null));
    try std.testing.expectEqualStrings("", hyphen_only);
}

test "getOptions expands ranges and supports validation-only counting" {
    var values = [_]i32{ 0, 0, 0, 0, 0 };
    const rest = getOptions("1-3,5", values.len, &values);
    try std.testing.expectEqualStrings("", rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 1, 2, 3, 5 }, &values);

    var validate = [_]i32{0};
    const validate_rest = getOptions("7-9,11", 0, &validate);
    try std.testing.expectEqualStrings("", validate_rest);
    try std.testing.expectEqual(@as(i32, 4), validate[0]);
}

test "getOptions stops on descending ranges and unparseable suffixes" {
    var values = [_]i32{ 0, 0, 0, 0 };
    const descending_rest = getOptions("4-2,9", values.len, &values);
    try std.testing.expectEqualStrings("2,9", descending_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 0, 4, 0, 0 }, &values);

    var partial = [_]i32{ 0, 0, 0 };
    const partial_rest = getOptions("8,xx", partial.len, &partial);
    try std.testing.expectEqualStrings("xx", partial_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 8, 0 }, &partial);
}

test "getOptions stops at array capacity even when a range still has an upper bound pending" {
    var limited = [_]i32{ 0, 0, 0 };
    const limited_rest = getOptions("1-4,8", limited.len, &limited);
    try std.testing.expectEqualStrings("4,8", limited_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 1, 2 }, &limited);

    var validate = [_]i32{0} ** 8;
    const validate_rest = getOptions("1-4,8", 0, &validate);
    try std.testing.expectEqualStrings("", validate_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 0, 0, 0, 0, 0, 0, 0 }, &validate);
}

test "getOptions fails closed on out-of-range range bounds instead of trapping" {
    var values = [_]i32{ 0, 0, 0 };
    const rest = getOptions("2147483647-2147483648,9", values.len, &values);
    try std.testing.expectEqualStrings("2147483648,9", rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 0, 2147483647, 0 }, &values);

    var validate = [_]i32{0};
    const validate_rest = getOptions("2147483647-2147483648", 0, &validate);
    try std.testing.expectEqualStrings("2147483648", validate_rest);
    try std.testing.expectEqual(@as(i32, 0), validate[0]);
}

test "memparse handles size suffixes and reports where parsing stopped" {
    var index: usize = 999;
    try std.testing.expectEqual(@as(u64, 2 * 1024 * 1024), memparse("2M", &index));
    try std.testing.expectEqual(@as(usize, 2), index);

    try std.testing.expectEqual(@as(u64, 16 * 1024), memparse("0x10Krest", &index));
    try std.testing.expectEqual(@as(usize, 5), index);

    try std.testing.expectEqual(@as(u64, 0), memparse("G5", &index));
    try std.testing.expectEqual(@as(usize, 1), index);

    try std.testing.expectEqual(@as(u64, 0), memparse("bad", &index));
    try std.testing.expectEqual(@as(usize, 0), index);
}

test "numeric parsing only treats 0x as hexadecimal when a hex digit follows" {
    var rest: []const u8 = "0x,tail";
    var value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 1), getOption(&rest, &value));
    try std.testing.expectEqual(@as(i32, 0), value);
    try std.testing.expectEqualStrings("x,tail", rest);

    var mem_index: usize = 999;
    try std.testing.expectEqual(@as(u64, 0), memparse("0xK", &mem_index));
    try std.testing.expectEqual(@as(usize, 1), mem_index);
}

test "numeric parsing rejects an explicit leading plus sign" {
    var rest: []const u8 = "+7,tail";
    var value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 0), getOption(&rest, &value));
    try std.testing.expectEqual(@as(i32, 0), value);
    try std.testing.expectEqualStrings("+7,tail", rest);

    var mem_index: usize = 999;
    try std.testing.expectEqual(@as(u64, 0), memparse("+32K", &mem_index));
    try std.testing.expectEqual(@as(usize, 0), mem_index);

    try std.testing.expectEqual(@as(u64, 0), memparse("+", &mem_index));
    try std.testing.expectEqual(@as(usize, 0), mem_index);
}

test "getOption zeroes the output slot for non-empty invalid tokens" {
    var rest: []const u8 = "d=eEc";
    var value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 0), getOption(&rest, &value));
    try std.testing.expectEqual(@as(i32, 0), value);
    try std.testing.expectEqualStrings("d=eEc", rest);
}

test "parseOptionStr matches C empty-option edge behavior around commas" {
    try std.testing.expect(parseOptionStr(",debug", ""));
    try std.testing.expect(parseOptionStr("quiet,,debug", ""));
    try std.testing.expect(!parseOptionStr("", ""));
    try std.testing.expect(!parseOptionStr("quiet,", ""));
}

test "parseOptionStr matches only exact bare options before NUL" {
    try std.testing.expect(parseOptionStr("quiet,debug,nohlt", "debug"));
    try std.testing.expect(!parseOptionStr("quiet,debug=1,nohlt", "debug"));
    try std.testing.expect(!parseOptionStr("quiet,debug\x00,nohlt", "nohlt"));
}

test "nextArg preserves leading equals sentinels and trims trailing spaces" {
    var sentinel_input = [_]u8{ '=', 'b', 'a', 'd', ' ', 'n', 'e', 'x', 't', 0 };
    const sentinel = nextArg(sentinel_input[0..]);
    try std.testing.expectEqualStrings("=bad", sentinel.param);
    try std.testing.expectEqual(@as(?[]const u8, null), sentinel.value);
    try std.testing.expectEqualStrings("next", cStringPrefix(sentinel.rest));

    var spaced_input = [_]u8{ 'm', 'o', 'd', 'e', '=', 'f', 'a', 's', 't', ' ', ' ', ' ', 0 };
    const spaced = nextArg(spaced_input[0..]);
    try std.testing.expectEqualStrings("mode", spaced.param);
    try std.testing.expectEqualStrings("fast", spaced.value.?);
    try std.testing.expectEqualStrings("", cStringPrefix(spaced.rest));
}

test "nextArg keeps empty quoted bare tokens isolated from the trailing cursor" {
    var empty_quoted = [_]u8{ '"', '"', ' ', 'n', 'e', 'x', 't', 0 };
    const parsed = nextArg(empty_quoted[0..]);
    try std.testing.expectEqualStrings("", parsed.param);
    try std.testing.expectEqual(@as(?[]const u8, null), parsed.value);
    try std.testing.expectEqualStrings("next", cStringPrefix(parsed.rest));

    var terminal_empty_quoted = [_]u8{ '"', '"', 0 };
    const terminal = nextArg(terminal_empty_quoted[0..]);
    try std.testing.expectEqualStrings("", terminal.param);
    try std.testing.expectEqual(@as(?[]const u8, null), terminal.value);
    try std.testing.expectEqualStrings("", cStringPrefix(terminal.rest));
}

test "nextArg matches serialized edge fixtures" {
    for (next_arg_cases) |case| {
        try expectNextArgFixture(case);
    }
}

test "getOption matches malformed-token classification from the Linux KUnit corpus" {
    const cases = [_]GetOptionCase{
        .{ .input = "\"\"", .expected_rc = 0, .expected_rest = "\"\"" },
        .{ .input = "", .expected_rc = 0, .expected_rest = "" },
        .{ .input = "=", .expected_rc = 0, .expected_rest = "=" },
        .{ .input = "\"-", .expected_rc = 0, .expected_rest = "\"-" },
        .{ .input = ",", .expected_rc = 0, .expected_rest = "," },
        .{ .input = "-,", .expected_rc = 0, .expected_rest = "," },
        .{ .input = ",-", .expected_rc = 0, .expected_rest = ",-" },
        .{ .input = "-", .expected_rc = 0, .expected_rest = "" },
        .{ .input = "+,", .expected_rc = 0, .expected_rest = "+," },
        .{ .input = "--", .expected_rc = 0, .expected_rest = "-" },
        .{ .input = ",,", .expected_rc = 0, .expected_rest = ",," },
        .{ .input = "''", .expected_rc = 0, .expected_rest = "''" },
        .{ .input = "\"\",", .expected_rc = 0, .expected_rest = "\"\"," },
        .{ .input = "\",\"", .expected_rc = 0, .expected_rest = "\",\"" },
        .{ .input = "-\"\"", .expected_rc = 0, .expected_rest = "\"\"" },
        .{ .input = "\"", .expected_rc = 0, .expected_rest = "\"" },
        .{ .input = "37,", .expected_rc = 2, .expected_rest = "" },
        .{ .input = "37--", .expected_rc = 3, .expected_rest = "--" },
        .{ .input = "\"\"37", .expected_rc = 0, .expected_rest = "\"\"37" },
        .{ .input = "-21", .expected_rc = 1, .expected_rest = "" },
    };

    for (cases) |case| {
        try expectGetOptionCase(case);
    }
}

test "getOption matches leading-integer pointer advance from the Linux KUnit corpus" {
    const cases = [_]GetOptionCase{
        .{ .input = "37\"\"", .expected_rc = 1, .expected_rest = "\"\"" },
        .{ .input = "37=", .expected_rc = 1, .expected_rest = "=" },
        .{ .input = "37\"-", .expected_rc = 1, .expected_rest = "\"-" },
        .{ .input = "37,", .expected_rc = 2, .expected_rest = "" },
        .{ .input = "37-,", .expected_rc = 3, .expected_rest = "-," },
        .{ .input = "37,-", .expected_rc = 2, .expected_rest = "-" },
        .{ .input = "37-", .expected_rc = 3, .expected_rest = "-" },
        .{ .input = "37+,", .expected_rc = 1, .expected_rest = "+," },
        .{ .input = "37--", .expected_rc = 3, .expected_rest = "--" },
        .{ .input = "37,,", .expected_rc = 2, .expected_rest = "," },
        .{ .input = "37''", .expected_rc = 1, .expected_rest = "''" },
        .{ .input = "37\"\",", .expected_rc = 1, .expected_rest = "\"\"," },
        .{ .input = "37\",\"", .expected_rc = 1, .expected_rest = "\",\"" },
        .{ .input = "37-\"\"", .expected_rc = 3, .expected_rest = "-\"\"" },
        .{ .input = "37\"", .expected_rc = 1, .expected_rest = "\"" },
    };

    for (cases) |case| {
        try expectGetOptionCase(case);
    }
}

test "getOption matches trailing-integer pointer advance from the Linux KUnit corpus" {
    const cases = [_]GetOptionCase{
        .{ .input = "\"\"37", .expected_rc = 0, .expected_rest = "\"\"37" },
        .{ .input = "=37", .expected_rc = 0, .expected_rest = "=37" },
        .{ .input = "\"-37", .expected_rc = 0, .expected_rest = "\"-37" },
        .{ .input = ",37", .expected_rc = 0, .expected_rest = ",37" },
        .{ .input = "-,37", .expected_rc = 0, .expected_rest = ",37" },
        .{ .input = ",-37", .expected_rc = 0, .expected_rest = ",-37" },
        .{ .input = "-37", .expected_rc = 1, .expected_rest = "" },
        .{ .input = "+,37", .expected_rc = 0, .expected_rest = "+,37" },
        .{ .input = "--37", .expected_rc = 0, .expected_rest = "-37" },
        .{ .input = ",,37", .expected_rc = 0, .expected_rest = ",,37" },
        .{ .input = "''37", .expected_rc = 0, .expected_rest = "''37" },
        .{ .input = "\"\",37", .expected_rc = 0, .expected_rest = "\"\",37" },
        .{ .input = "\",\"37", .expected_rc = 0, .expected_rest = "\",\"37" },
        .{ .input = "-\"\"37", .expected_rc = 0, .expected_rest = "\"\"37" },
        .{ .input = "\"37", .expected_rc = 0, .expected_rest = "\"37" },
        .{ .input = "37", .expected_rc = 1, .expected_rest = "" },
    };

    for (cases) |case| {
        try expectGetOptionCase(case);
    }
}

test "getOptions matches malformed-range counting from the Linux KUnit corpus" {
    const cases = [_]GetOptionsCase{
        .{ .input = "-7", .expected = &[_]i32{ 1, -7 } },
        .{ .input = "--7", .expected = &[_]i32{ 0, 0 } },
        .{ .input = "-1-2", .expected = &[_]i32{ 4, -1, 0, 1, 2 } },
        .{ .input = "7--9", .expected = &[_]i32{ 0, 7 } },
        .{ .input = "7-", .expected = &[_]i32{ 0, 7 } },
        .{ .input = "-7--9", .expected = &[_]i32{ 0, -7 } },
        .{ .input = "7-9,", .expected = &[_]i32{ 3, 7, 8, 9, 0 } },
        .{ .input = "9-7", .expected = &[_]i32{ 0, 9 } },
        .{ .input = "5-a", .expected = &[_]i32{ 0, 5 } },
        .{ .input = "a-5", .expected = &[_]i32{ 0, 0 } },
        .{ .input = "5-8", .expected = &[_]i32{ 4, 5, 6, 7, 8 } },
        .{ .input = ",8-5", .expected = &[_]i32{ 0, 0 } },
        .{ .input = "+,1", .expected = &[_]i32{ 0, 0 } },
        .{ .input = "-,4", .expected = &[_]i32{ 0, 0 } },
        .{ .input = "-3,0-1,6", .expected = &[_]i32{ 4, -3, 0, 1, 6 } },
        .{ .input = "4,-", .expected = &[_]i32{ 1, 4 } },
        .{ .input = " +2", .expected = &[_]i32{ 0, 0 } },
        .{ .input = " -9", .expected = &[_]i32{ 0, 0 } },
        .{ .input = "0-1,-3,6", .expected = &[_]i32{ 4, 0, 1, -3, 6 } },
        .{ .input = "- 9", .expected = &[_]i32{ 0, 0 } },
    };

    for (cases) |case| {
        try expectGetOptionsCase(case);
    }
}

test "large parsed integers wrap like the C helper instead of trapping Zig safety checks" {
    var positive_rest: []const u8 = "18446744073709551615,tail";
    var positive_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 2), getOption(&positive_rest, &positive_value));
    try std.testing.expectEqual(@as(i32, -1), positive_value);
    try std.testing.expectEqualStrings("tail", positive_rest);

    var negative_rest: []const u8 = "-18446744073709551615,tail";
    var negative_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 2), getOption(&negative_rest, &negative_value));
    try std.testing.expectEqual(@as(i32, 1), negative_value);
    try std.testing.expectEqualStrings("tail", negative_rest);
}
