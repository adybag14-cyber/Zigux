const std = @import("std");
const rbtree = @import("rbtree");

fn orderToInt(order: std.math.Order) i32 {
    return switch (order) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn attachRoot(root: *rbtree.Root, entry: *Entry) void {
    rbtree.linkNode(&entry.node, null, &root.node);
    entry.node.color = .black;
}

fn expectManualTraversalOrder() !void {
    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 2 },
        .{ .key = 7 },
        .{ .key = 12 },
    };
    var root = rbtree.Root.init();

    attachRoot(&root, &entries[0]);
    rbtree.linkNode(&entries[1].node, &entries[0].node, &entries[0].node.left);
    rbtree.linkNode(&entries[2].node, &entries[0].node, &entries[0].node.right);
    rbtree.linkNode(&entries[3].node, &entries[1].node, &entries[1].node.left);
    rbtree.linkNode(&entries[4].node, &entries[1].node, &entries[1].node.right);
    rbtree.linkNode(&entries[5].node, &entries[2].node, &entries[2].node.left);

    const expected = [_]i32{ 2, 5, 7, 10, 12, 15 };
    var actual: [expected.len]i32 = undefined;
    var index: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        actual[index] = entry.key;
        index += 1;
    }

    try std.testing.expectEqual(expected.len, index);
    try std.testing.expectEqualSlices(i32, &expected, actual[0..index]);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.last(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.next(&entries[4].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[5].node), rbtree.prev(&entries[2].node));
}

fn expectStarterBalanceInvariants(root: *const rbtree.Root) !void {
    try std.testing.expectEqual(rbtree.Color.black, root.node.?.color);

    var current = rbtree.first(root);
    while (current) |node| : (current = rbtree.next(node)) {
        if (node.color == .red) {
            try std.testing.expectEqual(rbtree.Color.black, if (node.left) |left| left.color else .black);
            try std.testing.expectEqual(rbtree.Color.black, if (node.right) |right| right.color else .black);
        }
    }
}

test "phase 7 rbtree module imports cleanly" {
    _ = rbtree;
}

test "phase 7 rbtree traversal helpers walk a manually linked tree" {
    try expectManualTraversalOrder();
}

test "phase 7 rbtree replaceNode and postorder helpers preserve structure" {
    var root_entry = Entry{ .key = 10 };
    var left_entry = Entry{ .key = 5 };
    var right_entry = Entry{ .key = 15 };
    var left_left_entry = Entry{ .key = 2 };
    var replacement = Entry{ .key = 5 };
    var root = rbtree.Root.init();

    attachRoot(&root, &root_entry);
    rbtree.linkNode(&left_entry.node, &root_entry.node, &root_entry.node.left);
    rbtree.linkNode(&right_entry.node, &root_entry.node, &root_entry.node.right);
    rbtree.linkNode(&left_left_entry.node, &left_entry.node, &left_entry.node.left);

    rbtree.replaceNode(&left_entry.node, &replacement.node, &root);

    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), root_entry.node.left);
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_left_entry.node), rbtree.first(&root));

    var count: usize = 0;
    var current = rbtree.firstPostorder(&root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
}

test "phase 7 rbtree balancing helpers keep ordered insert erase traversal stable" {
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

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const inserted_expected = [_]i32{ 5, 10, 15, 20, 25 };
    var inserted_actual: [inserted_expected.len]i32 = undefined;
    var inserted_index: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        inserted_actual[inserted_index] = entry.key;
        inserted_index += 1;
    }
    try std.testing.expectEqual(inserted_expected.len, inserted_index);
    try std.testing.expectEqualSlices(i32, &inserted_expected, inserted_actual[0..inserted_index]);

    const reverse_expected = [_]i32{ 25, 20, 15, 10, 5 };
    var reverse_actual: [reverse_expected.len]i32 = undefined;
    var reverse_index: usize = 0;
    current = rbtree.last(&root);
    while (current) |node| : (current = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        reverse_actual[reverse_index] = entry.key;
        reverse_index += 1;
    }
    try std.testing.expectEqual(reverse_expected.len, reverse_index);
    try std.testing.expectEqualSlices(i32, &reverse_expected, reverse_actual[0..reverse_index]);
    try expectStarterBalanceInvariants(&root);

    rbtree.erase(&entries[1].node, &root);
    rbtree.replaceNode(&entries[0].node, &replacement.node, &root);

    const replaced_expected = [_]i32{ 5, 10, 15, 25 };
    var replaced_actual: [replaced_expected.len]i32 = undefined;
    var replaced_index: usize = 0;
    current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        replaced_actual[replaced_index] = entry.key;
        replaced_index += 1;
    }
    try std.testing.expectEqual(replaced_expected.len, replaced_index);
    try std.testing.expectEqualSlices(i32, &replaced_expected, replaced_actual[0..replaced_index]);
}

test "phase 7 rbtree clearNode marks detached nodes as empty" {
    var node = rbtree.Node.init();

    try std.testing.expect(!rbtree.emptyNode(&node));
    try std.testing.expect(rbtree.emptyRoot(&rbtree.Root.init()));

    rbtree.clearNode(&node);

    try std.testing.expect(rbtree.emptyNode(&node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.next(&node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(&node));
}

test "phase 7 rbtree find helpers walk duplicate-key ranges" {
    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return @intFromPtr(lhs) < @intFromPtr(rhs);
        }
    }.compare;

    const cmp = struct {
        fn compare(key: i32, node: *const rbtree.Node) i32 {
            const entry: *const Entry = @fieldParentPtr("node", node);
            return orderToInt(std.math.order(key, entry.key));
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 10 },
        .{ .key = 15 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const first_match = rbtree.findFirst(@as(i32, 10), &root, cmp) orelse return error.TestUnexpectedResult;
    const found = rbtree.find(@as(i32, 10), &root, cmp) orelse return error.TestUnexpectedResult;
    const second_match = rbtree.nextMatch(@as(i32, 10), first_match, cmp) orelse return error.TestUnexpectedResult;
    const third_match = rbtree.nextMatch(@as(i32, 10), second_match, cmp) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(i32, 10), (@as(*const Entry, @fieldParentPtr("node", found))).key);
    try std.testing.expectEqual(@as(i32, 10), (@as(*const Entry, @fieldParentPtr("node", first_match))).key);
    try std.testing.expectEqual(@as(i32, 10), (@as(*const Entry, @fieldParentPtr("node", second_match))).key);
    try std.testing.expectEqual(@as(i32, 10), (@as(*const Entry, @fieldParentPtr("node", third_match))).key);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextMatch(@as(i32, 10), third_match, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.find(@as(i32, 99), &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findFirst(@as(i32, 99), &root, cmp));
}
