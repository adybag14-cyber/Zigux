const std = @import("std");
const rbtree = @import("rbtree");

fn lessWithSerial(comptime Entry: type) rbtree.LessFn {
    return struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;
}

fn cmpWithSerial(comptime Entry: type) rbtree.CmpNodeFn {
    return struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;
}

fn keyOf(comptime Entry: type, node: ?*rbtree.Node) ?i32 {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return entry.key;
}

fn identityOf(comptime Entry: type, node: ?*rbtree.Node) ?struct { i32, usize } {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

test "phase 1 rbtree review anchor replay keeps ordered aliases aligned after replace" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = lessWithSerial(Entry);
    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };
    var primary_replacement = Entry{ .key = 10, .serial = 4 };
    var alias_replacement = Entry{ .key = 10, .serial = 4 };
    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, less);
        rbtree.add(&alias_entry.node, &alias_root, less);
    }

    var primary_forward: [5]i32 = undefined;
    var alias_forward: [5]i32 = undefined;
    var primary_count: usize = 0;
    var alias_count: usize = 0;

    var current = rbtree.first(&primary_root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        primary_forward[primary_count] = entry.key;
        primary_count += 1;
    }

    current = rbtree.rb_first(&alias_root);
    while (current) |node| : (current = rbtree.rb_next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_forward[alias_count] = entry.key;
        alias_count += 1;
    }

    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, primary_forward[0..primary_count], alias_forward[0..alias_count]);

    var primary_reverse: [5]i32 = undefined;
    var alias_reverse: [5]i32 = undefined;
    primary_count = 0;
    alias_count = 0;

    current = rbtree.last(&primary_root);
    while (current) |node| : (current = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        primary_reverse[primary_count] = entry.key;
        primary_count += 1;
    }

    current = rbtree.rb_last(&alias_root);
    while (current) |node| : (current = rbtree.rb_prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_reverse[alias_count] = entry.key;
        alias_count += 1;
    }

    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, primary_reverse[0..primary_count], alias_reverse[0..alias_count]);

    rbtree.replaceNode(&primary_entries[0].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node(&alias_entries[0].node, &alias_replacement.node, &alias_root);

    try std.testing.expectEqual(keyOf(Entry, rbtree.first(&primary_root)), keyOf(Entry, rbtree.rb_first(&alias_root)));
    try std.testing.expectEqual(keyOf(Entry, rbtree.last(&primary_root)), keyOf(Entry, rbtree.rb_last(&alias_root)));
}

test "phase 1 rbtree review anchor replay keeps cached-leftmost return serials aligned" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = lessWithSerial(Entry);

    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 12, .serial = 3 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 12, .serial = 3 },
    };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    var primary_returns: [5]?struct { i32, usize } = undefined;
    var alias_returns: [5]?struct { i32, usize } = undefined;

    primary_returns[0] = identityOf(Entry, rbtree.addCached(&primary_entries[0].node, &primary_root, less));
    alias_returns[0] = identityOf(Entry, rbtree.rb_add_cached(&alias_entries[0].node, &alias_root, less));
    primary_returns[1] = identityOf(Entry, rbtree.addCached(&primary_entries[1].node, &primary_root, less));
    alias_returns[1] = identityOf(Entry, rbtree.rb_add_cached(&alias_entries[1].node, &alias_root, less));
    primary_returns[2] = identityOf(Entry, rbtree.addCached(&primary_entries[2].node, &primary_root, less));
    alias_returns[2] = identityOf(Entry, rbtree.rb_add_cached(&alias_entries[2].node, &alias_root, less));
    primary_returns[3] = identityOf(Entry, rbtree.eraseCached(&primary_entries[1].node, &primary_root));
    alias_returns[3] = identityOf(Entry, rbtree.rb_erase_cached(&alias_entries[1].node, &alias_root));
    primary_returns[4] = identityOf(Entry, rbtree.eraseCached(&primary_entries[2].node, &primary_root));
    alias_returns[4] = identityOf(Entry, rbtree.rb_erase_cached(&alias_entries[2].node, &alias_root));

    try std.testing.expectEqualDeep(primary_returns, alias_returns);
    try std.testing.expectEqualDeep(
        [_]?struct { i32, usize }{
            .{ 10, 0 },
            .{ 5, 1 },
            null,
            .{ 5, 2 },
            .{ 10, 0 },
        },
        primary_returns,
    );

    _ = rbtree.addCached(&primary_entries[3].node, &primary_root, less);
    _ = rbtree.rb_add_cached(&alias_entries[3].node, &alias_root, less);
    try std.testing.expectEqual(keyOf(Entry, rbtree.firstCached(&primary_root)), keyOf(Entry, rbtree.rb_first_cached(&alias_root)));
    try std.testing.expectEqual(keyOf(Entry, rbtree.first(&primary_root.root)), keyOf(Entry, rbtree.firstCached(&primary_root)));
}

