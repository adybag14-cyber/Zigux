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

fn collectOrder(root: *const rbtree.Root, buffer: []i32) usize {
    var count: usize = 0;
    var current = rbtree.first(root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        buffer[count] = entry.key;
        count += 1;
    }
    return count;
}

test "phase1 rbtree eraseInit detaches a plain-root node and preserves sorted traversal" {
    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var root = rbtree.Root.init();

    try std.testing.expect(rbtree.emptyRoot(&root));

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    rbtree.eraseInit(&entries[0].node, &root);

    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expect(rbtree.next(&entries[0].node) == null);
    try std.testing.expect(rbtree.prev(&entries[0].node) == null);
    try std.testing.expect(!rbtree.emptyRoot(&root));

    var order: [3]i32 = undefined;
    const count = collectOrder(&root, &order);
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 15, 20 }, order[0..count]);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.first(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.last(&root));
}

test "phase1 rbtree eraseInit clears singleton roots before reseed" {
    var first_entry = Entry{ .key = 10 };
    var second_entry = Entry{ .key = 6 };
    var root = rbtree.Root.init();

    rbtree.add(&first_entry.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), root.node);
    try std.testing.expect(!rbtree.emptyRoot(&root));

    rbtree.eraseInit(&first_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&first_entry.node));
    try std.testing.expect(rbtree.emptyRoot(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.node);

    rbtree.add(&second_entry.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &second_entry.node), root.node);
    try std.testing.expectEqual(@as(?*rbtree.Node, &second_entry.node), rbtree.first(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &second_entry.node), rbtree.last(&root));
}
