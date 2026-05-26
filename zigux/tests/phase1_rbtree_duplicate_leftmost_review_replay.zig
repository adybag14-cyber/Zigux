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

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn nodeIdentity(node: ?*rbtree.Node) ?struct { i32, usize } {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

fn collectNextMatchSerials(key: *const i32, first_match: *rbtree.Node) [3]usize {
    var serials: [3]usize = undefined;
    var count: usize = 0;
    var cursor = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", cursor);
        serials[count] = entry.serial;
        count += 1;
        cursor = rbtree.nextMatch(key, cursor, cmpKey) orelse break;
    }
    std.debug.assert(count == serials.len);
    return serials;
}

fn collectIteratorSerials(root: *const rbtree.Root, key: *const i32) [3]usize {
    var replay_iter = rbtree.matchIterator(key, root, cmpKey);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (replay_iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }
    std.debug.assert(count == serials.len);
    return serials;
}

fn firstIdentity(root: *const rbtree.RootCached) ?struct { i32, usize } {
    return nodeIdentity(rbtree.firstCached(root));
}

test "phase 1 rbtree duplicate review replay keeps duplicate-search serials exact" {
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const wanted_found = @as(i32, 15);
    const found = rbtree.find(&wanted_found, &root, cmpKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 15), nodeIdentity(found).?.@"0");

    const wanted_missing = @as(i32, 17);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.find(&wanted_missing, &root, cmpKey));

    const wanted_duplicate = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted_duplicate, &root, cmpKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), nodeIdentity(first_match).?.@"1");

    const next_match_serials = collectNextMatchSerials(&wanted_duplicate, first_match);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, &next_match_serials);
    try std.testing.expect(rbtree.nextMatch(&wanted_duplicate, &entries[4].node, cmpKey) == null);

    const iter_serials = collectIteratorSerials(&root, &wanted_duplicate);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, &iter_serials);
}

test "phase 1 rbtree duplicate review replay keeps cached-leftmost return serials exact" {
    var root = rbtree.RootCached.init();

    var primary_first = Entry{ .key = 10, .serial = 0 };
    const primary_first_return = nodeIdentity(rbtree.addCached(&primary_first.node, &root, less));
    try std.testing.expectEqual(
        @as(?struct { i32, usize }, .{ 10, 0 }),
        primary_first_return,
    );
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 10, 0 }), firstIdentity(&root));
    try std.testing.expectEqual(nodeIdentity(rbtree.first(&root.root)), firstIdentity(&root));

    var primary_larger = Entry{ .key = 12, .serial = 1 };
    const primary_larger_return = nodeIdentity(rbtree.addCached(&primary_larger.node, &root, less));
    try std.testing.expectEqual(@as(?struct { i32, usize }, null), primary_larger_return);
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 10, 0 }), firstIdentity(&root));

    var primary_leftmost = Entry{ .key = 5, .serial = 2 };
    const primary_leftmost_return = nodeIdentity(rbtree.addCached(&primary_leftmost.node, &root, less));
    try std.testing.expectEqual(
        @as(?struct { i32, usize }, .{ 5, 2 }),
        primary_leftmost_return,
    );
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 2 }), firstIdentity(&root));
    try std.testing.expectEqual(nodeIdentity(rbtree.first(&root.root)), firstIdentity(&root));

    var primary_duplicate = Entry{ .key = 5, .serial = 3 };
    const primary_duplicate_return = nodeIdentity(rbtree.addCached(&primary_duplicate.node, &root, less));
    try std.testing.expectEqual(@as(?struct { i32, usize }, null), primary_duplicate_return);
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 2 }), firstIdentity(&root));

    const primary_promoted_return = nodeIdentity(rbtree.eraseCached(&primary_leftmost.node, &root));
    try std.testing.expectEqual(
        @as(?struct { i32, usize }, .{ 5, 3 }),
        primary_promoted_return,
    );
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 3 }), firstIdentity(&root));
    try std.testing.expectEqual(nodeIdentity(rbtree.first(&root.root)), firstIdentity(&root));

    const primary_larger_erase_return = nodeIdentity(rbtree.eraseCached(&primary_larger.node, &root));
    try std.testing.expectEqual(@as(?struct { i32, usize }, null), primary_larger_erase_return);
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 3 }), firstIdentity(&root));

    var primary_new_leftmost = Entry{ .key = 3, .serial = 4 };
    const primary_new_leftmost_return = nodeIdentity(rbtree.addCached(&primary_new_leftmost.node, &root, less));
    try std.testing.expectEqual(
        @as(?struct { i32, usize }, .{ 3, 4 }),
        primary_new_leftmost_return,
    );
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 3, 4 }), firstIdentity(&root));
    try std.testing.expectEqual(nodeIdentity(rbtree.first(&root.root)), firstIdentity(&root));
}
