const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn freeLegacyArgv(allocator: std.mem.Allocator, argv: [][]u8) void {
    for (argv) |arg| {
        allocator.free(arg);
    }
    allocator.free(argv);
}

fn expectArgvCursorAndCtypeMasks() !void {
    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        var result = try argv_split.argvSplit(std.testing.allocator, "Aa0 _- 0xFf mask");
        defer result.deinit();

        try expectTokenShape(result.argv);
    } else {
        const argv = try argv_split.argvSplit(std.testing.allocator, "Aa0 _- 0xFf mask");
        defer freeLegacyArgv(std.testing.allocator, argv);

        try expectTokenShape(argv);
    }
}

fn expectTokenShape(argv: []const []const u8) !void {
    try std.testing.expectEqual(@as(usize, 4), argv.len);
    try std.testing.expectEqualStrings("Aa0", argv[0]);
    try std.testing.expectEqualStrings("_-", argv[1]);
    try std.testing.expectEqualStrings("0xFf", argv[2]);
    try std.testing.expectEqualStrings("mask", argv[3]);

    var token_mask: u32 = 0;
    var xdigit_mask: u32 = 0;
    for (argv, 0..) |token, token_idx| {
        var has_alnum = false;
        var all_xdigit = token.len != 0;
        for (token) |byte| {
            has_alnum = has_alnum or ctype.isalnum(byte);
            all_xdigit = all_xdigit and ctype.isxdigit(byte);
        }
        if (has_alnum) token_mask |= @as(u32, 1) << @intCast(token_idx);
        if (all_xdigit) xdigit_mask |= @as(u32, 1) << @intCast(token_idx);
    }

    try std.testing.expectEqual(@as(u32, 0b1101), token_mask);
    try std.testing.expectEqual(@as(u32, 0b0001), xdigit_mask);
    try std.testing.expect(ctype.ispunct(argv[1][0]));
    try std.testing.expect(ctype.ispunct(argv[1][1]));
    try std.testing.expectEqual(@as(u8, 'f'), ctype.fastTolower(argv[2][2]));
    try std.testing.expectEqual(@as(u8, 'F'), ctype.toupper(argv[2][3]));

    const four_token_window: u32 = 0b1111;
    try std.testing.expectEqual(@as(u32, 3), hweight.swHweight8(token_mask));
    try std.testing.expectEqual(
        @as(u32, 4),
        hweight.swHweight8(token_mask) + hweight.swHweight8((~token_mask) & four_token_window),
    );
    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight16(xdigit_mask));
    if (@hasDecl(hweight, "__sw_hweight8")) {
        try std.testing.expectEqual(hweight.swHweight8(token_mask), hweight.__sw_hweight8(token_mask));
    }
}

test "argv tokens drive ctype classification and hweight complements" {
    try expectArgvCursorAndCtypeMasks();
}

test "cmdline cursors preserve remaining text while numeric complements stay bounded" {
    const options = "alpha,beta,gamma\x00ignored";
    try std.testing.expect(cmdline.parseOptionStr(options, "beta"));
    try std.testing.expect(!cmdline.parseOptionStr(options, "ignored"));

    const parsed = cmdline.memparse("0xffK rest");
    try std.testing.expectEqual(@as(u64, 0xff << 10), parsed.value);
    try std.testing.expectEqualStrings(" rest", parsed.rest);

    const low_bits: u32 = @intCast(parsed.value & 0xffff);
    try std.testing.expectEqual(
        @as(u32, 16),
        hweight.swHweight16(low_bits) + hweight.swHweight16((~low_bits) & 0xffff),
    );
    if (@hasDecl(hweight, "__sw_hweight16")) {
        try std.testing.expectEqual(hweight.swHweight16(low_bits), hweight.__sw_hweight16(low_bits));
    }

    if (@hasDecl(cmdline, "nextArg")) {
        const first = cmdline.nextArg("mode=fast root=\"/dev/sda1 quiet\" tail") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("mode", first.param);
        try std.testing.expectEqualStrings("fast", first.value.?);
        try std.testing.expectEqualStrings("root=\"/dev/sda1 quiet\" tail", first.remaining);

        const second = cmdline.nextArg(first.remaining) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("root", second.param);
        try std.testing.expectEqualStrings("/dev/sda1 quiet", second.value.?);
        try std.testing.expectEqualStrings("tail", second.remaining);

        const final = cmdline.nextArg(second.remaining) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("tail", final.param);
        try std.testing.expect(final.value == null);
        try std.testing.expectEqualStrings("", final.remaining);
    }
}
