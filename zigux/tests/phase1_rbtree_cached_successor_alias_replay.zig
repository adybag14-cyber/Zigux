const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    serial: usize = 0,
    node: rbtree.Node = rbtree.Node.init(),
};

fn collectOrder(root: *const rbtree.Root) [3]i32 {
    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }
    std.debug.assert(count == order.len);
    return order;
}

fn nodeIdentity(node: ?*rbtree.Node) ?struct { i32, usize } {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

test "phase 1 rbtree cached erase promotes the leftmost right-subtree successor" {
    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 8, .serial = 2 },
        .{ .key = 7, .serial = 3 },
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
    try std.testing.expectEqualSlices(i32, &[_]i32{ 7, 8, 10 }, &collectOrder(&root.root));
}

test "phase 1 rbtree cached Linux-style aliases mirror successor handoff state" {
    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 8, .serial = 2 },
        .{ .key = 7, .serial = 3 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 8, .serial = 2 },
        .{ .key = 7, .serial = 3 },
    };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_root, less);
    }

    try std.testing.expectEqual(nodeIdentity(rbtree.firstCached(&primary_root)), nodeIdentity(rbtree.rb_first_cached(&alias_root)));

    const primary_promoted = rbtree.eraseCached(&primary_entries[1].node, &primary_root);
    const alias_promoted = rbtree.rb_erase_cached(&alias_entries[1].node, &alias_root);

    try std.testing.expectEqual(nodeIdentity(primary_promoted), nodeIdentity(alias_promoted));
    try std.testing.expectEqual(nodeIdentity(rbtree.firstCached(&primary_root)), nodeIdentity(rbtree.rb_first_cached(&alias_root)));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
    try std.testing.expectEqualSlices(i32, &collectOrder(&primary_root.root), &collectOrder(&alias_root.root));
}
