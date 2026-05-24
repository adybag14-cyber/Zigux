const std = @import("std");
const rbtree = @import("../../lib/rbtree.zig");

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

test "rbtree traversal helpers preserve sorted order and alias parity" {
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 20, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var forward: [4]i32 = undefined;
    var forward_count: usize = 0;
    var cursor = rbtree.first(&root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        forward[forward_count] = entry.key;
        forward_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), forward_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15, 20 }, forward[0..forward_count]);
    try std.testing.expectEqual(rbtree.first(&root), rbtree.rb_first(&root));

    var reverse: [4]i32 = undefined;
    var reverse_count: usize = 0;
    cursor = rbtree.last(&root);
    while (cursor) |node| : (cursor = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        reverse[reverse_count] = entry.key;
        reverse_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), reverse_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 20, 15, 10, 5 }, reverse[0..reverse_count]);
    try std.testing.expectEqual(rbtree.last(&root), rbtree.rb_last(&root));

    const middle = rbtree.next(rbtree.first(&root).?);
    try std.testing.expectEqual(middle, rbtree.rb_next(rbtree.first(&root).?));
    try std.testing.expectEqual(rbtree.prev(rbtree.last(&root).?), rbtree.rb_prev(rbtree.last(&root).?));
}

test "rbtree postorder helpers keep detached nodes at null stops" {
    var entries = [_]Entry{
        .{ .key = 2, .serial = 0 },
        .{ .key = 1, .serial = 1 },
        .{ .key = 3, .serial = 2 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var cursor = rbtree.firstPostorder(&root);
    while (cursor) |node| : (cursor = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 3, 2 }, order[0..count]);
    try std.testing.expectEqual(rbtree.firstPostorder(&root), rbtree.rb_first_postorder(&root));
    try std.testing.expectEqual(
        rbtree.nextPostorder(rbtree.firstPostorder(&root)),
        rbtree.rb_next_postorder(rbtree.rb_first_postorder(&root)),
    );
    try std.testing.expect(rbtree.nextPostorder(null) == null);
    try std.testing.expect(rbtree.rb_next_postorder(null) == null);

    var detached = rbtree.Node.init();
    rbtree.clearNode(&detached);
    try std.testing.expect(rbtree.emptyNode(&detached));
    try std.testing.expect(rbtree.next(&detached) == null);
    try std.testing.expect(rbtree.prev(&detached) == null);
    try std.testing.expect(rbtree.nextPostorder(&detached) == null);
    try std.testing.expect(rbtree.rb_next_postorder(&detached) == null);
}
