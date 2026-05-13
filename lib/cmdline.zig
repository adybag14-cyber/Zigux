// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

const ParsedPrefix = struct {
    value: u64,
    len: usize,
};

pub fn getOption(str: *[]const u8, pint: ?*i32) u8 {
    const current = str.*;
    if (pint) |out| {
        out.* = 0;
    }
    if (current.len == 0) {
        return 0;
    }

    var value: i32 = 0;
    var consumed: usize = 0;

    if (current[0] == '-') {
        if (current.len == 1) {
            str.* = current[1..];
            return 0;
        }

        const parsed = parseUnsignedPrefix(current[1..]) orelse {
            str.* = current[1..];
            return 0;
        };
        value = truncateSignedMagnitudeToI32(true, parsed.value);
        consumed = 1 + parsed.len;
    } else {
        const parsed = parseUnsignedPrefix(current) orelse return 0;
        value = truncateSignedMagnitudeToI32(false, parsed.value);
        consumed = parsed.len;
    }

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
            if (range_count.? == 0) {
                i -= 1;
            } else {
                i += range_count.? - 1;
            }
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
    const parsed = parseUnsignedPrefix(ptr) orelse parseMemparseZeroPrefix(ptr);
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
    const haystack = cStringPrefix(str);
    const needle = cStringPrefix(option);
    if (haystack.len == 0) {
        return false;
    }

    var index: usize = 0;
    while (index < haystack.len) {
        if (std.mem.startsWith(u8, haystack[index..], needle)) {
            const end = index + needle.len;
            if (end == haystack.len or haystack[end] == ',') {
                return true;
            }
        }

        while (index < haystack.len and haystack[index] != ',') : (index += 1) {}
        if (index < haystack.len and haystack[index] == ',') {
            index += 1;
        }
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
        return .{ .rest = args, .param = args[0..0], .value = null };
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
    // Mirror Linux's sentinel behavior: '=' at offset 0 does not split the
    // token, but a leading quoted token still uses the first later '=' as the
    // param/value separator.
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

    const upper = parsed.value;
    const delta = @as(i64, upper) - @as(i64, lower);
    if (delta < 0) {
        return null;
    }

    var written: usize = 0;
    var x = lower;
    while (written < out.len and @as(i64, x) < upper) : (written += 1) {
        out[written] = x;
        x += 1;
    }

    return @intCast(delta);
}

fn cStringPrefix(s: []const u8) []const u8 {
    return s[0 .. std.mem.indexOfScalar(u8, s, 0) orelse s.len];
}

fn parseUnsignedPrefix(s: []const u8) ?ParsedPrefix {
    if (s.len == 0) {
        return null;
    }

    var base: u8 = 10;
    var start: usize = 0;
    var prefix_len: usize = 0;

    if (s[0] == '+') {
        prefix_len = 1;
        start = 1;
        if (s.len == 1) {
            return null;
        }
    }

    if (s.len >= start + 2 and s[start] == '0' and (s[start + 1] == 'x' or s[start + 1] == 'X')) {
        base = 16;
        start += 2;
    } else if (s[start] == '0') {
        base = 8;
        start += 1;
    }

    var index = start;
    while (index < s.len and isDigitForBase(s[index], base)) : (index += 1) {}

    if (index == start) {
        if (start == prefix_len + 1 or (base == 16 and start == prefix_len + 2)) {
            return .{ .value = 0, .len = prefix_len + 1 };
        }
        return null;
    }

    return .{
        .value = std.fmt.parseUnsigned(u64, s[start..index], base) catch return null,
        .len = index,
    };
}

fn parseMemparseZeroPrefix(s: []const u8) ?ParsedPrefix {
    if (s.len == 0) {
        return null;
    }

    var start: usize = 0;
    if (s[0] == '+') {
        start = 1;
        if (s.len == 1) {
            return null;
        }
    }

    if (s.len >= start + 2 and s[start] == '0' and (s[start + 1] == 'x' or s[start + 1] == 'X')) {
        return .{ .value = 0, .len = start + 1 };
    }

    return null;
}

fn parseSignedPrefix(s: []const u8) ?struct { value: i32, len: usize } {
    if (s.len == 0) {
        return null;
    }

    if (s[0] == '-') {
        const parsed = parseUnsignedPrefix(s[1..]) orelse return null;
        return .{
            .value = truncateSignedMagnitudeToI32(true, parsed.value),
            .len = 1 + parsed.len,
        };
    }

    const parsed = parseUnsignedPrefix(s) orelse return null;
    return .{
        .value = truncateSignedMagnitudeToI32(false, parsed.value),
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

fn truncateSignedMagnitudeToI32(is_negative: bool, magnitude: u64) i32 {
    const bits: u64 = if (is_negative) (~magnitude) +% 1 else magnitude;
    return @bitCast(@as(u32, @truncate(bits)));
}

fn skipSpaces(s: []u8) []u8 {
    var index: usize = 0;
    while (index < s.len and s[index] != 0 and std.ascii.isWhitespace(s[index])) : (index += 1) {}
    return s[index..];
}

test "getOption parses signed integers and updates the remaining slice" {
    var rest: []const u8 = "-5,tail";
    var value: i32 = 0;

    try std.testing.expectEqual(@as(u8, 2), getOption(&rest, &value));
    try std.testing.expectEqual(@as(i32, -5), value);
    try std.testing.expectEqualStrings("tail", rest);
}

test "getOption reports ranges, accepts leading plus, and consumes a standalone leading hyphen" {
    var range_rest: []const u8 = "1-3";
    var range_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 3), getOption(&range_rest, &range_value));
    try std.testing.expectEqual(@as(i32, 1), range_value);
    try std.testing.expectEqualStrings("-3", range_rest);

    var plus_rest: []const u8 = "+7";
    var plus_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 1), getOption(&plus_rest, &plus_value));
    try std.testing.expectEqual(@as(i32, 7), plus_value);
    try std.testing.expectEqualStrings("", plus_rest);

    var hyphen_only: []const u8 = "-";
    var hyphen_only_value: i32 = 99;
    try std.testing.expectEqual(@as(u8, 0), getOption(&hyphen_only, &hyphen_only_value));
    try std.testing.expectEqual(@as(i32, 0), hyphen_only_value);
    try std.testing.expectEqualStrings("", hyphen_only);
}

