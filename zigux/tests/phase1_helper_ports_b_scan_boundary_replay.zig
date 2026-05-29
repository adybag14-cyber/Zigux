const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

test "phase1 helper ports B scan boundaries stay aligned" {
    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        var argv = try argv_split.argvSplit(std.testing.allocator, " \talpha=1 beta,gamma\n0x2Ktail  ");
        defer argv.deinit();

        try std.testing.expectEqual(@as(usize, 3), argv.argc());
        try std.testing.expectEqualStrings("alpha=1", argv.argv[0]);
        try std.testing.expectEqualStrings("beta,gamma", argv.argv[1]);
        try std.testing.expectEqualStrings("0x2Ktail", argv.argv[2]);
    } else {
        const argv = try argv_split.argvSplit(std.testing.allocator, " \talpha=1 beta,gamma\n0x2Ktail  ");
        defer argv_split.argvFree(std.testing.allocator, argv);

        try std.testing.expectEqual(@as(usize, 3), argv.len);
        try std.testing.expectEqualStrings("alpha=1", argv[0]);
        try std.testing.expectEqualStrings("beta,gamma", argv[1]);
        try std.testing.expectEqualStrings("0x2Ktail", argv[2]);
    }

    try std.testing.expect(cmdline.parseOptionStr("alpha,beta,gamma", "beta"));
    try std.testing.expect(!cmdline.parseOptionStr("alpha,beta=1,gamma", "beta"));

    if (@hasDecl(cmdline, "nextArg")) {
        const parsed = cmdline.nextArg("beta=\"two words\" 0x2Ktail") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("beta", parsed.param);
        try std.testing.expectEqualStrings("two words", parsed.value.?);
        try std.testing.expectEqualStrings("0x2Ktail", parsed.remaining);
    }

    const parsed_size = cmdline.memparse("0x2Ktail");
    try std.testing.expectEqual(@as(u64, 2 << 10), parsed_size.value);
    try std.testing.expectEqualStrings("tail", parsed_size.rest);

    try std.testing.expect(ctype.isprint(' '));
    try std.testing.expect(!ctype.isgraph(' '));
    try std.testing.expect(ctype.isgraph('~'));
    try std.testing.expect(!ctype.isprint('\t'));
    try std.testing.expectEqual(ctype._S | ctype._SP, ctype.mask(' '));

    const bits32: u32 = 0x1357_2468;
    try std.testing.expectEqual(@as(u32, 32), hweight.swHweight32(bits32) + hweight.swHweight32(~bits32));

    const bits64: u64 = 0x1357_2468_ffff_0000;
    try std.testing.expectEqual(@as(u64, 64), hweight.swHweight64(bits64) + hweight.swHweight64(~bits64));

    if (@hasDecl(hweight, "__sw_hweight32")) {
        try std.testing.expectEqual(hweight.swHweight32(bits32), hweight.__sw_hweight32(bits32));
        try std.testing.expectEqual(hweight.swHweight64(bits64), hweight.__sw_hweight64(bits64));
    }
}
