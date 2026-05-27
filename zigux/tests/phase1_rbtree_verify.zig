const std = @import("std");
const rbtree = @import("../../tools/lib/rbtree.zig");

const ReplayEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),

    fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
        const lhs_entry: *const ReplayEntry = @fieldParentPtr("node", lhs);
        const rhs_entry: *const ReplayEntry = @fieldParentPtr("node", rhs);
        if (lhs_entry.key != rhs_entry.key) {
            return lhs_entry.key < rhs_entry.key;
        }
        return lhs_entry.serial < rhs_entry.serial;
    }

    fn cmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
        const wanted: *const i32 = @ptrCast(@alignCast(key));
        const entry: *const ReplayEntry = @fieldParentPtr("node", node);
        if (wanted.* < entry.key) return -1;
        if (wanted.* > entry.key) return 1;
        return 0;
    }
};

test "phase 1 rbtree verifier records the exact bounded checks" {
    var root = rbtree.Root.init();
    try std.testing.expect(root.node == null);

    var tree_entries = [_]ReplayEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 25, .serial = 4 },
        .{ .key = 15, .serial = 5 },
        .{ .key = 10, .serial = 6 },
    };
    for (&tree_entries) |*entry| {
        rbtree.add(&entry.node, &root, ReplayEntry.less);
    }

    var ordered: [5]i32 = undefined;
    var ordered_count: usize = 0;
    var node = rbtree.first(&root);
    while (node) |current_node| : (node = rbtree.next(current_node)) {
        const entry: *const ReplayEntry = @fieldParentPtr("node", current_node);
        if (entry.serial == 0 or entry.serial == 1 or entry.serial == 3 or entry.serial == 4 or entry.serial == 5) {
            ordered[ordered_count] = entry.key;
            ordered_count += 1;
        }
    }
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15, 20, 25 }, ordered[0..ordered_count]);

    var reverse: [5]i32 = undefined;
    var reverse_count: usize = 0;
    node = rbtree.last(&root);
    while (node) |current_node| : (node = rbtree.prev(current_node)) {
        const entry: *const ReplayEntry = @fieldParentPtr("node", current_node);
        if (entry.serial == 0 or entry.serial == 1 or entry.serial == 3 or entry.serial == 4 or entry.serial == 5) {
            reverse[reverse_count] = entry.key;
            reverse_count += 1;
        }
    }
    try std.testing.expectEqualSlices(i32, &[_]i32{ 25, 20, 15, 10, 5 }, reverse[0..reverse_count]);

    var replace_entries = [_]ReplayEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 15, .serial = 3 },
        .{ .key = 25, .serial = 4 },
    };
    var replacement = ReplayEntry{ .key = 10, .serial = 5 };
    var replace_root = rbtree.Root.init();
    for (&replace_entries) |*entry| {
        rbtree.add(&entry.node, &replace_root, ReplayEntry.less);
    }
    rbtree.erase(&replace_entries[1].node, &replace_root);
    rbtree.replaceNode(&replace_entries[0].node, &replacement.node, &replace_root);

    var replace_order: [4]i32 = undefined;
    var replace_count: usize = 0;
    node = rbtree.first(&replace_root);
    while (node) |current_node| : (node = rbtree.next(current_node)) {
        const entry: *const ReplayEntry = @fieldParentPtr("node", current_node);
        replace_order[replace_count] = entry.key;
        replace_count += 1;
    }
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15, 25 }, replace_order[0..replace_count]);

    rbtree.eraseInit(&replacement.node, &replace_root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));

    var erase_init_order: [3]i32 = undefined;
    var erase_init_count: usize = 0;
    node = rbtree.first(&replace_root);
    while (node) |current_node| : (node = rbtree.next(current_node)) {
        const entry: *const ReplayEntry = @fieldParentPtr("node", current_node);
        erase_init_order[erase_init_count] = entry.key;
        erase_init_count += 1;
    }
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 15, 25 }, erase_init_order[0..erase_init_count]);

    var detached = rbtree.Node.init();
    rbtree.clearNode(&detached);
    try std.testing.expect(rbtree.emptyNode(&detached));

    var postorder_entries = [_]ReplayEntry{
        .{ .key = 2, .serial = 0 },
        .{ .key = 1, .serial = 1 },
        .{ .key = 3, .serial = 2 },
    };
    var postorder_root = rbtree.Root.init();
    for (&postorder_entries) |*entry| {
        rbtree.add(&entry.node, &postorder_root, ReplayEntry.less);
    }
    var postorder_count: usize = 0;
    var postorder_node = rbtree.firstPostorder(&postorder_root);
    while (postorder_node) |current_node| : (postorder_node = rbtree.nextPostorder(current_node)) {
        _ = current_node;
        postorder_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), postorder_count);

    const duplicate_key = @as(i32, 10);
    const found = rbtree.find(&duplicate_key, &root, ReplayEntry.cmp) orelse return error.TestUnexpectedResult;
    const found_entry: *const ReplayEntry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(i32, 10), found_entry.key);

    const missing_key = @as(i32, 17);
    try std.testing.expect(rbtree.find(&missing_key, &root, ReplayEntry.cmp) == null);

    const first_duplicate = rbtree.findFirst(&duplicate_key, &root, ReplayEntry.cmp) orelse return error.TestUnexpectedResult;
    const first_duplicate_entry: *const ReplayEntry = @fieldParentPtr("node", first_duplicate);
    try std.testing.expectEqual(@as(usize, 0), first_duplicate_entry.serial);

    var duplicate_serials: [3]usize = undefined;
    var duplicate_count: usize = 0;
    var iter = rbtree.matchIterator(&duplicate_key, &root, ReplayEntry.cmp);
    while (iter.next()) |current_node| {
        const entry: *const ReplayEntry = @fieldParentPtr("node", current_node);
        duplicate_serials[duplicate_count] = entry.serial;
        duplicate_count += 1;
    }
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 6 }, duplicate_serials[0..duplicate_count]);

    duplicate_serials = undefined;
    duplicate_count = 0;
    var current_match: ?*rbtree.Node = first_duplicate;
    var terminal_match: *rbtree.Node = first_duplicate;
    while (current_match) |match_node| {
        const entry: *const ReplayEntry = @fieldParentPtr("node", match_node);
        duplicate_serials[duplicate_count] = entry.serial;
        duplicate_count += 1;
        terminal_match = match_node;
        current_match = rbtree.nextMatch(&duplicate_key, match_node, ReplayEntry.cmp);
    }
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 6 }, duplicate_serials[0..duplicate_count]);
    try std.testing.expect(rbtree.nextMatch(&duplicate_key, terminal_match, ReplayEntry.cmp) == null);

    var cached_entries = [_]ReplayEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 12, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 5, .serial = 3 },
    };
    var cached_root = rbtree.RootCached.init();
    var return_serials: [4]i32 = undefined;
    return_serials[0] = serialOrSentinel(rbtree.addCached(&cached_entries[0].node, &cached_root, ReplayEntry.less));
    return_serials[1] = serialOrSentinel(rbtree.addCached(&cached_entries[1].node, &cached_root, ReplayEntry.less));
    return_serials[2] = serialOrSentinel(rbtree.addCached(&cached_entries[2].node, &cached_root, ReplayEntry.less));
    return_serials[3] = serialOrSentinel(rbtree.addCached(&cached_entries[3].node, &cached_root, ReplayEntry.less));
    try std.testing.expectEqualSlices(i32, &[_]i32{ 0, -1, 2, -1 }, &return_serials);

    var cached_transition_entries = [_]ReplayEntry{
        .{ .key = 10, .serial = 1 },
        .{ .key = 5, .serial = 0 },
        .{ .key = 20, .serial = 3 },
        .{ .key = 15, .serial = 5 },
    };
    var cached_replacement = ReplayEntry{ .key = 10, .serial = 4 };
    var cached_new_leftmost = ReplayEntry{ .key = 3, .serial = 2 };
    var cached_transition_root = rbtree.RootCached.init();
    for (&cached_transition_entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &cached_transition_root, ReplayEntry.less);
    }
    var cached_transition_serials: [4]i32 = undefined;
    cached_transition_serials[0] = serialOrSentinel(rbtree.firstCached(&cached_transition_root));
    _ = rbtree.eraseCached(&cached_transition_entries[2].node, &cached_transition_root);
    cached_transition_serials[1] = serialOrSentinel(rbtree.firstCached(&cached_transition_root));
    rbtree.replaceNodeCached(&cached_transition_entries[1].node, &cached_replacement.node, &cached_transition_root);
    cached_transition_serials[2] = serialOrSentinel(rbtree.firstCached(&cached_transition_root));
    _ = rbtree.addCached(&cached_new_leftmost.node, &cached_transition_root, ReplayEntry.less);
    cached_transition_serials[3] = serialOrSentinel(rbtree.firstCached(&cached_transition_root));
    try std.testing.expectEqualSlices(i32, &[_]i32{ 0, 0, 4, 2 }, &cached_transition_serials);
}

fn serialOrSentinel(node: ?*rbtree.Node) i32 {
    const current = node orelse return -1;
    const entry: *const ReplayEntry = @fieldParentPtr("node", current);
    return @as(i32, @intCast(entry.serial));
}
