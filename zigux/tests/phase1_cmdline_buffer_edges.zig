const std = @import("std");
const cmdline = @import("cmdline");

test "phase1 cmdline buffer edges keep keyed slices borrowed from caller storage" {
    const buffer = [_]u8{
        ' ', ' ',
        'r', 'o',
        'o', 't',
        '=', '"',
        '/', 'd',
        'e', 'v',
        '/', 's',
        'd', 'a',
        '1', ' ',
        'q', 'u',
        'i', 'e',
        't', '"',
        ' ', ' ',
        'p', 'a',
        'n', 'i',
        'c', '=',
        '-', '1',
    };

    const parsed = cmdline.nextArg(&buffer) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", parsed.param);
    try std.testing.expectEqualStrings("/dev/sda1 quiet", parsed.value.?);
    try std.testing.expectEqualStrings("panic=-1", parsed.remaining);

    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[2])), @as(usize, @intFromPtr(parsed.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[8])), @as(usize, @intFromPtr(parsed.value.?.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[26])), @as(usize, @intFromPtr(parsed.remaining.ptr)));
}

test "phase1 cmdline buffer edges keep quoted full-token slices borrowed from caller storage" {
    const buffer = [_]u8{
        '"',
        'm',
        'o',
        'd',
        'e',
        '=',
        'f',
        'a',
        's',
        't',
        ' ',
        'p',
        'a',
        't',
        'h',
        '"',
        ' ',
        ' ',
        't',
        'a',
        'i',
        'l',
    };

    const parsed = cmdline.next_arg(&buffer) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", parsed.param);
    try std.testing.expectEqualStrings("fast path", parsed.value.?);
    try std.testing.expectEqualStrings("tail", parsed.remaining);

    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[1])), @as(usize, @intFromPtr(parsed.param.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[6])), @as(usize, @intFromPtr(parsed.value.?.ptr)));
    try std.testing.expectEqual(@as(usize, @intFromPtr(&buffer[18])), @as(usize, @intFromPtr(parsed.remaining.ptr)));
}

test "phase1 cmdline buffer edges trim inter-token whitespace across sequential parses" {
    const first = cmdline.nextArg("  alpha   beta=two   gamma") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("alpha", first.param);
    try std.testing.expect(first.value == null);
    try std.testing.expectEqualStrings("beta=two   gamma", first.remaining);

    const second = cmdline.nextArg(first.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("beta", second.param);
    try std.testing.expectEqualStrings("two", second.value.?);
    try std.testing.expectEqualStrings("gamma", second.remaining);
}

test "phase1 cmdline buffer edges keep saturated and invalid memparse rest splits aligned" {
    const saturated = cmdline.memparse("+9223372036854775808Krest");
    try std.testing.expectEqual(@as(u64, std.math.maxInt(i64)), saturated.value);
    try std.testing.expectEqualStrings("rest", saturated.rest);

    const invalid = cmdline.memparse("-0xKtail");
    try std.testing.expectEqual(@as(u64, 0), invalid.value);
    try std.testing.expectEqualStrings("-0xKtail", invalid.rest);
}
