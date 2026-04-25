const std = @import("std");
const argv_split = @import("argv_split");

test "phase 7 argv_split module imports cleanly" {
    _ = argv_split;
}

test "phase 7 argvSplit collapses repeated whitespace into distinct argv entries" {
    var split = try argv_split.argvSplit(std.testing.allocator, " init=/init   console=ttyS0\tpanic=-1 ");
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 3), split.argv.len);
    try std.testing.expectEqualStrings("init=/init", split.argv[0]);
    try std.testing.expectEqualStrings("console=ttyS0", split.argv[1]);
    try std.testing.expectEqualStrings("panic=-1", split.argv[2]);
    try std.testing.expectEqual(@as(usize, 3), argv_split.countArgc(" init=/init   console=ttyS0\tpanic=-1 "));
}

test "phase 7 argv helpers stop at the first NUL byte" {
    var split = try argv_split.argvSplit(std.testing.allocator, "root=/dev/vda rw\x00ignored debug");
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 2), argv_split.countArgc("root=/dev/vda rw\x00ignored debug"));
    try std.testing.expectEqual(@as(usize, 2), split.argv.len);
    try std.testing.expectEqualStrings("root=/dev/vda", split.argv[0]);
    try std.testing.expectEqualStrings("rw", split.argv[1]);
}

test "phase 7 argvSplit keeps quote characters instead of doing cmdline parsing" {
    var split = try argv_split.argvSplit(std.testing.allocator, "root=\"/dev/sda 1\" single");
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 3), split.argv.len);
    try std.testing.expectEqualStrings("root=\"/dev/sda", split.argv[0]);
    try std.testing.expectEqualStrings("1\"", split.argv[1]);
    try std.testing.expectEqualStrings("single", split.argv[2]);
}

test "phase 7 argvSplit token buffer does not alias the source text" {
    var source = [_]u8{ 'r', 'o', 'o', 't', '=', '/', 'd', 'e', 'v', '/', 'v', 'd', 'a', ' ', 'r', 'w' };
    var split = try argv_split.argvSplit(std.testing.allocator, &source);
    defer split.deinit(std.testing.allocator);

    source[0] = 'X';
    source[5] = 'Y';

    try std.testing.expectEqualStrings("root=/dev/vda", split.argv[0]);
    try std.testing.expectEqualStrings("rw", split.argv[1]);
}
