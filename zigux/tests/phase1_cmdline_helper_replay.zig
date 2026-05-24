const std = @import("std");
const cmdline = @import("cmdline");

test "phase1 cmdline replay keeps signed memparse boundaries aligned" {
    const negative_hex = cmdline.memparse("-0x2K tail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative_hex.value);
    try std.testing.expectEqualStrings(" tail", negative_hex.rest);

    const positive_octal = cmdline.memparse("+010M rest");
    try std.testing.expectEqual(@as(u64, 8 << 20), positive_octal.value);
    try std.testing.expectEqualStrings(" rest", positive_octal.rest);

    const saturated = cmdline.memparse("+9223372036854775808");
    try std.testing.expectEqual(@as(u64, @intCast(std.math.maxInt(i64))), saturated.value);
    try std.testing.expectEqualStrings("", saturated.rest);
}

test "phase1 cmdline replay keeps exact bare-option parsing aligned" {
    try std.testing.expect(cmdline.parseOptionStr("rootwait,quiet", "quiet"));
    try std.testing.expect(cmdline.parseOptionStr(",quiet", ""));
    try std.testing.expect(cmdline.parseOptionStr("rootwait,,quiet", ""));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,", ""));
    try std.testing.expect(!cmdline.parseOptionStr("rootwait,quiet=1", "quiet"));
    try std.testing.expect(cmdline.parse_option_str("rootwait,quiet", "rootwait"));
}

test "phase1 cmdline replay keeps quoted nextArg sequencing aligned" {
    const keyed = cmdline.nextArg("console=ttyS0,115200 root=\"/dev/sda1 quiet\" panic=-1") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("console", keyed.param);
    try std.testing.expectEqualStrings("ttyS0,115200", keyed.value.?);
    try std.testing.expectEqualStrings("root=\"/dev/sda1 quiet\" panic=-1", keyed.remaining);

    const quoted_pair = cmdline.nextArg(keyed.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", quoted_pair.param);
    try std.testing.expectEqualStrings("/dev/sda1 quiet", quoted_pair.value.?);
    try std.testing.expectEqualStrings("panic=-1", quoted_pair.remaining);

    const quoted_token = cmdline.next_arg("\"mode=fast path\" tail") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", quoted_token.param);
    try std.testing.expectEqualStrings("fast path", quoted_token.value.?);
    try std.testing.expectEqualStrings("tail", quoted_token.remaining);

    const empty_value = cmdline.nextArg("root=\"\" quiet") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", empty_value.param);
    try std.testing.expectEqualStrings("", empty_value.value.?);
    try std.testing.expectEqualStrings("quiet", empty_value.remaining);

    const unterminated = cmdline.nextArg("mode=\"fast boot") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", unterminated.param);
    try std.testing.expectEqualStrings("fast boot", unterminated.value.?);
    try std.testing.expectEqualStrings("", unterminated.remaining);
}
