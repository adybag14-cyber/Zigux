const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    serial: usize,
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

fn cmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn nodeIdentity(node: ?*rbtree.Node) ?struct { i32, usize } {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

fn firstKey(root: *const rbtree.RootCached) ?i32 {
    const node = rbtree.firstCached(root) orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

test "phase 1 rbtree cached review replay keeps low-level aliases and postorder traversal aligned" {
    var root = rbtree.Root.init();
    try std.testing.expect(rbtree.emptyRoot(&root));

    var detached = rbtree.Node.init();
    rbtree.clearNode(&detached);
    try std.testing.expect(rbtree.emptyNode(&detached));
    try std.testing.expect(rbtree.next(&detached) == null);
    try std.testing.expect(rbtree.prev(&detached) == null);

    var entries = [_]Entry{
        .{ .key = 2, .serial = 0 },
        .{ .key = 1, .serial = 1 },
        .{ .key = 3, .serial = 2 },
    };
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var primary_count: usize = 0;
    var alias_count: usize = 0;
    var cursor = rbtree.firstPostorder(&root);
    while (cursor) |node| : (cursor = rbtree.nextPostorder(node)) {
        primary_count += 1;
    }
    cursor = rbtree.rb_first_postorder(&root);
    while (cursor) |node| : (cursor = rbtree.rb_next_postorder(node)) {
        alias_count += 1;
    }

    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqual(@as(usize, 3), primary_count);
    try std.testing.expectEqual(rbtree.firstPostorder(&root), rbtree.rb_first_postorder(&root));
    try std.testing.expectEqual(rbtree.nextPostorder(rbtree.firstPostorder(&root)), rbtree.rb_next_postorder(rbtree.rb_first_postorder(&root)));
}

test "phase 1 rbtree cached review replay keeps cached-root aliases aligned across leftmost transitions" {
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

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
    for (&primary_entries, &alias_entries) |*primary, *alias| {
        try std.testing.expectEqual(nodeIdentity(rbtree.addCached(&primary.node, &primary_root, less)), nodeIdentity(rbtree.rb_add_cached(&alias.node, &alias_root, less)));
    }
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    var primary_duplicate = Entry{ .key = 10, .serial = 3 };
    var alias_duplicate = Entry{ .key = 10, .serial = 3 };
    try std.testing.expectEqual(
        nodeIdentity(rbtree.findAddCached(&primary_duplicate.node, &primary_root, cmpNode)),
        nodeIdentity(rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, cmpNode)),
    );
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    try std.testing.expectEqual(
        nodeIdentity(rbtree.eraseCached(&primary_entries[1].node, &primary_root)),
        nodeIdentity(rbtree.rb_erase_cached(&alias_entries[1].node, &alias_root)),
    );
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    var primary_replacement = Entry{ .key = 10, .serial = 4 };
    var alias_replacement = Entry{ .key = 10, .serial = 4 };
    rbtree.replaceNodeCached(&primary_entries[0].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_entries[0].node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));
    try std.testing.expectEqual(nodeIdentity(rbtree.firstCached(&primary_root)), nodeIdentity(rbtree.rb_first_cached(&alias_root)));

    rbtree.eraseInitCached(&primary_replacement.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_replacement.node, &alias_root);
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));
    try std.testing.expectEqual(nodeIdentity(rbtree.first(&primary_root.root)), nodeIdentity(rbtree.firstCached(&primary_root)));
    try std.testing.expectEqual(nodeIdentity(rbtree.first(&alias_root.root)), nodeIdentity(rbtree.rb_first_cached(&alias_root)));
}

test "phase 1 rbtree cached review replay keeps singleton cached-root reseed visible" {
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    var primary_first = Entry{ .key = 8, .serial = 0 };
    var alias_first = Entry{ .key = 8, .serial = 0 };
    _ = rbtree.addCached(&primary_first.node, &primary_root, less);
    _ = rbtree.rb_add_cached(&alias_first.node, &alias_root, less);

    rbtree.eraseInitCached(&primary_first.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_first.node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_first.node));
    try std.testing.expect(rbtree.emptyNode(&alias_first.node));
    try std.testing.expectEqual(nodeIdentity(rbtree.firstCached(&primary_root)), nodeIdentity(rbtree.rb_first_cached(&alias_root)));

    var primary_second = Entry{ .key = 6, .serial = 1 };
    var alias_second = Entry{ .key = 6, .serial = 1 };
    try std.testing.expectEqual(
        nodeIdentity(rbtree.addCached(&primary_second.node, &primary_root, less)),
        nodeIdentity(rbtree.rb_add_cached(&alias_second.node, &alias_root, less)),
    );
    try std.testing.expectEqual(nodeIdentity(rbtree.firstCached(&primary_root)), nodeIdentity(rbtree.rb_first_cached(&alias_root)));
    try std.testing.expectEqual(nodeIdentity(rbtree.first(&primary_root.root)), nodeIdentity(rbtree.firstCached(&primary_root)));
    try std.testing.expectEqual(nodeIdentity(rbtree.first(&alias_root.root)), nodeIdentity(rbtree.rb_first_cached(&alias_root)));
}
