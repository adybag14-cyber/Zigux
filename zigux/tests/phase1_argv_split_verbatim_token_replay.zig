const std = @import("std");
const argv_split = @import("argv_split");

test "argvSplit preserves punctuation-heavy tokens verbatim across whitespace boundaries" {
    const input =
        "--flag=value\tpath=./zigux/tests,meta\n" ++
        "quote\"kept\" bracket[ok] comma,separated utf8:\xC3\xA9";

    var result = try argv_split.argvSplit(std.testing.allocator, input);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 6), result.argc());
    try std.testing.expectEqualStrings("--flag=value", result.argv[0]);
    try std.testing.expectEqualStrings("path=./zigux/tests,meta", result.argv[1]);
    try std.testing.expectEqualStrings("quote\"kept\"", result.argv[2]);
    try std.testing.expectEqualStrings("bracket[ok]", result.argv[3]);
    try std.testing.expectEqualStrings("comma,separated", result.argv[4]);
    try std.testing.expectEqualStrings("utf8:\xC3\xA9", result.argv[5]);
}

test "argv_split aliases keep quotes backslashes and raw bytes inside tokens" {
    const input =
        "name=\"zigux builder\" slash\\\\kept\n" ++
        "raw:\xC3\xA9 plain";

    var result = try argv_split.argv_split(std.testing.allocator, input);
    defer argv_split.argv_free(&result);

    try std.testing.expectEqual(@as(usize, 5), result.argc());
    try std.testing.expectEqualStrings("name=\"zigux", result.argv[0]);
    try std.testing.expectEqualStrings("builder\"", result.argv[1]);
    try std.testing.expectEqualStrings("slash\\\\kept", result.argv[2]);
    try std.testing.expectEqualStrings("raw:\xC3\xA9", result.argv[3]);
    try std.testing.expectEqualStrings("plain", result.argv[4]);
}

test "argvSplit keeps raw-byte tokens and trailing token order intact" {
    const input =
        "raw:\xC3\xA9 plain tail=done";

    var result = try argv_split.argvSplit(std.testing.allocator, input);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 3), result.argc());
    try std.testing.expectEqualStrings("raw:\xC3\xA9", result.argv[0]);
    try std.testing.expectEqualStrings("plain", result.argv[1]);
    try std.testing.expectEqualStrings("tail=done", result.argv[2]);
}
