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
    var it = std.mem.splitScalar(u8, str, ',');
    while (it.next()) |segment| {
        if (std.mem.eql(u8, segment, option)) {
            return true;
        }
    }
    return false;
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

fn parseUnsignedPrefix(s: []const u8) ?struct { value: u64, len: usize } {
    if (s.len == 0) {
        return null;
    }

    var base: u8 = 10;
    var start: usize = 0;

    if (s.len >= 2 and s[0] == '0' and (s[1] == 'x' or s[1] == 'X')) {
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

test "parseOptionStr only matches full comma-delimited options" {
    try std.testing.expect(parseOptionStr("quiet,debug", "debug"));
    try std.testing.expect(parseOptionStr("debug", "debug"));
    try std.testing.expect(!parseOptionStr("nodebug,quiet", "debug"));
    try std.testing.expect(!parseOptionStr("debug=1,quiet", "debug"));
}
