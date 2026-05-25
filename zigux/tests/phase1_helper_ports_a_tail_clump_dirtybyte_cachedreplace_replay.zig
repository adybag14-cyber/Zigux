const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap aliases clamp weighted-or and complement tails" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 8) };
    const rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) };
    var direct_or = [_]bitmap.Word{ 0, 0 };
    var alias_or = [_]bitmap.Word{ 0, 0 };

    const direct_weight = bitmap.weightedOr(&direct_or, &lhs, &rhs, nbits);
    const alias_weight = bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_weight);
    try std.testing.expectEqual(direct_weight, alias_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_or, &alias_or);
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8) | (@as(bitmap.Word, 1) << 9)), direct_or[1]);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_or, nbits));

    const src = [_]bitmap.Word{
        0b1010,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 7) | (@as(bitmap.Word, 1) << 10),
    };
    var direct_complement = [_]bitmap.Word{ 0, 0 };
    var alias_complement = [_]bitmap.Word{ 0, 0 };
    bitmap.complement(&direct_complement, &src, nbits);
    bitmap.bitmap_complement(&alias_complement, &src, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_complement, &alias_complement);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), direct_complement[1]);
}

test "phase1 helper ports A find_bit clump aliases keep aligned bytes isolated" {
    const last_aligned_byte = find_bit.bits_per_long - 8;
    const nbits = find_bit.bits_per_long * 2;
    const map = [_]find_bit.Word{
        @as(find_bit.Word, 0xa5) << @intCast(last_aligned_byte),
        @as(find_bit.Word, 0x11),
    };

    var direct_clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, last_aligned_byte), find_bit.findFirstClump8(&direct_clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0xa5), direct_clump);

    var alias_clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_next_clump8(&alias_clump, &map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x11), alias_clump);

    var past_end_clump: u8 = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&past_end_clump, &map, nbits, nbits + 4));
    try std.testing.expectEqual(@as(u8, 0x5a), past_end_clump);
}

test "phase1 helper ports A string dirty-byte and bounded search helpers stop at C-string edges" {
    var bytes = [_]u8{0} ** 32;
    bytes[13] = 7;
    try std.testing.expectEqual(@as(?usize, 13), string.memchrInv(bytes[0..], 0));
    try std.testing.expectEqual(@as(?usize, 13), string.memchr_inv(bytes[0..], 0));

    const cstr = [_]u8{ 'm', 'o', 'd', 'e', 0, 'x', 'y' };
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&cstr, 4, 'd'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, cstr.len, 'x'));

    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(replace_buf[0..], '-', '+'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '+', 'b', 0, '-' }, replace_buf[0..]);
}

test "phase1 helper ports A rbtree cached replace alias keeps non-leftmost leftmost stable" {
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
    var middle = Entry{ .key = 10 };
    var left = Entry{ .key = 5 };
    var right = Entry{ .key = 20 };
    var replacement = Entry{ .key = 20 };

    _ = rbtree.rb_add_cached(&middle.node, &root, less);
    _ = rbtree.rb_add_cached(&left.node, &root, less);
    _ = rbtree.rb_add_cached(&right.node, &root, less);

    try std.testing.expectEqual(@as(?*rbtree.Node, &left.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.rb_first_cached(&root));

    rbtree.rb_replace_node_cached(&right.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &left.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.last(&root.root));
}