test "getOption keeps incomplete hex prefixes aligned with Linux simple_strtoull consumption" {
    var plain_hex_rest: []const u8 = "0x";
    var plain_hex_value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 1), getOption(&plain_hex_rest, &plain_hex_value));
    try std.testing.expectEqual(@as(i32, 0), plain_hex_value);
    try std.testing.expectEqualStrings("x", plain_hex_rest);

    var plus_hex_rest: []const u8 = "+0x";
    var plus_hex_value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 1), getOption(&plus_hex_rest, &plus_hex_value));
    try std.testing.expectEqual(@as(i32, 0), plus_hex_value);
    try std.testing.expectEqualStrings("x", plus_hex_rest);

    var negative_hex_rest: []const u8 = "-0x";
    var negative_hex_value: i32 = -1;
    try std.testing.expectEqual(@as(u8, 1), getOption(&negative_hex_rest, &negative_hex_value));
    try std.testing.expectEqual(@as(i32, 0), negative_hex_value);
    try std.testing.expectEqualStrings("x", negative_hex_rest);
}

test "getOptions expands ranges, supports validation-only counting, and accepts leading plus" {
    var values = [_]i32{ 0, 0, 0, 0, 0 };
    const rest = getOptions("1-3,5", values.len, &values);
    try std.testing.expectEqualStrings("", rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 1, 2, 3, 5 }, &values);

    var validate = [_]i32{0};
    const validate_rest = getOptions("7-9,11", 0, &validate);
    try std.testing.expectEqualStrings("", validate_rest);
    try std.testing.expectEqual(@as(i32, 4), validate[0]);

    var single = [_]i32{ 0, 0, 0 };
    const single_rest = getOptions("1-1", single.len, &single);
    try std.testing.expectEqualStrings("", single_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 1, 0 }, &single);

    var single_validate = [_]i32{0};
    const single_validate_rest = getOptions("1-1", 0, &single_validate);
    try std.testing.expectEqualStrings("", single_validate_rest);
    try std.testing.expectEqual(@as(i32, 1), single_validate[0]);

    var plus_values = [_]i32{ 0, 0, 0 };
    const plus_options_rest = getOptions("+7", plus_values.len, &plus_values);
    try std.testing.expectEqualStrings("", plus_options_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 7, 0 }, &plus_values);

    var plus_validate = [_]i32{0};
    const plus_validate_rest = getOptions("+7", 0, &plus_validate);
    try std.testing.expectEqualStrings("", plus_validate_rest);
    try std.testing.expectEqual(@as(i32, 1), plus_validate[0]);
}

