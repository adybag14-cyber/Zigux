const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

const TokenSet = struct {
    argv: []const []u8,

    fn len(self: TokenSet) usize {
        return self.argv.len;
    }

    fn at(self: TokenSet, index: usize) []const u8 {
        return self.argv[index];
    }
};

fn splitTokens(text: []const u8) !if (@hasDecl(argv_split, "ArgvSplitResult")) argv_split.ArgvSplitResult else [][]u8 {
    return argv_split.argvSplit(std.testing.allocator, text);
}

fn tokenSet(split: anytype) TokenSet {
    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        return .{ .argv = split.argv };
    }

    return .{ .argv = split };
}

fn freeTokens(split: anytype) void {
    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        var owned = split;
        owned.deinit();
    } else {
        argv_split.argvFree(std.testing.allocator, split);
    }
}

fn expectKeyValueToken(token: []const u8, expected_key: []const u8, expected_value: []const u8) !void {
    const eq = std.mem.indexOfScalar(u8, token, '=') orelse return error.TestUnexpectedResult;
    const key = token[0..eq];
    const value = token[eq + 1 ..];

    try std.testing.expectEqualStrings(expected_key, key);
    try std.testing.expectEqualStrings(expected_value, value);

    for (key) |ch| {
        try std.testing.expect(ctype.isalnum(ch) or ch == '_');
        try std.testing.expect(!ctype.isspace(ch));
    }

    try std.testing.expect(ctype.ispunct('='));
    try std.testing.expect(!ctype.isalnum('='));
}

fn tokenClassMask(tokens: TokenSet) u32 {
    var mask: u32 = 0;

    var index: usize = 0;
    while (index < tokens.len()) : (index += 1) {
        var has_digit = false;
        var has_punct = false;

        for (tokens.at(index)) |ch| {
            has_digit = has_digit or ctype.isdigit(ch);
            has_punct = has_punct or ctype.ispunct(ch);
        }

        if (has_digit) {
            mask |= @as(u32, 1) << @intCast(index);
        }
        if (has_punct) {
            mask |= @as(u32, 1) << @intCast(index + 8);
        }
    }

    return mask;
}

test "helper ports b classify split key value tokens without whitespace bleed" {
    const split = try splitTokens(" console=ttyS0,115200 initcall_debug debug_mask=0x2f ");
    defer freeTokens(split);

    const tokens = tokenSet(split);
    try std.testing.expectEqual(@as(usize, 3), tokens.len());
    try expectKeyValueToken(tokens.at(0), "console", "ttyS0,115200");
    try std.testing.expectEqualStrings("initcall_debug", tokens.at(1));
    try expectKeyValueToken(tokens.at(2), "debug_mask", "0x2f");

    for (tokens.at(1)) |ch| {
        try std.testing.expect(ctype.isalnum(ch) or ch == '_');
        try std.testing.expect(!ctype.isspace(ch));
        try std.testing.expect((ch == '_') == ctype.ispunct(ch));
    }
}

test "helper ports b route numeric token tails through cmdline and hweight" {
    const split = try splitTokens("console=ttyS0,115200 debug_mask=0x2f panic=32K");
    defer freeTokens(split);

    const tokens = tokenSet(split);
    try std.testing.expectEqual(@as(usize, 3), tokens.len());

    const debug_eq = std.mem.indexOfScalar(u8, tokens.at(1), '=') orelse return error.TestUnexpectedResult;
    const debug_value = cmdline.memparse(tokens.at(1)[debug_eq + 1 ..]);
    try std.testing.expectEqual(@as(u64, 0x2f), debug_value.value);
    try std.testing.expectEqualStrings("", debug_value.rest);

    const panic_eq = std.mem.indexOfScalar(u8, tokens.at(2), '=') orelse return error.TestUnexpectedResult;
    const panic_value = cmdline.memparse(tokens.at(2)[panic_eq + 1 ..]);
    try std.testing.expectEqual(@as(u64, 32 << 10), panic_value.value);
    try std.testing.expectEqualStrings("", panic_value.rest);

    const mask = tokenClassMask(tokens);
    try std.testing.expectEqual(@as(u32, 6), hweight.swHweight16(mask));
    try std.testing.expectEqual(@popCount(mask), hweight.swHweight32(mask));
    try std.testing.expectEqual(@as(u64, @intCast(@popCount(@as(u64, mask)))), hweight.swHweight64(mask));
    try std.testing.expectEqual(@as(usize, @intCast(@popCount(@as(usize, mask)))), hweight.hweightLong(mask));
}

test "helper ports b keep option lists exact after split classification" {
    const split = try splitTokens("quiet console=ttyS0,115200 nohlt");
    defer freeTokens(split);

    const tokens = tokenSet(split);
    try std.testing.expectEqual(@as(usize, 3), tokens.len());

    var options = std.ArrayList(u8).empty;
    defer options.deinit(std.testing.allocator);

    var index: usize = 0;
    while (index < tokens.len()) : (index += 1) {
        if (index != 0) {
            try options.append(std.testing.allocator, ',');
        }

        const token = tokens.at(index);
        const end = std.mem.indexOfScalar(u8, token, '=') orelse token.len;
        try options.appendSlice(std.testing.allocator, token[0..end]);
    }

    try std.testing.expect(cmdline.parseOptionStr(options.items, "quiet"));
    try std.testing.expect(cmdline.parseOptionStr(options.items, "console"));
    try std.testing.expect(cmdline.parseOptionStr(options.items, "nohlt"));
    try std.testing.expect(!cmdline.parseOptionStr(options.items, "ttyS0"));

    const mask = tokenClassMask(tokens);
    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight8(mask & 0xff));
    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight8((mask >> 8) & 0xff));
}
