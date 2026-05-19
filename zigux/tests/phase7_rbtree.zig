const std = @import("std");
const rbtree = @import("../../tools/lib/rbtree.zig");

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
