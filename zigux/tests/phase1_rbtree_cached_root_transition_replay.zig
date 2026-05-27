const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    serial: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn firstSerial(root: *const rbtree.RootCached) ?i32 {
    const node = rbtree.firstCached(root) orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.serial;
}

fn returnedSerial(node: ?*rbtree.Node) ?i32 {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return entry.serial;
}

test "phase1 lane06 rbtree cached add and erase transitions keep leftmost return flow stable" {
    var first_entry = Entry{ .key = 10, .serial = 0 };
    var larger_entry = Entry{ .key = 12, .serial = 1 };
    var smaller_entry = Entry{ .key = 5, .serial = 2 };
    var duplicate_entry = Entry{ .key = 5, .serial = 3 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?i32, 0), returnedSerial(rbtree.addCached(&first_entry.node, &root, less)));
    try std.testing.expectEqual(@as(?i32, 0), firstSerial(&root));

    try std.testing.expectEqual(@as(?i32, null), returnedSerial(rbtree.addCached(&larger_entry.node, &root, less)));
    try std.testing.expectEqual(@as(?i32, 0), firstSerial(&root));

    try std.testing.expectEqual(@as(?i32, 2), returnedSerial(rbtree.addCached(&smaller_entry.node, &root, less)));
    try std.testing.expectEqual(@as(?i32, 2), firstSerial(&root));

    try std.testing.expectEqual(@as(?i32, null), returnedSerial(rbtree.addCached(&duplicate_entry.node, &root, less)));
    try std.testing.expectEqual(@as(?i32, 2), firstSerial(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?i32, null), returnedSerial(rbtree.eraseCached(&larger_entry.node, &root)));
    try std.testing.expectEqual(@as(?i32, 2), firstSerial(&root));

    try std.testing.expectEqual(@as(?i32, 3), returnedSerial(rbtree.eraseCached(&smaller_entry.node, &root)));
    try std.testing.expectEqual(@as(?i32, 3), firstSerial(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}

test "phase1 lane06 rbtree cached replacement and detach transitions preserve leftmost alignment" {
    var root_entry = Entry{ .key = 10, .serial = 0 };
    var leftmost_entry = Entry{ .key = 5, .serial = 1 };
    var right_entry = Entry{ .key = 15, .serial = 2 };
    var replacement = Entry{ .key = 10, .serial = 3 };
    var reseed = Entry{ .key = 3, .serial = 4 };
    var root = rbtree.RootCached.init();

    _ = rbtree.addCached(&root_entry.node, &root, less);
    _ = rbtree.addCached(&leftmost_entry.node, &root, less);
    _ = rbtree.addCached(&right_entry.node, &root, less);
    try std.testing.expectEqual(@as(?i32, 1), firstSerial(&root));

    rbtree.replaceNodeCached(&root_entry.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?i32, 1), firstSerial(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&leftmost_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&leftmost_entry.node));
    try std.testing.expectEqual(@as(?i32, 3), firstSerial(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(?i32, 2), firstSerial(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&right_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&right_entry.node));
    try std.testing.expectEqual(@as(?i32, null), firstSerial(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);

    try std.testing.expectEqual(@as(?i32, 4), returnedSerial(rbtree.addCached(&reseed.node, &root, less)));
    try std.testing.expectEqual(@as(?i32, 4), firstSerial(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
