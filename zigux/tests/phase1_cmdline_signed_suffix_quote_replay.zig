const std = @import("std");
const cmdline = @import("cmdline");

test "phase1 cmdline signed suffix and bare option markers stay aligned" {
    const negative_hex = cmdline.memparse("-0x2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative_hex.value);
    try std.testing.expectEqualStrings("tail", negative_hex.rest);

    const positive_octal = cmdline.memparse("+010Mmore");
    try std.testing.expectEqual(@as(u64, 8 << 20), positive_octal.value);
    try std.testing.expectEqualStrings("more", positive_octal.rest);

    const invalid_positive = cmdline.memparse("+nope");
    try std.testing.expectEqual(@as(u64, 0), invalid_positive.value);
    try std.testing.expectEqualStrings("+nope", invalid_positive.rest);

    try std.testing.expect(cmdline.parseOptionStr("quiet,debug\x00,nohlt", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug=1,nohlt", "debug"));
    try std.testing.expect(cmdline.parseOptionStr("debug,,quiet", ""));
    try std.testing.expect(!cmdline.parseOptionStr("debug,", ""));
}

test "phase1 cmdline quoted argument boundaries stay aligned" {
    const quoted = cmdline.nextArg("\"mode=fast path\" tail") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", quoted.param);
    try std.testing.expectEqualStrings("fast path", quoted.value.?);
    try std.testing.expectEqualStrings("tail", quoted.remaining);

    const empty_value = cmdline.nextArg("root=\"\" quiet") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", empty_value.param);
    try std.testing.expectEqualStrings("", empty_value.value.?);
    try std.testing.expectEqualStrings("quiet", empty_value.remaining);

    const unterminated = cmdline.nextArg("mode=\"fast boot") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", unterminated.param);
    try std.testing.expectEqualStrings("fast boot", unterminated.value.?);
    try std.testing.expectEqualStrings("", unterminated.remaining);
}
