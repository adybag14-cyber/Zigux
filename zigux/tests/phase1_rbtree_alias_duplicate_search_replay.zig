const std = @import("std");
const rbtree = @import("rbtree");

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

fn addReplayEntries(root: *rbtree.Root, entries: []ReplayEntry) void {
    for (entries) |*entry| {
        rbtree.rb_add(&entry.node, root, ReplayEntry.less);
    }
}

fn collectPrimaryDuplicateSerials(
    key: *const i32,
    first_match: *rbtree.Node,
) [3]usize {
    var serials: [3]usize = undefined;
    var count: usize = 0;
    var cursor: ?*rbtree.Node = first_match;
    while (cursor) |node| {
        const entry: *const ReplayEntry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
        cursor = rbtree.nextMatch(key, node, ReplayEntry.cmp);
    }
    std.debug.assert(count == serials.len);
    return serials;
}

fn collectAliasDuplicateSerials(
    key: *const i32,
    first_match: *rbtree.Node,
) [3]usize {
    var serials: [3]usize = undefined;
    var count: usize = 0;
    var cursor: ?*rbtree.Node = first_match;
    while (cursor) |node| {
        const entry: *const ReplayEntry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
        cursor = rbtree.rb_next_match(key, node, ReplayEntry.cmp);
    }
    std.debug.assert(count == serials.len);
    return serials;
}

test "phase1 rbtree alias duplicate-search replay keeps lookup wrappers aligned" {
    var entries = [_]ReplayEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var root = rbtree.Root.init();
    addReplayEntries(&root, &entries);

    const wanted = @as(i32, 15);
    const primary_found = rbtree.find(&wanted, &root, ReplayEntry.cmp) orelse return error.TestUnexpectedResult;
    const alias_found = rbtree.rb_find(&wanted, &root, ReplayEntry.cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(primary_found, alias_found);

    const found_entry: *const ReplayEntry = @fieldParentPtr("node", primary_found);
    try std.testing.expectEqual(@as(i32, 15), found_entry.key);
    try std.testing.expectEqual(@as(usize, 5), found_entry.serial);

    const missing = @as(i32, 17);
    try std.testing.expect(rbtree.find(&missing, &root, ReplayEntry.cmp) == null);
    try std.testing.expect(rbtree.rb_find(&missing, &root, ReplayEntry.cmp) == null);

    const duplicate = @as(i32, 10);
    const primary_first = rbtree.findFirst(&duplicate, &root, ReplayEntry.cmp) orelse return error.TestUnexpectedResult;
    const alias_first = rbtree.rb_find_first(&duplicate, &root, ReplayEntry.cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(primary_first, alias_first);

    const first_entry: *const ReplayEntry = @fieldParentPtr("node", primary_first);
    try std.testing.expectEqual(@as(usize, 0), first_entry.serial);

    try std.testing.expectEqualSlices(
        usize,
        &collectPrimaryDuplicateSerials(&duplicate, primary_first),
        &collectAliasDuplicateSerials(&duplicate, alias_first),
    );
}

test "phase1 rbtree alias duplicate-search replay keeps iterator wrappers aligned" {
    var entries = [_]ReplayEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var root = rbtree.Root.init();
    addReplayEntries(&root, &entries);

    const duplicate = @as(i32, 10);

    var primary_iter = rbtree.matchIterator(&duplicate, &root, ReplayEntry.cmp);
    var alias_iter = rbtree.rb_match_iterator(&duplicate, &root, ReplayEntry.cmp);

    var primary_serials: [3]usize = undefined;
    var alias_serials: [3]usize = undefined;
    var primary_count: usize = 0;
    var alias_count: usize = 0;

    while (primary_iter.next()) |node| {
        const entry: *const ReplayEntry = @fieldParentPtr("node", node);
        primary_serials[primary_count] = entry.serial;
        primary_count += 1;
    }
    while (alias_iter.next()) |node| {
        const entry: *const ReplayEntry = @fieldParentPtr("node", node);
        alias_serials[alias_count] = entry.serial;
        alias_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), primary_count);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(usize, primary_serials[0..primary_count], alias_serials[0..alias_count]);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, alias_serials[0..alias_count]);

    const missing = @as(i32, 17);
    var missing_primary = rbtree.matchIterator(&missing, &root, ReplayEntry.cmp);
    var missing_alias = rbtree.rb_match_iterator(&missing, &root, ReplayEntry.cmp);
    try std.testing.expect(missing_primary.next() == null);
    try std.testing.expect(missing_alias.next() == null);
}
