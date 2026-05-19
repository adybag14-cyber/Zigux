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

fn cmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "phase1 rbtree replay keeps duplicate walks stable after cached leftmost promotion" {
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 3, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    const promoted = rbtree.eraseCached(&entries[3].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[1].node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    const duplicate = @as(i32, 10);
    var iter = rbtree.matchIterator(&duplicate, &root.root, cmpKey);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);
}

test "phase1 rbtree replay keeps cached leftmost and duplicate lookup aligned through replace and erase-init" {
    var root = rbtree.RootCached.init();
    var leftmost = Entry{ .key = 5, .serial = 0 };
    var duplicate_a = Entry{ .key = 10, .serial = 1 };
    var duplicate_b = Entry{ .key = 10, .serial = 2 };
    var greater = Entry{ .key = 15, .serial = 3 };
    var replacement = Entry{ .key = 5, .serial = 4 };

    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.addCached(&leftmost.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&duplicate_a.node, &root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&greater.node, &root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, &duplicate_a.node), rbtree.findAddCached(&duplicate_b.node, &root, cmpNode));

    rbtree.replaceNodeCached(&leftmost.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    const duplicate = @as(i32, 10);
    const first_duplicate = rbtree.findFirst(&duplicate, &root.root, cmpKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &duplicate_a.node), first_duplicate);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextMatch(&duplicate, &duplicate_a.node, cmpKey));

    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &duplicate_a.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    const found_duplicate = rbtree.find(&duplicate, &root.root, cmpKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &duplicate_a.node), found_duplicate);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextMatch(&duplicate, &duplicate_a.node, cmpKey));

    rbtree.eraseInitCached(&duplicate_a.node, &root);
    try std.testing.expect(rbtree.emptyNode(&duplicate_a.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &greater.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
