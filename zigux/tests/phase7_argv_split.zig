const std = @import("std");
const argv_split = @import("argv_split");
const fixture_vectors = @import("fixtures/phase7_argv_split_vectors.zig");

fn expectVectorReplay(
    vector: fixture_vectors.ArgvSplitVector,
    split: *const argv_split.ArgvSplitResult,
    argc: usize,
) !void {
    try std.testing.expectEqual(vector.expected_argc, argc);
    try std.testing.expectEqual(vector.expected_tokens.len, split.argv.len);

    const c_argv = split.cArgv();
    for (vector.expected_tokens, 0..) |expected, index| {
        try std.testing.expectEqualStrings(expected, split.argv[index]);
        try std.testing.expectEqualStrings(expected, std.mem.span(c_argv[index].?));
    }
    try std.testing.expectEqual(@as(?[*:0]const u8, null), c_argv[vector.expected_tokens.len]);

    if (vector.expect_empty_storage_view) {
        try std.testing.expectEqual(@as(usize, 0), split.storage.len);
        try std.testing.expectEqual(@as(usize, 0), split.argv.len);
        try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
        try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    }

    if (vector.expect_first_nul_truncation) {
        try std.testing.expect(std.mem.indexOf(u8, split.storage, "ignored tail") == null);
    }
}

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

test "phase 7 argv split companion replays non-blank cross-call ownership independence" {
    var first = try argv_split.argvSplit(std.testing.allocator, "alpha beta");
    defer first.deinit(std.testing.allocator);
    var second = try argv_split.argvSplit(std.testing.allocator, "alpha beta");
    defer second.deinit(std.testing.allocator);

    try std.testing.expect(first.storage.ptr != second.storage.ptr);
    try std.testing.expect(first.argv.ptr != second.argv.ptr);
    try std.testing.expect(first.argv_null_terminated.ptr != second.argv_null_terminated.ptr);
    try std.testing.expect(@intFromPtr(first.cArgv()) != @intFromPtr(second.cArgv()));

    for (first.argv, second.argv, 0..) |first_token, second_token, index| {
        try std.testing.expectEqualStrings(first_token, second_token);
        try std.testing.expect(first_token.ptr != second_token.ptr);
        try std.testing.expectEqual(@intFromPtr(first_token.ptr), @intFromPtr(first.cArgv()[index].?));
        try std.testing.expectEqual(@intFromPtr(second_token.ptr), @intFromPtr(second.cArgv()[index].?));
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

test "phase 7 argv split companion replays repeated blank-result sentinel reuse" {
    var first_argc: usize = std.math.maxInt(usize);
    var first = try argv_split.argvSplitWithArgc(std.testing.allocator, " \t\n", &first_argc);
    defer first.deinit(std.testing.allocator);

    var second_argc: usize = std.math.maxInt(usize);
    var second = try argv_split.argvSplitWithArgc(std.testing.allocator, "", &second_argc);
    defer second.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 0), first_argc);
    try std.testing.expectEqual(@as(usize, 0), second_argc);
    try std.testing.expectEqual(@as(usize, 0), first.argv.len);
    try std.testing.expectEqual(@as(usize, 0), second.argv.len);
    try std.testing.expectEqual(@as(usize, 1), first.argv_null_terminated.len);
    try std.testing.expectEqual(@as(usize, 1), second.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), first.cArgv()[0]);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), second.cArgv()[0]);
    try std.testing.expectEqual(first.storage.ptr, second.storage.ptr);
    try std.testing.expectEqual(first.argv.ptr, second.argv.ptr);
    try std.testing.expectEqual(first.argv_null_terminated.ptr, second.argv_null_terminated.ptr);
    try std.testing.expectEqual(first.cArgv(), second.cArgv());
}

test "phase 7 argv split companion replays whitespace-before-first-NUL sentinel reuse" {
    const vectors = fixture_vectors.phase7_argv_split_vectors;

    var blank_argc: usize = std.math.maxInt(usize);
    var blank = try argv_split.argvSplitWithArgc(std.testing.allocator, vectors[1].input, &blank_argc);
    defer blank.deinit(std.testing.allocator);
    try expectVectorReplay(vectors[1], &blank, blank_argc);

    var whitespace_before_nul_argc: usize = std.math.maxInt(usize);
    var whitespace_before_nul = try argv_split.argvSplitWithArgc(
        std.testing.allocator,
        vectors[2].input,
        &whitespace_before_nul_argc,
    );
    defer whitespace_before_nul.deinit(std.testing.allocator);
    try expectVectorReplay(vectors[2], &whitespace_before_nul, whitespace_before_nul_argc);

    try std.testing.expectEqual(blank.storage.ptr, whitespace_before_nul.storage.ptr);
    try std.testing.expectEqual(blank.argv.ptr, whitespace_before_nul.argv.ptr);
    try std.testing.expectEqual(blank.argv_null_terminated.ptr, whitespace_before_nul.argv_null_terminated.ptr);
    try std.testing.expectEqual(blank.cArgv(), whitespace_before_nul.cArgv());
}

test "phase 7 argv split companion replays fixture-backed leading-NUL ownership and quoted-token boundaries" {
    const vectors = fixture_vectors.phase7_argv_split_vectors;

    var blank_argc: usize = std.math.maxInt(usize);
    var blank = try argv_split.argvSplitWithArgc(std.testing.allocator, vectors[1].input, &blank_argc);
    defer blank.deinit(std.testing.allocator);
    try expectVectorReplay(vectors[1], &blank, blank_argc);

    var leading_nul_argc: usize = std.math.maxInt(usize);
    var leading_nul = try argv_split.argvSplitWithArgc(std.testing.allocator, vectors[3].input, &leading_nul_argc);
    defer leading_nul.deinit(std.testing.allocator);
    try expectVectorReplay(vectors[3], &leading_nul, leading_nul_argc);

    try std.testing.expectEqual(blank.storage.ptr, leading_nul.storage.ptr);
    try std.testing.expectEqual(blank.argv.ptr, leading_nul.argv.ptr);
    try std.testing.expectEqual(blank.argv_null_terminated.ptr, leading_nul.argv_null_terminated.ptr);
    try std.testing.expectEqual(blank.cArgv(), leading_nul.cArgv());

    var truncated_argc: usize = std.math.maxInt(usize);
    var truncated = try argv_split.argvSplitWithArgc(std.testing.allocator, vectors[4].input, &truncated_argc);
    defer truncated.deinit(std.testing.allocator);
    try expectVectorReplay(vectors[4], &truncated, truncated_argc);

    var quoted_argc: usize = std.math.maxInt(usize);
    var quoted = try argv_split.argvSplitWithArgc(std.testing.allocator, vectors[5].input, &quoted_argc);
    defer quoted.deinit(std.testing.allocator);
    try expectVectorReplay(vectors[5], &quoted, quoted_argc);

    try std.testing.expect(truncated.storage.ptr != blank.storage.ptr);
    try std.testing.expect(truncated.argv_null_terminated.ptr != blank.argv_null_terminated.ptr);
    try std.testing.expect(quoted.storage.ptr != blank.storage.ptr);
    try std.testing.expect(quoted.argv_null_terminated.ptr != blank.argv_null_terminated.ptr);
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