test "phase 1 rbtree review anchor replay keeps cached-root alias detach and reseed paths aligned" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = lessWithSerial(Entry);
    const cmp = cmpWithSerial(Entry);

    var primary_root_entry = Entry{ .key = 10, .serial = 0 };
    var alias_root_entry = Entry{ .key = 10, .serial = 0 };
    var primary_leftmost = Entry{ .key = 5, .serial = 1 };
    var alias_leftmost = Entry{ .key = 5, .serial = 1 };
    var primary_larger = Entry{ .key = 15, .serial = 2 };
    var alias_larger = Entry{ .key = 15, .serial = 2 };
    var primary_duplicate = Entry{ .key = 10, .serial = 3 };
    var alias_duplicate = Entry{ .key = 10, .serial = 3 };
    var primary_non_leftmost_replacement = Entry{ .key = 15, .serial = 4 };
    var alias_non_leftmost_replacement = Entry{ .key = 15, .serial = 4 };
    var primary_reseed = Entry{ .key = 6, .serial = 5 };
    var alias_reseed = Entry{ .key = 6, .serial = 5 };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_root_entry.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_root_entry.node, &alias_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_leftmost.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_leftmost.node, &alias_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_larger.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_larger.node, &alias_root, cmp));

    const primary_existing = rbtree.findAddCached(&primary_duplicate.node, &primary_root, cmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(identityOf(Entry, primary_existing), identityOf(Entry, alias_existing));

    rbtree.replaceNodeCached(&primary_larger.node, &primary_non_leftmost_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_larger.node, &alias_non_leftmost_replacement.node, &alias_root);
    try std.testing.expectEqual(keyOf(Entry, rbtree.firstCached(&primary_root)), keyOf(Entry, rbtree.rb_first_cached(&alias_root)));
    try std.testing.expectEqual(keyOf(Entry, rbtree.last(&primary_root.root)), keyOf(Entry, rbtree.rb_last(&alias_root.root)));

    rbtree.eraseInitCached(&primary_leftmost.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_leftmost.node, &alias_root);
    try std.testing.expectEqual(keyOf(Entry, rbtree.firstCached(&primary_root)), keyOf(Entry, rbtree.rb_first_cached(&alias_root)));

    rbtree.eraseInitCached(&primary_root_entry.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_root_entry.node, &alias_root);
    try std.testing.expectEqual(keyOf(Entry, rbtree.firstCached(&primary_root)), keyOf(Entry, rbtree.rb_first_cached(&alias_root)));

    rbtree.eraseInitCached(&primary_non_leftmost_replacement.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_non_leftmost_replacement.node, &alias_root);
    try std.testing.expectEqual(@as(?i32, null), keyOf(Entry, rbtree.firstCached(&primary_root)));
    try std.testing.expectEqual(@as(?i32, null), keyOf(Entry, rbtree.rb_first_cached(&alias_root)));

    try std.testing.expect(rbtree.emptyNode(&primary_leftmost.node));
    try std.testing.expect(rbtree.emptyNode(&primary_root_entry.node));
    try std.testing.expect(rbtree.emptyNode(&primary_non_leftmost_replacement.node));

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_reseed.node), rbtree.addCached(&primary_reseed.node, &primary_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_reseed.node), rbtree.rb_add_cached(&alias_reseed.node, &alias_root, less));
    try std.testing.expectEqual(keyOf(Entry, rbtree.first(&primary_root.root)), keyOf(Entry, rbtree.firstCached(&primary_root)));
    try std.testing.expectEqual(keyOf(Entry, rbtree.firstCached(&primary_root)), keyOf(Entry, rbtree.rb_first_cached(&alias_root)));
}
