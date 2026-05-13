const std = @import("std");
const argv_split = @import("argv_split");
const phase7_vectors = @import("fixtures/phase7_argv_split_vectors.zig");

fn expectFixture(fixture: phase7_vectors.ArgvSplitCase) !void {
    var argc: usize = std.math.maxInt(usize);
    var split = try argv_split.argvSplitWithArgc(std.testing.allocator, fixture.input, &argc);
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(fixture.expected.len, argv_split.countArgc(fixture.input));
    try std.testing.expectEqual(fixture.expected.len, argc);
    try std.testing.expectEqual(fixture.expected.len, split.argv.len);

    const c_argv = split.cArgv();
    for (fixture.expected, 0..) |expected, index| {
        try std.testing.expectEqualStrings(expected, split.argv[index]);
        try std.testing.expectEqualStrings(expected, std.mem.span(c_argv[index].?));
    }

    try std.testing.expectEqual(@as(?[*:0]const u8, null), c_argv[fixture.expected.len]);
}

fn runArgvSplitWithFailingAllocator(allocator: std.mem.Allocator, text: []const u8) !void {
    var split = try argv_split.argvSplit(allocator, text);
    defer split.deinit(allocator);
}

test "phase 7 argv_split module imports cleanly" {
    _ = argv_split;
}

test "phase 7 argvSplit matches focused parity fixtures" {
    for (phase7_vectors.argv_split_cases) |fixture| {
        try expectFixture(fixture);
    }
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

test "phase 7 argvSplit keeps every shared token pointer inside the owned storage copy" {
    var split = try argv_split.argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda rw");
    defer split.deinit(std.testing.allocator);

    const storage_start = @intFromPtr(split.storage.ptr);
    const storage_end = storage_start + split.storage.len;
    const c_argv = split.cArgv();

    for (split.argv, 0..) |token, index| {
        const token_start = @intFromPtr(token.ptr);
        const token_end = token_start + token.len;
        const offset = token_start - storage_start;

        try std.testing.expect(token_start >= storage_start);
        try std.testing.expect(token_end <= storage_end);
        try std.testing.expectEqual(@intFromPtr(token.ptr), @intFromPtr(c_argv[index].?));
        try std.testing.expectEqual(@as(u8, 0), split.storage[offset + token.len]);
    }
}

test "phase 7 argvSplit zeroes copied whitespace separators across the tokenized buffer" {
    var split = try argv_split.argvSplit(std.testing.allocator, " alpha  beta\tgamma\n");
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(u8, 0), split.storage[0]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[6]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[7]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[12]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[18]);
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta", split.argv[1]);
    try std.testing.expectEqualStrings("gamma", split.argv[2]);
}

test "phase 7 argvSplit zeroes carriage-return, vertical-tab, and form-feed separators too" {
    var split = try argv_split.argvSplit(std.testing.allocator, "\ralpha\x0bbeta\x0cgamma\r\n\tdelta");
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(u8, 0), split.storage[0]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[6]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[11]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[17]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[18]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[19]);
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta", split.argv[1]);
    try std.testing.expectEqualStrings("gamma", split.argv[2]);
    try std.testing.expectEqualStrings("delta", split.argv[3]);
}

test "phase 7 argvSplitWithArgc reports the split length through the optional out parameter" {
    var argc: usize = 99;
    var split = try argv_split.argvSplitWithArgc(std.testing.allocator, "console=ttyS0 root=/dev/vda rw", &argc);
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 3), argc);
    try std.testing.expectEqual(argc, split.argv.len);
}

test "phase 7 argvSplit keeps the final token C-string terminator and trailing argv sentinel aligned" {
    var split = try argv_split.argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda");
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqualStrings("root=/dev/vda", std.mem.span(split.cArgv()[1].?));
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[split.argv.len]);
}

