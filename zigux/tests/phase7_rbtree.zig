const std = @import("std");
const rbtree = @import("rbtree");

fn orderToInt(order: std.math.Order) i32 {
    return switch (order) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

const Fixture = struct {
    ordered: struct {
        insert_order: []const i32,
        reverse_order: []const i32,
        replace_order: []const i32,
    },
    duplicates: struct {
        key: i32,
        match_serials: []const i32,
    },
    erase_init: struct {
        remaining_order: []const i32,
        detached_is_empty: bool,
        detached_next_is_null: bool,
        detached_prev_is_null: bool,
    },
    postorder: struct {
        traversal: []const i32,
    },
};

fn loadFixture(allocator: std.mem.Allocator) !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, allocator, @embedFile("fixtures/phase7_rbtree.json"), .{
        .ignore_unknown_fields = true,
    });
}

const Entry = struct {
    key: i32,
    serial: i32 = 0,
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
    var parsed = try loadFixture(std.testing.allocator);
    defer parsed.deinit();
    const fixture = parsed.value;

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
    try std.testing.expectEqual(inserted_expected.len, fixture.ordered.insert_order.len);
    try std.testing.expectEqual(inserted_expected.len, inserted_index);
    try std.testing.expectEqualSlices(i32, fixture.ordered.insert_order, inserted_actual[0..inserted_index]);

    const reverse_expected = [_]i32{ 25, 20, 15, 10, 5 };
    var reverse_actual: [reverse_expected.len]i32 = undefined;
    var reverse_index: usize = 0;
    current = rbtree.last(&root);
    while (current) |node| : (current = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        reverse_actual[reverse_index] = entry.key;
        reverse_index += 1;
    }
    try std.testing.expectEqual(reverse_expected.len, fixture.ordered.reverse_order.len);
    try std.testing.expectEqual(reverse_expected.len, reverse_index);
    try std.testing.expectEqualSlices(i32, fixture.ordered.reverse_order, reverse_actual[0..reverse_index]);
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
    try std.testing.expectEqual(replaced_expected.len, fixture.ordered.replace_order.len);
    try std.testing.expectEqual(replaced_expected.len, replaced_index);
    try std.testing.expectEqualSlices(i32, fixture.ordered.replace_order, replaced_actual[0..replaced_index]);
}