test "getOptions keeps incomplete hex prefixes as zero-valued leaves" {
    var values = [_]i32{ 0, 0, 0 };
    const rest = getOptions("0x,7", values.len, &values);
    try std.testing.expectEqualStrings("x,7", rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 0, 0 }, &values);

    var validate = [_]i32{0};
    const validate_rest = getOptions("+0x,7", 0, &validate);
    try std.testing.expectEqualStrings("x,7", validate_rest);
    try std.testing.expectEqual(@as(i32, 1), validate[0]);
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

test "memparse handles size suffixes, accepts leading plus, and reports where parsing stopped" {
    var index: usize = 999;
    try std.testing.expectEqual(@as(u64, 2 * 1024 * 1024), memparse("2M", &index));
    try std.testing.expectEqual(@as(usize, 2), index);

    try std.testing.expectEqual(@as(u64, 16 * 1024), memparse("0x10Krest", &index));
    try std.testing.expectEqual(@as(usize, 5), index);

    try std.testing.expectEqual(@as(u64, 0), memparse("0xK", &index));
    try std.testing.expectEqual(@as(usize, 1), index);

    try std.testing.expectEqual(@as(u64, 0), memparse("+0xK", &index));
    try std.testing.expectEqual(@as(usize, 2), index);

    try std.testing.expectEqual(@as(u64, 0), memparse("+0x", &index));
    try std.testing.expectEqual(@as(usize, 2), index);

    try std.testing.expectEqual(@as(u64, 1024), memparse("+1K", &index));
    try std.testing.expectEqual(@as(usize, 3), index);

    try std.testing.expectEqual(@as(u64, 0), memparse("K", &index));
    try std.testing.expectEqual(@as(usize, 1), index);

    try std.testing.expectEqual(@as(u64, 0), memparse("krest", &index));
    try std.testing.expectEqual(@as(usize, 1), index);

    try std.testing.expectEqual(@as(u64, 0), memparse("bad", &index));
    try std.testing.expectEqual(@as(usize, 0), index);
}

test "parseOptionStr only matches full comma-delimited options" {
    try std.testing.expect(parseOptionStr("quiet,debug", "debug"));
    try std.testing.expect(parseOptionStr("debug", "debug"));
    try std.testing.expect(!parseOptionStr("nodebug,quiet", "debug"));
    try std.testing.expect(!parseOptionStr("debug=1,quiet", "debug"));
    try std.testing.expect(!parseOptionStr("debug,panic\x00,quiet", "quiet"));
    try std.testing.expect(parseOptionStr(",debug", ""));
    try std.testing.expect(parseOptionStr("debug,,quiet", ""));
    try std.testing.expect(!parseOptionStr("debug,", ""));
    try std.testing.expect(!parseOptionStr("", ""));
}

test "nextArg splits parameter-value pairs and trims quoted values" {
    var buffer = [_]u8{ 'm', 'o', 'd', 'e', '=', '"', 'f', 'a', 's', 't', ' ', 'b', 'o', 'o', 't', '"', ' ', 'n', 'e', 'x', 't', 0 };
    const parsed = nextArg(&buffer);

    try std.testing.expectEqualStrings("mode", parsed.param);
    try std.testing.expectEqualStrings("fast boot", parsed.value.?);
    try std.testing.expectEqualStrings("next", cStringPrefix(parsed.rest));
}

test "nextArg keeps embedded equals inside quoted values" {
    var buffer = [_]u8{ 'm', 'o', 'd', 'e', '=', '"', 'f', 'a', 's', 't', '=', 'b', 'o', 'o', 't', '"', ' ', 'n', 'e', 'x', 't', 0 };
    const parsed = nextArg(&buffer);

    try std.testing.expectEqualStrings("mode", parsed.param);
    try std.testing.expectEqualStrings("fast=boot", parsed.value.?);
    try std.testing.expectEqualStrings("next", cStringPrefix(parsed.rest));
}

