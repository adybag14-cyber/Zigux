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

fn expectControlTokenShape(argv: []const []const u8) !void {
    try std.testing.expectEqual(@as(usize, 4), argv.len);
    try std.testing.expectEqualStrings("alpha\x01beta", argv[0]);
    try std.testing.expectEqualStrings("del\x7f", argv[1]);
    try std.testing.expectEqualStrings("+077K", argv[2]);
    try std.testing.expectEqualStrings("0XfG", argv[3]);

    var control_token_mask: u32 = 0;
    var printable_token_mask: u32 = 0;
    var numeric_token_mask: u32 = 0;
    for (argv, 0..) |token, token_idx| {
        var has_control = false;
        var all_printable = token.len != 0;
        var starts_like_number = false;
        if (token.len != 0) {
            starts_like_number = token[0] == '+' or token[0] == '-' or ctype.isdigit(token[0]);
        }

        for (token) |byte| {
            has_control = has_control or ctype.iscntrl(byte);
            all_printable = all_printable and ctype.isprint(byte);
        }

        const bit = @as(u32, 1) << @intCast(token_idx);
        if (has_control) control_token_mask |= bit;
        if (all_printable) printable_token_mask |= bit;
        if (starts_like_number) numeric_token_mask |= bit;
    }

    try std.testing.expectEqual(@as(u32, 0b0011), control_token_mask);
    try std.testing.expectEqual(@as(u32, 0b1100), printable_token_mask);
    try std.testing.expectEqual(@as(u32, 0b1100), numeric_token_mask);
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight8(control_token_mask));
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight8(printable_token_mask));
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(control_token_mask | printable_token_mask));

    try std.testing.expect(ctype.iscntrl(argv[0][5]));
    try std.testing.expect(ctype.iscntrl(argv[1][3]));
    try std.testing.expect(ctype.isascii(argv[1][3]));
    try std.testing.expectEqual(@as(u8, 0x7f), ctype.toascii(argv[1][3]));
    try std.testing.expect(ctype.ispunct(argv[2][0]));
    try std.testing.expect(ctype.isodigit(argv[2][1]));
    try std.testing.expect(ctype.isxdigit(argv[3][2]));
    try std.testing.expectEqual(@as(u8, 'x'), ctype.fastTolower(argv[3][1]));
}

test "argv control bytes feed ctype masks and hweight accounting" {
    const text = " \t alpha\x01beta \n del\x7f  +077K 0XfG \r";

    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        var result = try argv_split.argvSplit(std.testing.allocator, text);
        defer result.deinit();

        try expectControlTokenShape(result.argv);
    } else {
        const argv = try argv_split.argvSplit(std.testing.allocator, text);
        defer freeLegacyArgv(std.testing.allocator, argv);

        try expectControlTokenShape(argv);
    }
}

test "cmdline numeric rests and nul option fences preserve control boundaries" {
    const signed_octal = cmdline.memparse("+077K,tail");
    try std.testing.expectEqual(@as(u64, 63 << 10), signed_octal.value);
    try std.testing.expectEqualStrings(",tail", signed_octal.rest);

    const uppercase_hex = cmdline.memparse("0XfG rest");
    try std.testing.expectEqual(@as(u64, 15 << 30), uppercase_hex.value);
    try std.testing.expectEqualStrings(" rest", uppercase_hex.rest);

    const options = "alpha,ctrl\x01,del\x7f,empty,,stop\x00late,ctrl\x02";
    try std.testing.expect(cmdline.parseOptionStr(options, "ctrl\x01"));
    try std.testing.expect(cmdline.parseOptionStr(options, "del\x7f"));
    try std.testing.expect(cmdline.parseOptionStr(options, ""));
    try std.testing.expect(!cmdline.parseOptionStr(options, "late"));
    try std.testing.expect(!cmdline.parseOptionStr(options, "ctrl\x02"));

    var matched_mask: u32 = 0;
    const probes = [_][]const u8{ "ctrl\x01", "del\x7f", "", "late" };
    for (probes, 0..) |probe, idx| {
        if (cmdline.parseOptionStr(options, probe)) {
            matched_mask |= @as(u32, 1) << @intCast(idx);
        }
    }
    try std.testing.expectEqual(@as(u32, 0b0111), matched_mask);
    try std.testing.expectEqual(@as(u32, 3), hweight.swHweight16(matched_mask));

    if (@hasDecl(cmdline, "nextArg")) {
        const parsed = cmdline.nextArg("flag\x7f=on +077K") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("flag\x7f", parsed.param);
        try std.testing.expectEqualStrings("on", parsed.value.?);
        try std.testing.expectEqualStrings("+077K", parsed.remaining);
        try std.testing.expect(ctype.iscntrl(parsed.param[4]));
    }

    if (@hasDecl(hweight, "__sw_hweight16")) {
        try std.testing.expectEqual(hweight.swHweight16(matched_mask), hweight.__sw_hweight16(matched_mask));
    }
}
