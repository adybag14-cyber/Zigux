const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryKey(node: *const rbtree.Node) i32 {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn wireShape(root: *rbtree.Root, entries: []Entry) void {
    root.node = &entries[0].node;
    entries[0].node.parent = null;
    entries[0].node.left = &entries[1].node;
    entries[0].node.right = null;

    entries[1].node.parent = &entries[0].node;
    entries[1].node.left = null;
    entries[1].node.right = &entries[2].node;

    entries[2].node.parent = &entries[1].node;
    entries[2].node.left = null;
    entries[2].node.right = null;
}

fn collectPostorder(root: *const rbtree.Root, use_aliases: bool) [3]i32 {
    var order: [3]i32 = undefined;
    var count: usize = 0;
    var cursor = if (use_aliases) rbtree.rb_first_postorder(root) else rbtree.firstPostorder(root);
    while (cursor) |node| : (cursor = if (use_aliases) rbtree.rb_next_postorder(node) else rbtree.nextPostorder(node)) {
        order[count] = entryKey(node);
        count += 1;
    }
    std.debug.assert(count == order.len);
    return order;
}

test "phase 1 rbtree postorder review replay keeps left-deep and right-sibling branches exact" {
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

    const primary_order = collectPostorder(&root, false);
    const alias_order = collectPostorder(&root, true);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 3, 2 }, &primary_order);
    try std.testing.expectEqualSlices(i32, &primary_order, &alias_order);
}

test "phase 1 rbtree postorder review replay unwinds parents when no right sibling subtree exists" {
    var primary_entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 6 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 6 },
    };
    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    wireShape(&primary_root, &primary_entries);
    wireShape(&alias_root, &alias_entries);

    const primary_order = collectPostorder(&primary_root, false);
    const alias_order = collectPostorder(&alias_root, true);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 6, 4, 8 }, &primary_order);
    try std.testing.expectEqualSlices(i32, &primary_order, &alias_order);
}

test "phase 1 rbtree postorder review replay keeps the null contract explicit" {
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextPostorder(null));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_next_postorder(null));
}
