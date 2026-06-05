const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "bitmap copy extend masks the copied tail before find-bit scans" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 9;
    const count = bitmap.bits_per_long + 3;

    var source = [_]Word{0} ** 2;
    var extended = [_]Word{~@as(Word, 0)} ** 2;

    source[0] =
        (@as(Word, 1) << 1) |
        (@as(Word, 1) << 3) |
        (@as(Word, 1) << (bitmap.bits_per_long - 1));
    source[1] =
        (@as(Word, 1) << 2) |
        (@as(Word, 1) << 8);

    bitmap.copyAndExtend(&extended, &source, count, nbits);

    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&extended, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&extended, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findNextBit(&extended, nbits, 2));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long - 1), find_bit.findNextBit(&extended, nbits, 4));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 2), find_bit.findNextBit(&extended, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&extended, nbits, bitmap.bits_per_long + 3));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&extended, nbits, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 2), find_bit.findLastBit(&extended, nbits));
    try std.testing.expect(!bitmap.full(&extended, nbits));

    const empty_words = [_]Word{};
    try std.testing.expect(bitmap.empty(&empty_words, 0));
    try std.testing.expect(bitmap.full(&empty_words, 0));
    try std.testing.expectEqual(@as(usize, 0), bitmap.weight(&empty_words, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstBit(&empty_words, 0));
}

test "strlcpy returns the full C-string length while preserving boundaries" {
    var copied = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x' };
    const copied_len = string.strlcpy(&copied, &[_]u8{ 'z', 'i', 'u', 'x', 0, 'h', 'i', 'd', 'd', 'e', 'n' });

    try std.testing.expectEqual(@as(usize, 4), copied_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'u', 'x', 0 }, copied[0..5]);
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&copied, copied.len, 'h'));
    try std.testing.expectEqual(@as(?usize, 4), string.strnchr(&copied, copied.len, 0));

    var truncated = [_]u8{ '!', '!', '!', '!' };
    const truncated_len = string.strlcpy(&truncated, "abcdef");

    try std.testing.expectEqual(@as(usize, 6), truncated_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 0 }, &truncated);
    try std.testing.expect(string.strEndsWith(&truncated, "bc"));
    try std.testing.expect(!string.strEndsWith(&truncated, "def"));
}

test "rbtree findAddCached rejects duplicates without moving cached leftmost" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const cmp_node = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    const cmp_key = struct {
        fn compare(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
            const key: *const i32 = @ptrCast(@alignCast(key_ptr));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (key.* < entry.key) return -1;
            if (key.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 3 },
        .{ .key = 13 },
    };

    for (&entries) |*entry| {
        try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&entry.node, &root, cmp_node));
    }
    try std.testing.expectEqual(&entries[1].node, rbtree.rb_first_cached(&root).?);

    var duplicate = Entry{ .key = 3 };
    try std.testing.expectEqual(&entries[1].node, rbtree.findAddCached(&duplicate.node, &root, cmp_node).?);
    try std.testing.expectEqual(&entries[1].node, rbtree.rb_first_cached(&root).?);

    var smaller = Entry{ .key = 1 };
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&smaller.node, &root, cmp_node));
    try std.testing.expectEqual(&smaller.node, rbtree.rb_first_cached(&root).?);

    const duplicate_key: i32 = 3;
    try std.testing.expectEqual(&entries[1].node, rbtree.find(&duplicate_key, &root.root, cmp_key).?);

    var order: [4]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.rb_first(&root.root);
    while (current) |node| : (current = rbtree.rb_next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 3, 8, 13 }, order[0..count]);
}
