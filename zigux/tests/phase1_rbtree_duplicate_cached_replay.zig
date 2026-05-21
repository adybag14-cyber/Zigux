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

fn cmpNodeByKey(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn cmpKeyByKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "rbtree duplicate walkers keep duplicate serial order aligned" {
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
        rbtree.add(&entry.node, &root, lessByKeyThenSerial);
    }

    const unique_key = @as(i32, 15);
    const unique = rbtree.find(&unique_key, &root, cmpKeyByKey) orelse return error.TestUnexpectedResult;
    const unique_entry: *const Entry = @fieldParentPtr("node", unique);
    try std.testing.expectEqual(@as(usize, 5), unique_entry.serial);

    const missing_key = @as(i32, 17);
    try std.testing.expect(rbtree.find(&missing_key, &root, cmpKeyByKey) == null);

    const duplicate_key = @as(i32, 10);
    const first_match = rbtree.findFirst(&duplicate_key, &root, cmpKeyByKey) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_match_entry.serial);

    var next_match_serials: [3]usize = undefined;
    var count: usize = 0;
    var cursor = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", cursor);
        next_match_serials[count] = entry.serial;
        count += 1;
        cursor = rbtree.nextMatch(&duplicate_key, cursor, cmpKeyByKey) orelse break;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, next_match_serials[0..count]);
    try std.testing.expect(rbtree.nextMatch(&duplicate_key, cursor, cmpKeyByKey) == null);

    var iter = rbtree.matchIterator(&duplicate_key, &root, cmpKeyByKey);
    var iter_serials: [3]usize = undefined;
    var iter_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        iter_serials[iter_count] = entry.serial;
        iter_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), iter_count);
    try std.testing.expectEqualSlices(usize, next_match_serials[0..count], iter_serials[0..iter_count]);
}

test "rbtree findAddCached rejects duplicates without disturbing cached leftmost" {
    var leftmost = Entry{ .key = 5, .serial = 0 };
    var root_entry = Entry{ .key = 10, .serial = 1 };
    var larger_entry = Entry{ .key = 15, .serial = 2 };
    var duplicate_root = Entry{ .key = 10, .serial = 3 };
    var duplicate_leftmost = Entry{ .key = 5, .serial = 4 };
    var new_leftmost = Entry{ .key = 4, .serial = 5 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&root_entry.node, &root, cmpNodeByKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&leftmost.node, &root, cmpNodeByKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&larger_entry.node, &root, cmpNodeByKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    const existing_root = rbtree.findAddCached(&duplicate_root.node, &root, cmpNodeByKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), existing_root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    const existing_leftmost = rbtree.findAddCached(&duplicate_leftmost.node, &root, cmpNodeByKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &leftmost.node), existing_leftmost);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    const promoted = rbtree.eraseCached(&leftmost.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &new_leftmost.node), rbtree.addCached(&new_leftmost.node, &root, lessByKeyThenSerial));
    try std.testing.expectEqual(@as(?*rbtree.Node, &new_leftmost.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
