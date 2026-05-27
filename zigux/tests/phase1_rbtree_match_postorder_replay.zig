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

test "rbtree match helpers keep duplicate ranges in insertion order" {
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

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &root, cmpKey) orelse return error.TestUnexpectedResult;
    const first_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_entry.serial);

    var serials_from_next: [3]usize = undefined;
    var next_count: usize = 0;
    var cursor: *const rbtree.Node = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", cursor);
        serials_from_next[next_count] = entry.serial;
        next_count += 1;
        cursor = rbtree.nextMatch(&wanted, cursor, cmpKey) orelse break;
    }
    try std.testing.expectEqual(@as(usize, 3), next_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials_from_next[0..next_count]);

    var serials_from_iterator: [3]usize = undefined;
    var iterator_count: usize = 0;
    var iter = rbtree.matchIterator(&wanted, &root, cmpKey);
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials_from_iterator[iterator_count] = entry.serial;
        iterator_count += 1;
    }
    try std.testing.expectEqual(next_count, iterator_count);
    try std.testing.expectEqualSlices(
        usize,
        serials_from_next[0..next_count],
        serials_from_iterator[0..iterator_count],
    );

    const missing = @as(i32, 17);
    try std.testing.expect(rbtree.findFirst(&missing, &root, cmpKey) == null);
    var missing_iter = rbtree.matchIterator(&missing, &root, cmpKey);
    try std.testing.expect(missing_iter.next() == null);
}

test "rbtree postorder replay keeps leaves ahead of the root and exhausts cleanly" {
    var entries = [_]Entry{
        .{ .key = 2, .serial = 0 },
        .{ .key = 1, .serial = 1 },
        .{ .key = 3, .serial = 2 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var keys: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.firstPostorder(&root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        keys[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 3, 2 }, keys[0..count]);
    try std.testing.expect(rbtree.nextPostorder(null) == null);

    var detached = rbtree.Node.init();
    rbtree.clearNode(&detached);
    try std.testing.expect(rbtree.emptyNode(&detached));
}
