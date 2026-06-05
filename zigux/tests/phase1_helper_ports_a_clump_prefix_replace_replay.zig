const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "helper ports A clump traversal feeds bitmap complement tail accounting" {
    const nbits = bits_per_long + 11;
    var map = [_]Word{ 0, 0 };
    bitmap.zero(&map, nbits);
    bitmap.setRange(&map, bits_per_long + 2, 1);
    bitmap.setRange(&map, bits_per_long + 9, 1);

    var clump: u8 = 0xaa;
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findFirstClump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_0100), clump);

    clump = 0xaa;
    try std.testing.expectEqual(@as(usize, bits_per_long + 8), find_bit.findNextClump8(&clump, &map, nbits, bits_per_long + 3));
    try std.testing.expectEqual(@as(u8, 0b0000_0010), clump);

    var complement = [_]Word{ 0, 0 };
    bitmap.complement(&complement, &map, nbits);
    try std.testing.expectEqual(nbits - 2, bitmap.weight(&complement, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findFirstZeroBit(&complement, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 9), find_bit.findNextZeroBit(&complement, nbits, bits_per_long + 3));
    try std.testing.expectEqual(@as(usize, nbits - 1), find_bit.findLastBit(&complement, nbits));
}

test "helper ports A string prefix and suffix aliases honor embedded C boundaries" {
    const cstr = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', '-', 'v', '1', 0, 'x' };
    try std.testing.expectEqual(@as(usize, 6), string.strHasPrefix(&cstr, "prefix"));
    try std.testing.expectEqual(@as(usize, 6), string.str_has_prefix(&cstr, "prefix"));
    try std.testing.expect(string.strstarts(&cstr, "prefix"));
    try std.testing.expect(!string.strstarts(&cstr, "v1"));

    try std.testing.expect(string.strEndsWith(&cstr, "v1"));
    try std.testing.expect(string.str_ends_with(&cstr, "v1"));
    try std.testing.expect(!string.strEndsWith(&cstr, "x"));

    var rewrite = [_]u8{ ' ', 'p', 'r', 'e', 'f', 'i', 'x', '-', 'v', '1', ' ', 0, 'x' };
    const trimmed = string.strstrip(&rewrite);
    try std.testing.expectEqualStrings("prefix-v1", trimmed);
    try std.testing.expectEqual(@as(?usize, 6), string.strnchr(trimmed, trimmed.len, '-'));
}

const TreeEntry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn lessByKey(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const TreeEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const TreeEntry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

test "helper ports A rbtree cached replacement keeps leftmost and traversal stable" {
    var root = rbtree.RootCached.init();
    var low = TreeEntry{ .key = 10 };
    var mid = TreeEntry{ .key = 20 };
    var high = TreeEntry{ .key = 30 };
    var replacement = TreeEntry{ .key = 5 };

    try std.testing.expectEqual(&mid.node, rbtree.addCached(&mid.node, &root, lessByKey).?);
    try std.testing.expectEqual(&low.node, rbtree.addCached(&low.node, &root, lessByKey).?);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&high.node, &root, lessByKey));
    try std.testing.expectEqual(&low.node, rbtree.firstCached(&root).?);

    rbtree.replaceNodeCached(&low.node, &replacement.node, &root);
    try std.testing.expectEqual(&replacement.node, rbtree.firstCached(&root).?);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(&replacement.node));
    try std.testing.expectEqual(&mid.node, rbtree.next(&replacement.node).?);
    try std.testing.expectEqual(&high.node, rbtree.next(&mid.node).?);
    try std.testing.expectEqual(&high.node, rbtree.last(&root.root).?);

    var seen = [_]i32{ 0, 0, 0 };
    var idx: usize = 0;
    var cursor = rbtree.first(&root.root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const TreeEntry = @fieldParentPtr("node", node);
        seen[idx] = entry.key;
        idx += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), idx);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 20, 30 }, &seen);
}
