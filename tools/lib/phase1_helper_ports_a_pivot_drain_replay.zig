const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: usize,
    ordinal: usize,
    node: rbtree.Node = .{},
};

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry = entryFromNode(lhs);
    const rhs_entry = entryFromNode(rhs);
    return if (lhs_entry.key == rhs_entry.key)
        lhs_entry.ordinal < rhs_entry.ordinal
    else
        lhs_entry.key < rhs_entry.key;
}

fn cmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry = entryFromNode(lhs);
    const rhs_entry = entryFromNode(rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    if (lhs_entry.ordinal < rhs_entry.ordinal) return -1;
    if (lhs_entry.ordinal > rhs_entry.ordinal) return 1;
    return 0;
}

fn keyOf(node: ?*const rbtree.Node) ?usize {
    const found = node orelse return null;
    return entryFromNode(found).key;
}

fn expectForward(root: *const rbtree.Root, expected: []const usize) !void {
    var idx: usize = 0;
    var cursor = rbtree.rb_first(root);
    while (cursor) |node| : (cursor = rbtree.rb_next(node)) {
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], entryFromNode(node).key);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);
}

fn expectReverse(root: *const rbtree.Root, expected: []const usize) !void {
    var idx: usize = 0;
    var cursor = rbtree.rb_last(root);
    while (cursor) |node| : (cursor = rbtree.rb_prev(node)) {
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], entryFromNode(node).key);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);
}

test "bitmap and OR cursor keys drain through cached rbtree pivots" {
    const nbits = bits_per_long + 24;
    var base = [_]Word{ 0, 0 };
    var pivot = [_]Word{ 0, 0 };
    var merged = [_]Word{ 0, 0 };
    var sparse = [_]Word{ 0, 0 };
    var shared = [_]Word{ 0, 0 };
    var drained = [_]Word{ 0, 0 };

    bitmap.bitmap_set(&base, 2, 3);
    bitmap.bitmap_set(&base, 11, 1);
    bitmap.bitmap_set(&base, bits_per_long + 3, 2);
    bitmap.bitmap_set(&pivot, 4, 1);
    bitmap.bitmap_set(&pivot, bits_per_long + 4, 3);
    bitmap.orBits(&merged, &base, &pivot, nbits);

    try std.testing.expectEqual(@as(usize, 8), bitmap.bitmap_weighted_or(&sparse, &base, &pivot, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&merged, &sparse, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&base, &merged, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&pivot, &merged, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&base, &pivot, nbits));
    try std.testing.expect(bitmap.andBits(&shared, &base, &pivot, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&shared, nbits));
    try std.testing.expect(bitmap.andNotBits(&drained, &merged, &base, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&drained, nbits));

    var complement = [_]Word{ 0, 0 };
    bitmap.bitmap_complement(&complement, &merged, nbits);
    try std.testing.expectEqual(@as(usize, 2), find_bit.findNextZeroBit(&complement, nbits, 0));
    try std.testing.expectEqual(@as(usize, bits_per_long + 6), find_bit.findLastBit(&merged, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&clump, &merged, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0b0001_1100), clump);
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextClump8(&clump, &merged, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0111_1000), clump);

    var rendered: [96]u8 = undefined;
    const rendered_len = bitmap.bitmap_scnprintf(&merged, nbits, &rendered);
    var token: [128]u8 = undefined;
    @memset(&token, 0);
    @memcpy(token[0.."  lane06:".len], "  lane06:");
    @memcpy(token["  lane06:".len .. "  lane06:".len + rendered_len], rendered[0..rendered_len]);
    @memcpy(token["  lane06:".len + rendered_len .. "  lane06:".len + rendered_len + 3], "  \n");

    const trimmed = string.strim(&token);
    try std.testing.expectEqual(@as(usize, "lane06:".len), string.strHasPrefix(trimmed, "lane06:"));
    try std.testing.expect(string.strEndsWith(trimmed, "67-70"));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv("llll", 'l'));
    try std.testing.expectEqual(@as(?usize, 0), string.memchrInv(trimmed[0.."lane06".len], 'a'));
    try std.testing.expect(string.sysfsStreq("lane06:pivot\n", "lane06:pivot"));

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(&merged, nbits), .ordinal = 0 },
        .{ .key = find_bit.findNextBit(&merged, nbits, 4), .ordinal = 1 },
        .{ .key = find_bit.findNextBit(&merged, nbits, 5), .ordinal = 2 },
        .{ .key = find_bit.findNextBit(&merged, nbits, bits_per_long), .ordinal = 3 },
        .{ .key = find_bit.findNextBit(&merged, nbits, bits_per_long + 5), .ordinal = 4 },
    };
    for (&entries) |*entry| {
        try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&entry.node, &root, cmp));
    }

    try std.testing.expectEqual(@as(?usize, 2), keyOf(rbtree.rb_first_cached(&root)));
    try expectForward(&root.root, &.{ 2, 4, 11, bits_per_long + 3, bits_per_long + 5 });
    try expectReverse(&root.root, &.{ bits_per_long + 5, bits_per_long + 3, 11, 4, 2 });

    try std.testing.expectEqual(@as(?usize, 4), keyOf(rbtree.rb_erase_cached(&entries[0].node, &root)));
    try std.testing.expectEqual(@as(?usize, 4), keyOf(rbtree.rb_first_cached(&root)));

    var replacement = Entry{ .key = bits_per_long + 6, .ordinal = 9 };
    rbtree.rb_replace_node_cached(&entries[4].node, &replacement.node, &root);
    try expectForward(&root.root, &.{ 4, 11, bits_per_long + 3, bits_per_long + 6 });

    rbtree.rb_erase_init_cached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try expectForward(&root.root, &.{ 11, bits_per_long + 3, bits_per_long + 6 });
}
