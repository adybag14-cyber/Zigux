const std = @import("std");
const rbtree = @import("rbtree");

test "phase 1 rbtree review anchor replay keeps ordered traversal and replacement stable" {
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
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 25 },
    };
    var replacement = Entry{ .key = 10 };
    var root = rbtree.Root.init();

    try std.testing.expect(rbtree.emptyRoot(&root));

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var order: [5]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 5), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15, 20, 25 }, order[0..count]);

    var reverse_order: [5]i32 = undefined;
    var reverse_count: usize = 0;
    current = rbtree.last(&root);
    while (current) |node| : (current = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        reverse_order[reverse_count] = entry.key;
        reverse_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 5), reverse_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 25, 20, 15, 10, 5 }, reverse_order[0..reverse_count]);

    rbtree.erase(&entries[1].node, &root);
    rbtree.replaceNode(&entries[0].node, &replacement.node, &root);

    var replaced_order: [4]i32 = undefined;
    var replaced_count: usize = 0;
    current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        replaced_order[replaced_count] = entry.key;
        replaced_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), replaced_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15, 25 }, replaced_order[0..replaced_count]);

    rbtree.eraseInit(&entries[2].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[2].node));
}

test "phase 1 rbtree review anchor replay keeps duplicate-range search order explicit" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

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

    const cmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

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
    const found = rbtree.find(&wanted, &root, cmp) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(i32, 15), found_entry.key);

    const missing = @as(i32, 17);
    try std.testing.expect(rbtree.find(&missing, &root, cmp) == null);

    const duplicate = @as(i32, 10);
    const first_match = rbtree.findFirst(&duplicate, &root, cmp) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_match_entry.serial);

    var next_match_serials: [3]usize = undefined;
    var next_match_count: usize = 0;
    var cursor = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", cursor);
        next_match_serials[next_match_count] = entry.serial;
        next_match_count += 1;
        cursor = rbtree.nextMatch(&duplicate, cursor, cmp) orelse break;
    }

    try std.testing.expectEqual(@as(usize, 3), next_match_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, next_match_serials[0..next_match_count]);
    try std.testing.expect(rbtree.nextMatch(&duplicate, cursor, cmp) == null);

    var iter = rbtree.matchIterator(&duplicate, &root, cmp);
    var iter_serials: [3]usize = undefined;
    var iter_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        iter_serials[iter_count] = entry.serial;
        iter_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), iter_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, iter_serials[0..iter_count]);
}

test "phase 1 rbtree review anchor replay keeps cached leftmost returns aligned" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

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

    const returnedIdentity = struct {
        fn read(node: ?*rbtree.Node) ?struct { i32, usize } {
            const current = node orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", current);
            return .{ entry.key, entry.serial };
        }
    }.read;

    var first_entry = Entry{ .key = 10, .serial = 0 };
    var larger_entry = Entry{ .key = 12, .serial = 1 };
    var smaller_entry = Entry{ .key = 5, .serial = 2 };
    var replacement = Entry{ .key = 10, .serial = 3 };
    var manual_alias_entry = Entry{ .key = 1, .serial = 4 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.addCached(&first_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&larger_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &smaller_entry.node), rbtree.addCached(&smaller_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &smaller_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    try std.testing.expectEqual(
        @as(?struct { i32, usize }, null),
        returnedIdentity(rbtree.eraseCached(&larger_entry.node, &root)),
    );
    try std.testing.expectEqual(@as(?*rbtree.Node, &smaller_entry.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(
        @as(?struct { i32, usize }, .{ 10, 0 }),
        returnedIdentity(rbtree.eraseCached(&smaller_entry.node, &root)),
    );
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&first_entry.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);

    var alias_root = rbtree.RootCached.init();
    rbtree.linkNode(&manual_alias_entry.node, null, &alias_root.root.node);
    rbtree.rb_insert_color_cached(&manual_alias_entry.node, &alias_root, true);
    try std.testing.expectEqual(@as(?*rbtree.Node, &manual_alias_entry.node), rbtree.rb_first_cached(&alias_root));
}
