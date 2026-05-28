const std = @import("std");
const testing = std.testing;

const string_helpers = @import("string_helpers");
const cmdline = @import("cmdline");
const argv_split = @import("argv_split");
const rbtree = @import("rbtree");

test "phase7 packet keeps borrowed cmdline parsing aligned with owned argv splitting" {
    const command = "console=ttyS0 root=\"/dev/vda1 quiet\" panic=-1";

    const first = cmdline.nextArg(command);
    try testing.expectEqualStrings("console", first.param);
    try testing.expectEqualStrings("ttyS0", first.value.?);

    const second = cmdline.nextArg(first.remaining);
    try testing.expectEqualStrings("root", second.param);
    try testing.expectEqualStrings("/dev/vda1 quiet", second.value.?);

    var argc: usize = 0;
    var split = try argv_split.argvSplitWithArgc(testing.allocator, command, &argc);
    defer split.deinit(testing.allocator);

    try testing.expectEqual(@as(usize, 3), argc);
    try testing.expectEqualStrings("console=ttyS0", split.argv[0]);
    try testing.expectEqualStrings("root=\"/dev/vda1", split.argv[1]);
    try testing.expectEqualStrings("quiet\"", split.argv[2]);
}

test "phase7 packet keeps string helper replacement and cmdline quoting reviewable" {
    const duplicated = try string_helpers.kstrdupAndReplace(testing.allocator, "ttyS0/early", '/', '_');
    defer testing.allocator.free(duplicated);
    try testing.expectEqualStrings("ttyS0_early", duplicated);

    const quoted = (try string_helpers.kstrdupQuotableCmdline(
        testing.allocator,
        "zig\x00build\n\x22\x00",
    )).?;
    defer testing.allocator.free(quoted);
    try testing.expectEqualStrings("zig build\\x0A\\x22", quoted);
}

test "phase7 packet keeps memparse and integer option expansion explicit" {
    const parsed = cmdline.memparse("64K tail");
    try testing.expectEqual(@as(u64, 64 << 10), parsed.value);
    try testing.expectEqualStrings(" tail", parsed.rest);

    var values = [_]i32{ 0, 0, 0, 0, 0 };
    const rest = cmdline.getOptions("2-4,9", values.len, &values);
    try testing.expectEqualStrings("", rest);
    try testing.expectEqualSlices(i32, &[_]i32{ 4, 2, 3, 4, 9 }, &values);
}

test "phase7 packet keeps cached rbtree ordering stable for parsed values" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var values = [_]i32{ 0, 0, 0, 0, 0 };
    _ = cmdline.getOptions("3-5,8", values.len, &values);

    var entries = [_]Entry{
        .{ .key = values[1] },
        .{ .key = values[2] },
        .{ .key = values[3] },
        .{ .key = values[4] },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    const leftmost = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    const leftmost_entry: *const Entry = @fieldParentPtr("node", leftmost);
    try testing.expectEqual(@as(i32, 3), leftmost_entry.key);

    rbtree.eraseInitCached(&entries[0].node, &root);
    const new_leftmost = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    const new_leftmost_entry: *const Entry = @fieldParentPtr("node", new_leftmost);
    try testing.expectEqual(@as(i32, 4), new_leftmost_entry.key);
}

test "phase7 packet keeps duplicate mode values queryable across argv split cmdline parsing and rbtree matching" {
    const Entry = struct {
        key: [:0]u8,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return std.mem.order(u8, lhs_entry.key, rhs_entry.key) == .lt;
        }
    }.compare;

    const cmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const needle: *const []const u8 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            return switch (std.mem.order(u8, needle.*, entry.key)) {
                .lt => -1,
                .eq => 0,
                .gt => 1,
            };
        }
    }.compare;

    const command = "mode=fast-path mode=fast-path mode=safe";
    var split = try argv_split.argvSplit(testing.allocator, command);
    defer split.deinit(testing.allocator);

    var entries: [3]Entry = undefined;
    var root = rbtree.RootCached.init();

    for (split.argv, 0..) |token, index| {
        const parsed = cmdline.nextArg(token);
        try testing.expectEqualStrings("mode", parsed.param);

        const normalized = try string_helpers.kstrdupAndReplace(
            testing.allocator,
            parsed.value.?,
            '-',
            '_',
        );
        entries[index] = .{ .key = normalized };
        _ = rbtree.addCached(&entries[index].node, &root, less);
    }
    defer for (&entries) |*entry| testing.allocator.free(entry.key);

    const key = "fast_path";
    const first_match = rbtree.findFirst(@ptrCast(&key), &root.root, cmp) orelse {
        return error.TestUnexpectedResult;
    };
    const first_entry: *const Entry = @fieldParentPtr("node", first_match);
    try testing.expectEqualStrings("fast_path", first_entry.key);

    var iterator = rbtree.matchIterator(@ptrCast(&key), &root.root, cmp);
    var count: usize = 0;
    while (iterator.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        try testing.expectEqualStrings("fast_path", entry.key);
        count += 1;
    }

    try testing.expectEqual(@as(usize, 2), count);
    const leftmost = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    const leftmost_entry: *const Entry = @fieldParentPtr("node", leftmost);
    try testing.expectEqualStrings("fast_path", leftmost_entry.key);
}
