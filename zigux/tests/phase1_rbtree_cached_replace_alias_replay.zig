const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn lessByKeyThenSerial(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn collectOrder(root: *const rbtree.RootCached, out: []Entry) usize {
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.*;
        count += 1;
    }
    return count;
}

test "phase1 cached replace replay imports the live cached replacement helpers" {
    try std.testing.expect(@hasDecl(rbtree, "replaceNodeCached"));
    try std.testing.expect(@hasDecl(rbtree, "rb_replace_node_cached"));
    try std.testing.expect(@hasDecl(rbtree, "firstCached"));
    try std.testing.expect(@hasDecl(rbtree, "rb_first_cached"));
}

test "phase1 cached replace replay keeps leftmost and traversal aliases aligned" {
    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 20, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 20, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };
    var primary_leftmost_replacement = Entry{ .key = 5, .serial = 10 };
    var alias_leftmost_replacement = Entry{ .key = 5, .serial = 10 };
    var primary_right_replacement = Entry{ .key = 20, .serial = 11 };
    var alias_right_replacement = Entry{ .key = 20, .serial = 11 };

    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, lessByKeyThenSerial);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_root, lessByKeyThenSerial);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_entries[1].node), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entries[1].node), rbtree.rb_first_cached(&alias_root));

    rbtree.replaceNodeCached(&primary_entries[1].node, &primary_leftmost_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_entries[1].node, &alias_leftmost_replacement.node, &alias_root);

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_leftmost_replacement.node), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_leftmost_replacement.node), rbtree.rb_first_cached(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));

    const primary_after_leftmost = rbtree.firstCached(&primary_root) orelse return error.TestUnexpectedResult;
    const alias_after_leftmost = rbtree.rb_first_cached(&alias_root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_entries[0].node), rbtree.next(primary_after_leftmost));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entries[0].node), rbtree.rb_next(alias_after_leftmost));
    try std.testing.expectEqual(@as(?*rbtree.Node, primary_after_leftmost), rbtree.prev(&primary_entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, alias_after_leftmost), rbtree.rb_prev(&alias_entries[0].node));

    rbtree.replaceNodeCached(&primary_entries[2].node, &primary_right_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_entries[2].node, &alias_right_replacement.node, &alias_root);

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_leftmost_replacement.node), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_leftmost_replacement.node), rbtree.rb_first_cached(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_right_replacement.node), rbtree.last(&primary_root.root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_right_replacement.node), rbtree.rb_last(&alias_root.root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_entries[3].node), rbtree.prev(&primary_right_replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entries[3].node), rbtree.rb_prev(&alias_right_replacement.node));

    var primary_order: [4]Entry = undefined;
    var alias_order: [4]Entry = undefined;
    const primary_count = collectOrder(&primary_root, &primary_order);
    const alias_count = collectOrder(&alias_root, &alias_order);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqual(@as(usize, 4), primary_count);
    for (primary_order[0..primary_count], alias_order[0..alias_count]) |primary_entry, alias_entry| {
        try std.testing.expectEqual(primary_entry.key, alias_entry.key);
        try std.testing.expectEqual(primary_entry.serial, alias_entry.serial);
    }
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15, 20 }, &[_]i32{
        primary_order[0].key,
        primary_order[1].key,
        primary_order[2].key,
        primary_order[3].key,
    });
    try std.testing.expectEqualSlices(usize, &[_]usize{ 10, 0, 3, 11 }, &[_]usize{
        primary_order[0].serial,
        primary_order[1].serial,
        primary_order[2].serial,
        primary_order[3].serial,
    });
}
