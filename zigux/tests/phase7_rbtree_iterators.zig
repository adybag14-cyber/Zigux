const std = @import("std");
const rbtree = @import("../../lib/rbtree.zig");

test "rbtree matchIterator walks duplicate-key runs and stops at the first non-match" {
    const Entry = struct {
        key: i32,
        serial: i32,
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

    const cmp_key = struct {
        fn compare(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
            const key: *const i32 = @ptrCast(@alignCast(key_ptr));
            const entry: *const Entry = @fieldParentPtr("node", node);
            return switch (std.math.order(key.*, entry.key)) {
                .lt => -1,
                .eq => 0,
                .gt => 1,
            };
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 2, .serial = 0 },
        .{ .key = 1, .serial = 0 },
        .{ .key = 2, .serial = 1 },
        .{ .key = 3, .serial = 0 },
        .{ .key = 2, .serial = 2 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const key: i32 = 2;
    const first_match = rbtree.findFirst(&key, &root, cmp_key).?;
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), first_match);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.nextMatch(&key, first_match, cmp_key));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[4].node), rbtree.nextMatch(&key, &entries[2].node, cmp_key));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextMatch(&key, &entries[4].node, cmp_key));

    var iterator = rbtree.matchIterator(&key, &root, cmp_key);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), iterator.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), iterator.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[4].node), iterator.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iterator.next());

    var alias_iterator = rbtree.rb_match_iterator(&key, &root, cmp_key);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), alias_iterator.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), alias_iterator.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[4].node), alias_iterator.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, null), alias_iterator.next());
}

test "rbtree postorder helpers visit children before parents and stop after cleared sentinels" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 3 },
        .{ .key = 7 },
        .{ .key = 12 },
        .{ .key = 18 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const expected = [_]i32{ 3, 7, 5, 12, 18, 15, 10 };
    var seen: [expected.len]i32 = undefined;
    var count: usize = 0;

    var current = rbtree.firstPostorder(&root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), current);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        seen[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(expected.len, count);
    try std.testing.expectEqualSlices(i32, &expected, seen[0..count]);

    var alias_seen: [expected.len]i32 = undefined;
    var alias_count: usize = 0;
    current = rbtree.rb_first_postorder(&root);
    while (current) |node| : (current = rbtree.rb_next_postorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_seen[alias_count] = entry.key;
        alias_count += 1;
    }
    try std.testing.expectEqual(expected.len, alias_count);
    try std.testing.expectEqualSlices(i32, &expected, alias_seen[0..alias_count]);

    rbtree.clearNode(&entries[0].node);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextPostorder(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_next_postorder(&entries[0].node));
}
