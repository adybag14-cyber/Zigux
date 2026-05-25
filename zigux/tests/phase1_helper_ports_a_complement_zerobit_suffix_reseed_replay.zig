const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap complement aliases aligned across a partial tail" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;
    const src = [_]Word{
        0b1010,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 9),
    };
    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    bitmap.complement(&direct, &src, nbits);
    bitmap.bitmap_complement(&alias, &src, nbits);

    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expectEqual(~@as(Word, 0b1010), direct[0]);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), direct[1]);
}

test "lane06 replay keeps next-zero aliases aligned when tail scans cross words" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 6;
    const map = [_]Word{
        ~@as(Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(Word, 1) << 1) | (@as(Word, 1) << 4)),
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.findNextZeroBit(&map, nbits, find_bit.bits_per_long + 1),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.find_next_zero_bit(&map, nbits, find_bit.bits_per_long + 1),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextZeroBit(&map, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.find_next_zero_bit(&map, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextZeroBit(&map, nbits, find_bit.bits_per_long + 5),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.find_next_zero_bit(&map, nbits, find_bit.bits_per_long + 5),
    );
}

test "lane06 replay keeps suffix and padded-copy string helpers aligned" {
    var direct = [_]u8{ 1, 1, 1, 1, 1, 1 };
    var alias = [_]u8{ 2, 2, 2, 2, 2, 2 };

    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&direct, &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(&alias, &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &direct, &alias);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &alias);

    try std.testing.expect(string.strEndsWith(&[_]u8{ 'm', 'o', 'd', 'e', 0, 'x' }, "de"));
    try std.testing.expect(string.str_ends_with("mode-check", "check"));
    try std.testing.expect(!string.strEndsWith("mode-check", "mode"));
    try std.testing.expect(string.strstarts("mode-check", "mode"));
}

test "lane06 replay keeps cached erase-init aliases aligned as the leftmost entry advances" {
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
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.rb_erase_init_cached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.rb_erase_init_cached(&entries[2].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[2].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);
}
