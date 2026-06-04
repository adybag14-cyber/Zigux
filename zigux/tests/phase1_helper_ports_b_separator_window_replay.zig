const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn argvLen(result: anytype) usize {
    return if (@TypeOf(result) == [][]u8) result.len else result.argc();
}

fn argvAt(result: anytype, index: usize) []const u8 {
    return if (@TypeOf(result) == [][]u8) result[index] else result.argv[index];
}

fn argvDeinit(result: anytype) void {
    if (@TypeOf(result.*) == [][]u8) {
        argv_split.argvFree(std.testing.allocator, result.*);
    } else {
        result.deinit();
    }
}

fn expectBytePopcount(byte: u8) !void {
    try std.testing.expectEqual(@as(u32, @popCount(byte)), hweight.swHweight8(byte));
    if (@hasDecl(hweight, "__sw_hweight8")) {
        try std.testing.expectEqual(hweight.swHweight8(byte), hweight.__sw_hweight8(byte));
    }
}

test "separator bytes split argv and fence cmdline options" {
    var split = try argv_split.argvSplit(std.testing.allocator, "\talpha\nbeta  gamma");
    defer argvDeinit(&split);
    try std.testing.expectEqual(@as(usize, 3), argvLen(split));
    try std.testing.expectEqualStrings("alpha", argvAt(split, 0));
    try std.testing.expectEqualStrings("beta", argvAt(split, 1));
    try std.testing.expectEqualStrings("gamma", argvAt(split, 2));

    if (@hasDecl(cmdline, "nextArg")) {
        const first = cmdline.next_arg("\tmode=fast\npanic=1") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("mode", first.param);
        try std.testing.expectEqualStrings("fast", first.value.?);
        try std.testing.expectEqualStrings("panic=1", first.remaining);
    }

    try std.testing.expect(cmdline.parseOptionStr("quiet,debug\x00nohlt", "debug"));
    try std.testing.expect(!cmdline.parse_option_str("quiet,debug\x00nohlt", "nohlt"));
    try std.testing.expect(cmdline.parseOptionStr("quiet,,debug", ""));

    const parsed = cmdline.memparse("32K\tend");
    try std.testing.expectEqual(@as(u64, 32 << 10), parsed.value);
    try std.testing.expectEqualStrings("\tend", parsed.rest);
}

test "ctype and hweight agree on separator and token byte windows" {
    const separators = [_]u8{ ' ', '\t', '\n', '\r' };
    for (separators) |byte| {
        try std.testing.expect(ctype.isspace(byte));
        try std.testing.expect(!ctype.isgraph(byte));
        try std.testing.expect(!ctype.isalnum(byte));
        try expectBytePopcount(byte);
    }

    const token = "Az9_";
    var aggregate: u32 = 0;
    for (token) |byte| {
        try std.testing.expect(!ctype.isspace(byte));
        try std.testing.expect(ctype.isgraph(byte));
        aggregate += hweight.swHweight8(byte);
        try expectBytePopcount(byte);
    }

    try std.testing.expect(ctype.isupper('A'));
    try std.testing.expect(ctype.islower('z'));
    try std.testing.expect(ctype.isdigit('9'));
    try std.testing.expect(ctype.ispunct('_'));
    try std.testing.expectEqual(@as(u32, @popCount(@as(u32, 'A') | (@as(u32, 'z') << 8))), hweight.swHweight16((@as(u32, 'z') << 8) | 'A'));
    try std.testing.expectEqual(@as(u32, @popCount(@as(u32, 'A')) + @popCount(@as(u32, 'z')) + @popCount(@as(u32, '9')) + @popCount(@as(u32, '_'))), aggregate);
}
