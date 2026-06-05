const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = find_bit.Word;

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

test "phase1 helper ports A sparse cursor replay" {
    const nbits = find_bit.bits_per_long + 13;
    var mask = [_]Word{0} ** 2;
    var guard = [_]Word{0} ** 2;
    var diff = [_]Word{0} ** 2;

    bitmap.bitmap_set(&mask, 3, 5);
    bitmap.bitmap_set(&mask, find_bit.bits_per_long + 4, 3);
    bitmap.bitmap_set(&guard, 5, 2);
    bitmap.bitmap_set(&guard, find_bit.bits_per_long + 5, 1);
    try std.testing.expect(bitmap.bitmap_andnot(&diff, &mask, &guard, nbits));

    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(&diff, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.find_first_bit(&diff, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.find_next_bit(&diff, nbits, 4));
    try std.testing.expectEqual(@as(usize, 7), find_bit.find_next_bit(&diff, nbits, 5));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_next_bit(&diff, nbits, 8));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 6), find_bit.find_last_bit(&diff, nbits));

    var clump: u8 = 0;
    const clump_offset = find_bit.find_next_clump8(&clump, &diff, nbits, 0);
    try std.testing.expectEqual(@as(usize, 0), clump_offset);
    try std.testing.expectEqual(@as(u8, 0b10011000), clump);

    var label = [_]u8{ ' ', '\t', 's', 'p', 'a', 'r', 's', 'e', ':', '3', '-', '7', '\n', ' ' };
    const trimmed = string.strim(&label);
    try std.testing.expectEqualStrings("sparse:3-7", trimmed);
    try std.testing.expectEqual(trimmed.len, string.strreplace(trimmed, '-', '/'));
    try std.testing.expectEqualStrings("sparse:3/7", trimmed);
    try std.testing.expectEqual(@as(?usize, 1), string.memchr_inv(trimmed[0..6], 's'));

    var entries = [_]Entry{
        .{ .key = @intCast(find_bit.find_first_bit(&diff, nbits)) },
        .{ .key = @intCast(find_bit.find_next_bit(&diff, nbits, 4)) },
        .{ .key = @intCast(find_bit.find_last_bit(&diff, nbits)) },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    rbtree.eraseInit(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));

    var order: [2]i32 = undefined;
    var count: usize = 0;
    var cursor = rbtree.first(&root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, @intCast(find_bit.bits_per_long + 6) }, order[0..count]);
}
