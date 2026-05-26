const std = @import("std");
const cmdline = @import("cmdline");

test "phase1 cmdline invalid-window replay keeps blank and empty quoted tokens aligned" {
    try std.testing.expect(cmdline.nextArg(" \t \n") == null);

    const empty_quoted = cmdline.nextArg("\"\" tail") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("", empty_quoted.param);
    try std.testing.expect(empty_quoted.value == null);
    try std.testing.expectEqualStrings("tail", empty_quoted.remaining);

    const bare_quoted = cmdline.next_arg("\"quiet mode\" next") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("quiet mode", bare_quoted.param);
    try std.testing.expect(bare_quoted.value == null);
    try std.testing.expectEqualStrings("next", bare_quoted.remaining);
}

test "phase1 cmdline invalid-window replay keeps invalid signed prefixes on the original rest" {
    const negative_prefix_only = cmdline.memparse("-0x tail");
    try std.testing.expectEqual(@as(u64, 0), negative_prefix_only.value);
    try std.testing.expectEqualStrings("-0x tail", negative_prefix_only.rest);

    const positive_prefix_only = cmdline.memparse("+0X tail");
    try std.testing.expectEqual(@as(u64, 0), positive_prefix_only.value);
    try std.testing.expectEqualStrings("+0X tail", positive_prefix_only.rest);

    const sign_only = cmdline.memparse("+");
    try std.testing.expectEqual(@as(u64, 0), sign_only.value);
    try std.testing.expectEqualStrings("+", sign_only.rest);
}

test "phase1 cmdline invalid-window replay keeps empty entries and NUL stops explicit" {
    try std.testing.expect(cmdline.parseOptionStr(",\x00tail", ""));
    try std.testing.expect(!cmdline.parseOptionStr("debug,\x00tail", ""));
    try std.testing.expect(cmdline.parseOptionStr("debug,,\x00tail", ""));
    try std.testing.expect(!cmdline.parse_option_str("debug\x00tail", "tail"));
}
