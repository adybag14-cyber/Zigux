const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    serial: u8,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key == rhs_entry.key) {
        return lhs_entry.serial < rhs_entry.serial;
    }
    return lhs_entry.key < rhs_entry.key;
}

fn identity(node: ?*rbtree.Node) ?struct { i32, u8 } {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

fn expectOrder(root: *const rbtree.RootCached, expected: []const i32) !void {
    var actual: [16]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.firstCached(root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        actual[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(expected.len, count);
    try std.testing.expectEqualSlices(i32, expected, actual[0..count]);
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(root));
}

fn insertCachedPrimary(root: *rbtree.RootCached, entry: *Entry) void {
    var link = &root.root.node;
    var parent: ?*rbtree.Node = null;
    var leftmost = true;

    while (link.*) |current| {
        parent = current;
        if (less(&entry.node, current)) {
            link = &current.left;
        } else {
            link = &current.right;
            leftmost = false;
        }
    }

    rbtree.linkNode(&entry.node, parent, link);
    rbtree.insertColorCached(&entry.node, root, leftmost);
}

fn insertCachedAlias(root: *rbtree.RootCached, entry: *Entry) void {
    var link = &root.root.node;
    var parent: ?*rbtree.Node = null;
    var leftmost = true;

    while (link.*) |current| {
        parent = current;
        if (less(&entry.node, current)) {
            link = &current.left;
        } else {
            link = &current.right;
            leftmost = false;
        }
    }

    rbtree.linkNode(&entry.node, parent, link);
    rbtree.rb_insert_color_cached(&entry.node, root, leftmost);
}

test "phase1 rbtree low-level cached insert aliases keep leftmost and order aligned" {
    var primary_entries = [_]Entry{
        .{ .key = 20, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 30, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 15, .serial = 4 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 20, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 30, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 15, .serial = 4 },
    };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expect(rbtree.emptyRoot(&primary_root.root));
    try std.testing.expect(rbtree.emptyRoot(&alias_root.root));

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        insertCachedPrimary(&primary_root, primary_entry);
        insertCachedAlias(&alias_root, alias_entry);
    }

    try expectOrder(&primary_root, &.{ 5, 10, 15, 20, 30 });
    try expectOrder(&alias_root, &.{ 5, 10, 15, 20, 30 });
    try std.testing.expectEqual(identity(rbtree.firstCached(&primary_root)), identity(rbtree.rb_first_cached(&alias_root)));
    try std.testing.expectEqual(identity(rbtree.rb_last(&primary_root.root)), identity(rbtree.last(&alias_root.root)));
}

test "phase1 rbtree low-level replace aliases keep cached leftmost stable" {
    var primary_entries = [_]Entry{
        .{ .key = 20, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 30, .serial = 2 },
        .{ .key = 25, .serial = 3 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 20, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 30, .serial = 2 },
        .{ .key = 25, .serial = 3 },
    };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.addCached(&alias_entry.node, &alias_root, less);
    }

    var primary_replacement = Entry{ .key = 30, .serial = 9 };
    var alias_replacement = Entry{ .key = 30, .serial = 9 };

    rbtree.replaceNodeCached(&primary_entries[2].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_entries[2].node, &alias_replacement.node, &alias_root);

    try expectOrder(&primary_root, &.{ 10, 20, 25, 30 });
    try expectOrder(&alias_root, &.{ 10, 20, 25, 30 });
    try std.testing.expectEqual(identity(rbtree.firstCached(&primary_root)), identity(rbtree.firstCached(&alias_root)));
    try std.testing.expectEqual(identity(rbtree.rb_prev(&primary_replacement.node)), identity(rbtree.prev(&alias_replacement.node)));
    try std.testing.expectEqual(identity(rbtree.next(&primary_entries[3].node)), identity(rbtree.rb_next(&alias_entries[3].node)));
}

test "phase1 rbtree low-level erase-init aliases clear detached cached nodes" {
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
    var spare = rbtree.Node.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.addCached(&alias_entry.node, &alias_root, less);
    }

    rbtree.clearNode(&spare);
    try std.testing.expect(rbtree.emptyNode(&spare));

    rbtree.eraseInitCached(&primary_entries[1].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[1].node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_entries[1].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[1].node));
    try std.testing.expectEqual(identity(rbtree.firstCached(&primary_root)), identity(rbtree.firstCached(&alias_root)));
    try std.testing.expectEqual(identity(rbtree.firstCached(&primary_root)), .{ 10, 0 });

    rbtree.eraseInitCached(&primary_entries[0].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[0].node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_entries[0].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[0].node));
    try std.testing.expectEqual(identity(rbtree.firstCached(&primary_root)), identity(rbtree.firstCached(&alias_root)));
    try std.testing.expectEqual(identity(rbtree.firstCached(&primary_root)), .{ 15, 2 });

    rbtree.eraseInitCached(&primary_entries[2].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[2].node, &alias_root);
    try std.testing.expect(rbtree.emptyRoot(&primary_root.root));
    try std.testing.expect(rbtree.emptyRoot(&alias_root.root));
    try std.testing.expect(rbtree.firstCached(&primary_root) == null);
    try std.testing.expect(rbtree.firstCached(&alias_root) == null);
}
