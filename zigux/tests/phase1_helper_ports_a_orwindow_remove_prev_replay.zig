const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "bitmap weighted OR and find_bit OR scans share the declared tail window" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 9;
    const tail_noise = @as(Word, 1) << 12;

    var lhs = [_]Word{ 0, tail_noise };
    var rhs = [_]Word{ 0, tail_noise };
    var out = [_]Word{ 0, 0 };

    lhs[0] = @as(Word, 1) << 2;
    rhs[1] |= @as(Word, 1) << 4;

    try std.testing.expectEqual(@as(usize, 2), bitmap.weightedOr(&out, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&out, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findNextOrBit(&lhs, &rhs, nbits, 0));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 4), find_bit.find_next_or_bit(&lhs, &rhs, nbits, 3));
    try std.testing.expectEqual(nbits, find_bit.find_next_or_bit(&lhs, &rhs, nbits, bitmap.bits_per_long + 5));
}

test "string remove and replace helpers stop at the C terminator" {
    var text = [_]u8{ ' ', 'a', ' ', 'b', ' ', ' ', 'c', 0, ' ', 'z' };

    const compact = string.removeSpaces(&text);
    try std.testing.expectEqualStrings("abc", compact);
    try std.testing.expectEqual(@as(u8, 0), text[3]);
    try std.testing.expectEqual(@as(u8, ' '), text[8]);

    const nul_idx = string.strreplace(&text, 'b', 'B');
    try std.testing.expectEqual(@as(usize, 3), nul_idx);
    try std.testing.expectEqualStrings("aBc", text[0..3]);
    try std.testing.expectEqual(@as(?usize, 1), string.memchrInv(text[0..3], 'a'));
}

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    return entryFromNode(lhs).key < entryFromNode(rhs).key;
}

test "rbtree cached erase keeps leftmost stable and prev walks remaining keys" {
    var entries = [_]Entry{
        .{ .key = 40 },
        .{ .key = 20 },
        .{ .key = 60 },
        .{ .key = 10 },
        .{ .key = 30 },
        .{ .key = 50 },
        .{ .key = 70 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(i32, 10), entryFromNode(rbtree.firstCached(&root).?).key);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.eraseCached(&entries[2].node, &root));
    try std.testing.expectEqual(@as(i32, 10), entryFromNode(rbtree.rb_first_cached(&root).?).key);

    var cursor = rbtree.last(&root.root).?;
    const expected = [_]i32{ 70, 50, 40, 30, 20, 10 };
    for (expected) |key| {
        try std.testing.expectEqual(key, entryFromNode(cursor).key);
        cursor = rbtree.prev(cursor) orelse break;
    }
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(&entries[3].node));
}
