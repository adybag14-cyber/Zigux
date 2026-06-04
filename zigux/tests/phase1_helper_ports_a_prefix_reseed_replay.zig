const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;

test "bitmap prefix reseed keeps later tail scans authoritative" {
    const nbits = find_bit.bits_per_long + 12;
    var map = [_]Word{ 0, 0 };

    bitmap.bitmap_set(&map, 3, 5);
    bitmap.bitmap_set(&map, find_bit.bits_per_long + 4, 3);
    bitmap.bitmap_clear(&map, 0, find_bit.bits_per_long);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_first_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.find_next_bit(&map, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 7), find_bit.find_next_zero_bit(&map, nbits, find_bit.bits_per_long + 4));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 6), find_bit.find_last_bit(&map, nbits));

    var clump: u8 = 0xaa;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_next_clump8(&clump, &map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0111_0000), clump);
}

test "string prefix cleanup leaves bounded cursor and suffix helpers aligned" {
    var token = [_]u8{ ' ', ' ', 'r', 'e', 's', 'e', 'e', 'd', '-', 'o', 'k', 0, 'x' };
    const trimmed = string.strim(token[0..]);

    try std.testing.expectEqualStrings("reseed-ok", trimmed);
    try std.testing.expectEqual(@as(usize, 7), string.str_has_prefix(trimmed, "reseed-"));
    try std.testing.expect(string.strEndsWith(trimmed, "ok"));
    try std.testing.expectEqual(@as(?usize, 6), string.strnchr(trimmed, trimmed.len, '-'));

    try std.testing.expectEqual(@as(?usize, null), string.strnchr(trimmed, 6, '-'));
}

test "rbtree erase-init reseed restores traversal and detached-node state" {
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
    var second_entry = Entry{ .key = 5 };
    var third_entry = Entry{ .key = 15 };
    var root = rbtree.Root.init();

    rbtree.add(&first_entry.node, &root, less);
    rbtree.add(&second_entry.node, &root, less);
    rbtree.add(&third_entry.node, &root, less);

    rbtree.eraseInit(&second_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&second_entry.node));
    try std.testing.expectEqual(@as(*rbtree.Node, &first_entry.node), rbtree.first(&root).?);
    try std.testing.expectEqual(@as(*rbtree.Node, &third_entry.node), rbtree.last(&root).?);

    second_entry.key = 3;
    rbtree.add(&second_entry.node, &root, less);
    try std.testing.expectEqual(@as(*rbtree.Node, &second_entry.node), rbtree.first(&root).?);
    try std.testing.expectEqual(@as(*rbtree.Node, &first_entry.node), rbtree.next(&second_entry.node).?);
}
