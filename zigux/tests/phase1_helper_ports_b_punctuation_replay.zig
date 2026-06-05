const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn optionPunctuationMask(options: []const u8) u32 {
    var mask: u32 = 0;
    for (options, 0..) |byte, idx| {
        if (ctype.ispunct(byte)) {
            mask |= @as(u32, 1) << @intCast(idx);
        }
    }
    return mask;
}

test "punctuation tokens stay whole while comma option parsing remains narrow" {
    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        var result = try argv_split.argvSplit(std.testing.allocator, "alpha:beta quiet;debug nohlt,trace");
        defer result.deinit();

        try std.testing.expectEqual(@as(usize, 3), result.argc());
        try std.testing.expectEqualStrings("alpha:beta", result.argv[0]);
        try std.testing.expectEqualStrings("quiet;debug", result.argv[1]);
        try std.testing.expectEqualStrings("nohlt,trace", result.argv[2]);

        try std.testing.expect(!cmdline.parseOptionStr(result.argv[1], "quiet"));
        try std.testing.expect(!cmdline.parseOptionStr(result.argv[1], "debug"));
        try std.testing.expect(cmdline.parseOptionStr(result.argv[2], "nohlt"));
        try std.testing.expect(cmdline.parseOptionStr(result.argv[2], "trace"));
    } else {
        const argv = try argv_split.argvSplit(std.testing.allocator, "alpha:beta quiet;debug nohlt,trace");
        defer argv_split.argvFree(std.testing.allocator, argv);

        try std.testing.expectEqual(@as(usize, 3), argv.len);
        try std.testing.expectEqualStrings("alpha:beta", argv[0]);
        try std.testing.expectEqualStrings("quiet;debug", argv[1]);
        try std.testing.expectEqualStrings("nohlt,trace", argv[2]);

        try std.testing.expect(!cmdline.parseOptionStr(argv[1], "quiet"));
        try std.testing.expect(!cmdline.parseOptionStr(argv[1], "debug"));
        try std.testing.expect(cmdline.parseOptionStr(argv[2], "nohlt"));
        try std.testing.expect(cmdline.parseOptionStr(argv[2], "trace"));
    }
}

test "ctype punctuation masks agree with hweight over option bytes" {
    const options = "debug;trace,quiet:boot";
    const mask = optionPunctuationMask(options);

    try std.testing.expect(ctype.ispunct(';'));
    try std.testing.expect(ctype.ispunct(','));
    try std.testing.expect(ctype.ispunct(':'));
    try std.testing.expect(ctype.isgraph(';'));
    try std.testing.expect(ctype.isgraph(','));
    try std.testing.expect(ctype.isgraph(':'));
    try std.testing.expect(!ctype.isspace(';'));
    try std.testing.expect(!ctype.isspace(','));
    try std.testing.expect(!ctype.isspace(':'));

    try std.testing.expectEqual(@as(u32, 3), hweight.swHweight32(mask));
    if (@hasDecl(hweight, "__sw_hweight32")) {
        try std.testing.expectEqual(hweight.swHweight32(mask), hweight.__sw_hweight32(mask));
    }
    try std.testing.expectEqual(@as(u32, 3), @popCount(mask));
    try std.testing.expect(cmdline.parseOptionStr("debug;trace,quiet:boot,final", "final"));
    try std.testing.expect(!cmdline.parseOptionStr(options, "debug"));
    try std.testing.expect(!cmdline.parseOptionStr(options, "trace"));
    try std.testing.expect(!cmdline.parseOptionStr(options, "quiet"));
    try std.testing.expect(!cmdline.parseOptionStr(options, "boot"));
}

test "cmdline nextArg preserves punctuation value boundaries" {
    if (!@hasDecl(cmdline, "nextArg")) {
        return;
    }

    const parsed = cmdline.nextArg("root=/dev/sda1:ro debug;trace=on tail") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("root", parsed.param);
    try std.testing.expectEqualStrings("/dev/sda1:ro", parsed.value.?);
    try std.testing.expectEqualStrings("debug;trace=on tail", parsed.remaining);

    const second = cmdline.nextArg(parsed.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("debug;trace", second.param);
    try std.testing.expectEqualStrings("on", second.value.?);
    try std.testing.expectEqualStrings("tail", second.remaining);
}
