const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Entry = struct {
    key: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn entryFromMutableNode(node: *rbtree.Node) *Entry {
    return @fieldParentPtr("node", node);
}

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    return entryFromNode(lhs).key < entryFromNode(rhs).key;
}

fn expectTreeOrder(root: *const rbtree.RootCached, expected: []const usize) !void {
    var node = rbtree.firstCached(root);
    for (expected) |key| {
        const current = node orelse return error.MissingNode;
        try std.testing.expectEqual(key, entryFromNode(current).key);
        node = rbtree.next(current);
    }
    try std.testing.expect(node == null);
}

test "lane06 range rebuild cached replay" {
    const nbits = bitmap.bits_per_long + 24;
    const nwords = 2;

    var source = [_]bitmap.Word{0} ** nwords;
    var blocked = [_]bitmap.Word{0} ** nwords;
    var rebuilt = [_]bitmap.Word{0} ** nwords;

    bitmap.setRange(&source, 2, 6);
    bitmap.clearRange(&source, 5, 2);
    bitmap.setRange(&source, bitmap.bits_per_long - 1, 4);
    bitmap.setRange(&source, bitmap.bits_per_long + 12, 4);

    bitmap.setRange(&blocked, 3, 2);
    bitmap.setRange(&blocked, bitmap.bits_per_long, 2);
    bitmap.setRange(&blocked, bitmap.bits_per_long + 14, 1);

    try std.testing.expect(bitmap.andNotBits(&rebuilt, &source, &blocked, nbits));
    try std.testing.expectEqual(@as(usize, 7), bitmap.weight(&rebuilt, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstAndNotBit(&source, &blocked, nbits));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextAndNotBit(&source, &blocked, nbits, 3));
    try std.testing.expectEqual(bitmap.bits_per_long - 1, find_bit.findNextBit(&rebuilt, nbits, 8));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findNextZeroBit(&rebuilt, nbits, 2));
    try std.testing.expectEqual(bitmap.bits_per_long + 15, find_bit.findLastBit(&rebuilt, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&clump, &rebuilt, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0x84), clump);
    try std.testing.expectEqual(bitmap.bits_per_long - 8, find_bit.findNextClump8(&clump, &rebuilt, nbits, 8));
    try std.testing.expectEqual(@as(u8, 0x80), clump);
    try std.testing.expectEqual(bitmap.bits_per_long, find_bit.findNextClump8(&clump, &rebuilt, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x04), clump);

    var rendered = [_]u8{0} ** 64;
    const rendered_len = bitmap.scnprintf(&rebuilt, nbits, &rendered);
    const rendered_text = rendered[0..rendered_len];
    try std.testing.expectEqualStrings("2,7,63,66,76-77,79", rendered_text);

    var padded = [_]u8{0xaa} ** 64;
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), string.strscpyPad(&padded, rendered_text));
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&padded, "2,7"));
    try std.testing.expect(string.strEndsWith(&padded, "79"));
    try std.testing.expectEqual(rendered_len, string.strreplace(&padded, ',', '|'));
    try std.testing.expect(string.strstarts(&padded, "2|7"));
    try std.testing.expect(string.strEndsWith(&padded, "79"));

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = bitmap.bits_per_long + 15 },
        .{ .key = 2 },
        .{ .key = bitmap.bits_per_long - 1 },
        .{ .key = 7 },
        .{ .key = bitmap.bits_per_long + 12 },
        .{ .key = bitmap.bits_per_long + 13 },
        .{ .key = bitmap.bits_per_long + 2 },
    };

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }
    try expectTreeOrder(&root, &[_]usize{ 2, 7, bitmap.bits_per_long - 1, bitmap.bits_per_long + 2, bitmap.bits_per_long + 12, bitmap.bits_per_long + 13, bitmap.bits_per_long + 15 });

    const leftmost = rbtree.firstCached(&root).?;
    rbtree.eraseInitCached(leftmost, &root);
    try std.testing.expect(rbtree.emptyNode(leftmost));
    try expectTreeOrder(&root, &[_]usize{ 7, bitmap.bits_per_long - 1, bitmap.bits_per_long + 2, bitmap.bits_per_long + 12, bitmap.bits_per_long + 13, bitmap.bits_per_long + 15 });

    const removed_node = &entries[6].node;
    rbtree.eraseInitCached(removed_node, &root);
    try std.testing.expect(rbtree.emptyNode(removed_node));

    var reseeded = Entry{ .key = bitmap.bits_per_long + 1 };
    _ = rbtree.addCached(&reseeded.node, &root, less);
    try expectTreeOrder(&root, &[_]usize{ 7, bitmap.bits_per_long - 1, bitmap.bits_per_long + 1, bitmap.bits_per_long + 12, bitmap.bits_per_long + 13, bitmap.bits_per_long + 15 });
    try std.testing.expectEqual(@as(usize, 7), entryFromMutableNode(rbtree.firstCached(&root).?).key);
}
