const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap copy clear tail masks copied data before helpers inspect it" {
    const nbits = bits_per_long + 5;
    const in_range_tail = @as(Word, 1) << 2;
    const outside_tail = @as(Word, 1) << 9;
    const src = [_]Word{ @as(Word, 1) << (bits_per_long - 1), in_range_tail | outside_tail };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };

    bitmap.copyClearTail(&dst, &src, nbits);

    try std.testing.expectEqual(src[0], dst[0]);
    try std.testing.expectEqual(in_range_tail, dst[1]);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&dst, nbits));
    try std.testing.expect(bitmap.intersects(&dst, &[_]Word{ 0, in_range_tail }, nbits));
    try std.testing.expect(!bitmap.intersects(&dst, &[_]Word{ 0, outside_tail }, nbits));
}

test "find_bit last and zero scans clamp noisy tail words" {
    const nbits = bits_per_long + 5;
    var map = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 11) };

    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.find_last_bit(&map, nbits));

    map[1] &= ~(@as(Word, 1) << 4);
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findLastBit(&map, nbits));

    const full_declared = [_]Word{ ~@as(Word, 0), find_bit.lastWordMask(nbits) };
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&full_declared, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_zero_bit(&full_declared, nbits, bits_per_long));
}

test "string C-string helpers stop before later embedded data" {
    const with_nul = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    var copied = [_]u8{ 'x', 'x', 'x', 'x', 'x' };

    try std.testing.expectEqual(@as(usize, 2), string.strlcpy(&copied, &with_nul));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0, 'x', 'x' }, &copied);
    try std.testing.expect(string.streq(&with_nul, "ab"));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&with_nul, with_nul.len, 'd'));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&with_nul, with_nul.len, 'b'));
}

test "rbtree cached erase promotes the next node before replacement" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const @This() = @fieldParentPtr("node", lhs);
            const rhs_entry: *const @This() = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    };

    var entries = [_]Entry{
        .{ .key = 30 },
        .{ .key = 10 },
        .{ .key = 20 },
    };
    var replacement = Entry{ .key = 15 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.addCached(&entries[0].node, &root, Entry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_add_cached(&entries[1].node, &root, Entry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[2].node, &root, Entry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.rb_erase_cached(&entries[1].node, &root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.firstCached(&root));

    rbtree.rb_replace_node_cached(&entries[2].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_next(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_prev(&entries[0].node));
}
