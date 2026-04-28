// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub fn getOption(str: *[]const u8, pint: ?*i32) u8 {
    const current = str.*;
    if (current.len == 0) {
        return 0;
    }

    var parsed_value: i64 = 0;
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
        parsed_value = -@as(i64, @intCast(parsed.value));
        consumed = 1 + parsed.len;
    } else {
        const parsed = parseUnsignedPrefix(current) orelse return 0;
        parsed_value = @intCast(parsed.value);
        consumed = parsed.len;
    }

    if (pint) |out| {
        out.* = truncateToI32(parsed_value);
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
    const parsed = parseUnsignedPrefix(ptr) orelse {
        if (ret_index) |out| {
            out.* = 0;
        }
        return 0;
    };

    var value = parsed.value;
    var index = parsed.len;
    if (index < ptr.len) {
        const shift_blocks: u6 = switch (ptr[index]) {
            'E', 'e' => 6,
            'P', 'p' => 5,
            'T', 't' => 4,
            'G', 'g' => 3,
            'M', 'm' => 2,
            'K', 'k' => 1,
            else => 0,
        };
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
    var it = std.mem.splitScalar(u8, cStringPrefix(str), ',');
    const needle = cStringPrefix(option);
    while (it.next()) |segment| {
        if (std.mem.eql(u8, segment, needle)) {
            return true;
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

    const upper = parsed.value;
    const delta = upper - @as(i64, lower);
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
            .value = -@as(i64, @intCast(parsed.value)),
            .len = 1 + parsed.len,
        };
    }

    const parsed = parseUnsignedPrefix(s) orelse return null;
    return .{
        .value = @intCast(parsed.value),
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

fn truncateToI32(value: i64) i32 {
    const bits: u32 = @truncate(@as(u64, @bitCast(value)));
    return @bitCast(bits);
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

test "memparse handles size suffixes and reports where parsing stopped" {
    var index: usize = 999;
    try std.testing.expectEqual(@as(u64, 2 * 1024 * 1024), memparse("2M", &index));
    try std.testing.expectEqual(@as(usize, 2), index);

    try std.testing.expectEqual(@as(u64, 16 * 1024), memparse("0x10Krest", &index));
    try std.testing.expectEqual(@as(usize, 5), index);

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
    try std.testing.expectEqual(@as(i32, -1), value);
    try std.testing.expectEqualStrings("+7,tail", rest);

    var mem_index: usize = 999;
    try std.testing.expectEqual(@as(u64, 0), memparse("+32K", &mem_index));
    try std.testing.expectEqual(@as(usize, 0), mem_index);

    try std.testing.expectEqual(@as(u64, 0), memparse("+", &mem_index));
    try std.testing.expectEqual(@as(usize, 0), mem_index);
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
