const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn attachRoot(root: *rbtree.Root, entry: *Entry) void {
    rbtree.linkNode(&entry.node, null, &root.node);
    entry.node.color = .black;
}

fn expectManualTraversalOrder() !void {
    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 2 },
        .{ .key = 7 },
        .{ .key = 12 },
    };
    var root = rbtree.Root.init();

    attachRoot(&root, &entries[0]);
    rbtree.linkNode(&entries[1].node, &entries[0].node, &entries[0].node.left);
    rbtree.linkNode(&entries[2].node, &entries[0].node, &entries[0].node.right);
    rbtree.linkNode(&entries[3].node, &entries[1].node, &entries[1].node.left);
    rbtree.linkNode(&entries[4].node, &entries[1].node, &entries[1].node.right);
    rbtree.linkNode(&entries[5].node, &entries[2].node, &entries[2].node.left);

    const expected = [_]i32{ 2, 5, 7, 10, 12, 15 };
    var actual: [expected.len]i32 = undefined;
    var index: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        actual[index] = entry.key;
        index += 1;
    }

    try std.testing.expectEqual(expected.len, index);
    try std.testing.expectEqualSlices(i32, &expected, actual[0..index]);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.last(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.next(&entries[4].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[5].node), rbtree.prev(&entries[2].node));
}

test "phase 7 rbtree module imports cleanly" {
    _ = rbtree;
}

test "phase 7 rbtree traversal helpers walk a manually linked tree" {
    try expectManualTraversalOrder();
}

test "phase 7 rbtree replaceNode and postorder helpers preserve structure" {
    var root_entry = Entry{ .key = 10 };
    var left_entry = Entry{ .key = 5 };
    var right_entry = Entry{ .key = 15 };
    var left_left_entry = Entry{ .key = 2 };
    var replacement = Entry{ .key = 5 };
    var root = rbtree.Root.init();

    attachRoot(&root, &root_entry);
    rbtree.linkNode(&left_entry.node, &root_entry.node, &root_entry.node.left);
    rbtree.linkNode(&right_entry.node, &root_entry.node, &root_entry.node.right);
    rbtree.linkNode(&left_left_entry.node, &left_entry.node, &left_entry.node.left);

    rbtree.replaceNode(&left_entry.node, &replacement.node, &root);

    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), root_entry.node.left);
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_left_entry.node), rbtree.first(&root));

    var count: usize = 0;
    var current = rbtree.firstPostorder(&root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
}

test "phase 7 rbtree clearNode marks detached nodes as empty" {
    var node = rbtree.Node.init();

    try std.testing.expect(!rbtree.emptyNode(&node));
    try std.testing.expect(rbtree.emptyRoot(&rbtree.Root.init()));

    rbtree.clearNode(&node);

    try std.testing.expect(rbtree.emptyNode(&node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.next(&node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(&node));
}
