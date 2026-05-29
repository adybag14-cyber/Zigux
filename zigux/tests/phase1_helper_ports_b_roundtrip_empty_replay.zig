const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn expectBlankSplit() !void {
    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        var blank = try argv_split.argvSplit(std.testing.allocator, " \t\n\r ");
        defer blank.deinit();

        try std.testing.expectEqual(@as(usize, 0), blank.argc());
        try std.testing.expectEqual(@as(usize, 0), blank.argv.len);
    } else {
        const blank = try argv_split.argvSplit(std.testing.allocator, " \t\n\r ");
        defer argv_split.argvFree(std.testing.allocator, blank);

        try std.testing.expectEqual(@as(usize, 0), blank.len);
    }
}

fn expectRoundtripSplit() !void {
    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        var split = try argv_split.argvSplit(std.testing.allocator, " 64K  quiet   0x10M ");
        defer split.deinit();

        try std.testing.expectEqual(@as(usize, 3), split.argc());
        try expectTokenRoundtrip(split.argv);
    } else {
        const split = try argv_split.argvSplit(std.testing.allocator, " 64K  quiet   0x10M ");
        defer argv_split.argvFree(std.testing.allocator, split);

        try std.testing.expectEqual(@as(usize, 3), split.len);
        try expectTokenRoundtrip(split);
    }
}

fn expectTokenRoundtrip(tokens: []const []u8) !void {
    const first = cmdline.memparse(tokens[0]);
    try std.testing.expectEqual(@as(u64, 64 << 10), first.value);
    try std.testing.expectEqualStrings("", first.rest);

    try std.testing.expectEqualStrings("quiet", tokens[1]);

    const last = cmdline.memparse(tokens[2]);
    try std.testing.expectEqual(@as(u64, 0x10 << 20), last.value);
    try std.testing.expectEqualStrings("", last.rest);
}

test "helper ports b keep empty argv and cmdline null paths quiet" {
    try expectBlankSplit();

    const no_digits = cmdline.memparse("+tail");
    try std.testing.expectEqual(@as(u64, 0), no_digits.value);
    try std.testing.expectEqualStrings("+tail", no_digits.rest);
}

test "helper ports b preserve option token stops and delimiter classes" {
    try std.testing.expect(cmdline.parse_option_str("root=/dev/sda1,,quiet\x00debug", ""));
    try std.testing.expect(cmdline.parse_option_str("root=/dev/sda1,,quiet\x00debug", "quiet"));
    try std.testing.expect(!cmdline.parse_option_str("root=/dev/sda1,,quiet\x00debug", "debug"));
    try std.testing.expect(!cmdline.parse_option_str("root=/dev/sda1,,quiet\x00debug", "root"));

    try std.testing.expect(ctype.isspace('\n'));
    try std.testing.expect(ctype.iscntrl('\n'));
    try std.testing.expect(!ctype.isgraph(' '));
    try std.testing.expect(ctype.isprint(' '));
    try std.testing.expect(ctype.ispunct(','));
    try std.testing.expect(!ctype.isalnum(','));
}

test "helper ports b roundtrip split tokens through cmdline and popcounts" {
    try expectRoundtripSplit();

    var token_mask: u32 = 0;
    const tokens = [_][]const u8{ "64K", "quiet", "0x10M" };
    for (tokens) |arg| {
        token_mask |= @as(u32, 1) << @intCast(arg.len);
    }

    try std.testing.expectEqual(@popCount(token_mask), hweight.swHweight32(token_mask));
    try std.testing.expectEqual(@as(usize, @intCast(@popCount(@as(usize, token_mask)))), hweight.hweightLong(token_mask));
}
