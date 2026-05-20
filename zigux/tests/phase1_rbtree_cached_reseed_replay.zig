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

fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn collectKeys(root: *const rbtree.RootCached, out: []i32) usize {
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

fn collectSerials(iter: *rbtree.MatchIterator, out: []usize) usize {
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.serial;
        count += 1;
    }
    return count;
}

test "phase1 lane06 rbtree cached erase-init reseed keeps leftmost aligned" {
    var leftmost = Entry{ .key = 5, .serial = 0 };
    var root_entry = Entry{ .key = 10, .serial = 1 };
    var duplicate = Entry{ .key = 10, .serial = 2 };
    var higher = Entry{ .key = 15, .serial = 3 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.addCached(&leftmost.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&root_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&duplicate.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&higher.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&leftmost.node, &root);
    try std.testing.expect(rbtree.emptyNode(&leftmost.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&root_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&root_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &duplicate.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&duplicate.node, &root);
    try std.testing.expect(rbtree.emptyNode(&duplicate.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &higher.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&higher.node, &root);
    try std.testing.expect(rbtree.emptyNode(&higher.node));
    try std.testing.expect(rbtree.emptyRoot(&root.root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &duplicate.node), rbtree.addCached(&duplicate.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.addCached(&leftmost.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&higher.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    var keys: [3]i32 = undefined;
    const count = collectKeys(&root, &keys);
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15 }, keys[0..count]);
}

test "phase1 lane06 rbtree cached duplicate lookup survives reseed and replacement" {
    var bootstrap = Entry{ .key = 7, .serial = 0 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &bootstrap.node), rbtree.addCached(&bootstrap.node, &root, less));
    rbtree.eraseInitCached(&bootstrap.node, &root);
    try std.testing.expect(rbtree.emptyNode(&bootstrap.node));
    try std.testing.expect(rbtree.emptyRoot(&root.root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));

    var leftmost = Entry{ .key = 8, .serial = 1 };
    var first_dup = Entry{ .key = 10, .serial = 2 };
    var second_dup = Entry{ .key = 10, .serial = 3 };
    var higher = Entry{ .key = 12, .serial = 4 };
    var replacement = Entry{ .key = 10, .serial = 9 };

    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.addCached(&leftmost.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&first_dup.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&second_dup.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&higher.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&first_dup.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &root.root, keyCmp) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 9), first_match_entry.serial);

    var iter = rbtree.matchIterator(&wanted, &root.root, keyCmp);
    var serials: [2]usize = undefined;
    const match_count = collectSerials(&iter, &serials);
    try std.testing.expectEqual(@as(usize, 2), match_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 9, 3 }, serials[0..match_count]);

    rbtree.eraseInitCached(&leftmost.node, &root);
    try std.testing.expect(rbtree.emptyNode(&leftmost.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));

    var keys: [3]i32 = undefined;
    const count = collectKeys(&root, &keys);
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 10, 10, 12 }, keys[0..count]);
}
