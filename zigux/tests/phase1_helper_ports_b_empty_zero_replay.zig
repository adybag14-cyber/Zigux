const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn argvLen(result: anytype) usize {
    return if (@TypeOf(result) == [][]u8) result.len else result.argc();
}

fn argvDeinit(result: anytype) void {
    if (@TypeOf(result.*) == [][]u8) {
        argv_split.argvFree(std.testing.allocator, result.*);
    } else {
        result.deinit();
    }
}

test "empty inputs stay inert across helper ports B" {
    var empty = try argv_split.argvSplit(std.testing.allocator, "");
    defer argvDeinit(&empty);
    try std.testing.expectEqual(@as(usize, 0), argvLen(empty));

    if (@hasDecl(argv_split, "argv_split")) {
        var spaces = try argv_split.argv_split(std.testing.allocator, " \t\n ");
        defer argv_split.argv_free(&spaces);
        try std.testing.expectEqual(@as(usize, 0), argvLen(spaces));
    } else {
        var spaces = try argv_split.argvSplit(std.testing.allocator, " \t\n ");
        defer argvDeinit(&spaces);
        try std.testing.expectEqual(@as(usize, 0), argvLen(spaces));
    }

    if (@hasDecl(cmdline, "nextArg")) {
        try std.testing.expect(cmdline.nextArg("") == null);
        try std.testing.expect(cmdline.next_arg(" \t\n ") == null);
    }
    try std.testing.expect(!cmdline.parseOptionStr("", "quiet"));
    try std.testing.expect(!cmdline.parse_option_str("", ""));

    const empty_parse = cmdline.memparse("");
    try std.testing.expectEqual(@as(u64, 0), empty_parse.value);
    try std.testing.expectEqualStrings("", empty_parse.rest);

    const sign_only = cmdline.memparse("+");
    try std.testing.expectEqual(@as(u64, 0), sign_only.value);
    try std.testing.expectEqualStrings("+", sign_only.rest);
}

test "zero byte and zero value contracts stay explicit across helper ports B" {
    try std.testing.expect(ctype.iscntrl(0));
    try std.testing.expect(!ctype.isprint(0));
    try std.testing.expect(!ctype.isgraph(0));
    try std.testing.expect(!ctype.isalnum(0));
    try std.testing.expect(ctype.isascii(0));
    try std.testing.expectEqual(@as(u8, 0), ctype.toascii(0));
    try std.testing.expectEqual(@as(u8, 0), ctype.toascii(0x80));

    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight8(0));
    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight16(0));
    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight32(0));
    try std.testing.expectEqual(@as(u64, 0), hweight.swHweight64(0));
    try std.testing.expectEqual(@as(usize, 0), hweight.hweightLong(0));

    if (@hasDecl(hweight, "__sw_hweight8")) {
        try std.testing.expectEqual(hweight.swHweight8(0), hweight.__sw_hweight8(0));
        try std.testing.expectEqual(hweight.swHweight16(0), hweight.__sw_hweight16(0));
        try std.testing.expectEqual(hweight.swHweight32(0), hweight.__sw_hweight32(0));
        try std.testing.expectEqual(hweight.swHweight64(0), hweight.__sw_hweight64(0));
        try std.testing.expectEqual(hweight.hweightLong(0), hweight.hweight_long(0));
    }
}
