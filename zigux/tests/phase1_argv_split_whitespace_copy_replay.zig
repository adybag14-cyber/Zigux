const std = @import("std");
const argv_split = @import("argv_split");

test "phase1 argv_split replay keeps every ASCII whitespace boundary exact" {
    const text = "alpha\tbeta\n\rgamma\x0bdelta\x0cepsilon";
    var result = try argv_split.argvSplit(std.testing.allocator, text);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 5), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
    try std.testing.expectEqualStrings("gamma", result.argv[2]);
    try std.testing.expectEqualStrings("delta", result.argv[3]);
    try std.testing.expectEqualStrings("epsilon", result.argv[4]);
}

test "phase1 argv_split replay preserves punctuation-heavy tokens" {
    const text = "--flag alpha=1 beta,gamma path/to/file";
    var result = try argv_split.argvSplit(std.testing.allocator, text);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 4), result.argc());
    try std.testing.expectEqualStrings("--flag", result.argv[0]);
    try std.testing.expectEqualStrings("alpha=1", result.argv[1]);
    try std.testing.expectEqualStrings("beta,gamma", result.argv[2]);
    try std.testing.expectEqualStrings("path/to/file", result.argv[3]);
}

test "phase1 argv_split replay returns copied storage through alias helpers" {
    var source = [_]u8{ 'a', 'l', 'p', 'h', 'a', ' ', 'b', 'e', 't', 'a' };
    var result = try argv_split.argv_split(std.testing.allocator, source[0..]);
    defer argv_split.argv_free(&result);

    source[0] = 'z';
    source[6] = 'q';

    try std.testing.expectEqual(@as(usize, 2), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
}
