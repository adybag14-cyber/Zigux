const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

test "bitmap copy-clear-tail keeps equality and weight scoped to declared bits" {
    const nbits = bitmap.bits_per_long + 5;
    const source = [_]Word{
        (@as(Word, 1) << 2) | (@as(Word, 1) << (bitmap.bits_per_long - 1)),
        (@as(Word, 1) << 3) | (@as(Word, 1) << 9),
    };
    var copied = [_]Word{ 0, 0 };
    var expected = [_]Word{ source[0], @as(Word, 1) << 3 };

    bitmap.bitmap_copy_clear_tail(&copied, &source, nbits);
    try std.testing.expectEqualSlices(Word, &expected, &copied);
    try std.testing.expect(bitmap.bitmap_equal(&copied, &source, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&copied, nbits));

    bitmap.bitmap_clear(&copied, bitmap.bits_per_long + 3, 1);
    expected[1] = 0;
    try std.testing.expectEqualSlices(Word, &expected, &copied);
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&copied, nbits));
}

test "find_last_bit ignores out-of-window tail bits after bitmap tail clearing" {
    const nbits = find_bit.bits_per_long + 5;
    const in_range_offset = 4;
    const out_of_range_offset = 11;

    var map = [_]Word{ 0, (@as(Word, 1) << in_range_offset) | (@as(Word, 1) << out_of_range_offset) };
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + in_range_offset), find_bit.findLastBit(&map, nbits));

    map[1] = @as(Word, 1) << out_of_range_offset;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findLastBit(&map, nbits));
}

test "strnchr clamps counted scans at the first C terminator" {
    const text = [_]u8{ 'p', 'o', 'r', 't', 0, 'r', 'b', 't' };

    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&text, text.len, 'r'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&text, text.len, 'b'));
    try std.testing.expectEqual(@as(?usize, 4), string.strnchr(&text, text.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&text, 4, 0));
}

test "rbtree duplicate-key match iterator preserves leftmost cached insertion evidence" {
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

    const cmp_key = struct {
        fn compare(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
            const key: *const i32 = @ptrCast(@alignCast(key_ptr));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (key.* < entry.key) return -1;
            if (key.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = 7 },
        .{ .key = 3 },
        .{ .key = 7 },
        .{ .key = 9 },
        .{ .key = 7 },
    };

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.addCached(&entries[0].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.addCached(&entries[1].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[2].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[3].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[4].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    const duplicate_key: i32 = 7;
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, cmp_key);
    var seen: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        try std.testing.expectEqual(@as(i32, 7), entry.key);
        seen += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), seen);

    rbtree.clearNode(&entries[4].node);
    try std.testing.expect(rbtree.emptyNode(&entries[4].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.next(&entries[4].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(&entries[4].node));
}
