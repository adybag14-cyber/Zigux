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

fn nodeKey(node: ?*rbtree.Node) ?i32 {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return entry.key;
}

test "phase 1 rbtree cached eraseInit replay keeps leftmost promotion aligned" {
    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };

    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_root, less);
    }

    try std.testing.expectEqual(nodeKey(rbtree.firstCached(&primary_root)), nodeKey(rbtree.rb_first_cached(&alias_root)));
    try std.testing.expectEqual(nodeKey(rbtree.first(&primary_root.root)), nodeKey(rbtree.rb_first(&alias_root.root)));

    rbtree.eraseInitCached(&primary_entries[1].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[1].node, &alias_root);

    try std.testing.expect(rbtree.emptyNode(&primary_entries[1].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[1].node));
    try std.testing.expectEqual(nodeKey(rbtree.firstCached(&primary_root)), nodeKey(rbtree.rb_first_cached(&alias_root)));
    try std.testing.expectEqual(nodeKey(rbtree.first(&primary_root.root)), nodeKey(rbtree.rb_first(&alias_root.root)));
    try std.testing.expectEqual(@as(?i32, 10), nodeKey(rbtree.firstCached(&primary_root)));

    rbtree.eraseInitCached(&primary_entries[0].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[0].node, &alias_root);

    try std.testing.expect(rbtree.emptyNode(&primary_entries[0].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[0].node));
    try std.testing.expectEqual(nodeKey(rbtree.firstCached(&primary_root)), nodeKey(rbtree.rb_first_cached(&alias_root)));
    try std.testing.expectEqual(nodeKey(rbtree.first(&primary_root.root)), nodeKey(rbtree.rb_first(&alias_root.root)));
    try std.testing.expectEqual(@as(?i32, 15), nodeKey(rbtree.firstCached(&primary_root)));
}

test "phase 1 rbtree cached eraseInit replay clears singleton roots before reseed" {
    var primary_first = Entry{ .key = 10 };
    var alias_first = Entry{ .key = 10 };
    var primary_second = Entry{ .key = 6 };
    var alias_second = Entry{ .key = 6 };

    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    _ = rbtree.addCached(&primary_first.node, &primary_root, less);
    _ = rbtree.rb_add_cached(&alias_first.node, &alias_root, less);

    rbtree.eraseInitCached(&primary_first.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_first.node, &alias_root);

    try std.testing.expect(rbtree.emptyNode(&primary_first.node));
    try std.testing.expect(rbtree.emptyNode(&alias_first.node));
    try std.testing.expect(rbtree.next(&primary_first.node) == null);
    try std.testing.expect(rbtree.rb_next(&alias_first.node) == null);
    try std.testing.expect(rbtree.prev(&primary_first.node) == null);
    try std.testing.expect(rbtree.rb_prev(&alias_first.node) == null);
    try std.testing.expectEqual(nodeKey(primary_root.root.node), nodeKey(alias_root.root.node));
    try std.testing.expectEqual(nodeKey(rbtree.firstCached(&primary_root)), nodeKey(rbtree.rb_first_cached(&alias_root)));

    _ = rbtree.addCached(&primary_second.node, &primary_root, less);
    _ = rbtree.rb_add_cached(&alias_second.node, &alias_root, less);

    try std.testing.expectEqual(nodeKey(rbtree.firstCached(&primary_root)), nodeKey(rbtree.rb_first_cached(&alias_root)));
    try std.testing.expectEqual(nodeKey(rbtree.first(&primary_root.root)), nodeKey(rbtree.rb_first(&alias_root.root)));
    try std.testing.expectEqual(@as(?i32, 6), nodeKey(rbtree.firstCached(&primary_root)));
}
