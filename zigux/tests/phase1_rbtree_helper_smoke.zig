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

fn cmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn identity(node: ?*rbtree.Node) ?struct { i32, usize } {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

fn leftmostKey(root: *const rbtree.RootCached) ?i32 {
    const node = rbtree.firstCached(root) orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

test "phase1 dedicated rbtree smoke keeps cached alias misses and duplicates aligned" {
    var primary_first = Entry{ .key = 10, .serial = 0 };
    var alias_first = Entry{ .key = 10, .serial = 0 };
    var primary_leftmost = Entry{ .key = 5, .serial = 1 };
    var alias_leftmost = Entry{ .key = 5, .serial = 1 };
    var primary_larger = Entry{ .key = 15, .serial = 2 };
    var alias_larger = Entry{ .key = 15, .serial = 2 };
    var primary_duplicate = Entry{ .key = 10, .serial = 3 };
    var alias_duplicate = Entry{ .key = 10, .serial = 3 };

    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_first.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_first.node, &alias_root, cmp));
    try std.testing.expectEqual(leftmostKey(&primary_root), leftmostKey(&alias_root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_leftmost.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_leftmost.node, &alias_root, cmp));
    try std.testing.expectEqual(leftmostKey(&primary_root), leftmostKey(&alias_root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_larger.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_larger.node, &alias_root, cmp));
    try std.testing.expectEqual(leftmostKey(&primary_root), leftmostKey(&alias_root));

    const primary_existing = rbtree.findAddCached(&primary_duplicate.node, &primary_root, cmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(identity(primary_existing), identity(alias_existing));
    try std.testing.expectEqual(@as(?i32, 5), leftmostKey(&primary_root));
    try std.testing.expectEqual(leftmostKey(&primary_root), leftmostKey(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.firstCached(&alias_root));
}

test "phase1 dedicated rbtree smoke keeps cached replacement and detach aliases aligned" {
    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 20, .serial = 2 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 20, .serial = 2 },
    };
    var primary_replacement = Entry{ .key = 20, .serial = 4 };
    var alias_replacement = Entry{ .key = 20, .serial = 4 };

    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_root, less);
    }

    try std.testing.expectEqual(@as(?i32, 5), leftmostKey(&primary_root));
    try std.testing.expectEqual(leftmostKey(&primary_root), leftmostKey(&alias_root));

    rbtree.replaceNodeCached(&primary_entries[2].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_entries[2].node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(@as(?i32, 5), leftmostKey(&primary_root));
    try std.testing.expectEqual(leftmostKey(&primary_root), leftmostKey(&alias_root));

    rbtree.eraseInitCached(&primary_entries[1].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[1].node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_entries[1].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[1].node));
    try std.testing.expectEqual(leftmostKey(&primary_root), leftmostKey(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.firstCached(&alias_root));
}

test "phase1 dedicated rbtree smoke clears singleton cached roots before alias reseed" {
    var primary_first = Entry{ .key = 7, .serial = 0 };
    var alias_first = Entry{ .key = 7, .serial = 0 };
    var primary_second = Entry{ .key = 3, .serial = 1 };
    var alias_second = Entry{ .key = 3, .serial = 1 };

    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    _ = rbtree.addCached(&primary_first.node, &primary_root, less);
    _ = rbtree.rb_add_cached(&alias_first.node, &alias_root, less);
    try std.testing.expectEqual(@as(?i32, 7), leftmostKey(&primary_root));
    try std.testing.expectEqual(leftmostKey(&primary_root), leftmostKey(&alias_root));

    try std.testing.expectEqual(identity(rbtree.eraseCached(&primary_first.node, &primary_root)), identity(rbtree.rb_erase_cached(&alias_first.node, &alias_root)));
    try std.testing.expectEqual(@as(?i32, null), leftmostKey(&primary_root));
    try std.testing.expectEqual(leftmostKey(&primary_root), leftmostKey(&alias_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), primary_root.root.node);
    try std.testing.expectEqual(primary_root.root.node, alias_root.root.node);

    _ = rbtree.addCached(&primary_second.node, &primary_root, less);
    _ = rbtree.rb_add_cached(&alias_second.node, &alias_root, less);
    try std.testing.expectEqual(@as(?i32, 3), leftmostKey(&primary_root));
    try std.testing.expectEqual(leftmostKey(&primary_root), leftmostKey(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.firstCached(&alias_root));
}
