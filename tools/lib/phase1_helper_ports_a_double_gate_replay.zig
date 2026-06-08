const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = find_bit.Word;

const Entry = struct {
    key: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn keyOf(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn expectTreeOrder(root: *const rbtree.RootCached, expected: []const usize) !void {
    var cursor = rbtree.first(&root.root);
    var index: usize = 0;
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        try std.testing.expect(index < expected.len);
        try std.testing.expectEqual(expected[index], keyOf(node));
        index += 1;
    }
    try std.testing.expectEqual(expected.len, index);

    if (expected.len == 0) {
        try std.testing.expect(rbtree.firstCached(root) == null);
    } else {
        try std.testing.expectEqual(expected[0], keyOf(rbtree.firstCached(root).?));
        try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(root));
    }
}

test "phase1 helper ports A double-gate replay" {
    const nbits = find_bit.bits_per_long + 10;
    const words = find_bit.bitsToWords(nbits);

    var old_map = [_]Word{0} ** 3;
    var new_map = [_]Word{0} ** 3;
    var gate = [_]Word{0} ** 3;
    var merged = [_]Word{0} ** 3;
    var cursor_gate = [_]Word{0} ** 3;

    bitmap.bitmap_set(old_map[0..words], 2, 1);
    bitmap.bitmap_set(old_map[0..words], 5, 1);
    bitmap.bitmap_set(old_map[0..words], find_bit.bits_per_long + 1, 1);
    bitmap.bitmap_set(old_map[0..words], find_bit.bits_per_long + 8, 1);

    bitmap.bitmap_set(new_map[0..words], 3, 1);
    bitmap.bitmap_set(new_map[0..words], 5, 1);
    bitmap.bitmap_set(new_map[0..words], find_bit.bits_per_long + 4, 1);
    bitmap.bitmap_set(new_map[0..words], find_bit.bits_per_long + 9, 1);

    bitmap.bitmap_set(gate[0..words], find_bit.bits_per_long + 4, 1);
    bitmap.bitmap_set(gate[0..words], find_bit.bits_per_long + 8, 1);

    bitmap.bitmap_replace(merged[0..words], old_map[0..words], new_map[0..words], gate[0..words], nbits);

    try std.testing.expectEqual(@as(usize, 4), bitmap.bitmap_weight(merged[0..words], nbits));
    try std.testing.expect(bitmap.bitmap_subset(merged[0..words], old_map[0..words], nbits) == false);
    try std.testing.expect(bitmap.bitmap_intersects(merged[0..words], new_map[0..words], nbits));

    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(merged[0..words], nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findFirstAndBit(old_map[0..words], new_map[0..words], nbits));
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextAndNotBit(merged[0..words], old_map[0..words], nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.findNextBit(merged[0..words], nbits, find_bit.bits_per_long),
    );

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, merged[0..words], nbits));
    try std.testing.expectEqual(@as(u8, 0b0010_0100), clump);
    clump = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findNextClump8(&clump, merged[0..words], nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);

    _ = bitmap.bitmap_andnot(cursor_gate[0..words], merged[0..words], old_map[0..words], nbits);
    try std.testing.expectEqual(@as(usize, 1), bitmap.bitmap_weight(cursor_gate[0..words], nbits));
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findFirstBit(cursor_gate[0..words], nbits),
    );

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.bitmap_scnprintf(merged[0..words], nbits, &rendered);
    var expected_rendered: [64]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected_rendered,
        "2,5,{d},{d}",
        .{ find_bit.bits_per_long + 1, find_bit.bits_per_long + 4 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);

    var label = [_]u8{ ' ', 'l', 'a', 'n', 'e', '6', '-', 'd', 'o', 'u', 'b', 'l', 'e', 0, 'x' };
    const trimmed = string.strim(label[0..]);
    try std.testing.expectEqualStrings("lane6-double", trimmed);
    try std.testing.expect(string.strstarts(trimmed, "lane6"));
    try std.testing.expect(string.strEndsWith(trimmed, "double"));
    try std.testing.expectEqual(@as(usize, 12), string.strreplace(trimmed, '-', '_'));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&[_][]const u8{ "single", "lane6_double", "other" }, trimmed));
    try std.testing.expect(string.sysfs_streq("lane6_double\n", trimmed));

    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(merged[0..words], nbits) },
        .{ .key = find_bit.findNextBit(merged[0..words], nbits, 3) },
        .{ .key = find_bit.findNextBit(merged[0..words], nbits, find_bit.bits_per_long) },
        .{ .key = find_bit.findNextAndNotBit(merged[0..words], old_map[0..words], nbits, find_bit.bits_per_long) },
    };

    var tree = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &tree, less);
    }
    try expectTreeOrder(&tree, &[_]usize{ 2, 5, find_bit.bits_per_long + 1, find_bit.bits_per_long + 4 });

    rbtree.eraseInitCached(&entries[0].node, &tree);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try expectTreeOrder(&tree, &[_]usize{ 5, find_bit.bits_per_long + 1, find_bit.bits_per_long + 4 });

    rbtree.eraseInitCached(&entries[2].node, &tree);
    try std.testing.expect(rbtree.emptyNode(&entries[2].node));
    try expectTreeOrder(&tree, &[_]usize{ 5, find_bit.bits_per_long + 4 });

    _ = rbtree.addCached(&entries[0].node, &tree, less);
    try expectTreeOrder(&tree, &[_]usize{ 2, 5, find_bit.bits_per_long + 4 });
}
