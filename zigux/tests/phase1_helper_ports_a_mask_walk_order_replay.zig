const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

const Entry = struct {
    key: usize,
    label: []const u8,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const expected: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (expected.* < entry.key) return -1;
    if (expected.* > entry.key) return 1;
    return 0;
}

fn nodeKey(node: ?*const rbtree.Node) ?usize {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return entry.key;
}

fn addCached(entry: *Entry, root: *rbtree.RootCached) void {
    _ = rbtree.addCached(&entry.node, root, less);
}

test "lane06 mask walk order links bitmap cursors to string and rbtree traversal" {
    const nbits = find_bit.bits_per_long * 2 + 12;
    var mask = [_]Word{ 0, 0, 0 };

    bitmap.setRange(&mask, 3, 5);
    bitmap.setRange(&mask, find_bit.bits_per_long - 2, 5);
    bitmap.setRange(&mask, find_bit.bits_per_long + 9, 4);
    bitmap.setRange(&mask, find_bit.bits_per_long * 2 + 4, 3);
    bitmap.clearRange(&mask, find_bit.bits_per_long + 10, 1);

    try std.testing.expectEqual(@as(usize, 16), bitmap.weight(&mask, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstBit(&mask, nbits));
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextZeroBit(&mask, nbits, 3));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long - 2), find_bit.findNextBit(&mask, nbits, 8));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 10), find_bit.findNextZeroBit(&mask, nbits, find_bit.bits_per_long + 9));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long * 2 + 6), find_bit.findLastBit(&mask, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &mask, nbits));
    try std.testing.expectEqual(@as(u8, 0b1111_1000), clump);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 8), find_bit.findNextClump8(&clump, &mask, nbits, find_bit.bits_per_long + 8));
    try std.testing.expectEqual(@as(u8, 0b0001_1010), clump);

    var rendered = [_]u8{0} ** 96;
    const rendered_len = bitmap.scnprintf(&mask, nbits, &rendered);
    try std.testing.expectEqualStrings("3-7,62-66,73,75-76,132-134", rendered[0..rendered_len]);

    var padded = [_]u8{0xaa} ** 40;
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), string.strscpyPad(&padded, rendered[0..rendered_len]));
    try std.testing.expectEqual(@as(?usize, null), string.memchr_inv(padded[rendered_len + 1 ..], 0));

    var spaced = [_]u8{ ' ', '\t' } ++ "3-7,62-66,73,75-76,132-134\n".* ++ [_]u8{0} ** 4;
    const trimmed = string.strim(&spaced);
    try std.testing.expectEqualStrings("3-7,62-66,73,75-76,132-134", trimmed);

    const names = [_][]const u8{ "head", "3-7,62-66,73,75-76,132-134", "tail" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&names, "3-7,62-66,73,75-76,132-134\n"));
    try std.testing.expectEqual(@as(usize, 2), string.strHasPrefix(trimmed, "3-"));

    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(&mask, nbits), .label = "first" },
        .{ .key = find_bit.findNextBit(&mask, nbits, 8), .label = "second" },
        .{ .key = find_bit.findNextBit(&mask, nbits, find_bit.bits_per_long + 10), .label = "third" },
        .{ .key = find_bit.findLastBit(&mask, nbits), .label = "last" },
    };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        addCached(entry, &root);
    }

    try std.testing.expectEqual(@as(?usize, 3), nodeKey(rbtree.firstCached(&root)));
    try std.testing.expectEqual(@as(?usize, find_bit.bits_per_long * 2 + 6), nodeKey(rbtree.last(&root.root)));

    var replacement = Entry{ .key = entries[1].key, .label = "replacement" };
    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);

    var walk: [4]usize = undefined;
    var idx: usize = 0;
    var cursor = rbtree.first(&root.root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        walk[idx] = nodeKey(node).?;
        idx += 1;
    }
    try std.testing.expectEqualSlices(usize, &[_]usize{
        3,
        find_bit.bits_per_long - 2,
        find_bit.bits_per_long + 11,
        find_bit.bits_per_long * 2 + 6,
    }, walk[0..idx]);

    var key = replacement.key;
    var iter = rbtree.matchIterator(&key, &root.root, cmpKey);
    const matched = iter.next() orelse return error.TestExpectedEqual;
    const matched_entry: *const Entry = @fieldParentPtr("node", matched);
    try std.testing.expectEqualStrings("replacement", matched_entry.label);
    try std.testing.expect(iter.next() == null);

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?usize, find_bit.bits_per_long - 2), nodeKey(rbtree.firstCached(&root)));
}
