const std = @import("std");
const argv_split = @import("argv_split");

test "argvSplit returns owned copies independent of the source buffer" {
    var source = [_]u8{ 'a', 'l', 'p', 'h', 'a', ' ', 'b', 'e', 't', 'a' };

    var result = try argv_split.argvSplit(std.testing.allocator, source[0..]);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 2), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);

    @memset(source[0..], 'x');
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
}

test "argv_split alias preserves owned result semantics" {
    var source = [_]u8{ 'o', 'n', 'e', '\t', 't', 'w', 'o', '\n', 't', 'h', 'r', 'e', 'e' };

    var result = try argv_split.argv_split(std.testing.allocator, source[0..]);
    defer argv_split.argv_free(&result);

    try std.testing.expectEqual(@as(usize, 3), result.argc());
    try std.testing.expectEqualStrings("one", result.argv[0]);
    try std.testing.expectEqualStrings("two", result.argv[1]);
    try std.testing.expectEqualStrings("three", result.argv[2]);

    source[0] = 'z';
    source[4] = 'z';
    source[8] = 'z';
    try std.testing.expectEqualStrings("one", result.argv[0]);
    try std.testing.expectEqualStrings("two", result.argv[1]);
    try std.testing.expectEqualStrings("three", result.argv[2]);
}

test "argvFree leaves a stable empty result after deinit" {
    var result = try argv_split.argvSplit(std.testing.allocator, "left right");
    try std.testing.expectEqual(@as(usize, 2), result.argc());

    argv_split.argvFree(&result);
    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);
}
