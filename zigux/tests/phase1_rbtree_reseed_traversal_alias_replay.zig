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

fn encode(node: *const rbtree.Node) i32 {
    const entry: *const OrderedEntry = @fieldParentPtr("node", node);
    return entry.key * 10 + @as(i32, @intCast(entry.serial));
}

fn recordForward(root: *const rbtree.Root, use_aliases: bool, out: []i32) usize {
    var count: usize = 0;
    var current = if (use_aliases) rbtree.rb_first(root) else rbtree.first(root);
    while (current) |node| : (current = if (use_aliases) rbtree.rb_next(node) else rbtree.next(node)) {
        out[count] = encode(node);
        count += 1;
    }
    return count;
}

fn recordReverse(root: *const rbtree.Root, use_aliases: bool, out: []i32) usize {
    var count: usize = 0;
    var current = if (use_aliases) rbtree.rb_last(root) else rbtree.last(root);
    while (current) |node| : (current = if (use_aliases) rbtree.rb_prev(node) else rbtree.prev(node)) {
        out[count] = encode(node);
        count += 1;
    }
    return count;
}

test "phase1 rbtree reseed replay keeps singleton eraseInit and alias traversals aligned" {
    var primary_singleton = OrderedEntry{ .key = 10, .serial = 0 };
    var alias_singleton = OrderedEntry{ .key = 10, .serial = 0 };
    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    rbtree.add(&primary_singleton.node, &primary_root, orderedLess);
    rbtree.add(&alias_singleton.node, &alias_root, orderedLess);

    try std.testing.expect(!rbtree.emptyRoot(&primary_root));
    try std.testing.expect(!rbtree.emptyRoot(&alias_root));
    try std.testing.expectEqual(encode(rbtree.first(&primary_root).?), encode(rbtree.rb_first(&alias_root).?));
    try std.testing.expectEqual(encode(rbtree.last(&primary_root).?), encode(rbtree.rb_last(&alias_root).?));

    rbtree.eraseInit(&primary_singleton.node, &primary_root);
    rbtree.eraseInit(&alias_singleton.node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_singleton.node));
    try std.testing.expect(rbtree.emptyNode(&alias_singleton.node));
    try std.testing.expect(rbtree.emptyRoot(&primary_root));
    try std.testing.expect(rbtree.emptyRoot(&alias_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.first(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_first(&alias_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.last(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_last(&alias_root));

    var primary_entries = [_]OrderedEntry{
        .{ .key = 6, .serial = 1 },
        .{ .key = 14, .serial = 2 },
        .{ .key = 11, .serial = 3 },
    };
    var alias_entries = [_]OrderedEntry{
        .{ .key = 6, .serial = 1 },
        .{ .key = 14, .serial = 2 },
        .{ .key = 11, .serial = 3 },
    };

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, orderedLess);
        rbtree.add(&alias_entry.node, &alias_root, orderedLess);
    }

    var primary_forward: [3]i32 = undefined;
    var alias_forward: [3]i32 = undefined;
    const primary_forward_count = recordForward(&primary_root, false, &primary_forward);
    const alias_forward_count = recordForward(&alias_root, true, &alias_forward);
    try std.testing.expectEqual(primary_forward_count, alias_forward_count);
    try std.testing.expectEqualSlices(i32, primary_forward[0..primary_forward_count], alias_forward[0..alias_forward_count]);
    try std.testing.expectEqualSlices(i32, &.{ 61, 113, 142 }, primary_forward[0..primary_forward_count]);

    var primary_reverse: [3]i32 = undefined;
    var alias_reverse: [3]i32 = undefined;
    const primary_reverse_count = recordReverse(&primary_root, false, &primary_reverse);
    const alias_reverse_count = recordReverse(&alias_root, true, &alias_reverse);
    try std.testing.expectEqual(primary_reverse_count, alias_reverse_count);
    try std.testing.expectEqualSlices(i32, primary_reverse[0..primary_reverse_count], alias_reverse[0..alias_reverse_count]);
    try std.testing.expectEqualSlices(i32, &.{ 142, 113, 61 }, primary_reverse[0..primary_reverse_count]);
}

test "phase1 rbtree reseed replay keeps replacement and collapse traversal aligned" {
    var primary_entries = [_]OrderedEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 20, .serial = 2 },
        .{ .key = 12, .serial = 3 },
    };
    var alias_entries = [_]OrderedEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 20, .serial = 2 },
        .{ .key = 12, .serial = 3 },
    };
    var primary_replacement = OrderedEntry{ .key = 10, .serial = 4 };
    var alias_replacement = OrderedEntry{ .key = 10, .serial = 4 };
    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, orderedLess);
        rbtree.add(&alias_entry.node, &alias_root, orderedLess);
    }

    rbtree.replaceNode(&primary_entries[0].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node(&alias_entries[0].node, &alias_replacement.node, &alias_root);

    var primary_forward: [4]i32 = undefined;
    var alias_forward: [4]i32 = undefined;
    var primary_count = recordForward(&primary_root, false, &primary_forward);
    var alias_count = recordForward(&alias_root, true, &alias_forward);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, primary_forward[0..primary_count], alias_forward[0..alias_count]);
    try std.testing.expectEqualSlices(i32, &.{ 51, 104, 123, 202 }, primary_forward[0..primary_count]);

    rbtree.eraseInit(&primary_entries[1].node, &primary_root);
    rbtree.eraseInit(&alias_entries[1].node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_entries[1].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[1].node));
    try std.testing.expectEqual(encode(rbtree.first(&primary_root).?), encode(rbtree.rb_first(&alias_root).?));

    rbtree.eraseInit(&primary_replacement.node, &primary_root);
    rbtree.eraseInit(&alias_replacement.node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_replacement.node));
    try std.testing.expect(rbtree.emptyNode(&alias_replacement.node));

    primary_count = recordForward(&primary_root, false, &primary_forward);
    alias_count = recordForward(&alias_root, true, &alias_forward);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, primary_forward[0..primary_count], alias_forward[0..alias_count]);
    try std.testing.expectEqualSlices(i32, &.{ 123, 202 }, primary_forward[0..primary_count]);

    rbtree.eraseInit(&primary_entries[3].node, &primary_root);
    rbtree.eraseInit(&alias_entries[3].node, &alias_root);
    rbtree.eraseInit(&primary_entries[2].node, &primary_root);
    rbtree.eraseInit(&alias_entries[2].node, &alias_root);
    try std.testing.expect(rbtree.emptyRoot(&primary_root));
    try std.testing.expect(rbtree.emptyRoot(&alias_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_first(&alias_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_last(&alias_root));
}
