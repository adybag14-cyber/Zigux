const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

test "bitmap complement span feeds find-bit first and last scans" {
    const nbits = bits_per_long + 7;
    const tail_noise = (@as(Word, 1) << 9) | (@as(Word, 1) << 13);
    const source = [_]Word{
        ~(@as(Word, 1) << 4),
        bitmap.lastWordMask(nbits) & ~(@as(Word, 1) << 5) | tail_noise,
    };
    var complement = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    bitmap.complement(&complement, &source, nbits);
    bitmap.bitmap_complement(&alias, &source, nbits);

    try std.testing.expectEqualSlices(Word, &complement, &alias);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&complement, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findFirstBit(&complement, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 5), find_bit.findLastBit(&complement, nbits));
}

test "bitmap weighted xor preserves the declared find-bit window" {
    const nbits = bits_per_long + 6;
    const lhs = [_]Word{
        (@as(Word, 1) << 3) | (@as(Word, 1) << 8),
        (@as(Word, 1) << 2) | (@as(Word, 1) << 9),
    };
    const rhs = [_]Word{
        (@as(Word, 1) << 8),
        (@as(Word, 1) << 5) | (@as(Word, 1) << 12),
    };
    var dst = [_]Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weighted_xor(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstBit(&dst, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findNextBit(&dst, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 5), find_bit.findNextBit(&dst, nbits, bits_per_long + 3));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&dst, nbits, bits_per_long + 6));
}

test "string suffix helpers and bounded searches stop at C-string limits" {
    const cstr = [_]u8{ 'd', 'r', 'i', 'v', 'e', 'r', 0, 'x' };

    try std.testing.expect(string.strEndsWith(&cstr, "ver"));
    try std.testing.expect(string.str_ends_with(&cstr, "driver"));
    try std.testing.expect(!string.str_ends_with(&cstr, "erx"));
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr(&cstr, cstr.len, 'v'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, cstr.len, 'x'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("driver", 3, 'v'));
}

test "rbtree cached cursor survives erase and replacement aliases" {
    var root = rbtree.RootCached.init();
    var left = Entry{ .key = 3, .serial = 0 };
    var middle = Entry{ .key = 7, .serial = 1 };
    var right = Entry{ .key = 11, .serial = 2 };
    var replacement = Entry{ .key = 7, .serial = 3 };

    try std.testing.expectEqual(@as(?*rbtree.Node, &middle.node), rbtree.rb_add_cached(&middle.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &left.node), rbtree.rb_add_cached(&left.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&right.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &left.node), rbtree.rb_first_cached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_erase_cached(&right.node, &root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &left.node), rbtree.rb_first_cached(&root));
    try std.testing.expect(rbtree.rb_next(&left.node) == &middle.node);

    rbtree.rb_replace_node_cached(&middle.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &left.node), rbtree.rb_first_cached(&root));
    try std.testing.expect(rbtree.rb_next(&left.node) == &replacement.node);

    rbtree.rb_erase_init_cached(&left.node, &root);
    try std.testing.expect(rbtree.emptyNode(&left.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_first_cached(&root));
}