test "nextArg keeps the first unquoted equals as the only separator" {
    var buffer = [_]u8{ 'k', 'e', 'y', '=', 'a', 'l', 'p', 'h', 'a', '=', 'b', 'e', 't', 'a', ' ', 't', 'a', 'i', 'l', 0 };
    const parsed = nextArg(&buffer);

    try std.testing.expectEqualStrings("key", parsed.param);
    try std.testing.expectEqualStrings("alpha=beta", parsed.value.?);
    try std.testing.expectEqualStrings("tail", cStringPrefix(parsed.rest));
}

test "nextArg keeps first-unquoted-equals param, value, and rest borrowed from the caller buffer" {
    var buffer = [_]u8{ 'k', 'e', 'y', '=', 'a', 'l', 'p', 'h', 'a', '=', 'b', 'e', 't', 'a', ' ', 't', 'a', 'i', 'l', 0 };
    const parsed = nextArg(&buffer);

    try std.testing.expectEqualStrings("key", parsed.param);
    try std.testing.expectEqualStrings("alpha=beta", parsed.value.?);
    try std.testing.expectEqualStrings("tail", cStringPrefix(parsed.rest));

    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[0])), @as(usize, @intFromPtr(parsed.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[4])), @as(usize, @intFromPtr(parsed.value.?.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[15])), @as(usize, @intFromPtr(parsed.rest.ptr)));
    try std.testing.expectEqual(@as(u8, 0), buffer[3]);
    try std.testing.expectEqual(@as(u8, 0), buffer[14]);
}

test "nextArg keeps a whole quoted token together without inventing a value" {
    var buffer = [_]u8{ '"', 't', 'w', 'o', ' ', 'w', 'o', 'r', 'd', 's', '"', ' ', 't', 'a', 'i', 'l', 0 };
    const parsed = nextArg(&buffer);

    try std.testing.expectEqualStrings("two words", parsed.param);
    try std.testing.expectEqual(@as(?[]const u8, null), parsed.value);
    try std.testing.expectEqualStrings("tail", cStringPrefix(parsed.rest));
}

test "nextArg splits a leading quoted token at the first equals like Linux" {
    var buffer = [_]u8{ '"', 'k', 'e', 'y', '=', 'v', 'a', 'l', 'u', 'e', '"', ' ', 'n', 'e', 'x', 't', 0 };
    const parsed = nextArg(&buffer);

    try std.testing.expectEqualStrings("key", parsed.param);
    try std.testing.expectEqualStrings("value", parsed.value.?);
    try std.testing.expectEqualStrings("next", cStringPrefix(parsed.rest));
}

test "nextArg keeps leading quoted param, value, and rest borrowed from the caller buffer" {
    var buffer = [_]u8{ '"', 'k', 'e', 'y', '=', 'v', 'a', 'l', 'u', 'e', '"', ' ', 'n', 'e', 'x', 't', 0 };
    const parsed = nextArg(&buffer);

    try std.testing.expectEqualStrings("key", parsed.param);
    try std.testing.expectEqualStrings("value", parsed.value.?);
    try std.testing.expectEqualStrings("next", cStringPrefix(parsed.rest));

    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[1])), @as(usize, @intFromPtr(parsed.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[5])), @as(usize, @intFromPtr(parsed.value.?.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[12])), @as(usize, @intFromPtr(parsed.rest.ptr)));
    try std.testing.expectEqual(@as(u8, 0), buffer[4]);
    try std.testing.expectEqual(@as(u8, 0), buffer[10]);
    try std.testing.expectEqual(@as(u8, 0), buffer[11]);
}

test "nextArg keeps an empty quoted bare token unsplit" {
    var buffer = [_]u8{ '"', '"', ' ', 'n', 'e', 'x', 't', 0 };
    const parsed = nextArg(&buffer);

    try std.testing.expectEqualStrings("", parsed.param);
    try std.testing.expectEqual(@as(?[]const u8, null), parsed.value);
    try std.testing.expectEqualStrings("next", cStringPrefix(parsed.rest));
}

