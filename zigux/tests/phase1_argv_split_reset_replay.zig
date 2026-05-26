const std = @import("std");
const argv_split = @import("argv_split");

test "phase1 argv_split deinit resets the public result before reuse" {
    var result = try argv_split.argvSplit(std.testing.allocator, "root=/dev/vda rw quiet");

    try std.testing.expectEqual(@as(usize, 3), result.argc());
    try std.testing.expectEqualStrings("root=/dev/vda", result.argv[0]);
    try std.testing.expectEqualStrings("rw", result.argv[1]);
    try std.testing.expectEqualStrings("quiet", result.argv[2]);

    result.deinit();

    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);

    result = try argv_split.argvSplit(std.testing.allocator, "panic=-1");
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 1), result.argc());
    try std.testing.expectEqualStrings("panic=-1", result.argv[0]);
}

test "phase1 argvFree keeps sibling results intact and resets alias-based cleanup" {
    var first = try argv_split.argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda");
    var second = try argv_split.argv_split(std.testing.allocator, "panic=-1 init=/init");

    argv_split.argvFree(&first);

    try std.testing.expectEqual(@as(usize, 0), first.argc());
    try std.testing.expectEqual(@as(usize, 0), first.argv.len);
    try std.testing.expectEqual(@as(usize, 2), second.argc());
    try std.testing.expectEqualStrings("panic=-1", second.argv[0]);
    try std.testing.expectEqualStrings("init=/init", second.argv[1]);

    argv_split.argv_free(&second);

    try std.testing.expectEqual(@as(usize, 0), second.argc());
    try std.testing.expectEqual(@as(usize, 0), second.argv.len);
}
