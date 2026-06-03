const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn nodeKey(node: ?*rbtree.Node) ?i32 {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return entry.key;
}

test "replaceNodeCached promotes replacement when victim is cached leftmost" {
    var leftmost = Entry{ .key = 5 };
    var middle = Entry{ .key = 10 };
    var rightmost = Entry{ .key = 20 };
    var replacement = Entry{ .key = 5 };
    var root = rbtree.RootCached.init();

    _ = rbtree.addCached(&middle.node, &root, less);
    _ = rbtree.addCached(&leftmost.node, &root, less);
    _ = rbtree.addCached(&rightmost.node, &root, less);

    try std.testing.expectEqual(@as(?i32, 5), nodeKey(rbtree.firstCached(&root)));

    rbtree.replaceNodeCached(&leftmost.node, &replacement.node, &root);

    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?i32, 5), nodeKey(rbtree.first(&root.root)));
    try std.testing.expectEqual(@as(?i32, 10), nodeKey(rbtree.next(&replacement.node)));
    try std.testing.expectEqual(@as(?i32, null), nodeKey(rbtree.prev(&replacement.node)));
}

test "rb_replace_node_cached mirrors leftmost replacement semantics" {
    var leftmost = Entry{ .key = 3 };
    var middle = Entry{ .key = 8 };
    var rightmost = Entry{ .key = 13 };
    var replacement = Entry{ .key = 3 };
    var root = rbtree.RootCached.init();

    _ = rbtree.rb_add_cached(&middle.node, &root, less);
    _ = rbtree.rb_add_cached(&leftmost.node, &root, less);
    _ = rbtree.rb_add_cached(&rightmost.node, &root, less);

    try std.testing.expectEqual(@as(?i32, 3), nodeKey(rbtree.rb_first_cached(&root)));

    rbtree.rb_replace_node_cached(&leftmost.node, &replacement.node, &root);

    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?i32, 3), nodeKey(rbtree.rb_first(&root.root)));
    try std.testing.expectEqual(@as(?i32, 8), nodeKey(rbtree.rb_next(&replacement.node)));
    try std.testing.expectEqual(@as(?i32, null), nodeKey(rbtree.rb_prev(&replacement.node)));
}