test "phase 7 non-blank argvSplit calls keep owned storage and C-argv views distinct across callers" {
    var first = try argv_split.argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda rw");
    defer first.deinit(std.testing.allocator);

    var second = try argv_split.argvSplit(std.testing.allocator, "panic=-1 init=/init");
    defer second.deinit(std.testing.allocator);

    try std.testing.expect(first.storage.ptr != second.storage.ptr);
    try std.testing.expect(first.argv.ptr != second.argv.ptr);
    try std.testing.expect(first.cArgv() != second.cArgv());

    try std.testing.expectEqualStrings("console=ttyS0", first.argv[0]);
    try std.testing.expectEqualStrings("root=/dev/vda", first.argv[1]);
    try std.testing.expectEqualStrings("rw", first.argv[2]);
    try std.testing.expectEqualStrings("panic=-1", second.argv[0]);
    try std.testing.expectEqualStrings("init=/init", second.argv[1]);
    try std.testing.expectEqualStrings("console=ttyS0", std.mem.span(first.cArgv()[0].?));
    try std.testing.expectEqualStrings("panic=-1", std.mem.span(second.cArgv()[0].?));
}

test "phase 7 argvSplit deinit on one non-blank result keeps sibling caller-owned views intact" {
    var first = try argv_split.argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda rw");
    var second = try argv_split.argvSplit(std.testing.allocator, "panic=-1 init=/init");
    defer second.deinit(std.testing.allocator);

    const second_storage_ptr = second.storage.ptr;
    const second_argv_ptr = second.argv.ptr;
    const second_c_argv = second.cArgv();

    first.deinit(std.testing.allocator);

    try std.testing.expect(second.storage.ptr == second_storage_ptr);
    try std.testing.expect(second.argv.ptr == second_argv_ptr);
    try std.testing.expect(second.cArgv() == second_c_argv);
    try std.testing.expectEqual(@as(usize, 2), second.argv.len);
    try std.testing.expectEqualStrings("panic=-1", second.argv[0]);
    try std.testing.expectEqualStrings("init=/init", second.argv[1]);
    try std.testing.expectEqualStrings("panic=-1", std.mem.span(second.cArgv()[0].?));
    try std.testing.expectEqualStrings("init=/init", std.mem.span(second.cArgv()[1].?));
    try std.testing.expectEqual(@as(?[*:0]const u8, null), second.cArgv()[second.argv.len]);
}

test "phase 7 argvFree on one non-blank result keeps sibling caller-owned views intact" {
    var first = try argv_split.argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda rw");
    var second = try argv_split.argvSplit(std.testing.allocator, "panic=-1 init=/init");
    defer second.deinit(std.testing.allocator);

    const second_storage_ptr = second.storage.ptr;
    const second_argv_ptr = second.argv.ptr;
    const second_c_argv = second.cArgv();

    argv_split.argvFree(std.testing.allocator, &first);

    try std.testing.expect(second.storage.ptr == second_storage_ptr);
    try std.testing.expect(second.argv.ptr == second_argv_ptr);
    try std.testing.expect(second.cArgv() == second_c_argv);
    try std.testing.expectEqual(@as(usize, 2), second.argv.len);
    try std.testing.expectEqualStrings("panic=-1", second.argv[0]);
    try std.testing.expectEqualStrings("init=/init", second.argv[1]);
    try std.testing.expectEqualStrings("panic=-1", std.mem.span(second.cArgv()[0].?));
    try std.testing.expectEqualStrings("init=/init", std.mem.span(second.cArgv()[1].?));
    try std.testing.expectEqual(@as(?[*:0]const u8, null), second.cArgv()[second.argv.len]);
}

test "phase 7 argvFree on a non-blank result restores the canonical blank sentinels" {
    var split = try argv_split.argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda rw");
    var blank = try argv_split.argvSplitWithArgc(std.testing.allocator, "", null);
    defer blank.deinit(std.testing.allocator);

    argv_split.argvFree(std.testing.allocator, &split);

    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
    try std.testing.expect(split.storage.ptr == blank.storage.ptr);
    try std.testing.expect(split.argv_null_terminated.ptr == blank.argv_null_terminated.ptr);
    try std.testing.expect(split.cArgv() == blank.cArgv());
}

