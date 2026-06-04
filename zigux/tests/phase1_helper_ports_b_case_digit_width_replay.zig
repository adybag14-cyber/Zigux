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

fn expectLowLaneCounts(value: u32) !void {
    try std.testing.expectEqual(@as(u32, @popCount(@as(u8, @truncate(value)))), hweight.swHweight8(value));
    try std.testing.expectEqual(@as(u32, @popCount(@as(u16, @truncate(value)))), hweight.swHweight16(value));
    try std.testing.expectEqual(@as(u32, @popCount(value)), hweight.swHweight32(value));

    if (@hasDecl(hweight, "__sw_hweight8")) {
        try std.testing.expectEqual(hweight.swHweight8(value), hweight.__sw_hweight8(value));
        try std.testing.expectEqual(hweight.swHweight16(value), hweight.__sw_hweight16(value));
        try std.testing.expectEqual(hweight.swHweight32(value), hweight.__sw_hweight32(value));
    }
}

test "case and digit tokens retain literal argv bytes and parse numeric widths" {
    var split = try argv_split.argvSplit(std.testing.allocator, "Alpha7 beta08 HEX0x1f");
    defer argvDeinit(&split);

    try std.testing.expectEqual(@as(usize, 3), argvLen(split));
    try std.testing.expectEqualStrings("Alpha7", argvAt(split, 0));
    try std.testing.expectEqualStrings("beta08", argvAt(split, 1));
    try std.testing.expectEqualStrings("HEX0x1f", argvAt(split, 2));

    const hex = cmdline.memparse("0x1fKtail");
    try std.testing.expectEqual(@as(u64, 31 << 10), hex.value);
    try std.testing.expectEqualStrings("tail", hex.rest);

    const octal = cmdline.memparse("0777 stop");
    try std.testing.expectEqual(@as(u64, 0o777), octal.value);
    try std.testing.expectEqualStrings(" stop", octal.rest);

    const invalid_octal = cmdline.memparse("08more");
    try std.testing.expectEqual(@as(u64, 0), invalid_octal.value);
    try std.testing.expectEqualStrings("8more", invalid_octal.rest);

    if (@hasDecl(cmdline, "nextArg")) {
        const parsed = cmdline.next_arg("HexWidth=0x1fK tail") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("HexWidth", parsed.param);
        try std.testing.expectEqualStrings("0x1fK", parsed.value.?);
        try std.testing.expectEqualStrings("tail", parsed.remaining);
    }
}

test "ctype case digit boundaries align with hweight lane widths" {
    const bytes = [_]u8{ 'A', 'F', 'G', 'a', 'f', 'g', '0', '7', '8', '9' };
    for (bytes) |byte| {
        try expectLowLaneCounts(byte);
        try std.testing.expectEqual(byte <= 0x7f, ctype.isascii(byte));
    }

    try std.testing.expect(ctype.isupper('A'));
    try std.testing.expect(ctype.isupper('F'));
    try std.testing.expect(ctype.isupper('G'));
    try std.testing.expect(ctype.islower('a'));
    try std.testing.expect(ctype.islower('f'));
    try std.testing.expect(ctype.islower('g'));
    try std.testing.expect(ctype.isdigit('0'));
    try std.testing.expect(ctype.isdigit('9'));
    try std.testing.expect(ctype.isodigit('7'));
    try std.testing.expect(!ctype.isodigit('8'));
    try std.testing.expect(ctype.isxdigit('F'));
    try std.testing.expect(ctype.isxdigit('f'));
    try std.testing.expect(!ctype.isxdigit('G'));
    try std.testing.expect(!ctype.isxdigit('g'));
    try std.testing.expectEqual(@as(u8, 'a'), ctype.tolower('A'));
    try std.testing.expectEqual(@as(u8, 'A'), ctype.toupper('a'));

    const packed_word: u32 = (@as(u32, 'A') << 24) | (@as(u32, 'f') << 16) | (@as(u32, '8') << 8) | 'g';
    try std.testing.expectEqual(@as(u32, @popCount(@as(u8, 'g'))), hweight.swHweight8(packed_word));
    try std.testing.expectEqual(
        @as(u32, @popCount(@as(u16, (@as(u16, '8') << 8) | 'g'))),
        hweight.swHweight16(packed_word),
    );
    try std.testing.expectEqual(@as(u32, @popCount(packed_word)), hweight.swHweight32(packed_word));
}
