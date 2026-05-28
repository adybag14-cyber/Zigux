const std = @import("std");
const argv_split = @import("argv_split");

fn expectToken(result: argv_split.ArgvSplitResult, index: usize, expected: []const u8) !void {
    try std.testing.expectEqualStrings(expected, result.argv[index]);
}

test "argvSplit keeps high-byte and utf8 token bytes verbatim" {
    const input = "caf\xC3\xA9\t\xA0latin1\nutf8-\xE2\x98\x83 \xFFtail";

    var result = try argv_split.argvSplit(std.testing.allocator, input);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 4), result.argc());
    try expectToken(result, 0, "caf\xC3\xA9");
    try expectToken(result, 1, "\xA0latin1");
    try expectToken(result, 2, "utf8-\xE2\x98\x83");
    try expectToken(result, 3, "\xFFtail");
}

test "argvSplit only treats ascii whitespace as separators" {
    const input = "left\xC2\xA0middle right\xA0edge";

    var result = try argv_split.argv_split(std.testing.allocator, input);
    defer argv_split.argv_free(&result);

    try std.testing.expectEqual(@as(usize, 2), result.argc());
    try expectToken(result, 0, "left\xC2\xA0middle");
    try expectToken(result, 1, "right\xA0edge");
}

test "argvFree resets the public result after high-byte tokens" {
    var result = try argv_split.argvSplit(std.testing.allocator, "\xE2\x98\x83 snow \xA0ice");
    try std.testing.expectEqual(@as(usize, 3), result.argc());

    argv_split.argvFree(&result);

    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);
}
