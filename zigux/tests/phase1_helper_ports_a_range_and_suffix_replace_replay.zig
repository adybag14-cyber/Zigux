const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "bitmap range aliases leave zero-length requests untouched" {
    var map = [_]bitmap.Word{ 0x55aa, 0xaa55 };
    const original = map;

    bitmap.bitmap_set(&map, bitmap.bits_per_long - 1, 0);
    try std.testing.expectEqualSlices(bitmap.Word, &original, &map);

    bitmap.bitmap_clear(&map, bitmap.bits_per_long + 3, 0);
    try std.testing.expectEqualSlices(bitmap.Word, &original, &map);

    bitmap.setRange(&map, bitmap.bits_per_long - 1, 2);
    try std.testing.expectEqual(@as(bitmap.Word, 0x55aa | (@as(bitmap.Word, 1) << @intCast(bitmap.bits_per_long - 1))), map[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0xaa55 | 1), map[1]);

    bitmap.clearRange(&map, bitmap.bits_per_long - 1, 2);
    try std.testing.expectEqual(@as(bitmap.Word, 0x55aa & ~(@as(bitmap.Word, 1) << @intCast(bitmap.bits_per_long - 1))), map[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0xaa55 & ~@as(bitmap.Word, 1)), map[1]);
}

test "find_bit AND scans preserve public and underscore aliases at tail edges" {
    const nbits = find_bit.bits_per_long + 6;
    const lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_next_and_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 3));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_and_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&lhs, &rhs, nbits, nbits));
}

test "string suffix helpers honor C-string and empty suffix boundaries" {
    try std.testing.expect(string.strEndsWith("kernel.zig", "zig"));
    try std.testing.expect(string.str_ends_with("kernel.zig", ""));

    const cstr = [_]u8{ 'm', 'o', 'd', '.', 'z', 'i', 'g', 0, '.', 'c' };
    try std.testing.expect(string.strEndsWith(&cstr, "zig"));
    try std.testing.expect(!string.strEndsWith(&cstr, ".c"));
}

test "rbtree cached replacement preserves leftmost and traversal aliases" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const @This() = @fieldParentPtr("node", lhs);
            const rhs_entry: *const @This() = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    };

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = 20 },
        .{ .key = 10 },
        .{ .key = 30 },
    };
    var replacement = Entry{ .key = 10 };

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, Entry.less);
    }

    try std.testing.expectEqual(&entries[1].node, rbtree.rb_first_cached(&root).?);
    rbtree.rb_replace_node_cached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(&replacement.node, rbtree.firstCached(&root).?);

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.rb_first(&root.root);
    while (current) |node| : (current = rbtree.rb_next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 10, 20, 30 }, order[0..count]);
}
