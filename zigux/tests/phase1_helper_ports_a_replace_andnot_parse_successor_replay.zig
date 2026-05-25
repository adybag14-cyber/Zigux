const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap replace masked to the declared tail window" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;

    const old = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4),
    };
    const new = [_]Word{
        0,
        (@as(Word, 1) << 0) | (@as(Word, 1) << 3) | (@as(Word, 1) << 6),
    };
    const mask = [_]Word{
        0,
        (@as(Word, 1) << 0) |
            (@as(Word, 1) << 1) |
            (@as(Word, 1) << 3) |
            (@as(Word, 1) << 6),
    };
    const expected = [_]Word{
        0,
        (@as(Word, 1) << 0) | (@as(Word, 1) << 3) | (@as(Word, 1) << 4),
    };

    var primary_dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    var alias_dst = [_]Word{ 0, 0 };

    bitmap.replace(&primary_dst, &old, &new, &mask, nbits);
    bitmap.bitmap_replace(&alias_dst, &old, &new, &mask, nbits);

    try std.testing.expectEqualSlices(Word, &expected, &primary_dst);
    try std.testing.expect(bitmap.equal(&primary_dst, &alias_dst, nbits));
    try std.testing.expect(bitmap.subset(&primary_dst, &expected, nbits));
    try std.testing.expect(bitmap.subset(&expected, &primary_dst, nbits));
}

test "lane06 replay keeps and-not scans and last-bit reads inside the tail mask" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 6),
    };
    const rhs = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 6),
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findFirstAndNotBit(&lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findLastBit(&lhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findLastBit(&rhs, nbits));
}

test "lane06 replay keeps signed base parsing and bounded searches aligned" {
    const positive_hex = string.memparse("+0x10Ktail");
    try std.testing.expectEqual(@as(u64, 0x10 << 10), positive_hex.value);
    try std.testing.expectEqualStrings("tail", positive_hex.rest);

    const negative_octal = string.memparse("-010Mmore");
    try std.testing.expectEqual(
        @as(u64, @bitCast(@as(i64, -(8 << 20)))),
        negative_octal.value,
    );
    try std.testing.expectEqualStrings("more", negative_octal.rest);

    const counted = [_]u8{ 'm', 'o', 'd', 'e', 0, 'x', 'y' };
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&counted, 3, 'd'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&counted, counted.len, 'x'));
    try std.testing.expectEqual(@as(?usize, 4), string.strnchr(&counted, counted.len, 0));
}

test "lane06 replay keeps cached-rbtree successor promotion and reverse traversal stable" {
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
        .{ .key = 8 },
        .{ .key = 7 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[3].node), promoted_leftmost);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    var forward: [3]i32 = undefined;
    var reverse: [3]i32 = undefined;
    var count: usize = 0;

    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        forward[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 7, 8, 10 }, forward[0..count]);

    var reverse_count: usize = 0;
    current = rbtree.last(&root.root);
    while (current) |node| : (current = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        reverse[reverse_count] = entry.key;
        reverse_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), reverse_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 10, 8, 7 }, reverse[0..reverse_count]);
}
