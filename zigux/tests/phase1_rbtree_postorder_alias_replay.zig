const std = @import("std");
const rbtree = @import("rbtree");

const OrderedEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn encode(node: *const rbtree.Node) i32 {
    const entry: *const OrderedEntry = @fieldParentPtr("node", node);
    return entry.key * 10 + @as(i32, @intCast(entry.serial));
}

fn orderedLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const OrderedEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const OrderedEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn recordPostorder(root: *const rbtree.Root, use_aliases: bool, out: []i32) usize {
    var count: usize = 0;
    var current = if (use_aliases) rbtree.rb_first_postorder(root) else rbtree.firstPostorder(root);
    while (current) |node| : (current = if (use_aliases) rbtree.rb_next_postorder(node) else rbtree.nextPostorder(node)) {
        out[count] = encode(node);
        count += 1;
    }
    return count;
}

fn wireManualTree(
    root: *rbtree.Root,
    root_entry: *OrderedEntry,
    left_entry: *OrderedEntry,
    right_entry: *OrderedEntry,
    left_left_entry: *OrderedEntry,
    left_right_entry: *OrderedEntry,
) void {
    rbtree.linkNode(&root_entry.node, null, &root.node);
    rbtree.linkNode(&left_entry.node, &root_entry.node, &root_entry.node.left);
    rbtree.linkNode(&right_entry.node, &root_entry.node, &root_entry.node.right);
    rbtree.linkNode(&left_left_entry.node, &left_entry.node, &left_entry.node.left);
    rbtree.linkNode(&left_right_entry.node, &left_entry.node, &left_entry.node.right);
}

test "phase1 rbtree postorder aliases keep a fixed-shape replacement walk aligned" {
    var primary_root_entry = OrderedEntry{ .key = 10, .serial = 0 };
    var primary_left_entry = OrderedEntry{ .key = 5, .serial = 1 };
    var primary_right_entry = OrderedEntry{ .key = 15, .serial = 2 };
    var primary_left_left_entry = OrderedEntry{ .key = 3, .serial = 3 };
    var primary_left_right_entry = OrderedEntry{ .key = 7, .serial = 4 };
    var primary_replacement = OrderedEntry{ .key = 6, .serial = 5 };

    var alias_root_entry = OrderedEntry{ .key = 10, .serial = 0 };
    var alias_left_entry = OrderedEntry{ .key = 5, .serial = 1 };
    var alias_right_entry = OrderedEntry{ .key = 15, .serial = 2 };
    var alias_left_left_entry = OrderedEntry{ .key = 3, .serial = 3 };
    var alias_left_right_entry = OrderedEntry{ .key = 7, .serial = 4 };
    var alias_replacement = OrderedEntry{ .key = 6, .serial = 5 };

    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    wireManualTree(
        &primary_root,
        &primary_root_entry,
        &primary_left_entry,
        &primary_right_entry,
        &primary_left_left_entry,
        &primary_left_right_entry,
    );
    wireManualTree(
        &alias_root,
        &alias_root_entry,
        &alias_left_entry,
        &alias_right_entry,
        &alias_left_left_entry,
        &alias_left_right_entry,
    );

    var primary_postorder: [5]i32 = undefined;
    var alias_postorder: [5]i32 = undefined;
    var primary_count = recordPostorder(&primary_root, false, &primary_postorder);
    var alias_count = recordPostorder(&alias_root, true, &alias_postorder);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqual(@as(usize, 5), primary_count);
    try std.testing.expectEqualSlices(i32, primary_postorder[0..primary_count], alias_postorder[0..alias_count]);
    try std.testing.expectEqualSlices(i32, &.{ 33, 74, 51, 152, 100 }, primary_postorder[0..primary_count]);

    rbtree.replaceNode(&primary_left_entry.node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node(&alias_left_entry.node, &alias_replacement.node, &alias_root);

    primary_count = recordPostorder(&primary_root, false, &primary_postorder);
    alias_count = recordPostorder(&alias_root, true, &alias_postorder);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, primary_postorder[0..primary_count], alias_postorder[0..alias_count]);
    try std.testing.expectEqualSlices(i32, &.{ 33, 74, 65, 152, 100 }, primary_postorder[0..primary_count]);
}

