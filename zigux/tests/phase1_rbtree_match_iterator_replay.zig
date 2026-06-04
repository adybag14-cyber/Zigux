const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn less(lhs_node: *const rbtree.Node, rhs_node: *const rbtree.Node) bool {
    const lhs = entryFromNode(lhs_node);
    const rhs = entryFromNode(rhs_node);
    if (lhs.key == rhs.key) {
        return lhs.ordinal < rhs.ordinal;
    }
    return lhs.key < rhs.key;
}

fn cmpNode(lhs_node: *const rbtree.Node, rhs_node: *const rbtree.Node) i32 {
    const lhs = entryFromNode(lhs_node);
    const rhs = entryFromNode(rhs_node);
    if (lhs.key < rhs.key) {
        return -1;
    }
    if (lhs.key > rhs.key) {
        return 1;
    }
    if (lhs.ordinal < rhs.ordinal) {
        return -1;
    }
    if (lhs.ordinal > rhs.ordinal) {
        return 1;
    }
    return 0;
}

fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const i32 = @ptrCast(@alignCast(key_ptr));
    const entry = entryFromNode(node);
    if (key.* < entry.key) {
        return -1;
    }
    if (key.* > entry.key) {
        return 1;
    }
    return 0;
}

fn insertAll(root: *rbtree.Root, entries: []Entry) void {
    for (entries) |*entry| {
        rbtree.add(&entry.node, root, less);
    }
}

test "phase1 rbtree replay keeps match iterator ordered across duplicates" {
    var entries = [_]Entry{
        .{ .key = 8, .ordinal = 0 },
        .{ .key = 4, .ordinal = 1 },
        .{ .key = 8, .ordinal = 2 },
        .{ .key = 12, .ordinal = 3 },
        .{ .key = 8, .ordinal = 4 },
        .{ .key = 10, .ordinal = 5 },
    };
    var root = rbtree.Root.init();
    insertAll(&root, entries[0..]);

    const key: i32 = 8;
    var iter = rbtree.matchIterator(&key, &root, cmpKey);
    const first = iter.next() orelse return error.TestExpectedEqual;
    const second = iter.next() orelse return error.TestExpectedEqual;
    const third = iter.next() orelse return error.TestExpectedEqual;

    try std.testing.expectEqual(@as(usize, 0), entryFromNode(first).ordinal);
    try std.testing.expectEqual(@as(usize, 2), entryFromNode(second).ordinal);
    try std.testing.expectEqual(@as(usize, 4), entryFromNode(third).ordinal);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iter.next());
}

test "phase1 rbtree replay keeps find first and next match bounded" {
    var entries = [_]Entry{
        .{ .key = -1, .ordinal = 0 },
        .{ .key = 3, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 5, .ordinal = 3 },
        .{ .key = 7, .ordinal = 4 },
    };
    var root = rbtree.Root.init();
    insertAll(&root, entries[0..]);

    const key: i32 = 3;
    const first = rbtree.findFirst(&key, &root, cmpKey) orelse return error.TestExpectedEqual;
    try std.testing.expectEqual(@as(usize, 1), entryFromNode(first).ordinal);

    const second = rbtree.nextMatch(&key, first, cmpKey) orelse return error.TestExpectedEqual;
    try std.testing.expectEqual(@as(usize, 2), entryFromNode(second).ordinal);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextMatch(&key, second, cmpKey));
}

test "phase1 rbtree replay keeps find add duplicate ownership stable" {
    var entries = [_]Entry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 6, .ordinal = 1 },
        .{ .key = 9, .ordinal = 2 },
    };
    var duplicate = Entry{ .key = 6, .ordinal = 1 };
    var new_entry = Entry{ .key = 6, .ordinal = 3 };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAdd(&entry.node, &root, cmpNode));
    }

    const existing = rbtree.findAdd(&duplicate.node, &root, cmpNode) orelse return error.TestExpectedEqual;
    try std.testing.expectEqual(@as(usize, 1), entryFromNode(existing).ordinal);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAdd(&new_entry.node, &root, cmpNode));

    const key: i32 = 6;
    var iter = rbtree.matchIterator(&key, &root, cmpKey);
    try std.testing.expectEqual(@as(usize, 1), entryFromNode(iter.next() orelse return error.TestExpectedEqual).ordinal);
    try std.testing.expectEqual(@as(usize, 3), entryFromNode(iter.next() orelse return error.TestExpectedEqual).ordinal);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iter.next());
}
