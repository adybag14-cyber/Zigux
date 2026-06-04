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

fn expectNulTailTokenShape(argv: []const []const u8) !void {
    try std.testing.expectEqual(@as(usize, 3), argv.len);
    try std.testing.expectEqualStrings("alpha\x00late", argv[0]);
    try std.testing.expectEqualStrings("mask=0x0f", argv[1]);
    try std.testing.expectEqualStrings("8K\x00tail", argv[2]);

    var nul_token_mask: u32 = 0;
    var digit_head_mask: u32 = 0;
    var punctuation_mask: u32 = 0;
    for (argv, 0..) |token, token_idx| {
        if (token.len != 0 and ctype.isdigit(token[0])) {
            digit_head_mask |= @as(u32, 1) << @intCast(token_idx);
        }
        for (token) |byte| {
            if (byte == 0) {
                nul_token_mask |= @as(u32, 1) << @intCast(token_idx);
            }
            if (ctype.ispunct(byte)) {
                punctuation_mask |= @as(u32, 1) << @intCast(token_idx);
            }
        }
    }

    try std.testing.expect(ctype.iscntrl(0));
    try std.testing.expect(!ctype.isspace(0));
    try std.testing.expect(ctype.isxdigit('8'));
    try std.testing.expectEqual(@as(u32, 0b101), nul_token_mask);
    try std.testing.expectEqual(@as(u32, 0b100), digit_head_mask);
    try std.testing.expectEqual(@as(u32, 0b010), punctuation_mask);
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight8(nul_token_mask));
    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight8(digit_head_mask));
    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight16(punctuation_mask));
    if (@hasDecl(hweight, "__sw_hweight8")) {
        try std.testing.expectEqual(hweight.swHweight8(nul_token_mask), hweight.__sw_hweight8(nul_token_mask));
    }
}

test "argv embedded nul tokens feed ctype and hweight tail masks" {
    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        var result = try argv_split.argvSplit(std.testing.allocator, " alpha\x00late mask=0x0f 8K\x00tail ");
        defer result.deinit();

        try expectNulTailTokenShape(result.argv);
    } else {
        const argv = try argv_split.argvSplit(std.testing.allocator, " alpha\x00late mask=0x0f 8K\x00tail ");
        defer freeLegacyArgv(std.testing.allocator, argv);

        try expectNulTailTokenShape(argv);
    }
}

test "cmdline nul fences and suffix tails align with ctype masks" {
    const options = "early,mask\x00late,debug";
    try std.testing.expect(cmdline.parseOptionStr(options, "early"));
    try std.testing.expect(cmdline.parseOptionStr(options, "mask"));
    try std.testing.expect(!cmdline.parseOptionStr(options, "late"));
    try std.testing.expect(!cmdline.parseOptionStr(options, "debug"));

    const parsed = cmdline.memparse("8K\x00tail");
    try std.testing.expectEqual(@as(u64, 8 << 10), parsed.value);
    try std.testing.expectEqualStrings("\x00tail", parsed.rest);
    try std.testing.expect(ctype.iscntrl(parsed.rest[0]));
    try std.testing.expect(ctype.islower(parsed.rest[1]));

    var tail_mask: u32 = 0;
    for (parsed.rest, 0..) |byte, idx| {
        if (ctype.iscntrl(byte) or ctype.islower(byte)) {
            tail_mask |= @as(u32, 1) << @intCast(idx);
        }
    }
    try std.testing.expectEqual(@as(u32, 0b1_1111), tail_mask);
    try std.testing.expectEqual(@as(u32, 5), hweight.swHweight16(tail_mask));

    if (@hasDecl(cmdline, "nextArg")) {
        const next = cmdline.nextArg("boot=ok\x00hidden tail") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("boot", next.param);
        try std.testing.expectEqualStrings("ok\x00hidden", next.value.?);
        try std.testing.expectEqualStrings("tail", next.remaining);
    }
}
