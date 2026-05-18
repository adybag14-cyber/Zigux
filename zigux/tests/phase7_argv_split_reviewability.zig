const std = @import("std");
const argv_split = @import("../../lib/argv_split.zig");

test "phase7 argv_split counts only tokens before the first NUL" {
    try std.testing.expectEqual(@as(usize, 2), argv_split.countArgc("alpha beta\x00ignored tail"));
    try std.testing.expectEqual(@as(usize, 0), argv_split.countArgc("\x00ignored tail"));
}

test "phase7 argv_split keeps owned token pointers inside its duplicated storage" {
    var split = try argv_split.argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda rw");
    defer split.deinit(std.testing.allocator);

    const storage_start = @intFromPtr(split.storage.ptr);
    const storage_end = storage_start + split.storage.len;
    const c_argv = split.cArgv();

    try std.testing.expectEqual(@as(usize, 3), split.argv.len);
    for (split.argv, 0..) |token, index| {
        const token_start = @intFromPtr(token.ptr);
        const token_end = token_start + token.len;

        try std.testing.expect(token_start >= storage_start);
        try std.testing.expect(token_end <= storage_end);
        try std.testing.expectEqual(@intFromPtr(token.ptr), @intFromPtr(c_argv[index].?));
    }
    try std.testing.expectEqual(@as(?[*:0]const u8, null), c_argv[split.argv.len]);
}

test "phase7 argv_split reuses shared blank-input sentinel views" {
    var buffer = [_]u8{};
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    var argc: usize = std.math.maxInt(usize);
    var split = try argv_split.argvSplitWithArgc(fba.allocator(), " \t\n\x00ignored tail", &argc);
    defer split.deinit(fba.allocator());

    try std.testing.expectEqual(@as(usize, 0), argc);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "phase7 argv_split teardown resets exported views for repeated callers" {
    var first = try argv_split.argvSplit(std.testing.allocator, "alpha beta");
    var second = try argv_split.argvSplit(std.testing.allocator, "gamma delta");
    defer second.deinit(std.testing.allocator);

    const second_storage_ptr = second.storage.ptr;
    const second_argv_ptr = second.argv.ptr;
    const second_c_argv = second.cArgv();

    argv_split.argvFree(std.testing.allocator, &first);
    argv_split.argvFree(std.testing.allocator, &first);

    try std.testing.expectEqual(@as(usize, 0), first.storage.len);
    try std.testing.expectEqual(@as(usize, 0), first.argv.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), first.cArgv()[0]);

    try std.testing.expect(second.storage.ptr == second_storage_ptr);
    try std.testing.expect(second.argv.ptr == second_argv_ptr);
    try std.testing.expect(second.cArgv() == second_c_argv);
    try std.testing.expectEqualStrings("gamma", second.argv[0]);
    try std.testing.expectEqualStrings("delta", second.argv[1]);
}