test "phase1 rbtree postorder aliases stay aligned through eraseInit collapse and reseed" {
    var primary_entries = [_]OrderedEntry{
        .{ .key = 8, .serial = 0 },
        .{ .key = 3, .serial = 1 },
        .{ .key = 12, .serial = 2 },
        .{ .key = 1, .serial = 3 },
        .{ .key = 6, .serial = 4 },
    };
    var alias_entries = [_]OrderedEntry{
        .{ .key = 8, .serial = 0 },
        .{ .key = 3, .serial = 1 },
        .{ .key = 12, .serial = 2 },
        .{ .key = 1, .serial = 3 },
        .{ .key = 6, .serial = 4 },
    };
    var reseed_primary = [_]OrderedEntry{
        .{ .key = 4, .serial = 5 },
        .{ .key = 9, .serial = 6 },
    };
    var reseed_alias = [_]OrderedEntry{
        .{ .key = 4, .serial = 5 },
        .{ .key = 9, .serial = 6 },
    };
    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, orderedLess);
        rbtree.add(&alias_entry.node, &alias_root, orderedLess);
    }

    var primary_postorder: [5]i32 = undefined;
    var alias_postorder: [5]i32 = undefined;
    var primary_count = recordPostorder(&primary_root, false, &primary_postorder);
    var alias_count = recordPostorder(&alias_root, true, &alias_postorder);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqual(@as(usize, 5), primary_count);
    try std.testing.expectEqualSlices(i32, primary_postorder[0..primary_count], alias_postorder[0..alias_count]);

    rbtree.eraseInit(&primary_entries[3].node, &primary_root);
    rbtree.eraseInit(&primary_entries[2].node, &primary_root);
    rbtree.eraseInit(&alias_entries[3].node, &alias_root);
    rbtree.eraseInit(&alias_entries[2].node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_entries[3].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[3].node));
    try std.testing.expect(rbtree.nextPostorder(null) == null);
    try std.testing.expect(rbtree.rb_next_postorder(null) == null);

    primary_count = recordPostorder(&primary_root, false, primary_postorder[0..3]);
    alias_count = recordPostorder(&alias_root, true, alias_postorder[0..3]);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqual(@as(usize, 3), primary_count);
    try std.testing.expectEqualSlices(i32, primary_postorder[0..primary_count], alias_postorder[0..alias_count]);

    rbtree.eraseInit(&primary_entries[4].node, &primary_root);
    rbtree.eraseInit(&primary_entries[1].node, &primary_root);
    rbtree.eraseInit(&primary_entries[0].node, &primary_root);
    rbtree.eraseInit(&alias_entries[4].node, &alias_root);
    rbtree.eraseInit(&alias_entries[1].node, &alias_root);
    rbtree.eraseInit(&alias_entries[0].node, &alias_root);
    try std.testing.expect(rbtree.firstPostorder(&primary_root) == null);
    try std.testing.expect(rbtree.rb_first_postorder(&alias_root) == null);

    for (&reseed_primary, &reseed_alias) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, orderedLess);
        rbtree.add(&alias_entry.node, &alias_root, orderedLess);
    }

    primary_count = recordPostorder(&primary_root, false, primary_postorder[0..2]);
    alias_count = recordPostorder(&alias_root, true, alias_postorder[0..2]);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqual(@as(usize, 2), primary_count);
    try std.testing.expectEqualSlices(i32, primary_postorder[0..primary_count], alias_postorder[0..alias_count]);
    try std.testing.expectEqualSlices(i32, &.{ 96, 45 }, primary_postorder[0..primary_count]);
}
