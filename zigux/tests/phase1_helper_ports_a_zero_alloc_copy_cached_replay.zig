const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "ports A zero allocation clump copy and cached tree replay" {
    const allocator = std.testing.allocator;
    const nbits = bitmap.bits_per_long + 5;

    var zero_alloc: ?[]bitmap.Word = try bitmap.bitmap_alloc(allocator, 0);
    defer bitmap.bitmap_free(allocator, &zero_alloc);
    if (zero_alloc) |words| {
        try std.testing.expectEqual(@as(usize, 0), words.len);
    }

    var zeroed_alloc: ?[]bitmap.Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &zeroed_alloc);
    try std.testing.expectEqual(bitmap.bitsToWords(nbits), zeroed_alloc.?.len);
    for (zeroed_alloc.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }
    bitmap.bitmap_free(allocator, &zeroed_alloc);
    try std.testing.expect(zeroed_alloc == null);

    var clump: u8 = 0x5a;
    const clump_nbits = find_bit.bits_per_long + 8;
    const clump_map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 7) };
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_first_clump8(&clump, &clump_map, clump_nbits));
    try std.testing.expectEqual(@as(u8, 0b1000_1000), clump);
    clump = 0xa5;
    try std.testing.expectEqual(clump_nbits, find_bit.find_next_clump8(&clump, &clump_map, clump_nbits, clump_nbits));
    try std.testing.expectEqual(@as(u8, 0xa5), clump);

    var copy_buf = [_]u8{ 9, 9, 9, 9 };
    try std.testing.expectEqual(@as(usize, 5), string.strlcpy(copy_buf[0..], "hello"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'e', 'l', 0 }, copy_buf[0..]);

    var padded_buf = [_]u8{ 7, 7, 7, 7, 7 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(padded_buf[0..], "ok"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0 }, padded_buf[0..]);

    var truncated_buf = [_]u8{ 8, 8, 8 };
    try std.testing.expect(string.strscpyPad(truncated_buf[0..], "abcd") < 0);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0 }, truncated_buf[0..]);

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

    var first = Entry{ .key = 10 };
    var second = Entry{ .key = 6 };
    var third = Entry{ .key = 14 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &first.node), rbtree.addCached(&first.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &second.node), rbtree.addCached(&second.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&third.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &second.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&second.node, &root);
    try std.testing.expect(rbtree.emptyNode(&second.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &first.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&first.node, &root);
    try std.testing.expect(rbtree.emptyNode(&first.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &third.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&third.node, &root);
    try std.testing.expect(rbtree.emptyNode(&third.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);
}
