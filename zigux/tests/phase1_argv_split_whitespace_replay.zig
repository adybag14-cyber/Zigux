const std = @import("std");
const argv_split = @import("argv_split");

test "argv split replay preserves token boundaries across ascii whitespace" {
    var result = try argv_split.argvSplit(
        std.testing.allocator,
        "\talpha\n beta\r\ngamma\x0bdelta\x0cepsilon  zeta",
    );
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 6), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
    try std.testing.expectEqualStrings("gamma", result.argv[2]);
    try std.testing.expectEqualStrings("delta", result.argv[3]);
    try std.testing.expectEqualStrings("epsilon", result.argv[4]);
    try std.testing.expectEqualStrings("zeta", result.argv[5]);
}

test "argv split replay treats punctuation as ordinary argument bytes" {
    var result = try argv_split.argv_split(
        std.testing.allocator,
        "root=/dev/vda1 console=ttyS0,115200n8 -- flag=value,more",
    );
    defer argv_split.argv_free(&result);

    try std.testing.expectEqual(@as(usize, 4), result.argc());
    try std.testing.expectEqualStrings("root=/dev/vda1", result.argv[0]);
    try std.testing.expectEqualStrings("console=ttyS0,115200n8", result.argv[1]);
    try std.testing.expectEqualStrings("--", result.argv[2]);
    try std.testing.expectEqualStrings("flag=value,more", result.argv[3]);
}

test "argv split replay leaves deinitialized results reusable as empty" {
    var result = try argv_split.argvSplit(std.testing.allocator, "one two");
    try std.testing.expectEqual(@as(usize, 2), result.argc());

    result.deinit();
    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);

    argv_split.argvFree(&result);
    try std.testing.expectEqual(@as(usize, 0), result.argc());
}
