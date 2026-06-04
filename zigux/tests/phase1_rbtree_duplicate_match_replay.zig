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

fn compareKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn collectMatches(first: *rbtree.Node, key: *const i32, out: []usize) usize {
    var count: usize = 0;
    var cursor: ?*rbtree.Node = first;
    while (cursor) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.serial;
        count += 1;
        cursor = rbtree.nextMatch(key, node, compareKey);
    }
    return count;
}

test "phase1 rbtree duplicate match replay keeps alias range iteration aligned" {
    var entries = [_]Entry{
        .{ .key = 8, .serial = 3 },
        .{ .key = 4, .serial = 0 },
        .{ .key = 8, .serial = 1 },
        .{ .key = 12, .serial = 6 },
        .{ .key = 8, .serial = 5 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 8, .serial = 2 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate = @as(i32, 8);
    const first_match = rbtree.findFirst(&duplicate, &root, compareKey) orelse return error.TestUnexpectedResult;
    const alias_first_match = rbtree.rb_find_first(&duplicate, &root, compareKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(first_match, alias_first_match);

    var serials: [4]usize = undefined;
    const count = collectMatches(first_match, &duplicate, &serials);
    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(usize, &.{ 1, 2, 3, 5 }, serials[0..count]);

    var iter = rbtree.matchIterator(&duplicate, &root, compareKey);
    var alias_iter = rbtree.rb_match_iterator(&duplicate, &root, compareKey);
    for (serials[0..count]) |expected_serial| {
        const node = iter.next() orelse return error.TestUnexpectedResult;
        const alias_node = alias_iter.next() orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(node, alias_node);
        const entry: *const Entry = @fieldParentPtr("node", node);
        try std.testing.expectEqual(expected_serial, entry.serial);
    }
    try std.testing.expect(iter.next() == null);
    try std.testing.expect(alias_iter.next() == null);

    const missing = @as(i32, 9);
    var missing_iter = rbtree.matchIterator(&missing, &root, compareKey);
    try std.testing.expect(missing_iter.next() == null);
}

test "phase1 rbtree duplicate match replay survives erase and replacement inside range" {
    var entries = [_]Entry{
        .{ .key = 8, .serial = 0 },
        .{ .key = 8, .serial = 2 },
        .{ .key = 8, .serial = 4 },
        .{ .key = 6, .serial = 1 },
        .{ .key = 10, .serial = 5 },
    };
    var replacement = Entry{ .key = 8, .serial = 2 };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate = @as(i32, 8);
    var first_match = rbtree.findFirst(&duplicate, &root, compareKey) orelse return error.TestUnexpectedResult;
    var serials: [3]usize = undefined;
    var count = collectMatches(first_match, &duplicate, &serials);
    try std.testing.expectEqualSlices(usize, &.{ 0, 2, 4 }, serials[0..count]);

    rbtree.eraseInit(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    first_match = rbtree.findFirst(&duplicate, &root, compareKey) orelse return error.TestUnexpectedResult;
    count = collectMatches(first_match, &duplicate, &serials);
    try std.testing.expectEqualSlices(usize, &.{ 2, 4 }, serials[0..count]);

    rbtree.replaceNode(&entries[1].node, &replacement.node, &root);
    first_match = rbtree.rb_find_first(&duplicate, &root, compareKey) orelse return error.TestUnexpectedResult;
    const first_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(*const Entry, &replacement), first_entry);

    count = collectMatches(first_match, &duplicate, &serials);
    try std.testing.expectEqualSlices(usize, &.{ 2, 4 }, serials[0..count]);
    const next_after_tail = rbtree.rb_next_match(&duplicate, rbtree.last(&root).?, compareKey);
    try std.testing.expect(next_after_tail == null);
}
