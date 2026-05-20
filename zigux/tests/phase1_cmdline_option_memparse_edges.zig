const std = @import("std");
const cmdline = @import("cmdline");

test "phase1 cmdline option edges keep exact bare matches visible" {
    try std.testing.expect(cmdline.parseOptionStr("quiet,debug,nohlt", "debug"));
    try std.testing.expect(cmdline.parse_option_str("quiet,debug,nohlt", "quiet"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug=1,nohlt", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug\x00,nohlt", "nohlt"));
    try std.testing.expect(cmdline.parseOptionStr(",debug", ""));
    try std.testing.expect(cmdline.parseOptionStr("debug,,quiet", ""));
    try std.testing.expect(!cmdline.parseOptionStr("debug,", ""));
}

test "phase1 cmdline memparse edges keep signed and saturated boundaries reviewable" {
    const negative_hex = cmdline.memparse("-0x2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative_hex.value);
    try std.testing.expectEqualStrings("tail", negative_hex.rest);

    const positive_octal = cmdline.memparse("+010Mmore");
    try std.testing.expectEqual(@as(u64, 8 << 20), positive_octal.value);
    try std.testing.expectEqualStrings("more", positive_octal.rest);

    const invalid_signed = cmdline.memparse("-xyz");
    try std.testing.expectEqual(@as(u64, 0), invalid_signed.value);
    try std.testing.expectEqualStrings("-xyz", invalid_signed.rest);

    const saturated = cmdline.memparse("9223372036854775808");
    try std.testing.expectEqual(@as(u64, std.math.maxInt(i64)), saturated.value);
    try std.testing.expectEqualStrings("", saturated.rest);
}
