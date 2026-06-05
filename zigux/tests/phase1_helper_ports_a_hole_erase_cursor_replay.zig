const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A hole erase cursor replay" {
    const Word = bitmap.Word;
    const nbits: usize = 80;

    var map = [_]Word{ 0, 0 };
    bitmap.bitmap_set(&map, 5, 7);
    bitmap.bitmap_clear(&map, 8, 2);
    bitmap.bitmap_set(&map, 70, 3);

    try std.testing.expectEqual(@as(usize, 8), bitmap.bitmap_weight(&map, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.find_first_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 8), find_bit.find_next_zero_bit(&map, nbits, 5));
    try std.testing.expectEqual(@as(usize, 10), find_bit.find_next_bit(&map, nbits, 8));
    try std.testing.expectEqual(@as(usize, 72), find_bit.find_last_bit(&map, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 64), find_bit.find_next_clump8(&clump, &map, nbits, 64));
    try std.testing.expectEqual(@as(u8, 0b1100_0000), clump);
    try std.testing.expectEqual(@as(usize, 72), find_bit.find_next_clump8(&clump, &map, nbits, 72));
    try std.testing.expectEqual(@as(u8, 0b0000_0001), clump);

    var token = [_]u8{ ' ', ' ', 'h', 'o', 'l', 'e', ' ', 'e', 'r', 'a', 's', 'e', '\n', 0, 'x' };
    const trimmed = string.strim(&token);
    try std.testing.expectEqualStrings("hole erase", trimmed);
    try std.testing.expectEqual(@as(usize, trimmed.len), string.strreplace(trimmed, ' ', '-'));
    try std.testing.expectEqualStrings("hole-erase", trimmed);
    try std.testing.expect(string.sysfs_streq(trimmed, "hole-erase\n"));
    try std.testing.expectEqual(@as(?usize, null), string.memchr_inv(".........", '.'));
    try std.testing.expectEqual(@as(?usize, 4), string.memchr_inv("....x....", '.'));

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

    var entries = [_]Entry{
        .{ .key = 5 },
        .{ .key = 8 },
        .{ .key = 10 },
        .{ .key = 12 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    rbtree.erase(&entries[1].node, &root);
    rbtree.eraseInit(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));

    var order: [2]i32 = undefined;
    var count: usize = 0;
    var cursor = rbtree.first(&root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 10, 12 }, order[0..count]);
}
