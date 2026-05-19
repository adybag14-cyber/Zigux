const std = @import("std");
const cmdline = @import("cmdline");

test "phase 7 cmdline companion replays exact bare-option matching boundaries" {
    try std.testing.expect(cmdline.parseOptionStr("quiet,debug,nohlt", "debug"));
    try std.testing.expect(cmdline.parse_option_str("quiet,debug,nohlt", "quiet"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug=1,nohlt", "debug"));
    try std.testing.expect(cmdline.parseOptionStr(",debug", ""));
    try std.testing.expect(!cmdline.parseOptionStr("", ""));
}

test "phase 7 cmdline companion replays option decoding, ranges, and malformed-input posture" {
    var option_rest: []const u8 = "3-5";
    var option_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 3), cmdline.getOption(&option_rest, &option_value));
    try std.testing.expectEqual(@as(i32, 3), option_value);
    try std.testing.expectEqualStrings("-5", option_rest);

    var values = [_]i32{ 0, 0, 0, 0, 0 };
    const rest = cmdline.getOptions("3-5,8", values.len, &values);
    try std.testing.expectEqualStrings("", rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 3, 4, 5, 8 }, &values);

    var malformed_negative: []const u8 = "-x";
    var malformed_negative_value: i32 = 99;
    try std.testing.expectEqual(@as(u8, 0), cmdline.getOption(&malformed_negative, &malformed_negative_value));
    try std.testing.expectEqual(@as(i32, 0), malformed_negative_value);
    try std.testing.expectEqualStrings("x", malformed_negative);
}

test "phase 7 cmdline companion replays quoted argument splitting and memparse boundaries" {
    const parsed = cmdline.nextArg("console=ttyS0,115200 root=\"/dev/sda1 quiet\" panic=-1");
    try std.testing.expectEqualStrings("console", parsed.param);
    try std.testing.expectEqualStrings("ttyS0,115200", parsed.value.?);
    try std.testing.expectEqualStrings("root=\"/dev/sda1 quiet\" panic=-1", parsed.remaining);

    const second = cmdline.next_arg(parsed.remaining);
    try std.testing.expectEqualStrings("root", second.param);
    try std.testing.expectEqualStrings("/dev/sda1 quiet", second.value.?);
    try std.testing.expectEqualStrings("panic=-1", second.remaining);

    const negative = cmdline.memparse("-2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative.value);
    try std.testing.expectEqualStrings("tail", negative.rest);

    const no_conversion = cmdline.memparse("+nope");
    try std.testing.expectEqual(@as(u64, 0), no_conversion.value);
    try std.testing.expectEqualStrings("+nope", no_conversion.rest);
}

test "phase 7 cmdline companion replays leading-whitespace sentinels and quoted full-token boundaries" {
    const leading = cmdline.nextArg(" \tmode=fast");
    try std.testing.expectEqualStrings("", leading.param);
    try std.testing.expect(leading.value == null);
    try std.testing.expectEqualStrings("mode=fast", leading.rest);
    try std.testing.expectEqualStrings("mode=fast", leading.remaining);

    const quoted = cmdline.next_arg("\"mode=fast path\" tail");
    try std.testing.expectEqualStrings("mode", quoted.param);
    try std.testing.expectEqualStrings("fast path", quoted.value.?);
    try std.testing.expectEqualStrings("tail", quoted.remaining);

    const nul_bounded = cmdline.nextArg("console=ttyS0\x00 root=/dev/vda");
    try std.testing.expectEqualStrings("console", nul_bounded.param);
    try std.testing.expectEqualStrings("ttyS0", nul_bounded.value.?);
    try std.testing.expectEqualStrings("", nul_bounded.remaining);
}
