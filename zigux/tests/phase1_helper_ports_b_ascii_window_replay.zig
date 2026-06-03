const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

const ArgvView = struct {
    result: @TypeOf(argv_split.argvSplit(std.testing.allocator, "") catch unreachable),

    fn init(allocator: std.mem.Allocator, text: []const u8) !ArgvView {
        return .{ .result = try argv_split.argvSplit(allocator, text) };
    }

    fn deinit(self: *ArgvView, allocator: std.mem.Allocator) void {
        switch (comptime @typeInfo(@TypeOf(self.result))) {
            .@"struct" => self.result.deinit(),
            else => argv_split.argvFree(allocator, self.result),
        }
    }

    fn items(self: *const ArgvView) []const []const u8 {
        switch (comptime @typeInfo(@TypeOf(self.result))) {
            .@"struct" => return self.result.argv,
            else => return self.result,
        }
    }
};

fn expectTokenShape(token: []const u8) !void {
    var digit_count: u32 = 0;
    var punctuation_count: u32 = 0;
    var alpha_count: u32 = 0;

    for (token) |ch| {
        try std.testing.expect(ctype.isprint(ch));
        try std.testing.expect(!ctype.isspace(ch));

        if (ctype.isdigit(ch)) {
            digit_count += 1;
        }
        if (ctype.ispunct(ch)) {
            punctuation_count += 1;
        }
        if (ctype.isalpha(ch)) {
            alpha_count += 1;
        }
    }

    const classification_mask =
        (if (digit_count != 0) @as(u32, 0b001) else 0) |
        (if (punctuation_count != 0) @as(u32, 0b010) else 0) |
        (if (alpha_count != 0) @as(u32, 0b100) else 0);

    try std.testing.expectEqual(@popCount(classification_mask), hweight.swHweight8(classification_mask));
    try std.testing.expect(hweight.swHweight32(classification_mask) <= token.len);
}

test "Lane 08 ASCII token windows preserve helper contracts together" {
    const allocator = std.testing.allocator;
    var view = try ArgvView.init(
        allocator,
        " \troot=0x20M console=ttyS0,115200 quiet debug=1\n",
    );
    defer view.deinit(allocator);

    const argv = view.items();
    try std.testing.expectEqual(@as(usize, 4), argv.len);
    try std.testing.expectEqualStrings("root=0x20M", argv[0]);
    try std.testing.expectEqualStrings("console=ttyS0,115200", argv[1]);
    try std.testing.expectEqualStrings("quiet", argv[2]);
    try std.testing.expectEqualStrings("debug=1", argv[3]);

    for (argv) |token| {
        try expectTokenShape(token);
    }

    const root_value = cmdline.memparse(argv[0]["root=".len..]);
    try std.testing.expectEqual(@as(u64, 0x20 << 20), root_value.value);
    try std.testing.expectEqualStrings("", root_value.rest);

    try std.testing.expect(cmdline.parseOptionStr("quiet,debug,panic", "quiet"));
    try std.testing.expect(cmdline.parse_option_str("quiet,debug,panic", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug=1,panic", "debug"));
}

test "Lane 08 ASCII delimiter byte windows keep masks and popcounts aligned" {
    const delimiters = [_]u8{ ',', '=', ':', '-', '_' };
    var delimiter_mask: u32 = 0;

    for (delimiters, 0..) |ch, idx| {
        try std.testing.expect(ctype.isascii(ch));
        try std.testing.expect(ctype.isprint(ch));
        try std.testing.expect(ctype.ispunct(ch));
        try std.testing.expect(!ctype.isspace(ch));
        delimiter_mask |= @as(u32, 1) << @intCast(idx);
    }

    try std.testing.expectEqual(@as(u32, delimiters.len), hweight.swHweight8(delimiter_mask));
    try std.testing.expectEqual(hweight.swHweight8(delimiter_mask), hweight.swHweight32(delimiter_mask));

    const ascii_fold = ctype.toascii(0xF1);
    try std.testing.expectEqual(@as(u8, 'q'), ascii_fold);
    try std.testing.expect(ctype.islower(ascii_fold));
    try std.testing.expectEqual(@as(u8, 'Q'), ctype.toupper(ascii_fold));
}
