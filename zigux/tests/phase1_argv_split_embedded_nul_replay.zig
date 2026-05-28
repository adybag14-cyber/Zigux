const std = @import("std");
const argv_split = @import("argv_split");

test "phase1 argv_split keeps embedded NUL bytes inside copied tokens" {
    var result = try argv_split.argv_split(std.testing.allocator, "alpha\x00beta gamma\x00delta");
    defer argv_split.argv_free(&result);

    try std.testing.expectEqual(@as(usize, 2), result.argc());
    try std.testing.expectEqual(@as(usize, 2), result.argv.len);
    try std.testing.expectEqualSlices(u8, "alpha\x00beta", result.argv[0]);
    try std.testing.expectEqualSlices(u8, "gamma\x00delta", result.argv[1]);
}

test "phase1 argv_split alias free resets one result without disturbing a sibling caller" {
    var first = try argv_split.argv_split(std.testing.allocator, "init=/init loglevel=7");
    var second = try argv_split.argvSplit(std.testing.allocator, "panic=-1 root=/dev/vda");
    defer second.deinit();

    const second_argv_ptr = second.argv.ptr;

    argv_split.argv_free(&first);

    try std.testing.expectEqual(@as(usize, 0), first.argc());
    try std.testing.expectEqual(@as(usize, 0), first.argv.len);
    try std.testing.expect(second.argv.ptr == second_argv_ptr);
    try std.testing.expectEqual(@as(usize, 2), second.argc());
    try std.testing.expectEqualStrings("panic=-1", second.argv[0]);
    try std.testing.expectEqualStrings("root=/dev/vda", second.argv[1]);
}
