const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),

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
};

fn keyOf(node: *const rbtree.Node) i32 {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn serialOf(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.serial;
}

test "phase1 rbtree edge replay keeps duplicate find-add traversal aligned" {
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, Entry.less);
    }

    var duplicate = Entry{ .key = 10, .serial = 99 };
    const existing = rbtree.findAdd(&duplicate.node, &root, Entry.cmpNode) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 10), keyOf(existing));
    try std.testing.expectEqual(@as(usize, 0), serialOf(existing));

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &root, Entry.cmpKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), serialOf(first_match));

    var iter = rbtree.matchIterator(&wanted, &root, Entry.cmpKey);
    var serials: [2]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        serials[count] = serialOf(node);
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(usize, &.{ 0, 2 }, serials[0..count]);

    const missing = @as(i32, 12);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.find(&missing, &root, Entry.cmpKey));
}

test "phase1 rbtree edge replay keeps cached replacement and erase-init edges aligned" {
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var cached_root = rbtree.RootCached.init();
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_add_cached(&entries[0].node, &cached_root, Entry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_add_cached(&entries[1].node, &cached_root, Entry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[2].node, &cached_root, Entry.less));
    try std.testing.expectEqual(@as(i32, 5), keyOf(rbtree.rb_first_cached(&cached_root).?));

    var replacement = Entry{ .key = 5, .serial = 99 };
    rbtree.rb_replace_node_cached(&entries[1].node, &replacement.node, &cached_root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_first_cached(&cached_root));
    try std.testing.expectEqual(@as(i32, 5), keyOf(rbtree.rb_first(&cached_root.root).?));

    rbtree.rb_erase_init_cached(&replacement.node, &cached_root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(i32, 10), keyOf(rbtree.rb_first_cached(&cached_root).?));

    rbtree.eraseInit(&entries[2].node, &cached_root.root);
    try std.testing.expect(rbtree.emptyNode(&entries[2].node));
    try std.testing.expectEqual(@as(i32, 10), keyOf(rbtree.rb_last(&cached_root.root).?));
}

test "phase1 rbtree edge replay keeps postorder traversal and cached duplicate insertion aligned" {
    var cached_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
        .{ .key = 10, .serial = 3 },
    };
    var cached_root = rbtree.RootCached.init();
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&cached_entries[0].node, &cached_root, Entry.cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&cached_entries[1].node, &cached_root, Entry.cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&cached_entries[2].node, &cached_root, Entry.cmpNode));

    const duplicate = rbtree.rb_find_add_cached(&cached_entries[3].node, &cached_root, Entry.cmpNode) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 10), keyOf(duplicate));
    try std.testing.expectEqual(@as(usize, 0), serialOf(duplicate));
    try std.testing.expectEqual(@as(i32, 5), keyOf(rbtree.rb_first_cached(&cached_root).?));

    var postorder: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.rb_first_postorder(&cached_root.root);
    while (current) |node| : (current = rbtree.rb_next_postorder(node)) {
        postorder[count] = keyOf(node);
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &.{ 5, 15, 10 }, postorder[0..count]);
}
