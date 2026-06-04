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

fn expectQuoteTokenShape(argv: []const []const u8) !void {
    try std.testing.expectEqual(@as(usize, 4), argv.len);
    try std.testing.expectEqualStrings("\"alpha=1\"", argv[0]);
    try std.testing.expectEqualStrings("beta\\gamma", argv[1]);
    try std.testing.expectEqualStrings("0x10K", argv[2]);
    try std.testing.expectEqualStrings("tail", argv[3]);

    var quoted_or_escaped_mask: u32 = 0;
    var hex_prefix_mask: u32 = 0;
    for (argv, 0..) |token, token_idx| {
        var has_quote_or_backslash = false;
        var has_hex_prefix = token.len >= 4 and token[0] == '0' and ctype.fastTolower(token[1]) == 'x';
        for (token, 0..) |byte, byte_idx| {
            has_quote_or_backslash = has_quote_or_backslash or byte == '"' or byte == '\\';
            if (byte_idx >= 2 and byte_idx < 4) {
                has_hex_prefix = has_hex_prefix and ctype.isxdigit(byte);
            }
        }
        if (has_quote_or_backslash) quoted_or_escaped_mask |= @as(u32, 1) << @intCast(token_idx);
        if (has_hex_prefix) hex_prefix_mask |= @as(u32, 1) << @intCast(token_idx);
    }

    try std.testing.expectEqual(@as(u32, 0b0011), quoted_or_escaped_mask);
    try std.testing.expectEqual(@as(u32, 0b0100), hex_prefix_mask);
    try std.testing.expect(ctype.ispunct(argv[0][0]));
    try std.testing.expect(ctype.ispunct(argv[0][argv[0].len - 1]));
    try std.testing.expect(ctype.ispunct(argv[1][4]));
    try std.testing.expectEqual(@as(u8, 'k'), ctype.fastTolower(argv[2][4]));
    try std.testing.expectEqual(@as(u8, 'T'), ctype.toupper(argv[3][0]));

    const four_token_window: u32 = 0b1111;
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight8(quoted_or_escaped_mask));
    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight8(hex_prefix_mask));
    try std.testing.expectEqual(
        @as(u32, 4),
        hweight.swHweight8(quoted_or_escaped_mask) +
            hweight.swHweight8((~quoted_or_escaped_mask) & four_token_window),
    );
    if (@hasDecl(hweight, "__sw_hweight8")) {
        try std.testing.expectEqual(hweight.swHweight8(quoted_or_escaped_mask), hweight.__sw_hweight8(quoted_or_escaped_mask));
    }
}

test "argv literal quote tokens feed ctype masks and hweight accounting" {
    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        var result = try argv_split.argvSplit(std.testing.allocator, " \"alpha=1\" beta\\gamma 0x10K tail ");
        defer result.deinit();

        try expectQuoteTokenShape(result.argv);
    } else {
        const argv = try argv_split.argvSplit(std.testing.allocator, " \"alpha=1\" beta\\gamma 0x10K tail ");
        defer freeLegacyArgv(std.testing.allocator, argv);

        try expectQuoteTokenShape(argv);
    }
}

test "cmdline suffix parsing and option fences align with ctype and hweight masks" {
    const signed = cmdline.memparse("-0x10K,rest");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -16 * 1024))), signed.value);
    try std.testing.expectEqualStrings(",rest", signed.rest);

    const unsigned = cmdline.memparse("020M+next");
    try std.testing.expectEqual(@as(u64, 16 << 20), unsigned.value);
    try std.testing.expectEqualStrings("+next", unsigned.rest);

    const options = "alpha,,quoted=\"1\",mask\x00late";
    try std.testing.expect(cmdline.parseOptionStr(options, ""));
    try std.testing.expect(!cmdline.parseOptionStr(options, "quoted"));
    try std.testing.expect(!cmdline.parseOptionStr(options, "late"));

    var suffix_mask: u32 = 0;
    const suffix_bytes = [_]u8{ 'K', 'M', ',', '+' };
    for (suffix_bytes, 0..) |byte, bit| {
        if (ctype.isupper(byte) or ctype.ispunct(byte)) {
            suffix_mask |= @as(u32, 1) << @intCast(bit);
        }
    }
    try std.testing.expectEqual(@as(u32, 0b1111), suffix_mask);
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight16(suffix_mask));
    if (@hasDecl(hweight, "__sw_hweight16")) {
        try std.testing.expectEqual(hweight.swHweight16(suffix_mask), hweight.__sw_hweight16(suffix_mask));
    }

    if (@hasDecl(cmdline, "nextArg")) {
        const parsed = cmdline.nextArg("root=\"/dev/sda1 quiet\" mask=0xf tail") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("root", parsed.param);
        try std.testing.expectEqualStrings("/dev/sda1 quiet", parsed.value.?);
        try std.testing.expectEqualStrings("mask=0xf tail", parsed.remaining);

        const second = cmdline.nextArg(parsed.remaining) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("mask", second.param);
        try std.testing.expectEqualStrings("0xf", second.value.?);
        try std.testing.expectEqualStrings("tail", second.remaining);
    }
}
