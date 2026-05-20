const std = @import("std");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn cmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn collectMatchSerials(root: *const rbtree.Root, key: i32, out: []usize) usize {
    var iter = rbtree.matchIterator(&key, root, cmpKey);
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.serial;
        count += 1;
    }
    return count;
}

test "phase1 rbtree cached replay keeps leftmost and duplicate iteration aligned" {
    var entries = [_]Entry{
        .{ .key = 5, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 20, .serial = 3 },
        .{ .key = 5, .serial = 4 },
    };
    var replacement = Entry{ .key = 5, .serial = 0 };
    var new_leftmost = Entry{ .key = 3, .serial = 5 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    var serials: [3]usize = undefined;
    var count = collectMatchSerials(&root.root, 5, &serials);
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &.{ 0, 2, 4 }, serials[0..count]);

    rbtree.replaceNodeCached(&entries[0].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    count = collectMatchSerials(&root.root, 5, &serials);
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &.{ 0, 2, 4 }, serials[0..count]);

    try std.testing.expectEqual(
        @as(?*rbtree.Node, &new_leftmost.node),
        rbtree.addCached(&new_leftmost.node, &root, less),
    );
    try std.testing.expectEqual(@as(?*rbtree.Node, &new_leftmost.node), rbtree.firstCached(&root));

    const promoted = rbtree.eraseCached(&new_leftmost.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &replacement.node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    count = collectMatchSerials(&root.root, 5, &serials);
    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(usize, &.{ 2, 4 }, serials[0..count]);
}

test "phase1 rbtree cached replay keeps alias helpers aligned across duplicate probes" {
    var primary_entries = [_]Entry{
        .{ .key = 7, .serial = 0 },
        .{ .key = 3, .serial = 1 },
        .{ .key = 7, .serial = 2 },
        .{ .key = 9, .serial = 3 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 7, .serial = 0 },
        .{ .key = 3, .serial = 1 },
        .{ .key = 7, .serial = 2 },
        .{ .key = 9, .serial = 3 },
    };
    var primary_probe = Entry{ .key = 7, .serial = 99 };
    var alias_probe = Entry{ .key = 7, .serial = 99 };
    var primary_smaller = Entry{ .key = 1, .serial = 4 };
    var alias_smaller = Entry{ .key = 1, .serial = 4 };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_root, less);
    }

    const primary_existing = rbtree.findAddCached(&primary_probe.node, &primary_root, cmpNode) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_probe.node, &alias_root, cmpNode) orelse return error.TestUnexpectedResult;
    const primary_existing_entry: *const Entry = @fieldParentPtr("node", primary_existing);
    const alias_existing_entry: *const Entry = @fieldParentPtr("node", alias_existing);
    try std.testing.expectEqual(@as(i32, 7), primary_existing_entry.key);
    try std.testing.expectEqual(primary_existing_entry.serial, alias_existing_entry.serial);
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.rb_first(&alias_root.root), rbtree.rb_first_cached(&alias_root));

    try std.testing.expectEqual(
        @as(?*rbtree.Node, &primary_smaller.node),
        rbtree.addCached(&primary_smaller.node, &primary_root, less),
    );
    try std.testing.expectEqual(
        @as(?*rbtree.Node, &alias_smaller.node),
        rbtree.rb_add_cached(&alias_smaller.node, &alias_root, less),
    );
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.rb_first(&alias_root.root), rbtree.rb_first_cached(&alias_root));

    rbtree.eraseInitCached(&primary_smaller.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_smaller.node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_smaller.node));
    try std.testing.expect(rbtree.emptyNode(&alias_smaller.node));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.rb_first(&alias_root.root), rbtree.rb_first_cached(&alias_root));

    var primary_serials: [2]usize = undefined;
    var alias_serials: [2]usize = undefined;
    const primary_count = collectMatchSerials(&primary_root.root, 7, &primary_serials);
    const alias_count = collectMatchSerials(&alias_root.root, 7, &alias_serials);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(usize, primary_serials[0..primary_count], alias_serials[0..alias_count]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 2 }, primary_serials[0..primary_count]);
}
