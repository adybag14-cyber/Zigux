const std = @import("std");
const rbtree = @import("rbtree");

const OrderedEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn orderedLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const OrderedEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const OrderedEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn orderedCmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const OrderedEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const OrderedEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn recordForward(root: *const rbtree.Root, use_aliases: bool, out: []i32) usize {
    var count: usize = 0;
    var current = if (use_aliases) rbtree.rb_first(root) else rbtree.first(root);
    while (current) |node| : (current = if (use_aliases) rbtree.rb_next(node) else rbtree.next(node)) {
        const entry: *const OrderedEntry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

fn recordReverse(root: *const rbtree.Root, use_aliases: bool, out: []i32) usize {
    var count: usize = 0;
    var current = if (use_aliases) rbtree.rb_last(root) else rbtree.last(root);
    while (current) |node| : (current = if (use_aliases) rbtree.rb_prev(node) else rbtree.prev(node)) {
        const entry: *const OrderedEntry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

fn returnedIdentity(node: ?*rbtree.Node) ?struct { i32, usize } {
    const current = node orelse return null;
    const entry: *const OrderedEntry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

test "phase1 rbtree alias-state replay keeps ordered aliases aligned" {
    var primary_entries = [_]OrderedEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };
    var alias_entries = [_]OrderedEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };
    var primary_probe = OrderedEntry{ .key = 12, .serial = 4 };
    var alias_probe = OrderedEntry{ .key = 12, .serial = 4 };
    var primary_duplicate = OrderedEntry{ .key = 15, .serial = 5 };
    var alias_duplicate = OrderedEntry{ .key = 15, .serial = 5 };
    var primary_replacement = OrderedEntry{ .key = 10, .serial = 6 };
    var alias_replacement = OrderedEntry{ .key = 10, .serial = 6 };

    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, orderedLess);
        rbtree.add(&alias_entry.node, &alias_root, orderedLess);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAdd(&primary_probe.node, &primary_root, orderedCmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAdd(&alias_probe.node, &alias_root, orderedCmp));

    const primary_existing = rbtree.findAdd(&primary_duplicate.node, &primary_root, orderedCmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.findAdd(&alias_duplicate.node, &alias_root, orderedCmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(returnedIdentity(primary_existing), returnedIdentity(alias_existing));

    var primary_forward: [5]i32 = undefined;
    var alias_forward: [5]i32 = undefined;
    const primary_forward_count = recordForward(&primary_root, false, &primary_forward);
    const alias_forward_count = recordForward(&alias_root, true, &alias_forward);
    try std.testing.expectEqual(primary_forward_count, alias_forward_count);
    try std.testing.expectEqualSlices(i32, primary_forward[0..primary_forward_count], alias_forward[0..alias_forward_count]);

    var primary_reverse: [5]i32 = undefined;
    var alias_reverse: [5]i32 = undefined;
    const primary_reverse_count = recordReverse(&primary_root, false, &primary_reverse);
    const alias_reverse_count = recordReverse(&alias_root, true, &alias_reverse);
    try std.testing.expectEqual(primary_reverse_count, alias_reverse_count);
    try std.testing.expectEqualSlices(i32, primary_reverse[0..primary_reverse_count], alias_reverse[0..alias_reverse_count]);

    rbtree.replaceNode(&primary_entries[0].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node(&alias_entries[0].node, &alias_replacement.node, &alias_root);

    const primary_after_replace = recordForward(&primary_root, false, &primary_forward);
    const alias_after_replace = recordForward(&alias_root, true, &alias_forward);
    try std.testing.expectEqual(primary_after_replace, alias_after_replace);
    try std.testing.expectEqualSlices(i32, primary_forward[0..primary_after_replace], alias_forward[0..alias_after_replace]);
}

test "phase1 rbtree alias-state replay keeps cached aliases and node-state helpers aligned" {
    var primary_first = OrderedEntry{ .key = 10, .serial = 0 };
    var alias_first = OrderedEntry{ .key = 10, .serial = 0 };
    var primary_leftmost = OrderedEntry{ .key = 5, .serial = 1 };
    var alias_leftmost = OrderedEntry{ .key = 5, .serial = 1 };
    var primary_larger = OrderedEntry{ .key = 15, .serial = 2 };
    var alias_larger = OrderedEntry{ .key = 15, .serial = 2 };
    var primary_duplicate = OrderedEntry{ .key = 10, .serial = 3 };
    var alias_duplicate = OrderedEntry{ .key = 10, .serial = 3 };
    var primary_replacement = OrderedEntry{ .key = 10, .serial = 4 };
    var alias_replacement = OrderedEntry{ .key = 10, .serial = 4 };

    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expect(rbtree.emptyRoot(&primary_root.root));
    try std.testing.expect(rbtree.emptyRoot(&alias_root.root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_first.node), rbtree.addCached(&primary_first.node, &primary_root, orderedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_first.node), rbtree.rb_add_cached(&alias_first.node, &alias_root, orderedLess));
    try std.testing.expectEqual(returnedIdentity(rbtree.firstCached(&primary_root)), returnedIdentity(rbtree.rb_first_cached(&alias_root)));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_leftmost.node, &primary_root, orderedCmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_leftmost.node, &alias_root, orderedCmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_larger.node, &primary_root, orderedCmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_larger.node, &alias_root, orderedCmp));
    try std.testing.expectEqual(returnedIdentity(rbtree.firstCached(&primary_root)), returnedIdentity(rbtree.rb_first_cached(&alias_root)));

    const primary_existing = rbtree.findAddCached(&primary_duplicate.node, &primary_root, orderedCmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, orderedCmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(returnedIdentity(primary_existing), returnedIdentity(alias_existing));

    try std.testing.expectEqual(
        returnedIdentity(rbtree.eraseCached(&primary_leftmost.node, &primary_root)),
        returnedIdentity(rbtree.rb_erase_cached(&alias_leftmost.node, &alias_root)),
    );
    try std.testing.expectEqual(returnedIdentity(rbtree.firstCached(&primary_root)), returnedIdentity(rbtree.rb_first_cached(&alias_root)));

    rbtree.replaceNodeCached(&primary_first.node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_first.node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(returnedIdentity(rbtree.firstCached(&primary_root)), returnedIdentity(rbtree.rb_first_cached(&alias_root)));

    rbtree.eraseInitCached(&primary_replacement.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_replacement.node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_replacement.node));
    try std.testing.expect(rbtree.emptyNode(&alias_replacement.node));
    try std.testing.expectEqual(returnedIdentity(rbtree.firstCached(&primary_root)), returnedIdentity(rbtree.rb_first_cached(&alias_root)));

    var primary_manual_root = rbtree.RootCached.init();
    var alias_manual_root = rbtree.RootCached.init();
    var primary_manual_entry = OrderedEntry{ .key = 1, .serial = 0 };
    var alias_manual_entry = OrderedEntry{ .key = 1, .serial = 0 };

    rbtree.linkNode(&primary_manual_entry.node, null, &primary_manual_root.root.node);
    rbtree.insertColorCached(&primary_manual_entry.node, &primary_manual_root, true);
    rbtree.linkNode(&alias_manual_entry.node, null, &alias_manual_root.root.node);
    rbtree.rb_insert_color_cached(&alias_manual_entry.node, &alias_manual_root, true);
    try std.testing.expectEqual(returnedIdentity(rbtree.firstCached(&primary_manual_root)), returnedIdentity(rbtree.rb_first_cached(&alias_manual_root)));

    var detached = rbtree.Node.init();
    rbtree.clearNode(&detached);
    try std.testing.expect(rbtree.emptyNode(&detached));
}
