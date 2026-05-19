const std = @import("std");
const cmdline = @import("cmdline");

test "phase1 cmdline alias edges keep alias exports wired to current helpers" {
    try std.testing.expectEqual(@TypeOf(cmdline.parseOptionStr), @TypeOf(cmdline.parse_option_str));
    try std.testing.expectEqual(@TypeOf(cmdline.nextArg), @TypeOf(cmdline.next_arg));
}

test "phase1 cmdline alias edges preserve exact bare-option matching" {
    try std.testing.expect(cmdline.parse_option_str("quiet,debug,\x00still-hidden", "debug"));
    try std.testing.expect(cmdline.parse_option_str(",debug", ""));
    try std.testing.expect(!cmdline.parse_option_str("quiet,debug=1", "debug"));
    try std.testing.expect(!cmdline.parse_option_str("quiet,\x00still-hidden", "still-hidden"));
}

test "phase1 cmdline alias edges keep quoted and keyed parsing aligned" {
    const keyed = cmdline.next_arg("console=ttyS0,115200 root=\"/dev/sda1 quiet\"") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("console", keyed.param);
    try std.testing.expectEqualStrings("ttyS0,115200", keyed.value.?);
    try std.testing.expectEqualStrings("root=\"/dev/sda1 quiet\"", keyed.remaining);

    const quoted = cmdline.next_arg("\"mode=fast path\" tail") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", quoted.param);
    try std.testing.expectEqualStrings("fast path", quoted.value.?);
    try std.testing.expectEqualStrings("tail", quoted.remaining);
}

test "phase1 cmdline alias edges preserve signed memparse suffix behavior" {
    const negative = cmdline.memparse("-0x2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative.value);
    try std.testing.expectEqualStrings("tail", negative.rest);

    const positive = cmdline.memparse("+010Mmore");
    try std.testing.expectEqual(@as(u64, 8 << 20), positive.value);
    try std.testing.expectEqualStrings("more", positive.rest);
}
