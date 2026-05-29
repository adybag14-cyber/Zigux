const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

test "bitmap complement masks the tail word before weight and equality checks" {
    const nbits = bitmap.bits_per_long + 6;
    const source = [_]Word{
        ~@as(Word, 0),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 9),
    };
    var complemented = [_]Word{ 0, ~@as(Word, 0) };
    const expected_tail = bitmap.lastWordMask(nbits) & ~(@as(Word, 1) << 1);

    bitmap.bitmap_complement(&complemented, &source, nbits);

    try std.testing.expectEqual(@as(Word, 0), complemented[0]);
    try std.testing.expectEqual(expected_tail, complemented[1]);
    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(&complemented, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&complemented, &[_]Word{ 0, expected_tail }, nbits));
}

test "find-bit zero and last scans agree at a declared tail window" {
    const nbits = find_bit.bits_per_long + 6;
    const map = [_]Word{
        ~@as(Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(Word, 1) << 4),
    };
    const noisy_tail = [_]Word{
        0,
        (@as(Word, 1) << 4) | (@as(Word, 1) << 11),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findFirstZeroBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextZeroBit(&map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&map, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findLastBit(&noisy_tail, nbits));
}

test "string prefix helpers stop at C-string and prefix boundaries" {
    const text = [_]u8{ 'b', 'i', 't', 0, 't', 'a', 'i', 'l' };
    const exact_prefix = [_]u8{ 'b', 'i', 't', 0, 'x' };
    const long_prefix = [_]u8{ 'b', 'i', 't', 's', 0 };

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&text, &exact_prefix));
    try std.testing.expect(string.strstarts(&text, &exact_prefix));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(&text, &long_prefix));
    try std.testing.expectEqual(@as(usize, 0), string.str_has_prefix(&[_]u8{ 'b', 0, 'i', 't' }, "bi"));
}

test "rbtree cached replacement preserves leftmost and traversal aliases" {
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

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 3 },
        .{ .key = 13 },
        .{ .key = 5 },
    };
    var left_replacement = Entry{ .key = 3 };
    var middle_replacement = Entry{ .key = 8 };

    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&root));

    rbtree.rb_replace_node_cached(&entries[1].node, &left_replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_replacement.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.rb_next(&left_replacement.node));

    rbtree.replaceNodeCached(&entries[0].node, &middle_replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.prev(&middle_replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.next(&middle_replacement.node));
}
