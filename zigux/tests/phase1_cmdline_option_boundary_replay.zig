const std = @import("std");
const cmdline = @import("cmdline");

test "phase1 cmdline parseOptionStr stops cleanly at NUL boundaries" {
    const bootargs = "quiet,debug,\x00panic,trace";

    try std.testing.expect(cmdline.parseOptionStr(bootargs, "quiet"));
    try std.testing.expect(cmdline.parseOptionStr(bootargs, "debug"));
    try std.testing.expect(!cmdline.parseOptionStr(bootargs, ""));
    try std.testing.expect(!cmdline.parseOptionStr(bootargs, "panic"));
    try std.testing.expect(!cmdline.parseOptionStr(bootargs, "trace"));
}

test "phase1 cmdline parseOptionStr keeps empty entries limited to comma slots" {
    const optionstr = ",rootwait,,audit=1,";

    try std.testing.expect(cmdline.parseOptionStr(optionstr, ""));
    try std.testing.expect(cmdline.parseOptionStr(optionstr, "rootwait"));
    try std.testing.expect(!cmdline.parseOptionStr(optionstr, "audit"));
    try std.testing.expect(!cmdline.parseOptionStr(optionstr, "audit=1,"));
    try std.testing.expect(cmdline.parse_option_str(optionstr, "rootwait"));
}

test "phase1 cmdline nextArg keeps comma-rich values aligned with later bare flags" {
    const first = cmdline.nextArg("console=ttyS0,115200n8 rootwait debug") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("console", first.param);
    try std.testing.expectEqualStrings("ttyS0,115200n8", first.value.?);
    try std.testing.expectEqualStrings("rootwait debug", first.remaining);

    const second = cmdline.nextArg(first.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("rootwait", second.param);
    try std.testing.expect(second.value == null);
    try std.testing.expectEqualStrings("debug", second.remaining);

    const third = cmdline.nextArg(second.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("debug", third.param);
    try std.testing.expect(third.value == null);
    try std.testing.expectEqualStrings("", third.remaining);
}