test "phase 7 rbtree cached helpers return leftmost handoff state" {
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
        .{ .key = 20 },
        .{ .key = 15 },
    };
    var replacement = Entry{ .key = 5 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.addCached(&entries[0].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.addCached(&entries[1].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[2].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[3].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.first(&root.root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.eraseCached(&replacement.node, &root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.first(&root.root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.eraseCached(&entries[3].node, &root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.first(&root.root));
}

test "phase 7 rbtree eraseInitCached clears detached cached nodes and keeps cached roots reusable" {
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
    };
    var reseed = Entry{ .key = 6 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&entries[2].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[2].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);

    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed.node), rbtree.addCached(&reseed.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}

test "phase 7 rbtree eraseCached clears final cached-leftmost handoff state" {
    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var lone = Entry{ .key = 10 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &lone.node), rbtree.addCached(&lone.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &lone.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &lone.node), rbtree.first(&root.root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.eraseCached(&lone.node, &root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.first(&root.root));
    try std.testing.expect(rbtree.emptyRoot(&root.root));
    try std.testing.expect(!rbtree.emptyNode(&lone.node));

    rbtree.clearNode(&lone.node);
    try std.testing.expect(rbtree.emptyNode(&lone.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.next(&lone.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(&lone.node));
}

test "phase 7 rbtree eraseInit detaches erased nodes and keeps traversal stable" {
    var parsed = try loadFixture(std.testing.allocator);
    defer parsed.deinit();
    const fixture = parsed.value;

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
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    rbtree.eraseInit(&entries[0].node, &root);

    try std.testing.expectEqual(fixture.erase_init.detached_is_empty, rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(fixture.erase_init.detached_next_is_null, rbtree.next(&entries[0].node) == null);
    try std.testing.expectEqual(fixture.erase_init.detached_prev_is_null, rbtree.prev(&entries[0].node) == null);

    var actual: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        actual[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(fixture.erase_init.remaining_order.len, count);
    try std.testing.expectEqualSlices(i32, fixture.erase_init.remaining_order, actual[0..count]);
}

test "phase 7 rbtree detached nodes stay non-empty until callers clear them" {
    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var erase_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var erase_root = rbtree.Root.init();

    for (&erase_entries) |*entry| {
        rbtree.add(&entry.node, &erase_root, less);
    }

    rbtree.erase(&erase_entries[0].node, &erase_root);
    try std.testing.expect(!rbtree.emptyNode(&erase_entries[0].node));

    rbtree.clearNode(&erase_entries[0].node);
    try std.testing.expect(rbtree.emptyNode(&erase_entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.next(&erase_entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(&erase_entries[0].node));

    var replace_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var replacement = Entry{ .key = 10 };
    var replace_root = rbtree.Root.init();

    for (&replace_entries) |*entry| {
        rbtree.add(&entry.node, &replace_root, less);
    }

    rbtree.replaceNode(&replace_entries[0].node, &replacement.node, &replace_root);
    try std.testing.expect(!rbtree.emptyNode(&replace_entries[0].node));

    rbtree.clearNode(&replace_entries[0].node);
    try std.testing.expect(rbtree.emptyNode(&replace_entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.next(&replace_entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(&replace_entries[0].node));
}

test "phase 7 rbtree replaceNode overwrites stale replacement ownership state before reconnecting" {
    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var root_entry = Entry{ .key = 10 };
    var left_entry = Entry{ .key = 5 };
    var right_entry = Entry{ .key = 15 };
    var replacement = Entry{ .key = 5 };
    var stale_parent = rbtree.Node.init();
    var stale_left = rbtree.Node.init();
    var stale_right = rbtree.Node.init();
    var root = rbtree.Root.init();

    rbtree.add(&root_entry.node, &root, less);
    rbtree.add(&left_entry.node, &root, less);
    rbtree.add(&right_entry.node, &root, less);

    replacement.node.parent = &stale_parent;
    replacement.node.left = &stale_left;
    replacement.node.right = &stale_right;
    replacement.node.color = .red;

    rbtree.replaceNode(&left_entry.node, &replacement.node, &root);

    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), root_entry.node.left);
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), replacement.node.parent);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), replacement.node.left);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), replacement.node.right);
    try std.testing.expectEqual(left_entry.node.color, replacement.node.color);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.prev(&root_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.next(&replacement.node));
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

test "phase 7 rbtree eraseLinked clears detached linked ownership state and reconnects neighbours" {
    const LinkedEntry = struct {
        key: i32,
        linked: rbtree.NodeLinked = rbtree.NodeLinked.init(),
    };

    const helpers = struct {
        fn entryFromNode(node: *const rbtree.Node) *const LinkedEntry {
            const linked: *const rbtree.NodeLinked = @fieldParentPtr("node", node);
            return @fieldParentPtr("linked", linked);
        }

        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            return entryFromNode(lhs).key < entryFromNode(rhs).key;
        }
    };

    var entries = [_]LinkedEntry{
        .{ .key = 10 },
        .{ .key = 15 },
        .{ .key = 5 },
        .{ .key = 12 },
    };
    var root = rbtree.RootLinked.init();

    try std.testing.expect(rbtree.addLinked(&entries[0].linked, &root, helpers.compare));
    try std.testing.expect(!rbtree.addLinked(&entries[1].linked, &root, helpers.compare));
    try std.testing.expect(rbtree.addLinked(&entries[2].linked, &root, helpers.compare));
    try std.testing.expect(!rbtree.addLinked(&entries[3].linked, &root, helpers.compare));

    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, &entries[2].linked), root.leftmost);
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, &entries[0].linked), entries[2].linked.next);
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, &entries[3].linked), entries[0].linked.next);
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, &entries[1].linked), entries[3].linked.next);

    try std.testing.expect(rbtree.eraseLinked(&entries[3].linked, &root));
    try std.testing.expect(rbtree.emptyNode(&entries[3].linked.node));
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, null), entries[3].linked.prev);
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, null), entries[3].linked.next);
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, &entries[0].linked), entries[2].linked.next);
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, &entries[2].linked), entries[0].linked.prev);
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, &entries[1].linked), entries[0].linked.next);
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, &entries[0].linked), entries[1].linked.prev);
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, &entries[2].linked), root.leftmost);

    try std.testing.expect(rbtree.eraseLinked(&entries[2].linked, &root));
    try std.testing.expect(rbtree.emptyNode(&entries[2].linked.node));
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, null), entries[2].linked.prev);
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, null), entries[2].linked.next);
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, &entries[0].linked), root.leftmost);
    try std.testing.expectEqual(@as(?*rbtree.NodeLinked, null), entries[0].linked.prev);
}

test "phase 7 rbtree find helpers walk duplicate-key ranges" {
    var parsed = try loadFixture(std.testing.allocator);
    defer parsed.deinit();
    const fixture = parsed.value;

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
        fn compare(key: i32, node: *const rbtree.Node) i32 {
            const entry: *const Entry = @fieldParentPtr("node", node);
            return orderToInt(std.math.order(key, entry.key));
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 5, .serial = 0 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 15, .serial = 0 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const first_match = rbtree.findFirst(fixture.duplicates.key, &root, cmp) orelse return error.TestUnexpectedResult;
    const found = rbtree.find(fixture.duplicates.key, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(fixture.duplicates.key, (@as(*const Entry, @fieldParentPtr("node", found))).key);

    var actual_serials: [3]i32 = undefined;
    var match_count: usize = 0;
    var current_match: ?*rbtree.Node = first_match;
    while (current_match) |match| : (current_match = rbtree.nextMatch(fixture.duplicates.key, match, cmp)) {
        const entry: *const Entry = @fieldParentPtr("node", match);
        try std.testing.expectEqual(fixture.duplicates.key, entry.key);
        actual_serials[match_count] = entry.serial;
        match_count += 1;
    }

    try std.testing.expectEqual(fixture.duplicates.match_serials.len, match_count);
    try std.testing.expectEqualSlices(i32, fixture.duplicates.match_serials, actual_serials[0..match_count]);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.find(@as(i32, 99), &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findFirst(@as(i32, 99), &root, cmp));
}

test "phase 7 rbtree postorder traversal matches committed parity fixture" {
    var parsed = try loadFixture(std.testing.allocator);
    defer parsed.deinit();
    const fixture = parsed.value;

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 2 },
        .{ .key = 1 },
        .{ .key = 3 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var actual: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.firstPostorder(&root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        actual[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(fixture.postorder.traversal.len, count);
    try std.testing.expectEqualSlices(i32, fixture.postorder.traversal, actual[0..count]);
}

test "phase 7 rbtree cleared detached nodes stop postorder traversal" {
    var detached = rbtree.Node.init();

    rbtree.clearNode(&detached);

    try std.testing.expect(rbtree.emptyNode(&detached));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextPostorder(&detached));
}
