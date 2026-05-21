const std = @import("std");
const rbtree = @import("../../lib/rbtree.zig");

test "phase 7 rbtree companion replays ordered traversal and duplicate-range helpers" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const key_cmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var order: [entries.len]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(entries.len, count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 10, 10, 15, 20 }, order[0..count]);
    try std.testing.expectEqual(rbtree.first(&root), rbtree.rb_first(&root));

    const duplicate = @as(i32, 10);
    const first_match = rbtree.findFirst(&duplicate, &root, key_cmp) orelse return error.TestUnexpectedResult;
    const alias_first_match = rbtree.rb_find_first(&duplicate, &root, key_cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(first_match, alias_first_match);

    var serials: [3]usize = undefined;
    var serial_count: usize = 0;
    var cursor = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", cursor);
        serials[serial_count] = entry.serial;
        serial_count += 1;
        cursor = rbtree.nextMatch(&duplicate, cursor, key_cmp) orelse break;
    }

    try std.testing.expectEqual(@as(usize, 3), serial_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..serial_count]);
    try std.testing.expect(rbtree.rb_next_match(&duplicate, cursor, key_cmp) == null);

    var iter = rbtree.matchIterator(&duplicate, &root, key_cmp);
    var iter_serials: [3]usize = undefined;
    var iter_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        iter_serials[iter_count] = entry.serial;
        iter_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), iter_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, iter_serials[0..iter_count]);

    var alias_iter = rbtree.rb_match_iterator(&duplicate, &root, key_cmp);
    var alias_iter_serials: [3]usize = undefined;
    var alias_iter_count: usize = 0;
    while (alias_iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_iter_serials[alias_iter_count] = entry.serial;
        alias_iter_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), alias_iter_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, alias_iter_serials[0..alias_iter_count]);
}

test "phase 7 rbtree companion replays cached-leftmost promotion and erase-init ownership boundaries" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    var first_entry = Entry{ .key = 10, .serial = 0 };
    var leftmost_entry = Entry{ .key = 5, .serial = 1 };
    var larger_entry = Entry{ .key = 15, .serial = 2 };
    var duplicate_entry = Entry{ .key = 10, .serial = 3 };
    var replacement_entry = Entry{ .key = 10, .serial = 4 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.addCached(&first_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.rb_add_cached(&leftmost_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.rb_first_cached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&larger_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.firstCached(&root));

    const existing = rbtree.findAddCached(&duplicate_entry.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &first_entry.node), existing);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.firstCached(&root));

    const promoted = rbtree.eraseCached(&leftmost_entry.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &first_entry.node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&first_entry.node, &replacement_entry.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&replacement_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &larger_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.rb_erase_init_cached(&larger_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&larger_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);
}

test "phase 7 rbtree companion replays plain erase-init ownership boundaries" {
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

    var root_entry = Entry{ .key = 10 };
    var left_entry = Entry{ .key = 5 };
    var right_entry = Entry{ .key = 15 };
    var reseed_entry = Entry{ .key = 12 };
    var root = rbtree.Root.init();

    rbtree.add(&root_entry.node, &root, less);
    rbtree.add(&left_entry.node, &root, less);
    rbtree.add(&right_entry.node, &root, less);

    rbtree.eraseInit(&root_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&root_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_entry.node), rbtree.first(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &right_entry.node), rbtree.last(&root));
    try std.testing.expect(rbtree.prev(&left_entry.node) == null);

    var order: [2]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 15 }, order[0..count]);

    rbtree.eraseInit(&left_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&left_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &right_entry.node), rbtree.first(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &right_entry.node), rbtree.last(&root));
    try std.testing.expect(rbtree.prev(&right_entry.node) == null);
    try std.testing.expect(rbtree.next(&right_entry.node) == null);

    rbtree.eraseInit(&right_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&right_entry.node));
    try std.testing.expect(rbtree.emptyRoot(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.node);

    rbtree.add(&reseed_entry.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed_entry.node), root.node);
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed_entry.node), rbtree.first(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed_entry.node), rbtree.last(&root));
}

test "phase 7 rbtree companion replays postorder aliases and null-stop handling" {
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

    var entries = [_]Entry{
        .{ .key = 2 },
        .{ .key = 1 },
        .{ .key = 3 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var order: [entries.len]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.firstPostorder(&root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 3, 2 }, order[0..count]);
    try std.testing.expectEqual(rbtree.firstPostorder(&root), rbtree.rb_first_postorder(&root));

    const first_postorder = rbtree.firstPostorder(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(rbtree.nextPostorder(first_postorder), rbtree.rb_next_postorder(rbtree.rb_first_postorder(&root)));
    try std.testing.expect(rbtree.nextPostorder(null) == null);
    try std.testing.expect(rbtree.rb_next_postorder(null) == null);
}

test "phase 7 rbtree companion replays reverse traversal aliases and detached null stops" {
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

    var entries = [_]Entry{
        .{ .key = 2 },
        .{ .key = 1 },
        .{ .key = 3 },
        .{ .key = 4 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    try std.testing.expectEqual(rbtree.last(&root), rbtree.rb_last(&root));

    var order: [entries.len]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.last(&root);
    while (current) |node| : (current = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(entries.len, count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 3, 2, 1 }, order[0..count]);

    const alias_last = rbtree.rb_last(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(rbtree.prev(alias_last), rbtree.rb_prev(alias_last));

    const first_node = rbtree.first(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expect(rbtree.prev(first_node) == null);
    try std.testing.expect(rbtree.rb_prev(first_node) == null);

    var detached = rbtree.Node.init();
    rbtree.clearNode(&detached);
    try std.testing.expect(rbtree.prev(&detached) == null);
    try std.testing.expect(rbtree.rb_prev(&detached) == null);
}
