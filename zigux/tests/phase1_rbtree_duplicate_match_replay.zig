const std = @import("std");
const rbtree = @import("rbtree");

const Node = rbtree.Node;
const Root = rbtree.Root;

const Entry = struct {
    key: i32,
    serial: usize,
    node: Node = Node.init(),
};

fn less(lhs: *const Node, rhs: *const Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn cmp(key: *const anyopaque, node: *const Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn collectDuplicateSerials(root: *const Root, wanted: i32, serials: []usize) !usize {
    var iter = rbtree.matchIterator(&wanted, root, cmp);
    var count: usize = 0;
    while (iter.next()) |node| {
        try std.testing.expect(count < serials.len);
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }
    return count;
}

fn collectKeys(root: *const Root, keys: []i32) !usize {
    var count: usize = 0;
    var cursor = rbtree.first(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        try std.testing.expect(count < keys.len);
        const entry: *const Entry = @fieldParentPtr("node", node);
        keys[count] = entry.key;
        count += 1;
    }
    return count;
}

test "phase1 rbtree duplicate erase promotes the next duplicate match" {
    var entries = [_]Entry{
        .{ .key = 8, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 10, .serial = 3 },
        .{ .key = 12, .serial = 4 },
    };
    var root = Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const wanted = @as(i32, 10);
    const first_before = rbtree.findFirst(&wanted, &root, cmp) orelse return error.TestUnexpectedResult;
    const first_before_entry: *const Entry = @fieldParentPtr("node", first_before);
    try std.testing.expectEqual(@as(usize, 1), first_before_entry.serial);

    rbtree.erase(&entries[1].node, &root);

    const first_after = rbtree.findFirst(&wanted, &root, cmp) orelse return error.TestUnexpectedResult;
    const first_after_entry: *const Entry = @fieldParentPtr("node", first_after);
    try std.testing.expectEqual(@as(usize, 2), first_after_entry.serial);

    var duplicate_serials: [2]usize = undefined;
    const duplicate_count = try collectDuplicateSerials(&root, wanted, duplicate_serials[0..]);
    try std.testing.expectEqual(@as(usize, 2), duplicate_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 3 }, duplicate_serials[0..duplicate_count]);

    rbtree.erase(&entries[3].node, &root);
    const final_match = rbtree.findFirst(&wanted, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*Node, &entries[2].node), final_match);
    try std.testing.expect(rbtree.nextMatch(&wanted, final_match, cmp) == null);

    rbtree.erase(&entries[2].node, &root);
    try std.testing.expect(rbtree.findFirst(&wanted, &root, cmp) == null);

    var remaining_keys: [2]i32 = undefined;
    const remaining_count = try collectKeys(&root, remaining_keys[0..]);
    try std.testing.expectEqual(@as(usize, 2), remaining_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 8, 12 }, remaining_keys[0..remaining_count]);
}

test "phase1 rbtree eraseInit lets a detached duplicate rejoin at a new serial" {
    var entries = [_]Entry{
        .{ .key = 9, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 10, .serial = 3 },
        .{ .key = 11, .serial = 4 },
    };
    var root = Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    rbtree.eraseInit(&entries[2].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[2].node));

    const wanted = @as(i32, 10);
    var serials_after_detach: [2]usize = undefined;
    const detached_count = try collectDuplicateSerials(&root, wanted, serials_after_detach[0..]);
    try std.testing.expectEqual(@as(usize, 2), detached_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 3 }, serials_after_detach[0..detached_count]);

    entries[2].serial = 5;
    rbtree.add(&entries[2].node, &root, less);

    var serials_after_rejoin: [3]usize = undefined;
    const rejoined_count = try collectDuplicateSerials(&root, wanted, serials_after_rejoin[0..]);
    try std.testing.expectEqual(@as(usize, 3), rejoined_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 3, 5 }, serials_after_rejoin[0..rejoined_count]);

    const first_match = rbtree.findFirst(&wanted, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*Node, &entries[1].node), first_match);

    const second_match = rbtree.nextMatch(&wanted, first_match, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*Node, &entries[3].node), second_match);

    const third_match = rbtree.nextMatch(&wanted, second_match, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*Node, &entries[2].node), third_match);
    try std.testing.expect(rbtree.nextMatch(&wanted, third_match, cmp) == null);
}
