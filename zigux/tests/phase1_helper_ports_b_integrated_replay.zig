const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn expectAsciiToken(token: []const u8) !void {
    for (token) |ch| {
        try std.testing.expect(ctype.isascii(ch));
        try std.testing.expect(ctype.isgraph(ch));
        try std.testing.expect(ctype.isprint(ch));
        try std.testing.expect(!ctype.isspace(ch));
    }
}

fn expectHelperPortsBContract(args: anytype) !void {
    try std.testing.expectEqual(@as(usize, 4), args.len);
    try std.testing.expectEqualStrings("debug", args[0]);
    try std.testing.expectEqualStrings("mem=64K", args[1]);
    try std.testing.expectEqualStrings("mask=0xf0", args[2]);
    try std.testing.expectEqualStrings("letters=AaZz", args[3]);

    for (args) |arg| {
        try expectAsciiToken(arg);
    }

    try std.testing.expect(cmdline.parseOptionStr("quiet,debug,trace\x00ignored", args[0]));
    try std.testing.expect(!cmdline.parse_option_str("quiet,debug=1,trace", "debug"));

    const mem = cmdline.memparse(args[1]["mem=".len..]);
    try std.testing.expectEqual(@as(u64, 64 << 10), mem.value);
    try std.testing.expectEqualStrings("", mem.rest);

    const mask = cmdline.memparse(args[2]["mask=".len..]);
    try std.testing.expectEqual(@as(u64, 0xf0), mask.value);
    try std.testing.expectEqualStrings("", mask.rest);
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(@intCast(mask.value)));

    if (@hasDecl(hweight, "__sw_hweight8")) {
        try std.testing.expectEqual(hweight.swHweight8(@intCast(mask.value)), hweight.__sw_hweight8(@intCast(mask.value)));
    }

    const letters = args[3]["letters=".len..];
    try std.testing.expectEqual(@as(u8, 'a'), ctype.fastTolower(letters[0]));
    try std.testing.expectEqual(@as(u8, 'a'), ctype.fastTolower(letters[1]));
    try std.testing.expectEqual(@as(u8, 'z'), ctype.fastTolower(letters[2]));
    try std.testing.expectEqual(@as(u8, 'z'), ctype.fastTolower(letters[3]));
}

fn expectSplitHelperPortsBContract(allocator: std.mem.Allocator, text: []const u8) !void {
    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        var result = try argv_split.argv_split(allocator, text);
        defer argv_split.argv_free(&result);
        try std.testing.expectEqual(result.argc(), result.argv.len);
        try expectHelperPortsBContract(result.argv);
    } else {
        const args = try argv_split.argvSplit(allocator, text);
        defer argv_split.argvFree(allocator, args);
        try expectHelperPortsBContract(args);
    }
}

test "helper ports B split cmdline ctype and hweight integrated replay" {
    try expectSplitHelperPortsBContract(
        std.testing.allocator,
        " \tdebug  mem=64K\nmask=0xf0  letters=AaZz ",
    );
}
