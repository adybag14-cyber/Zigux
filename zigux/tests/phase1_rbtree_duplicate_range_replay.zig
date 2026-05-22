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

fn collectNextMatchSerials(first_match: *rbtree.Node, wanted: *const i32) ![3]usize {
    var serials: [3]usize = undefined;
    var count: usize = 0;
    var cursor: *rbtree.Node = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", cursor);
        serials[count] = entry.serial;
        count += 1;
        const next_node = rbtree.nextMatch(wanted, cursor, cmpKey);
        cursor = next_node orelse break;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);
    const terminal = rbtree.nextMatch(wanted, cursor, cmpKey);
    try std.testing.expect(terminal == null);
    return serials;
}

fn collectIteratorSerials(root: *const rbtree.Root, wanted: *const i32) ![3]usize {
    var serials: [3]usize = undefined;
    var count: usize = 0;
    var iter = rbtree.matchIterator(wanted, root, cmpKey);
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);
    return serials;
}

test "phase1 rbtree duplicate replay keeps duplicate rejection aligned" {
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 5, .serial = 2 },
    };
    var duplicate_probe = Entry{ .key = 10, .serial = 3 };
    var fresh_probe = Entry{ .key = 15, .serial = 4 };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAdd(&entry.node, &root, cmpNode));
    }

    const existing = rbtree.findAdd(&duplicate_probe.node, &root, cmpNode) orelse return error.TestUnexpectedResult;
    const existing_entry: *const Entry = @fieldParentPtr("node", existing);
    try std.testing.expectEqual(@as(i32, 10), existing_entry.key);
    try std.testing.expectEqual(@as(usize, 0), existing_entry.serial);

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAdd(&fresh_probe.node, &root, cmpNode));

    var order: [4]i32 = undefined;
    var count: usize = 0;
    var cursor = rbtree.first(&root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15, 20 }, order[0..count]);
}

test "phase1 rbtree duplicate replay keeps duplicate-range lookups aligned" {
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

    const wanted = @as(i32, 15);
    const found = rbtree.find(&wanted, &root, cmpKey) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(i32, 15), found_entry.key);

    const missing = @as(i32, 17);
    try std.testing.expect(rbtree.find(&missing, &root, cmpKey) == null);

    const duplicate = @as(i32, 10);
    const first_match = rbtree.findFirst(&duplicate, &root, cmpKey) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_match_entry.serial);

    _ = try collectNextMatchSerials(first_match, &duplicate);
}

test "phase1 rbtree duplicate replay keeps iterator ordering aligned" {
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

    const duplicate = @as(i32, 10);
    _ = try collectIteratorSerials(&root, &duplicate);

    const missing = @as(i32, 17);
    var primary_missing = rbtree.matchIterator(&missing, &root, cmpKey);
    try std.testing.expect(primary_missing.next() == null);
}
