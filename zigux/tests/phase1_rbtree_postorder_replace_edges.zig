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

test "phase1 rbtree postorder replay keeps left-deep sibling order explicit" {
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
        .{ .key = 2, .serial = 3 },
        .{ .key = 7, .serial = 4 },
        .{ .key = 12, .serial = 5 },
        .{ .key = 18, .serial = 6 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var primary_order: [7]i32 = undefined;
    var alias_order: [7]i32 = undefined;
    var primary_count: usize = 0;
    var alias_count: usize = 0;

    var current = rbtree.firstPostorder(&root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        primary_order[primary_count] = entry.key;
        primary_count += 1;
    }

    current = rbtree.rb_first_postorder(&root);
    while (current) |node| : (current = rbtree.rb_next_postorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_order[alias_count] = entry.key;
        alias_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 7), primary_count);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, &.{ 2, 7, 5, 12, 18, 15, 10 }, primary_order[0..primary_count]);
    try std.testing.expectEqualSlices(i32, primary_order[0..primary_count], alias_order[0..alias_count]);
    try std.testing.expect(rbtree.nextPostorder(null) == null);
    try std.testing.expect(rbtree.rb_next_postorder(null) == null);
}

test "phase1 rbtree cached replacement replay keeps leftmost promotion aligned" {
    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
        .{ .key = 12, .serial = 3 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
        .{ .key = 12, .serial = 3 },
    };
    var primary_replacement = Entry{ .key = 15, .serial = 20 };
    var alias_replacement = Entry{ .key = 15, .serial = 20 };
    var primary_new_leftmost = Entry{ .key = 3, .serial = 30 };
    var alias_new_leftmost = Entry{ .key = 3, .serial = 30 };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_entries[1].node), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entries[1].node), rbtree.rb_first_cached(&alias_root));

    rbtree.replaceNodeCached(&primary_entries[2].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_entries[2].node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_entries[1].node), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entries[1].node), rbtree.rb_first_cached(&alias_root));
    try std.testing.expectEqual(rbtree.last(&primary_root.root), @as(?*rbtree.Node, &primary_replacement.node));
    try std.testing.expectEqual(rbtree.rb_last(&alias_root.root), @as(?*rbtree.Node, &alias_replacement.node));

    rbtree.eraseInitCached(&primary_entries[1].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[1].node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_entries[1].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_entries[0].node), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entries[0].node), rbtree.rb_first_cached(&alias_root));

    try std.testing.expectEqual(
        @as(?*rbtree.Node, &primary_new_leftmost.node),
        rbtree.addCached(&primary_new_leftmost.node, &primary_root, less),
    );
    try std.testing.expectEqual(
        @as(?*rbtree.Node, &alias_new_leftmost.node),
        rbtree.rb_add_cached(&alias_new_leftmost.node, &alias_root, less),
    );
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_new_leftmost.node), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_new_leftmost.node), rbtree.rb_first_cached(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.rb_first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
}
