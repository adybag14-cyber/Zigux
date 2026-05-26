const std = @import("std");
const rbtree = @import("./rbtree.zig");

test "phase7 rbtree duplicate-range helpers keep ordered matches reviewable" {
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

    const duplicate = @as(i32, 10);
    const found = rbtree.find(&duplicate, &root, cmp) orelse return error.TestUnexpectedResult;
    const alias_found = rbtree.rb_find(&duplicate, &root, cmp) orelse return error.TestUnexpectedResult;
    const first_match = rbtree.findFirst(&duplicate, &root, cmp) orelse return error.TestUnexpectedResult;
    const alias_first_match = rbtree.rb_find_first(&duplicate, &root, cmp) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(*rbtree.Node, first_match), alias_first_match);
    try std.testing.expectEqual(@as(i32, 10), (@as(*const Entry, @fieldParentPtr("node", found))).key);
    try std.testing.expectEqual(@as(i32, 10), (@as(*const Entry, @fieldParentPtr("node", alias_found))).key);

    var primary_serials: [3]usize = undefined;
    var alias_serials: [3]usize = undefined;
    var primary_count: usize = 0;
    var alias_count: usize = 0;

    var primary_cursor = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", primary_cursor);
        primary_serials[primary_count] = entry.serial;
        primary_count += 1;
        primary_cursor = rbtree.nextMatch(&duplicate, primary_cursor, cmp) orelse break;
    }

    var alias_cursor = alias_first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", alias_cursor);
        alias_serials[alias_count] = entry.serial;
        alias_count += 1;
        alias_cursor = rbtree.rb_next_match(&duplicate, alias_cursor, cmp) orelse break;
    }

    try std.testing.expectEqual(@as(usize, 3), primary_count);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, primary_serials[0..primary_count]);
    try std.testing.expectEqualSlices(usize, primary_serials[0..primary_count], alias_serials[0..alias_count]);

    var iter = rbtree.matchIterator(&duplicate, &root, cmp);
    var alias_iter = rbtree.rb_match_iterator(&duplicate, &root, cmp);
    var iter_serials: [3]usize = undefined;
    var alias_iter_serials: [3]usize = undefined;
    var iter_count: usize = 0;
    var alias_iter_count: usize = 0;

    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        iter_serials[iter_count] = entry.serial;
        iter_count += 1;
    }
    while (alias_iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_iter_serials[alias_iter_count] = entry.serial;
        alias_iter_count += 1;
    }

    try std.testing.expectEqual(primary_count, iter_count);
    try std.testing.expectEqual(iter_count, alias_iter_count);
    try std.testing.expectEqualSlices(usize, primary_serials[0..primary_count], iter_serials[0..iter_count]);
    try std.testing.expectEqualSlices(usize, iter_serials[0..iter_count], alias_iter_serials[0..alias_iter_count]);
}

test "phase7 rbtree detached nodes stay out of successor and postorder walks" {
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
        .{ .key = 2 },
        .{ .key = 1 },
        .{ .key = 4 },
        .{ .key = 3 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var primary_count: usize = 0;
    var alias_count: usize = 0;
    var primary_cursor = rbtree.firstPostorder(&root);
    var alias_cursor = rbtree.rb_first_postorder(&root);
    while (primary_cursor) |node| : (primary_cursor = rbtree.nextPostorder(node)) {
        primary_count += 1;
    }
    while (alias_cursor) |node| : (alias_cursor = rbtree.rb_next_postorder(node)) {
        alias_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), primary_count);
    try std.testing.expectEqual(primary_count, alias_count);

    var detached = rbtree.Node.init();
    rbtree.clearNode(&detached);
    try std.testing.expect(rbtree.emptyNode(&detached));
    try std.testing.expect(rbtree.next(&detached) == null);
    try std.testing.expect(rbtree.prev(&detached) == null);
    try std.testing.expect(rbtree.nextPostorder(&detached) == null);
    try std.testing.expect(rbtree.rb_next_postorder(&detached) == null);
}
