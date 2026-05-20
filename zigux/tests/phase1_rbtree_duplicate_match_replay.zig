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

fn collectMatchSerials(
    root: *const rbtree.Root,
    wanted: i32,
    serials: []usize,
) !usize {
    const first_match = rbtree.findFirst(&wanted, root, cmpKey) orelse return 0;
    var count: usize = 0;
    var cursor: *const rbtree.Node = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", cursor);
        serials[count] = entry.serial;
        count += 1;
        cursor = rbtree.nextMatch(&wanted, cursor, cmpKey) orelse break;
    }
    return count;
}

test "phase1 rbtree duplicate matches keep duplicate order stable" {
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

    const wanted = @as(i32, 10);
    const found = rbtree.find(&wanted, &root, cmpKey) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(i32, 10), found_entry.key);

    var serials: [3]usize = undefined;
    const count = try collectMatchSerials(&root, wanted, &serials);
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);

    const missing = @as(i32, 17);
    try std.testing.expect(rbtree.find(&missing, &root, cmpKey) == null);
    try std.testing.expect(rbtree.findFirst(&missing, &root, cmpKey) == null);
}

test "phase1 rbtree duplicate iterators mirror the primary walk" {
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

    const wanted = @as(i32, 10);
    const first_primary = rbtree.findFirst(&wanted, &root, cmpKey) orelse return error.TestUnexpectedResult;

    var primary_serials: [3]usize = undefined;
    var primary_count: usize = 0;
    var primary_cursor: *const rbtree.Node = first_primary;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", primary_cursor);
        primary_serials[primary_count] = entry.serial;
        primary_count += 1;
        primary_cursor = rbtree.nextMatch(&wanted, primary_cursor, cmpKey) orelse break;
    }

    var iter = rbtree.matchIterator(&wanted, &root, cmpKey);
    var iterator_serials: [3]usize = undefined;
    var iterator_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        iterator_serials[iterator_count] = entry.serial;
        iterator_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), primary_count);
    try std.testing.expectEqual(primary_count, iterator_count);
    try std.testing.expectEqualSlices(usize, primary_serials[0..primary_count], iterator_serials[0..iterator_count]);
}

test "phase1 rbtree cached duplicate insert helpers keep leftmost stable" {
    var leftmost = Entry{ .key = 5, .serial = 0 };
    var root_entry = Entry{ .key = 10, .serial = 1 };
    var larger_entry = Entry{ .key = 15, .serial = 2 };
    var duplicate_probe = Entry{ .key = 10, .serial = 3 };
    var alias_duplicate_probe = Entry{ .key = 10, .serial = 4 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&root_entry.node, &root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&leftmost.node, &root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&larger_entry.node, &root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.rb_first_cached(&root));

    const duplicate = rbtree.findAddCached(&duplicate_probe.node, &root, cmpNode) orelse return error.TestUnexpectedResult;
    const alias_duplicate = rbtree.rb_find_add_cached(&alias_duplicate_probe.node, &root, cmpNode) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), duplicate);
    try std.testing.expectEqual(duplicate, alias_duplicate);
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
