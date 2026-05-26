const std = @import("std");
const cmdline = @import("cmdline");

fn expectNextArg(
    args: []const u8,
    expected_param: []const u8,
    expected_value: ?[]const u8,
    expected_remaining: []const u8,
) !cmdline.NextArgResult {
    const parsed = cmdline.nextArg(args) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings(expected_param, parsed.param);
    if (expected_value) |value| {
        try std.testing.expectEqualStrings(value, parsed.value.?);
    } else {
        try std.testing.expect(parsed.value == null);
    }
    try std.testing.expectEqualStrings(expected_remaining, parsed.remaining);
    return parsed;
}

fn expectMemparse(text: []const u8, expected_value: u64, expected_rest: []const u8) !void {
    const parsed = cmdline.memparse(text);
    try std.testing.expectEqual(expected_value, parsed.value);
    try std.testing.expectEqualStrings(expected_rest, parsed.rest);
}

test "phase1 cmdline boot-arg walk keeps quoted, numeric, and option tokens aligned" {
    const first = try expectNextArg(
        "root=\"UUID=alpha beta\" mem=0x20M flags=quiet,debug,nohlt panic=-1",
        "root",
        "UUID=alpha beta",
        "mem=0x20M flags=quiet,debug,nohlt panic=-1",
    );

    const second = try expectNextArg(
        first.remaining,
        "mem",
        "0x20M",
        "flags=quiet,debug,nohlt panic=-1",
    );
    try expectMemparse(second.value.?, 0x20 << 20, "");

    const third = try expectNextArg(
        second.remaining,
        "flags",
        "quiet,debug,nohlt",
        "panic=-1",
    );
    try std.testing.expect(cmdline.parseOptionStr(third.value.?, "quiet"));
    try std.testing.expect(cmdline.parseOptionStr(third.value.?, "debug"));
    try std.testing.expect(!cmdline.parseOptionStr(third.value.?, "deb"));

    const fourth = try expectNextArg(third.remaining, "panic", "-1", "");
    try expectMemparse(fourth.value.?, @bitCast(@as(i64, -1)), "");
    try std.testing.expect(cmdline.nextArg(fourth.remaining) == null);
}

test "phase1 cmdline boot-arg walk keeps alias entry points and NUL option boundaries aligned" {
    const first = cmdline.next_arg("mem=+010M flags=quiet,debug\x00panic=1 tail") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mem", first.param);
    try std.testing.expectEqualStrings("+010M", first.value.?);
    try std.testing.expectEqualStrings("flags=quiet,debug\x00panic=1 tail", first.remaining);
    try expectMemparse(first.value.?, 8 << 20, "");

    const second = cmdline.next_arg(first.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("flags", second.param);
    try std.testing.expectEqualStrings("quiet,debug\x00panic=1", second.value.?);
    try std.testing.expectEqualStrings("tail", second.remaining);
    try std.testing.expect(cmdline.parse_option_str(second.value.?, "debug"));
    try std.testing.expect(!cmdline.parse_option_str(second.value.?, "panic"));

    const third = cmdline.next_arg(second.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("tail", third.param);
    try std.testing.expect(third.value == null);
    try std.testing.expectEqualStrings("", third.remaining);
}
