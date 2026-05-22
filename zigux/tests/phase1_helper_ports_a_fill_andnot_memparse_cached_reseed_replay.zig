const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap fill weighted and zero replay" {
    const nbits = bitmap.bits_per_long + 3;
    const tail_mask = bitmap.lastWordMask(nbits);

    var direct_fill = [_]bitmap.Word{ 0, 0 };
    var alias_fill = [_]bitmap.Word{ 0x55, 0xaa };
    bitmap.fill(&direct_fill, nbits);
    bitmap.bitmap_fill(&alias_fill, nbits);

    try std.testing.expectEqualSlices(bitmap.Word, &direct_fill, &alias_fill);
    try std.testing.expectEqual(~@as(bitmap.Word, 0), direct_fill[0]);
    try std.testing.expectEqual(tail_mask, direct_fill[1]);

    const lhs = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 3),
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 2),
    };
    const rhs = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 2),
    };

    var direct_weighted = [_]bitmap.Word{ 0, 0 };
    var alias_weighted = [_]bitmap.Word{ 0, 0 };
    const direct_or_weight = bitmap.weightedOr(&direct_weighted, &lhs, &rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_weighted, &lhs, &rhs, nbits);
    try std.testing.expectEqual(direct_or_weight, alias_or_weight);
    try std.testing.expectEqual(@as(usize, 6), direct_or_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_weighted, &alias_weighted);

    const direct_xor_weight = bitmap.weightedXor(&direct_weighted, &lhs, &rhs, nbits);
    const alias_xor_weight = bitmap.bitmap_weighted_xor(&alias_weighted, &lhs, &rhs, nbits);
    try std.testing.expectEqual(direct_xor_weight, alias_xor_weight);
    try std.testing.expectEqual(@as(usize, 4), direct_xor_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_weighted, &alias_weighted);

    bitmap.zero(&direct_fill, nbits);
    bitmap.bitmap_zero(&alias_fill, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_fill, &alias_fill);
    try std.testing.expect(bitmap.empty(&direct_fill, nbits));
}

test "phase1 helper ports A find_bit andnot tail alias replay" {
    const nbits = find_bit.bits_per_long + 3;
    const boundary = find_bit.bits_per_long;

    const lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 0) |
            (@as(find_bit.Word, 1) << 2) |
            (@as(find_bit.Word, 1) << 5),
    };
    const rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 0) |
            (@as(find_bit.Word, 1) << 5),
    };

    try std.testing.expectEqual(@as(usize, boundary + 2), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 2), find_bit._find_first_andnot_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 2), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary + 2), find_bit._find_next_andnot_bit(&lhs, &rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, boundary + 3));
}

test "phase1 helper ports A string memparse and pad replay" {
    const signed = string.memparse("-16 trailing");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -16))), signed.value);
    try std.testing.expectEqualStrings(" trailing", signed.rest);

    const clamped = string.memparse("+9223372036854775808");
    try std.testing.expectEqual(@as(u64, @intCast(std.math.maxInt(i64))), clamped.value);

    var single = [_]u8{0xaa};
    try std.testing.expectEqual(@as(isize, -7), string.strscpyPad(&single, "z"));
    try std.testing.expectEqual(@as(u8, 0), single[0]);

    const dup = try string.memdup(std.testing.allocator, "lane06");
    defer std.testing.allocator.free(dup);
    try std.testing.expectEqualStrings("lane06", dup);
}

test "phase1 helper ports A rbtree cached reseed and leftmost replacement replay" {
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

    var first_entry = Entry{ .key = 10 };
    var reseeded_entry = Entry{ .key = 6 };
    var right_entry = Entry{ .key = 12 };
    var replacement_leftmost = Entry{ .key = 6 };
    var root = rbtree.RootCached.init();

    _ = rbtree.addCached(&first_entry.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&first_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&first_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));

    _ = rbtree.addCached(&reseeded_entry.node, &root, less);
    _ = rbtree.addCached(&right_entry.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseeded_entry.node), rbtree.firstCached(&root));

    rbtree.rb_replace_node_cached(&reseeded_entry.node, &replacement_leftmost.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement_leftmost.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
