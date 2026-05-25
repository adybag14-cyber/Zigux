// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");
const rbtree = @import("../../lib/rbtree.zig");

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn entryCmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn entryCmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const want: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (want.* < entry.key) return -1;
    if (want.* > entry.key) return 1;
    return 0;
}

test "phase7 rbtree duplicate cached insertion keeps leftmost stable and leaves duplicate unlinked" {
    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
    };

    for (&entries) |*entry| {
        try std.testing.expect(rbtree.findAddCached(&entry.node, &root, entryCmpNode) == null);
    }

    var duplicate = Entry{ .key = 5 };
    const existing = rbtree.findAddCached(&duplicate.node, &root, entryCmpNode);

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), existing);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), duplicate.node.parent);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), duplicate.node.left);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), duplicate.node.right);
    try std.testing.expectEqual(rbtree.Color.red, duplicate.node.color);
}

test "phase7 rbtree postorder traversal keeps children before parents and stops at cleared sentinels" {
    var root = rbtree.Root.init();
    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 12 },
    };

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, entryLess);
    }

    var order: [entries.len]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.firstPostorder(&root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 12, 15, 10 }, order[0..count]);

    rbtree.clearNode(&entries[3].node);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));
    try std.testing.expect(rbtree.nextPostorder(&entries[3].node) == null);
    try std.testing.expect(rbtree.next(&entries[3].node) == null);
    try std.testing.expect(rbtree.prev(&entries[3].node) == null);
}

test "phase7 rbtree eraseInit clears removed nodes and keeps remaining lookup stable" {
    var root = rbtree.Root.init();
    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 12 },
    };

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, entryLess);
    }

    rbtree.eraseInit(&entries[2].node, &root);

    try std.testing.expect(rbtree.emptyNode(&entries[2].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.first(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.next(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.prev(&entries[3].node));

    const removed_key: i32 = 15;
    const survivor_key: i32 = 12;
    try std.testing.expectEqual(
        @as(?*rbtree.Node, null),
        rbtree.find(@as(*const anyopaque, @ptrCast(&removed_key)), &root, entryCmpKey),
    );
    try std.testing.expectEqual(
        @as(?*rbtree.Node, &entries[3].node),
        rbtree.find(@as(*const anyopaque, @ptrCast(&survivor_key)), &root, entryCmpKey),
    );
}
