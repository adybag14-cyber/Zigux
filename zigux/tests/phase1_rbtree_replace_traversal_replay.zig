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

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    return if (wanted.* < entry.key)
        -1
    else if (wanted.* > entry.key)
        1
    else
        0;
}

test "phase1 lane07 rbtree replaceNode keeps in-order traversal anchored on the replacement" {
    var root = rbtree.Root.init();
    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 12 },
    };
    var replacement = Entry{ .key = 10 };

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    rbtree.replaceNode(&entries[0].node, &replacement.node, &root);

    try std.testing.expectEqual(&entries[1].node, rbtree.first(&root).?);
    try std.testing.expectEqual(&entries[2].node, rbtree.last(&root).?);
    try std.testing.expectEqual(&replacement.node, rbtree.next(&entries[1].node).?);
    try std.testing.expectEqual(&entries[1].node, rbtree.prev(&replacement.node).?);
    try std.testing.expectEqual(&entries[3].node, rbtree.next(&replacement.node).?);
    try std.testing.expectEqual(&replacement.node, rbtree.prev(&entries[3].node).?);
    try std.testing.expectEqual(&entries[2].node, rbtree.next(&entries[3].node).?);

    const key: i32 = 10;
    try std.testing.expectEqual(&replacement.node, rbtree.find(&key, &root, cmpKey).?);
    try std.testing.expectEqual(&replacement.node, rbtree.findFirst(&key, &root, cmpKey).?);
}

test "phase1 lane07 rbtree replace aliases preserve singleton traversal boundaries" {
    var root = rbtree.Root.init();
    var original = Entry{ .key = 7 };
    var replacement = Entry{ .key = 7 };

    rbtree.add(&original.node, &root, less);
    rbtree.rb_replace_node(&original.node, &replacement.node, &root);

    try std.testing.expectEqual(&replacement.node, rbtree.rb_first(&root).?);
    try std.testing.expectEqual(&replacement.node, rbtree.rb_last(&root).?);
    try std.testing.expectEqual(null, rbtree.rb_prev(&replacement.node));
    try std.testing.expectEqual(null, rbtree.rb_next(&replacement.node));

    const key: i32 = 7;
    try std.testing.expectEqual(&replacement.node, rbtree.find(&key, &root, cmpKey).?);
}
