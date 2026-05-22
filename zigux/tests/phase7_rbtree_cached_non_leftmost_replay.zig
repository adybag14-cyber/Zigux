const std = @import("std");
const rbtree = @import("rbtree");

test "phase 7 rbtree companion replays non-leftmost cached erase ownership boundaries" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    var leftmost_entry = Entry{ .key = 5, .serial = 0 };
    var root_entry = Entry{ .key = 10, .serial = 1 };
    var middle_entry = Entry{ .key = 12, .serial = 2 };
    var right_entry = Entry{ .key = 15, .serial = 3 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.addCached(&leftmost_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&root_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&middle_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&right_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.firstCached(&root));

    const handoff = rbtree.rb_erase_cached(&middle_entry.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), handoff);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
    try std.testing.expect(!rbtree.emptyNode(&middle_entry.node));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15 }, order[0..count]);
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.next(&leftmost_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &right_entry.node), rbtree.next(&root_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.prev(&right_entry.node));

    rbtree.clearNode(&middle_entry.node);
    try std.testing.expect(rbtree.emptyNode(&middle_entry.node));

    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
