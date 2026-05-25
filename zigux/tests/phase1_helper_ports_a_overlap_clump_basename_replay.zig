const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap overlap helpers keep tail-masked subset results aligned" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{
        (@as(Word, 1) << 3) | (@as(Word, 1) << @intCast(bits_per_long - 1)),
        (@as(Word, 1) << 0) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9),
    };
    const rhs = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << @intCast(bits_per_long - 1)),
        (@as(Word, 1) << 4) | (@as(Word, 1) << 8),
    };
    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    try std.testing.expect(bitmap.andBits(&direct, &lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_and(&alias, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    try std.testing.expect(bitmap.intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.subset(&direct, &lhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&alias, &lhs, nbits));
    try std.testing.expect(!bitmap.subset(&lhs, &direct, nbits));
    try std.testing.expect(bitmap.equal(&direct, &alias, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&direct, &alias, nbits));
}

test "find_bit clump helpers keep tail-aligned byte views aligned" {
    const nbits = bits_per_long + 11;
    const words = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 0) |
            (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 5) |
            (@as(find_bit.Word, 1) << 10),
    };
    var direct_clump: u8 = 0;
    var alias_clump: u8 = 0;

    try std.testing.expectEqual(bits_per_long, find_bit.findFirstClump8(&direct_clump, &words, nbits));
    try std.testing.expectEqual(bits_per_long, find_bit.find_first_clump8(&alias_clump, &words, nbits));
    try std.testing.expectEqual(@as(u8, 0x23), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);
    try std.testing.expectEqual(@as(u8, 0x23), find_bit.getValue8(&words, bits_per_long));

    try std.testing.expectEqual(bits_per_long + 8, find_bit.findNextClump8(&direct_clump, &words, nbits, bits_per_long + 1));
    try std.testing.expectEqual(bits_per_long + 8, find_bit.find_next_clump8(&alias_clump, &words, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(u8, 0x04), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);

    try std.testing.expectEqual(bits_per_long + 10, find_bit.findLastBit(&words, nbits));
    try std.testing.expectEqual(bits_per_long + 10, find_bit.find_last_bit(&words, nbits));
}

test "string basename and inverse-byte helpers stop at visible boundaries" {
    const path = "/tmp/zigux/demo.txt\x00shadow";
    try std.testing.expectEqualStrings("demo.txt", string.kbasename(path));

    const padded = [_]u8{ 0, 0, 0, 'x', 0 };
    try std.testing.expectEqual(@as(?usize, 3), string.memchrInv(&padded, 0));
    try std.testing.expectEqual(@as(?usize, 3), string.memchr_inv(&padded, 0));

    const clean = [_]u8{ 'a', 'a', 'a', 'a' };
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(&clean, 'a'));

    const noisy = [_]u8{ 'a', 'a', 'b', 'a' };
    try std.testing.expectEqual(@as(?usize, 2), string.memchr_inv(&noisy, 'a'));
}

test "rbtree cached replacement and postorder traversal keep leftmost state aligned" {
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
    var left = Entry{ .key = 5 };
    var mid = Entry{ .key = 10 };
    var right = Entry{ .key = 20 };
    var right_left = Entry{ .key = 15 };

    _ = rbtree.addCached(&mid.node, &root, less);
    _ = rbtree.rb_add_cached(&left.node, &root, less);
    _ = rbtree.addCached(&right.node, &root, less);
    _ = rbtree.rb_add_cached(&right_left.node, &root, less);

    try std.testing.expectEqual(@as(?*rbtree.Node, &left.node), rbtree.firstCached(&root));

    var replacement = Entry{ .key = 5 };
    rbtree.replaceNodeCached(&left.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_first_cached(&root));

    var postorder: [4]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.firstPostorder(&root.root);
    while (current) |node| : (current = rbtree.rb_next_postorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        postorder[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 15, 20, 10 }, postorder[0..count]);

    rbtree.rb_erase_init_cached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &mid.node), rbtree.firstCached(&root));
}
