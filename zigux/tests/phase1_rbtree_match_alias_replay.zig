const std = @import("std");
const rbtree = @import("rbtree");

const OrderedEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn orderedLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const OrderedEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const OrderedEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn compareKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const OrderedEntry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn duplicateSerialsFromFirst(key: *const i32, root: *const rbtree.Root, use_aliases: bool, out: []usize) usize {
    const first_match = (if (use_aliases) rbtree.rb_find_first(key, root, compareKey) else rbtree.findFirst(key, root, compareKey)) orelse return 0;

    var count: usize = 0;
    var current = first_match;
    while (true) {
        const entry: *const OrderedEntry = @fieldParentPtr("node", current);
        out[count] = entry.serial;
        count += 1;
        const next_match = if (use_aliases) rbtree.rb_next_match(key, current, compareKey) else rbtree.nextMatch(key, current, compareKey);
        current = next_match orelse break;
    }

    return count;
}

fn iteratorSerials(key: *const i32, root: *const rbtree.Root, use_aliases: bool, out: []usize) usize {
    var iter = if (use_aliases) rbtree.rb_match_iterator(key, root, compareKey) else rbtree.matchIterator(key, root, compareKey);
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const OrderedEntry = @fieldParentPtr("node", node);
        out[count] = entry.serial;
        count += 1;
    }
    return count;
}

test "phase1 rbtree match aliases mirror duplicate find and next helpers" {
    var primary_entries = [_]OrderedEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var alias_entries = [_]OrderedEntry{
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
        rbtree.add(&primary_entry.node, &primary_root, orderedLess);
        rbtree.add(&alias_entry.node, &alias_root, orderedLess);
    }

    const exact = @as(i32, 15);
    const primary_hit = rbtree.find(&exact, &primary_root, compareKey) orelse return error.TestUnexpectedResult;
    const alias_hit = rbtree.rb_find(&exact, &alias_root, compareKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 15), (@as(*const OrderedEntry, @fieldParentPtr("node", primary_hit))).key);
    try std.testing.expectEqual(@as(i32, 15), (@as(*const OrderedEntry, @fieldParentPtr("node", alias_hit))).key);

    const missing = @as(i32, 17);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.find(&missing, &primary_root, compareKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find(&missing, &alias_root, compareKey));

    const duplicate = @as(i32, 10);
    var primary_serials: [3]usize = undefined;
    var alias_serials: [3]usize = undefined;
    const primary_count = duplicateSerialsFromFirst(&duplicate, &primary_root, false, &primary_serials);
    const alias_count = duplicateSerialsFromFirst(&duplicate, &alias_root, true, &alias_serials);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqual(@as(usize, 3), primary_count);
    try std.testing.expectEqualSlices(usize, primary_serials[0..primary_count], alias_serials[0..alias_count]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 2, 4 }, primary_serials[0..primary_count]);

    const primary_first = rbtree.findFirst(&duplicate, &primary_root, compareKey) orelse return error.TestUnexpectedResult;
    const alias_first = rbtree.rb_find_first(&duplicate, &alias_root, compareKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), (@as(*const OrderedEntry, @fieldParentPtr("node", primary_first))).serial);
    try std.testing.expectEqual(@as(usize, 0), (@as(*const OrderedEntry, @fieldParentPtr("node", alias_first))).serial);
    const primary_second = rbtree.nextMatch(&duplicate, primary_first, compareKey) orelse return error.TestUnexpectedResult;
    const alias_second = rbtree.rb_next_match(&duplicate, alias_first, compareKey) orelse return error.TestUnexpectedResult;
    const primary_last = rbtree.nextMatch(&duplicate, primary_second, compareKey) orelse return error.TestUnexpectedResult;
    const alias_last = rbtree.rb_next_match(&duplicate, alias_second, compareKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextMatch(&duplicate, primary_last, compareKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_next_match(&duplicate, alias_last, compareKey));
}

test "phase1 rbtree match iterator aliases stay aligned across duplicate-range reseed" {
    var primary_entries = [_]OrderedEntry{
        .{ .key = 8, .serial = 0 },
        .{ .key = 8, .serial = 1 },
        .{ .key = 3, .serial = 2 },
        .{ .key = 12, .serial = 3 },
    };
    var alias_entries = [_]OrderedEntry{
        .{ .key = 8, .serial = 0 },
        .{ .key = 8, .serial = 1 },
        .{ .key = 3, .serial = 2 },
        .{ .key = 12, .serial = 3 },
    };
    var reseed_primary = [_]OrderedEntry{
        .{ .key = 6, .serial = 4 },
        .{ .key = 6, .serial = 5 },
        .{ .key = 9, .serial = 6 },
    };
    var reseed_alias = [_]OrderedEntry{
        .{ .key = 6, .serial = 4 },
        .{ .key = 6, .serial = 5 },
        .{ .key = 9, .serial = 6 },
    };
    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, orderedLess);
        rbtree.add(&alias_entry.node, &alias_root, orderedLess);
    }

    const duplicate = @as(i32, 8);
    var primary_serials: [2]usize = undefined;
    var alias_serials: [2]usize = undefined;
    var primary_count = iteratorSerials(&duplicate, &primary_root, false, &primary_serials);
    var alias_count = iteratorSerials(&duplicate, &alias_root, true, &alias_serials);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(usize, primary_serials[0..primary_count], alias_serials[0..alias_count]);
    try std.testing.expectEqualSlices(usize, &.{ 0, 1 }, primary_serials[0..primary_count]);

    rbtree.eraseInit(&primary_entries[0].node, &primary_root);
    rbtree.eraseInit(&primary_entries[1].node, &primary_root);
    rbtree.eraseInit(&alias_entries[0].node, &alias_root);
    rbtree.eraseInit(&alias_entries[1].node, &alias_root);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findFirst(&duplicate, &primary_root, compareKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_first(&duplicate, &alias_root, compareKey));

    for (&reseed_primary, &reseed_alias) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, orderedLess);
        rbtree.add(&alias_entry.node, &alias_root, orderedLess);
    }

    const reseed_duplicate = @as(i32, 6);
    primary_count = iteratorSerials(&reseed_duplicate, &primary_root, false, &primary_serials);
    alias_count = iteratorSerials(&reseed_duplicate, &alias_root, true, &alias_serials);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqual(@as(usize, 2), primary_count);
    try std.testing.expectEqualSlices(usize, primary_serials[0..primary_count], alias_serials[0..alias_count]);
    try std.testing.expectEqualSlices(usize, &.{ 4, 5 }, primary_serials[0..primary_count]);

    const missing = @as(i32, 42);
    try std.testing.expectEqual(@as(usize, 0), iteratorSerials(&missing, &primary_root, false, &primary_serials));
    try std.testing.expectEqual(@as(usize, 0), iteratorSerials(&missing, &alias_root, true, &alias_serials));
}