test "phase 7 blank argvSplit deinit on one caller keeps shared sentinel views usable for another" {
    var buffer = [_]u8{};
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    var first = try argv_split.argvSplitWithArgc(fba.allocator(), " \t\n", null);
    var second = try argv_split.argvSplitWithArgc(fba.allocator(), "", null);
    defer second.deinit(fba.allocator());

    try std.testing.expectEqual(first.storage.ptr, second.storage.ptr);
    try std.testing.expectEqual(first.argv_null_terminated.ptr, second.argv_null_terminated.ptr);
    try std.testing.expectEqual(first.cArgv(), second.cArgv());

    first.deinit(fba.allocator());

    try std.testing.expectEqual(@as(usize, 0), first.storage.len);
    try std.testing.expectEqual(@as(u8, 0), first.storage[first.storage.len]);
    try std.testing.expectEqual(@as(usize, 1), first.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), first.cArgv()[0]);

    try std.testing.expectEqual(@as(usize, 0), second.storage.len);
    try std.testing.expectEqual(@as(u8, 0), second.storage[second.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), second.argv.len);
    try std.testing.expectEqual(@as(usize, 1), second.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), second.cArgv()[0]);
    try std.testing.expectEqual(first.storage.ptr, second.storage.ptr);
    try std.testing.expectEqual(first.argv_null_terminated.ptr, second.argv_null_terminated.ptr);
    try std.testing.expectEqual(first.cArgv(), second.cArgv());
}

test "phase 7 blank argvSplit input reuses the empty exported argv view" {
    var buffer: [4]u8 = undefined;
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    var argc: usize = std.math.maxInt(usize);
    var split = try argv_split.argvSplitWithArgc(fba.allocator(), " \t\n", &argc);
    var second_split = try argv_split.argvSplitWithArgc(fba.allocator(), "", null);
    defer split.deinit(fba.allocator());
    defer second_split.deinit(fba.allocator());

    try std.testing.expectEqual(@as(usize, 0), argc);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(split.argv_null_terminated.ptr, second_split.argv_null_terminated.ptr);
    try std.testing.expectEqual(split.cArgv(), second_split.cArgv());
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space" {
    var buffer = [_]u8{};
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    var argc: usize = std.math.maxInt(usize);
    var split = try argv_split.argvSplitWithArgc(fba.allocator(), " \t\n", &argc);
    var second_split = try argv_split.argvSplitWithArgc(fba.allocator(), "", null);
    defer split.deinit(fba.allocator());
    defer second_split.deinit(fba.allocator());

    try std.testing.expectEqual(@as(usize, 0), argc);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(split.storage.ptr, second_split.storage.ptr);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable" {
    var buffer = [_]u8{};
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    var argc: usize = std.math.maxInt(usize);
    var split = try argv_split.argvSplitWithArgc(fba.allocator(), " \t\n", &argc);

    try std.testing.expectEqual(@as(usize, 0), argc);

    argv_split.argvFree(fba.allocator(), &split);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);

    argv_split.argvFree(fba.allocator(), &split);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "phase 7 argvSplit deinit clears exported storage and argv views" {
    var split = try argv_split.argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda rw");

    try std.testing.expect(split.storage.len != 0);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 3), split.argv.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[split.argv.len]);

    split.deinit(std.testing.allocator);
    var blank = try argv_split.argvSplitWithArgc(std.testing.allocator, "", null);
    defer blank.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
    try std.testing.expect(split.storage.ptr == blank.storage.ptr);
    try std.testing.expect(split.argv_null_terminated.ptr == blank.argv_null_terminated.ptr);
    try std.testing.expect(split.cArgv() == blank.cArgv());
}

test "phase 7 argvSplit deinit stays safe when called after teardown already cleared the result" {
    var split = try argv_split.argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda rw");

    split.deinit(std.testing.allocator);
    split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable" {
    var split = try argv_split.argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda rw");

    argv_split.argvFree(std.testing.allocator, &split);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);

    argv_split.argvFree(std.testing.allocator, &split);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runArgvSplitWithFailingAllocator,
        .{"console=ttyS0 root=/dev/vda rw"},
    );
}
