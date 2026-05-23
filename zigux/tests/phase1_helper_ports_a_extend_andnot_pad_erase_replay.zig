const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap extend and tail-clear aliases keep masked growth aligned" {
    const count = bitmap.bits_per_long + 3;
    const size = bitmap.bits_per_long * 2 + 5;

    const src = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << (bitmap.bits_per_long - 1)),
        ~@as(bitmap.Word, 0),
    };

    var direct_extend = [_]bitmap.Word{ 0xffff, 0xffff, 0xffff };
    var alias_extend = [_]bitmap.Word{ 0xffff, 0xffff, 0xffff };
    bitmap.copyAndExtend(&direct_extend, &src, count, size);
    bitmap.bitmap_copy_and_extend(&alias_extend, &src, count, size);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_extend, &alias_extend);
    try std.testing.expectEqual(src[0], direct_extend[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(count), direct_extend[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct_extend[2]);

    var direct_tail = [_]bitmap.Word{ 0, 0 };
    var alias_tail = [_]bitmap.Word{ 0, 0 };
    bitmap.copyClearTail(&direct_tail, &src, count);
    bitmap.bitmap_copy_clear_tail(&alias_tail, &src, count);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_tail, &alias_tail);
    try std.testing.expectEqual(src[0], direct_tail[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(count), direct_tail[1]);
}

test "phase1 helper ports A find_bit and-not aliases keep cross-word tail searches aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const boundary = find_bit.bits_per_long;
    const lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 4),
    };
    const rhs = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << 3,
    };

    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.find_first_andnot_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit._find_first_andnot_bit(&lhs, &rhs, nbits));

    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, boundary + 2));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, boundary + 2));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit._find_next_andnot_bit(&lhs, &rhs, nbits, boundary + 2));

    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, boundary + 5));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, nbits + 3));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_andnot_bit(&lhs, &rhs, nbits, nbits + 7));
}

test "phase1 helper ports A string pad and space-removal helpers keep C-string boundaries aligned" {
    var direct_spaces = [_]u8{ ' ', 'A', ' ', 'B', ' ', 0, 'X' };
    var alias_spaces = [_]u8{ ' ', 'A', ' ', 'B', ' ', 0, 'X' };
    try std.testing.expectEqualStrings("AB", string.removeSpaces(direct_spaces[0..]));
    try std.testing.expectEqualStrings("AB", string.remove_spaces(alias_spaces[0..]));
    try std.testing.expectEqualSlices(u8, direct_spaces[0..], alias_spaces[0..]);

    var direct_pad = [_]u8{ '?', '?', '?', '?', '?' };
    var alias_pad = [_]u8{ '?', '?', '?', '?', '?' };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(direct_pad[0..], "xy"));
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(alias_pad[0..], "xy"));
    try std.testing.expectEqualSlices(u8, direct_pad[0..], alias_pad[0..]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', 0, 0, 0 }, direct_pad[0..]);

    try std.testing.expectEqualStrings("lead", string.skipSpaces(" \tlead"));
    try std.testing.expectEqualStrings("lead", string.skip_spaces(" \tlead"));
}

test "phase1 helper ports A rbtree cached erase aliases keep leftmost and traversal aligned" {
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

    const nodeKey = struct {
        fn read(node: ?*rbtree.Node) ?i32 {
            const current = node orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", current);
            return entry.key;
        }
    }.read;

    var primary_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 12 },
        .{ .key = 18 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 12 },
        .{ .key = 18 },
    };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary, *alias| {
        _ = rbtree.addCached(&primary.node, &primary_root, less);
        _ = rbtree.rb_add_cached(&alias.node, &alias_root, less);
    }

    try std.testing.expectEqual(nodeKey(rbtree.firstCached(&primary_root)), nodeKey(rbtree.rb_first_cached(&alias_root)));
    try std.testing.expectEqual(@as(?i32, 5), nodeKey(rbtree.firstCached(&primary_root)));

    const primary_next_leftmost = rbtree.eraseCached(&primary_entries[1].node, &primary_root);
    const alias_next_leftmost = rbtree.rb_erase_cached(&alias_entries[1].node, &alias_root);
    try std.testing.expectEqual(nodeKey(primary_next_leftmost), nodeKey(alias_next_leftmost));
    try std.testing.expectEqual(@as(?i32, 10), nodeKey(primary_next_leftmost));
    try std.testing.expectEqual(nodeKey(rbtree.firstCached(&primary_root)), nodeKey(rbtree.rb_first_cached(&alias_root)));

    rbtree.eraseInitCached(&primary_entries[2].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[2].node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_entries[2].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[2].node));

    var forward_primary: [3]i32 = undefined;
    var forward_alias: [3]i32 = undefined;
    var forward_count: usize = 0;
    var primary_cursor = rbtree.first(&primary_root.root);
    var alias_cursor = rbtree.rb_first(&alias_root.root);
    while (primary_cursor != null and alias_cursor != null) {
        forward_primary[forward_count] = nodeKey(primary_cursor).?;
        forward_alias[forward_count] = nodeKey(alias_cursor).?;
        forward_count += 1;
        primary_cursor = rbtree.next(primary_cursor.?);
        alias_cursor = rbtree.rb_next(alias_cursor.?);
    }
    try std.testing.expect(primary_cursor == null);
    try std.testing.expect(alias_cursor == null);
    try std.testing.expectEqual(@as(usize, 3), forward_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 10, 12, 18 }, forward_primary[0..forward_count]);
    try std.testing.expectEqualSlices(i32, forward_primary[0..forward_count], forward_alias[0..forward_count]);

    try std.testing.expectEqual(
        nodeKey(rbtree.prev(rbtree.last(&primary_root.root).?)),
        nodeKey(rbtree.rb_prev(rbtree.rb_last(&alias_root.root).?)),
    );
    try std.testing.expectEqual(@as(?i32, 12), nodeKey(rbtree.prev(rbtree.last(&primary_root.root).?)));
}
