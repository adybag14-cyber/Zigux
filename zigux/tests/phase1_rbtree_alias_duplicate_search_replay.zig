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
    if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
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

fn identity(node: ?*rbtree.Node) ?struct { i32, usize } {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

test "phase1 rbtree alias duplicate search wrappers mirror primary duplicate-range helpers" {
    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, less);
        rbtree.add(&alias_entry.node, &alias_root, less);
    }

    const wanted = @as(i32, 10);
    try std.testing.expectEqual(
        identity(rbtree.find(&wanted, &primary_root, cmpKey)),
        identity(rbtree.rb_find(&wanted, &alias_root, cmpKey)),
    );
    try std.testing.expectEqual(
        identity(rbtree.findFirst(&wanted, &primary_root, cmpKey)),
        identity(rbtree.rb_find_first(&wanted, &alias_root, cmpKey)),
    );

    var primary_serials: [3]usize = undefined;
    var alias_serials: [3]usize = undefined;
    var primary_count: usize = 0;
    var alias_count: usize = 0;

    var primary_cursor = rbtree.findFirst(&wanted, &primary_root, cmpKey) orelse return error.TestUnexpectedResult;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", primary_cursor);
        primary_serials[primary_count] = entry.serial;
        primary_count += 1;
        primary_cursor = rbtree.nextMatch(&wanted, primary_cursor, cmpKey) orelse break;
    }

    var alias_cursor = rbtree.rb_find_first(&wanted, &alias_root, cmpKey) orelse return error.TestUnexpectedResult;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", alias_cursor);
        alias_serials[alias_count] = entry.serial;
        alias_count += 1;
        alias_cursor = rbtree.rb_next_match(&wanted, alias_cursor, cmpKey) orelse break;
    }

    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(usize, primary_serials[0..primary_count], alias_serials[0..alias_count]);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, alias_serials[0..alias_count]);
    try std.testing.expect(rbtree.rb_next_match(&wanted, alias_cursor, cmpKey) == null);
}

test "phase1 rbtree alias match iterator keeps duplicate order and missing probes stable" {
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| rbtree.add(&entry.node, &root, less);

    const wanted = @as(i32, 10);
    var iter = rbtree.rb_match_iterator(&wanted, &root, cmpKey);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);

    const missing = @as(i32, 17);
    var missing_iter = rbtree.rb_match_iterator(&missing, &root, cmpKey);
    try std.testing.expect(missing_iter.next() == null);
}

test "phase1 rbtree cached duplicate-search aliases keep leftmost and duplicate hits aligned" {
    var primary_first = Entry{ .key = 10, .serial = 0 };
    var alias_first = Entry{ .key = 10, .serial = 0 };
    var primary_leftmost = Entry{ .key = 5, .serial = 1 };
    var alias_leftmost = Entry{ .key = 5, .serial = 1 };
    var primary_larger = Entry{ .key = 15, .serial = 2 };
    var alias_larger = Entry{ .key = 15, .serial = 2 };
    var primary_duplicate = Entry{ .key = 10, .serial = 3 };
    var alias_duplicate = Entry{ .key = 10, .serial = 3 };

    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_first.node, &primary_root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_first.node, &alias_root, cmpNode));
    try std.testing.expectEqual(identity(rbtree.firstCached(&primary_root)), identity(rbtree.firstCached(&alias_root)));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_leftmost.node, &primary_root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_leftmost.node, &alias_root, cmpNode));
    try std.testing.expectEqual(identity(rbtree.firstCached(&primary_root)), identity(rbtree.firstCached(&alias_root)));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_larger.node, &primary_root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_larger.node, &alias_root, cmpNode));
    try std.testing.expectEqual(identity(rbtree.firstCached(&primary_root)), identity(rbtree.firstCached(&alias_root)));

    try std.testing.expectEqual(
        identity(rbtree.findAddCached(&primary_duplicate.node, &primary_root, cmpNode)),
        identity(rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, cmpNode)),
    );
    try std.testing.expectEqual(identity(rbtree.firstCached(&primary_root)), identity(rbtree.firstCached(&alias_root)));
    try std.testing.expectEqual(identity(rbtree.first(&primary_root.root)), identity(rbtree.firstCached(&primary_root)));
    try std.testing.expectEqual(identity(rbtree.first(&alias_root.root)), identity(rbtree.firstCached(&alias_root)));
}
