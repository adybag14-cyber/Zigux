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

fn expectOrder(root: *const rbtree.Root, expected: []const i32) !void {
    var actual: [16]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        actual[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(expected.len, count);
    try std.testing.expectEqualSlices(i32, expected, actual[0..count]);
}

test "phase1 rbtree successor climb keeps in-order neighbors explicit" {
    var entries = [_]Entry{
        .{ .key = 40, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 60, .serial = 2 },
        .{ .key = 10, .serial = 3 },
        .{ .key = 30, .serial = 4 },
        .{ .key = 50, .serial = 5 },
        .{ .key = 70, .serial = 6 },
        .{ .key = 25, .serial = 7 },
        .{ .key = 35, .serial = 8 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    try expectOrder(&root, &.{ 10, 20, 25, 30, 35, 40, 50, 60, 70 });

    try std.testing.expectEqual(&entries[4].node, rbtree.rb_next(&entries[7].node).?);
    try std.testing.expectEqual(&entries[0].node, rbtree.next(&entries[8].node).?);
    try std.testing.expectEqual(&entries[7].node, rbtree.rb_prev(&entries[4].node).?);
    try std.testing.expectEqual(&entries[2].node, rbtree.prev(&entries[6].node).?);

    rbtree.clearNode(&entries[8].node);
    try std.testing.expect(rbtree.emptyNode(&entries[8].node));
    try std.testing.expect(rbtree.next(&entries[8].node) == null);
    try std.testing.expect(rbtree.prev(&entries[8].node) == null);
}

test "phase1 rbtree cached successor replay updates leftmost after erase and replace" {
    var entries = [_]Entry{
        .{ .key = 20, .serial = 0 },
        .{ .key = 40, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 30, .serial = 3 },
        .{ .key = 50, .serial = 4 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(&entries[2].node, rbtree.firstCached(&root).?);

    const first_successor = rbtree.eraseCached(&entries[2].node, &root).?;
    try std.testing.expectEqual(&entries[0].node, first_successor);
    try std.testing.expectEqual(&entries[0].node, rbtree.rb_first_cached(&root).?);

    var replacement = Entry{ .key = 20, .serial = 9 };
    rbtree.replaceNodeCached(&entries[0].node, &replacement.node, &root);
    try std.testing.expectEqual(&replacement.node, rbtree.firstCached(&root).?);
    try std.testing.expectEqual(&entries[3].node, rbtree.next(&replacement.node).?);
    try std.testing.expectEqual(&entries[1].node, rbtree.prev(&entries[4].node).?);
}

test "phase1 rbtree cached singleton reseed keeps successor handoff truthful" {
    var first_entry = Entry{ .key = 11, .serial = 0 };
    var second_entry = Entry{ .key = 13, .serial = 1 };
    var root = rbtree.RootCached.init();

    _ = rbtree.addCached(&first_entry.node, &root, less);
    try std.testing.expectEqual(&first_entry.node, rbtree.firstCached(&root).?);

    rbtree.eraseInitCached(&first_entry.node, &root);
    try std.testing.expect(rbtree.emptyRoot(&root.root));
    try std.testing.expect(rbtree.firstCached(&root) == null);
    try std.testing.expect(rbtree.emptyNode(&first_entry.node));

    _ = rbtree.addCached(&second_entry.node, &root, less);
    try std.testing.expectEqual(&second_entry.node, rbtree.firstCached(&root).?);
    try std.testing.expect(rbtree.next(&second_entry.node) == null);
    try std.testing.expect(rbtree.prev(&second_entry.node) == null);
}