test "nextArg keeps unquoted values and empty quoted values bounded to the current token" {
    var unquoted = [_]u8{ 'c', 'o', 'n', 's', 'o', 'l', 'e', '=', 't', 't', 'y', 'S', '0', ',', '1', '1', '5', '2', '0', '0', 'n', '8', ' ', 'p', 'a', 'n', 'i', 'c', '=', '-', '1', 0 };
    const parsed_unquoted = nextArg(&unquoted);

    try std.testing.expectEqualStrings("console", parsed_unquoted.param);
    try std.testing.expectEqualStrings("ttyS0,115200n8", parsed_unquoted.value.?);
    try std.testing.expectEqualStrings("panic=-1", cStringPrefix(parsed_unquoted.rest));

    var empty = [_]u8{ 'r', 'd', 'i', 'n', 'i', 't', '=', '"', '"', ' ', 'q', 'u', 'i', 'e', 't', 0 };
    const parsed_empty = nextArg(&empty);

    try std.testing.expectEqualStrings("rdinit", parsed_empty.param);
    try std.testing.expectEqualStrings("", parsed_empty.value.?);
    try std.testing.expectEqualStrings("quiet", cStringPrefix(parsed_empty.rest));
}

test "nextArg keeps empty whitespace-separated values and unterminated quoted values bounded to the current token" {
    var whitespace_value = [_]u8{ 'f', 'o', 'o', '=', ' ', 'b', 'a', 'r', 0 };
    const parsed_whitespace_value = nextArg(&whitespace_value);

    try std.testing.expectEqualStrings("foo", parsed_whitespace_value.param);
    try std.testing.expectEqualStrings("", parsed_whitespace_value.value.?);
    try std.testing.expectEqualStrings("bar", cStringPrefix(parsed_whitespace_value.rest));

    var unterminated_quote = [_]u8{ 'k', 'e', 'y', '=', '"', 'a', 'l', 'p', 'h', 'a', ' ', 'b', 'e', 't', 'a', 0 };
    const parsed_unterminated_quote = nextArg(&unterminated_quote);

    try std.testing.expectEqualStrings("key", parsed_unterminated_quote.param);
    try std.testing.expectEqualStrings("alpha beta", parsed_unterminated_quote.value.?);
    try std.testing.expectEqualStrings("", cStringPrefix(parsed_unterminated_quote.rest));
}

test "nextArg keeps param, value, and rest borrowed from the caller buffer" {
    var buffer = [_]u8{ 'r', 'o', 'o', 't', '=', '"', '/', 'd', 'e', 'v', '/', 's', 'd', 'a', '1', '"', ' ', 'r', 'o', 0 };
    const parsed = nextArg(&buffer);

    try std.testing.expectEqualStrings("root", parsed.param);
    try std.testing.expectEqualStrings("/dev/sda1", parsed.value.?);
    try std.testing.expectEqualStrings("ro", cStringPrefix(parsed.rest));

    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[0])), @as(usize, @intFromPtr(parsed.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[6])), @as(usize, @intFromPtr(parsed.value.?.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[17])), @as(usize, @intFromPtr(parsed.rest.ptr)));
    try std.testing.expectEqual(@as(u8, 0), buffer[4]);
    try std.testing.expectEqual(@as(u8, 0), buffer[15]);
    try std.testing.expectEqual(@as(u8, 0), buffer[16]);
}

