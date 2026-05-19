const std = @import("std");
const cmdline = @import("cmdline");

test "phase 7 cmdline companion replays bare-option and integer option boundaries" {
    try std.testing.expect(cmdline.parseOptionStr("console,panic", "console"));
    try std.testing.expect(!cmdline.parseOptionStr("console=ttyS0,panic", "console"));
    try std.testing.expect(cmdline.parse_option_str("panic,quiet", "quiet"));

    var option_rest: []const u8 = "7,tail";
    var option_value: i32 = 0;
    try std.testing.expectEqual(@as(u8, 2), cmdline.getOption(&option_rest, &option_value));
    try std.testing.expectEqual(@as(i32, 7), option_value);
    try std.testing.expectEqualStrings("tail", option_rest);

    var values = [_]i32{ 0, 0, 0, 0, 0 };
    const list_rest = cmdline.getOptions("1-3,8", values.len, &values);
    try std.testing.expectEqualStrings("", list_rest);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 1, 2, 3, 8 }, &values);
}

test "phase 7 cmdline companion replays nextArg borrowed-slice boundaries" {
    const pair = cmdline.nextArg("mode=\"safe boot\" root=/dev/vda");
    try std.testing.expectEqualStrings("mode", pair.param);
    try std.testing.expectEqualStrings("safe boot", pair.value.?);
    try std.testing.expectEqualStrings("root=/dev/vda", pair.rest);
    try std.testing.expectEqualStrings("root=/dev/vda", pair.remaining);

    const leading_equals = cmdline.next_arg("=value trailing");
    try std.testing.expectEqualStrings("=value", leading_equals.param);
    try std.testing.expect(leading_equals.value == null);
    try std.testing.expectEqualStrings("trailing", leading_equals.rest);

    const nul_bounded = [_]u8{ 'k', 'e', 'y', '=', 'v', 'a', 'l', 0, ' ', 'x' };
    const bounded = cmdline.nextArg(&nul_bounded);
    try std.testing.expectEqualStrings("key", bounded.param);
    try std.testing.expectEqualStrings("val", bounded.value.?);
    try std.testing.expectEqualStrings("", bounded.rest);
}

test "phase 7 cmdline companion replays memparse suffix and unchanged-rest behavior" {
    const mebibytes = cmdline.memparse("64M tail");
    try std.testing.expectEqual(@as(u64, 64) << 20, mebibytes.value);
    try std.testing.expectEqualStrings(" tail", mebibytes.rest);

    const negative = cmdline.memparse("-2K extra");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative.value);
    try std.testing.expectEqualStrings(" extra", negative.rest);

    const unchanged = cmdline.memparse("oops");
    try std.testing.expectEqual(@as(u64, 0), unchanged.value);
    try std.testing.expectEqualStrings("oops", unchanged.rest);
}
