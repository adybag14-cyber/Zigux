const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

test "bitmap weighted aliases feed find-bit tail boundary scans" {
    const nbits = bits_per_long + 6;
    const tail_noise = (@as(Word, 1) << 9) | (@as(Word, 1) << 12);
    const lhs = [_]Word{
        @as(Word, 1) << @intCast(bits_per_long - 1),
        (@as(Word, 1) << 2) | tail_noise,
    };
    const rhs = [_]Word{
        @as(Word, 1) << 5,
        (@as(Word, 1) << 5) | tail_noise,
    };
    var dst = [_]Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 4), bitmap.bitmap_weighted_or(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.find_first_bit(&dst, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long - 1), find_bit.find_next_bit(&dst, nbits, bits_per_long - 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 5), find_bit.find_next_bit(&dst, nbits, bits_per_long + 3));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_bit(&dst, nbits, bits_per_long + 6));
}

test "find-bit aliases preserve exhausted clump bytes at boundary offsets" {
    const nbits = bits_per_long + 5;
    const map = [_]Word{ 0, @as(Word, 1) << 3 };
    var clump: u8 = 0;

    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.find_first_clump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0xa5;
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&clump, &map, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0xa5), clump);
}

test "string bounded-NUL aliases keep count windows explicit" {
    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'd' };

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&cstr, 5, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, 5, 'd'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&cstr, 5, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, 5, 'z'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 3, 'z'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 3, 0));
}

test "rbtree cached erase-init aliases clear and reseed leftmost state" {
    var first = Entry{ .key = 9 };
    var left = Entry{ .key = 3 };
    var right = Entry{ .key = 12 };
    var reseed = Entry{ .key = 1 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &first.node), rbtree.rb_add_cached(&first.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &left.node), rbtree.rb_add_cached(&left.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&right.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &left.node), rbtree.rb_first_cached(&root));

    rbtree.rb_erase_init_cached(&left.node, &root);
    try std.testing.expect(rbtree.emptyNode(&left.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &first.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(rbtree.rb_first(&root.root), rbtree.rb_first_cached(&root));

    rbtree.rb_erase_init_cached(&first.node, &root);
    try std.testing.expect(rbtree.emptyNode(&first.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &right.node), rbtree.rb_first_cached(&root));

    rbtree.rb_erase_init_cached(&right.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_first_cached(&root));
    try std.testing.expect(rbtree.emptyRoot(&root.root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed.node), rbtree.rb_add_cached(&reseed.node, &root, less));
    try std.testing.expectEqual(rbtree.rb_first(&root.root), rbtree.rb_first_cached(&root));
}