test "nextArg keeps empty-input param and rest borrowed from the caller slice" {
    var buffer = [_]u8{};
    const args = buffer[0..];
    const parsed = nextArg(args);

    try std.testing.expectEqualStrings("", parsed.param);
    try std.testing.expectEqual(@as(?[]const u8, null), parsed.value);
    try std.testing.expectEqualStrings("", cStringPrefix(parsed.rest));
    try std.testing.expectEqual(@as(usize, @intFromPtr(args.ptr)), @as(usize, @intFromPtr(parsed.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(args.ptr)), @as(usize, @intFromPtr(parsed.rest.ptr)));
}

test "nextArg trims mixed trailing whitespace from rest and leaves whitespace-only tails empty" {
    var mixed_ws = [_]u8{ 'r', 'o', 'o', 't', '=', '/', 'd', 'e', 'v', '/', 's', 'd', 'a', '1', ' ', '\t', '\n', 'r', 'o', 0 };
    const parsed_mixed_ws = nextArg(&mixed_ws);

    try std.testing.expectEqualStrings("root", parsed_mixed_ws.param);
    try std.testing.expectEqualStrings("/dev/sda1", parsed_mixed_ws.value.?);
    try std.testing.expectEqualStrings("ro", cStringPrefix(parsed_mixed_ws.rest));

    var whitespace_only = [_]u8{ 'q', 'u', 'i', 'e', 't', ' ', '\t', '\n', 0 };
    const parsed_whitespace_only = nextArg(&whitespace_only);

    try std.testing.expectEqualStrings("quiet", parsed_whitespace_only.param);
    try std.testing.expectEqual(@as(?[]const u8, null), parsed_whitespace_only.value);
    try std.testing.expectEqualStrings("", cStringPrefix(parsed_whitespace_only.rest));
}

test "nextArg returns an empty sentinel token before leading whitespace and trims the following rest" {
    var leading_whitespace = [_]u8{ ' ', '\t', 'f', 'o', 'o', '=', '1', 0 };
    const parsed_leading_whitespace = nextArg(&leading_whitespace);

    try std.testing.expectEqualStrings("", parsed_leading_whitespace.param);
    try std.testing.expectEqual(@as(?[]const u8, null), parsed_leading_whitespace.value);
    try std.testing.expectEqualStrings("foo=1", cStringPrefix(parsed_leading_whitespace.rest));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&leading_whitespace[0])), @as(usize, @intFromPtr(parsed_leading_whitespace.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&leading_whitespace[2])), @as(usize, @intFromPtr(parsed_leading_whitespace.rest.ptr)));
    try std.testing.expectEqual(@as(u8, 0), leading_whitespace[0]);

    var whitespace_only = [_]u8{ ' ', '\t', '\n', 0 };
    const parsed_whitespace_only = nextArg(&whitespace_only);

    try std.testing.expectEqualStrings("", parsed_whitespace_only.param);
    try std.testing.expectEqual(@as(?[]const u8, null), parsed_whitespace_only.value);
    try std.testing.expectEqualStrings("", cStringPrefix(parsed_whitespace_only.rest));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&whitespace_only[0])), @as(usize, @intFromPtr(parsed_whitespace_only.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&whitespace_only[3])), @as(usize, @intFromPtr(parsed_whitespace_only.rest.ptr)));
    try std.testing.expectEqual(@as(u8, 0), whitespace_only[0]);
}

test "nextArg does not treat a leading equals sign as a value separator" {
    var buffer = [_]u8{ '=', 'b', 'a', 'd', ' ', 'n', 'e', 'x', 't', 0 };
    const parsed = nextArg(&buffer);

    try std.testing.expectEqualStrings("=bad", parsed.param);
    try std.testing.expectEqual(@as(?[]const u8, null), parsed.value);
    try std.testing.expectEqualStrings("next", cStringPrefix(parsed.rest));
}

test "getOptions expands negative ranges and negative upper bounds like Linux get_range" {
    var negative_values = [_]i32{ 0, 0, 0, 0, 0 };
    const negative_rest = getOptions("-2-1", negative_values.len, &negative_values);
    try std.testing.expectEqualStrings("", negative_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, -2, -1, 0, 1 }, &negative_values);

    var negative_validate = [_]i32{0};
    const negative_validate_rest = getOptions("-2-1", 0, &negative_validate);
    try std.testing.expectEqualStrings("", negative_validate_rest);
    try std.testing.expectEqual(@as(i32, 4), negative_validate[0]);

    var negative_upper_values = [_]i32{ 0, 0, 0, 0 };
    const negative_upper_rest = getOptions("-3--1", negative_upper_values.len, &negative_upper_values);
    try std.testing.expectEqualStrings("", negative_upper_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, -3, -2, -1 }, &negative_upper_values);

    var negative_upper_validate = [_]i32{0};
    const negative_upper_validate_rest = getOptions("-3--1", 0, &negative_upper_validate);
    try std.testing.expectEqualStrings("", negative_upper_validate_rest);
    try std.testing.expectEqual(@as(i32, 3), negative_upper_validate[0]);
}
