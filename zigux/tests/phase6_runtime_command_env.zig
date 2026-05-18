const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const string_helpers = @import("string_helpers");

test "phase6 command line parsing keeps bounded key value iteration stable" {
    const first = cmdline.nextArg("log_buf_len=1M root=/dev/vda1 init=\"/bin/sh -l\"") orelse {
        return error.TestUnexpectedResult;
    };
    try std.testing.expectEqualStrings("log_buf_len", first.param);
    try std.testing.expectEqualStrings("1M", first.value.?);
    try std.testing.expectEqualStrings("root=/dev/vda1 init=\"/bin/sh -l\"", first.remaining);

    const second = cmdline.nextArg(first.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", second.param);
    try std.testing.expectEqualStrings("/dev/vda1", second.value.?);

    const third = cmdline.next_arg(second.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("init", third.param);
    try std.testing.expectEqualStrings("/bin/sh -l", third.value.?);
    try std.testing.expectEqualStrings("", third.remaining);
}

test "phase6 argv split keeps environment assignments c-argv ready" {
    var split = try argv_split.argvSplit(
        std.testing.allocator,
        "PATH=/usr/bin HOME=/root TERM=xterm-256color",
    );
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 3), argv_split.countArgc("PATH=/usr/bin HOME=/root TERM=xterm-256color"));
    try std.testing.expectEqual(@as(usize, 3), split.argv.len);
    try std.testing.expectEqualStrings("PATH=/usr/bin", split.argv[0]);
    try std.testing.expectEqualStrings("HOME=/root", split.argv[1]);
    try std.testing.expectEqualStrings("TERM=xterm-256color", std.mem.span(split.cArgv()[2].?));
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[split.argv.len]);
}

test "phase6 quotable cmdline export normalizes embedded separators for logs" {
    const raw = [_]u8{ 'z', 'i', 'g', 0, 't', 'e', 's', 't', '\n', '"', 0, 0 };
    const quoted = (try string_helpers.kstrdupQuotableCmdline(std.testing.allocator, &raw)).?;
    defer std.testing.allocator.free(quoted);

    try std.testing.expectEqualStrings("zig test\\x0A\\x22", quoted);
}
