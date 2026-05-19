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

fn readKey(node: *const rbtree.Node) i32 {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn collectInOrder(root: *const rbtree.Root, out: []i32) usize {
    var count: usize = 0;
    var cursor = rbtree.first(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        out[count] = readKey(node);
        count += 1;
    }
    return count;
}

fn collectPostorder(root: *const rbtree.Root, out: []i32) usize {
    var count: usize = 0;
    var cursor = rbtree.firstPostorder(root);
    while (cursor) |node| : (cursor = rbtree.nextPostorder(node)) {
        out[count] = readKey(node);
        count += 1;
    }
    return count;
}

test "rbtree cached erase promotes the leftmost successor from the erased node right subtree" {
    var entries = [_]Entry{
        .{ .key = 5, .serial = 0 },
        .{ .key = 9, .serial = 1 },
        .{ .key = 7, .serial = 2 },
        .{ .key = 11, .serial = 3 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(i32, 5), readKey(rbtree.firstCached(&root).?));

    const promoted = rbtree.eraseCached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[2].node), promoted);
    try std.testing.expectEqual(@as(i32, 7), readKey(promoted));
    try std.testing.expectEqual(@as(i32, 7), readKey(rbtree.firstCached(&root).?));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    var order: [3]i32 = undefined;
    const count = collectInOrder(&root.root, &order);
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 7, 9, 11 }, order[0..count]);
}

test "rbtree alias cached erase keeps postorder traversal and leftmost reseed aligned" {
    var entries = [_]Entry{
        .{ .key = 5, .serial = 0 },
        .{ .key = 9, .serial = 1 },
        .{ .key = 7, .serial = 2 },
        .{ .key = 6, .serial = 3 },
        .{ .key = 11, .serial = 4 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, less);
    }

    const promoted = rbtree.rb_erase_cached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[3].node), promoted);
    try std.testing.expectEqual(@as(i32, 6), readKey(rbtree.rb_first_cached(&root).?));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.rb_first_cached(&root));

    var postorder: [4]i32 = undefined;
    var count: usize = 0;
    var cursor = rbtree.rb_first_postorder(&root.root);
    while (cursor) |node| : (cursor = rbtree.rb_next_postorder(node)) {
        postorder[count] = readKey(node);
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 4), count);
    std.mem.sort(i32, postorder[0..count], {}, std.sort.asc(i32));
    try std.testing.expectEqualSlices(i32, &[_]i32{ 6, 7, 9, 11 }, postorder[0..count]);

    var stable_postorder: [4]i32 = undefined;
    const stable_count = collectPostorder(&root.root, &stable_postorder);
    try std.testing.expectEqual(@as(usize, 4), stable_count);

    rbtree.rb_erase_init_cached(&entries[3].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));
    try std.testing.expectEqual(@as(i32, 7), readKey(rbtree.rb_first_cached(&root).?));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.rb_first_cached(&root));

    var order: [3]i32 = undefined;
    const in_order_count = collectInOrder(&root.root, &order);
    try std.testing.expectEqual(@as(usize, 3), in_order_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 7, 9, 11 }, order[0..in_order_count]);
}
