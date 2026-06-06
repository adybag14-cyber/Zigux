const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

test "helper ports A derive rbtree erase surface from bitmap and string cursors" {
    const nbits = bitmap.bits_per_long + 7;
    var lhs = [_]Word{ 0, 0 };
    var rhs = [_]Word{ 0, 0 };
    var remaining = [_]Word{ 0, 0 };

    lhs[0] = (@as(Word, 1) << 2) | (@as(Word, 1) << 5) | (@as(Word, 1) << 10);
    lhs[1] = @as(Word, 1) << 1;
    rhs[0] = @as(Word, 1) << 5;
    rhs[1] = @as(Word, 1) << 2;

    try std.testing.expect(bitmap.andNotBits(&remaining, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&remaining, nbits));
    try std.testing.expectEqual(@as(usize, 10), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 3));
    try std.testing.expectEqual(bitmap.bits_per_long + 1, find_bit.findLastBit(&remaining, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findNextZeroBit(&remaining, nbits, 3));

    var rendered_buffer = [_]u8{0} ** 32;
    const rendered_len = bitmap.scnprintf(&remaining, nbits, &rendered_buffer);
    const rendered = rendered_buffer[0..rendered_len];
    try std.testing.expectEqual(@as(usize, 2), string.strHasPrefix(rendered, "2,"));
    try std.testing.expect(string.sysfsStreq("2,10,65\n", rendered));
    try std.testing.expectEqual(@as(?usize, 1), string.memchr_inv(rendered, '2'));

    const Entry = struct {
        key: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs_node: *const rbtree.Node, rhs_node: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs_node);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs_node);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(&remaining, nbits) },
        .{ .key = find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 3) },
        .{ .key = find_bit.findLastBit(&remaining, nbits) },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    rbtree.erase(&entries[1].node, &root);
    var order: [3]usize = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, bitmap.bits_per_long + 1 }, order[0..count]);

    rbtree.eraseInit(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.first(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.last(&root));
}
