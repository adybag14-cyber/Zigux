const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn entryFromNodeMut(node: *rbtree.Node) *Entry {
    return @fieldParentPtr("node", node);
}

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    return entryFromNode(lhs).key < entryFromNode(rhs).key;
}

fn cmpNodes(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    return if (entryFromNode(lhs).key < entryFromNode(rhs).key)
        -1
    else if (entryFromNode(lhs).key > entryFromNode(rhs).key)
        1
    else
        0;
}

fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const i32 = @ptrCast(@alignCast(key_ptr));
    return if (key.* < entryFromNode(node).key)
        -1
    else if (key.* > entryFromNode(node).key)
        1
    else
        0;
}

fn expectOrder(root: *const rbtree.RootCached, expected: []const i32) !void {
    var idx: usize = 0;
    var cursor = rbtree.rb_first_cached(root);
    while (cursor) |node| : (cursor = rbtree.rb_next(node)) {
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], entryFromNode(node).key);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);
}

test "phase1 rbtree cached replay keeps leftmost updates and erase aliases aligned" {
    var entries = [_]Entry{
        .{ .key = 4 },
        .{ .key = 1 },
        .{ .key = 7 },
        .{ .key = 2 },
        .{ .key = 6 },
    };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_first_cached(&root));

    try std.testing.expectEqual(&entries[0].node, rbtree.rb_add_cached(&entries[0].node, &root, less).?);
    try std.testing.expectEqual(&entries[1].node, rbtree.rb_add_cached(&entries[1].node, &root, less).?);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[2].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[3].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[4].node, &root, less));

    try std.testing.expectEqual(@as(i32, 1), entryFromNode(rbtree.rb_first_cached(&root).?).key);
    try std.testing.expectEqual(@as(i32, 7), entryFromNode(rbtree.rb_last(&root.root).?).key);
    try expectOrder(&root, &[_]i32{ 1, 2, 4, 6, 7 });

    const promoted_leftmost = rbtree.rb_erase_cached(&entries[1].node, &root).?;
    try std.testing.expectEqual(@as(i32, 2), entryFromNode(promoted_leftmost).key);
    try std.testing.expectEqual(@as(i32, 2), entryFromNode(rbtree.rb_first_cached(&root).?).key);

    rbtree.rb_erase_init_cached(&entries[3].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));
    try std.testing.expectEqual(@as(i32, 4), entryFromNode(rbtree.rb_first_cached(&root).?).key);
    try expectOrder(&root, &[_]i32{ 4, 6, 7 });
}

test "phase1 rbtree cached replay rejects duplicate keyed inserts without shifting leftmost" {
    var entries = [_]Entry{
        .{ .key = 5 },
        .{ .key = 3 },
        .{ .key = 7 },
    };
    var duplicate = Entry{ .key = 5 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&entries[0].node, &root, cmpNodes));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&entries[1].node, &root, cmpNodes));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&entries[2].node, &root, cmpNodes));

    const duplicate_hit = rbtree.rb_find_add_cached(&duplicate.node, &root, cmpNodes).?;
    try std.testing.expectEqual(@as(i32, 5), entryFromNode(duplicate_hit).key);
    try std.testing.expectEqual(@as(i32, 3), entryFromNode(rbtree.rb_first_cached(&root).?).key);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), duplicate.node.parent);

    const key: i32 = 5;
    try std.testing.expectEqual(&entries[0].node, rbtree.find(&key, &root.root, cmpKey).?);
    try std.testing.expectEqual(&entries[0].node, rbtree.findFirst(&key, &root.root, cmpKey).?);
    try expectOrder(&root, &[_]i32{ 3, 5, 7 });
}

test "phase1 rbtree cached replay keeps cached replacement pointed at the new leftmost node" {
    var entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 3 },
        .{ .key = 11 },
    };
    var replacement = Entry{ .key = 3 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, less);
    }

    rbtree.rb_replace_node_cached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(i32, 3), entryFromNode(rbtree.rb_first_cached(&root).?).key);
    try std.testing.expectEqual(&replacement.node, rbtree.rb_first_cached(&root).?);
    try std.testing.expectEqual(@as(i32, 11), entryFromNode(rbtree.rb_last(&root.root).?).key);

    const leftmost_entry = entryFromNodeMut(rbtree.rb_first_cached(&root).?);
    try std.testing.expectEqual(@as(i32, 3), leftmost_entry.key);
    try expectOrder(&root, &[_]i32{ 3, 8, 11 });
}
