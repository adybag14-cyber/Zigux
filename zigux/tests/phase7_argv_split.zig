const std = @import("std");
const argv_split = @import("argv_split");

test "phase 7 argv split companion replays copied-storage token ownership" {
    var argc: usize = std.math.maxInt(usize);
    var split = try argv_split.argvSplitWithArgc(std.testing.allocator, " alpha  beta\tgamma\n", &argc);
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 3), argc);
    try std.testing.expectEqual(@as(usize, 3), argv_split.countArgc(" alpha  beta\tgamma\n"));
    try std.testing.expectEqual(@as(usize, 3), split.argv.len);
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta", split.argv[1]);
    try std.testing.expectEqualStrings("gamma", split.argv[2]);
    try std.testing.expectEqualStrings("alpha", std.mem.span(split.cArgv()[0].?));
    try std.testing.expectEqualStrings("beta", std.mem.span(split.cArgv()[1].?));
    try std.testing.expectEqualStrings("gamma", std.mem.span(split.cArgv()[2].?));
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[3]);

    const storage_start = @intFromPtr(split.storage.ptr);
    const storage_end = storage_start + split.storage.len;
    for (split.argv) |token| {
        const token_start = @intFromPtr(token.ptr);
        const token_end = token_start + token.len;
        try std.testing.expect(token_start >= storage_start);
        try std.testing.expect(token_end <= storage_end);
    }
}

test "phase 7 argv split companion replays blank-input sentinel reuse and first-NUL truncation" {
    var blank_argc: usize = std.math.maxInt(usize);
    var blank = try argv_split.argvSplitWithArgc(std.testing.allocator, " \t\n", &blank_argc);
    defer blank.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 0), blank_argc);
    try std.testing.expectEqual(@as(usize, 0), blank.argv.len);
    try std.testing.expectEqual(@as(usize, 1), blank.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), blank.cArgv()[0]);

    var truncated = try argv_split.argvSplit(std.testing.allocator, "alpha beta\x00ignored tail");
    defer truncated.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 2), truncated.argv.len);
    try std.testing.expectEqualStrings("alpha", truncated.argv[0]);
    try std.testing.expectEqualStrings("beta", truncated.argv[1]);
    try std.testing.expect(std.mem.indexOf(u8, truncated.storage, "ignored tail") == null);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), truncated.cArgv()[2]);
}

test "phase 7 argv split companion replays caller-owned teardown and failure boundaries" {
    var split = try argv_split.argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda");
    argv_split.argvFree(std.testing.allocator, &split);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);

    var backing = [_]u8{0} ** 15;
    var fba = std.heap.FixedBufferAllocator.init(&backing);
    var argc: usize = std.math.maxInt(usize);
    try std.testing.expectError(
        error.OutOfMemory,
        argv_split.argvSplitWithArgc(fba.allocator(), "alpha beta", &argc),
    );
    try std.testing.expectEqual(std.math.maxInt(usize), argc);
}
