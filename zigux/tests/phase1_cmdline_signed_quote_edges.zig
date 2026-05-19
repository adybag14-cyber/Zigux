const std = @import("std");
const cmdline = @import("cmdline");

test "phase1 cmdline signed memparse edges stay aligned across bases and invalid signs" {
    const negative_hex = cmdline.memparse("-0x2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative_hex.value);
    try std.testing.expectEqualStrings("tail", negative_hex.rest);

    const positive_octal = cmdline.memparse("+010Mmore");
    try std.testing.expectEqual(@as(u64, 8 << 20), positive_octal.value);
    try std.testing.expectEqualStrings("more", positive_octal.rest);

    const invalid_negative = cmdline.memparse("-xyz");
    try std.testing.expectEqual(@as(u64, 0), invalid_negative.value);
    try std.testing.expectEqualStrings("-xyz", invalid_negative.rest);

    const invalid_positive = cmdline.memparse("+nope");
    try std.testing.expectEqual(@as(u64, 0), invalid_positive.value);
    try std.testing.expectEqualStrings("+nope", invalid_positive.rest);
}

test "phase1 cmdline quoted value edges keep empty and unterminated windows intact" {
    const empty = cmdline.nextArg("root=\"\" quiet") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", empty.param);
    try std.testing.expectEqualStrings("", empty.value.?);
    try std.testing.expectEqualStrings("quiet", empty.remaining);

    const unterminated = cmdline.nextArg("mode=\"fast boot") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", unterminated.param);
    try std.testing.expectEqualStrings("fast boot", unterminated.value.?);
    try std.testing.expectEqualStrings("", unterminated.remaining);

    const full_token = cmdline.next_arg("\"mode=fast path\" tail") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", full_token.param);
    try std.testing.expectEqualStrings("fast path", full_token.value.?);
    try std.testing.expectEqualStrings("tail", full_token.remaining);
}

test "phase1 cmdline delimiter edges keep empty option windows exact" {
    try std.testing.expect(cmdline.parseOptionStr(",debug", ""));
    try std.testing.expect(cmdline.parseOptionStr("debug,,quiet", ""));
    try std.testing.expect(!cmdline.parseOptionStr("debug,", ""));
    try std.testing.expect(!cmdline.parseOptionStr("", ""));

    try std.testing.expect(cmdline.parse_option_str("quiet,debug,nohlt", "quiet"));
    try std.testing.expect(cmdline.parseOptionStr("quiet,debug\x00,nohlt", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug=1,nohlt", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug\x00,nohlt", "nohlt"));
}
