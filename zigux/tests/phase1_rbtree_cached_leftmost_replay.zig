const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    serial: usize = 0,
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

fn cmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

test "phase1 rbtree cached replay returns leftmost only for fresh minimum inserts" {
    var first_entry = Entry{ .key = 10, .serial = 0 };
    var larger_entry = Entry{ .key = 12, .serial = 1 };
    var smaller_entry = Entry{ .key = 5, .serial = 2 };
    var duplicate_entry = Entry{ .key = 5, .serial = 3 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.addCached(&first_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&larger_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &smaller_entry.node), rbtree.addCached(&smaller_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &smaller_entry.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&duplicate_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &smaller_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}

test "phase1 rbtree cached replay promotes and replaces the cached leftmost pointer" {
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var replacement = Entry{ .key = 10, .serial = 3 };
    var new_leftmost = Entry{ .key = 3, .serial = 4 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_erase_cached(&entries[2].node, &root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_erase_cached(&entries[1].node, &root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    rbtree.rb_replace_node_cached(&entries[0].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &new_leftmost.node), rbtree.rb_add_cached(&new_leftmost.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &new_leftmost.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}

test "phase1 rbtree cached replay keeps duplicate lookups and singleton reseed aligned" {
    var root_entry = Entry{ .key = 10, .serial = 0 };
    var leftmost = Entry{ .key = 5, .serial = 1 };
    var larger = Entry{ .key = 15, .serial = 2 };
    var duplicate = Entry{ .key = 10, .serial = 3 };
    var reseed = Entry{ .key = 6, .serial = 4 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&root_entry.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&leftmost.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&larger.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.findAddCached(&duplicate.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&leftmost.node, &root);
    try std.testing.expect(rbtree.emptyNode(&leftmost.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&root_entry.node, &root);
    rbtree.eraseInitCached(&larger.node, &root);
    try std.testing.expect(rbtree.emptyNode(&root_entry.node));
    try std.testing.expect(rbtree.emptyNode(&larger.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&reseed.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
