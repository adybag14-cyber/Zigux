const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn expectSplit(expected: []const []const u8, text: []const u8) !void {
    const allocator = std.testing.allocator;

    if (comptime @hasDecl(argv_split, "ArgvSplitResult")) {
        var result = try argv_split.argvSplit(allocator, text);
        defer result.deinit();

        try std.testing.expectEqual(expected.len, result.argv.len);
        for (expected, result.argv) |want, got| {
            try std.testing.expectEqualStrings(want, got);
        }
    } else {
        const result = try argv_split.argvSplit(allocator, text);
        defer argv_split.argvFree(allocator, result);

        try std.testing.expectEqual(expected.len, result.len);
        for (expected, result) |want, got| {
            try std.testing.expectEqualStrings(want, got);
        }
    }
}

test "punctuation and empty options stay separate from argv whitespace" {
    try expectSplit(&.{ ",", ",,", "debug=1" }, " \t ,  ,, \n debug=1 ");

    try std.testing.expect(cmdline.parseOptionStr(",debug,,quiet", ""));
    try std.testing.expect(cmdline.parseOptionStr("quiet,,debug", ""));
    try std.testing.expect(!cmdline.parseOptionStr("debug,", ""));
    try std.testing.expect(!cmdline.parseOptionStr("debug=1,,quiet", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("alpha\x00,beta", "beta"));

    try std.testing.expect(ctype.isspace('\t'));
    try std.testing.expect(ctype.isspace('\n'));
    try std.testing.expect(!ctype.isspace(','));
    try std.testing.expect(ctype.ispunct(','));
    try std.testing.expect(ctype.isprint(','));

    try std.testing.expectEqual(@as(u32, @popCount(@as(u8, ','))), hweight.swHweight8(','));
    if (comptime @hasDecl(hweight, "__sw_hweight8")) {
        try std.testing.expectEqual(hweight.swHweight8(','), hweight.__sw_hweight8(','));
    }
}

test "nul payloads and zero magnitudes keep low-lane accounting fenced" {
    try expectSplit(&.{ "alpha\x00beta", "tail" }, "alpha\x00beta tail");

    const zero_with_suffix = cmdline.memparse("0Ktail");
    try std.testing.expectEqual(@as(u64, 0), zero_with_suffix.value);
    try std.testing.expectEqualStrings("tail", zero_with_suffix.rest);

    const signed_zero_with_suffix = cmdline.memparse("+0Mrest");
    try std.testing.expectEqual(@as(u64, 0), signed_zero_with_suffix.value);
    try std.testing.expectEqualStrings("rest", signed_zero_with_suffix.rest);

    try std.testing.expect(ctype.iscntrl(0));
    try std.testing.expect(!ctype.isprint(0));
    try std.testing.expect(ctype.isascii(0));
    try std.testing.expect(!ctype.isascii(0x80));
    try std.testing.expectEqual(@as(u8, 0), ctype.toascii(0x80));

    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight8(0xffff_ff00));
    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight16(0xffff_0000));
    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight32(0));
    try std.testing.expectEqual(@as(u64, 0), hweight.swHweight64(0));

    if (comptime @hasDecl(hweight, "hweight_long")) {
        try std.testing.expectEqual(@as(usize, 0), hweight.hweight_long(0));
    }
}

test "current nextArg empty values remain compatible when the helper exposes them" {
    if (comptime @hasDecl(cmdline, "nextArg")) {
        const parsed = cmdline.nextArg("root=\"\" debug") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("root", parsed.param);
        try std.testing.expectEqualStrings("", parsed.value.?);
        try std.testing.expectEqualStrings("debug", parsed.remaining);

        const tail = cmdline.next_arg(parsed.remaining) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("debug", tail.param);
        try std.testing.expect(tail.value == null);
        try std.testing.expectEqualStrings("", tail.remaining);
    }
}
