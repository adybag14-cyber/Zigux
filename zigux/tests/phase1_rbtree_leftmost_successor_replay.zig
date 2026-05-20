const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

test "phase1 rbtree cached erase promotes the leftmost right-subtree successor" {
    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 8 },
        .{ .key = 7 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    const promoted = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[3].node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 7, 8, 10 }, order[0..count]);
}

test "phase1 rbtree cached erase alias mirrors leftmost successor promotion" {
    var primary_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 8 },
        .{ .key = 7 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 8 },
        .{ .key = 7 },
    };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_root, less);
    }

    const promoted_primary = rbtree.eraseCached(&primary_entries[1].node, &primary_root) orelse return error.TestUnexpectedResult;
    const promoted_alias = rbtree.rb_erase_cached(&alias_entries[1].node, &alias_root) orelse return error.TestUnexpectedResult;

    const primary_entry: *const Entry = @fieldParentPtr("node", promoted_primary);
    const alias_entry: *const Entry = @fieldParentPtr("node", promoted_alias);

    try std.testing.expectEqual(primary_entry.key, alias_entry.key);
    try std.testing.expectEqual(@as(i32, 7), primary_entry.key);
    const primary_leftmost = rbtree.firstCached(&primary_root) orelse return error.TestUnexpectedResult;
    const alias_leftmost = rbtree.rb_first_cached(&alias_root) orelse return error.TestUnexpectedResult;
    const primary_leftmost_entry: *const Entry = @fieldParentPtr("node", primary_leftmost);
    const alias_leftmost_entry: *const Entry = @fieldParentPtr("node", alias_leftmost);

    try std.testing.expectEqual(@as(i32, 7), primary_leftmost_entry.key);
    try std.testing.expectEqual(primary_leftmost_entry.key, alias_leftmost_entry.key);
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
}
