const std = @import("std");
const cmdline = @import("cmdline");

test "parseOptionStr stops matching after first NUL terminator" {
    const optionstr = "quiet,debug\x00nohlt,panic";

    try std.testing.expect(cmdline.parseOptionStr(optionstr, "quiet"));
    try std.testing.expect(cmdline.parseOptionStr(optionstr, "debug"));
    try std.testing.expect(!cmdline.parseOptionStr(optionstr, "nohlt"));
    try std.testing.expect(!cmdline.parseOptionStr(optionstr, "panic"));
}

test "parseOptionStr treats comma-bounded empty entries as empty option matches" {
    try std.testing.expect(cmdline.parseOptionStr(",debug", ""));
    try std.testing.expect(cmdline.parseOptionStr("debug,,quiet", ""));

    try std.testing.expect(!cmdline.parseOptionStr("debug,", ""));
    try std.testing.expect(!cmdline.parseOptionStr("debug,\x00quiet", ""));
    try std.testing.expect(!cmdline.parseOptionStr("debug\x00", ""));
    try std.testing.expect(!cmdline.parseOptionStr("", ""));
}

test "parse_option_str alias preserves exact option boundaries" {
    try std.testing.expect(cmdline.parse_option_str("ro,root=/dev/sda1,quiet", "ro"));
    try std.testing.expect(cmdline.parse_option_str("ro,root=/dev/sda1,quiet", "quiet"));

    try std.testing.expect(!cmdline.parse_option_str("ro,root=/dev/sda1,quiet", "root"));
    try std.testing.expect(!cmdline.parse_option_str("ro,root=/dev/sda1,quiet", "roo"));
    try std.testing.expect(!cmdline.parse_option_str("ro,root=/dev/sda1,quiet", "quietly"));
}
