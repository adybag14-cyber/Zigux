const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap range mutation is immediately visible to find-bit scans and formatting" {
    const nbits = bits_per_long + 13;
    const head_start = bits_per_long - 3;
    var map = [_]Word{ 0, 0 };

    bitmap.setRange(&map, head_start, 8);
    bitmap.clearRange(&map, bits_per_long, 2);

    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&map, nbits));
    try std.testing.expectEqual(head_start, find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(bits_per_long + 2, find_bit.findNextBit(&map, nbits, bits_per_long));
    try std.testing.expectEqual(bits_per_long + 4, find_bit.findLastBit(&map, nbits));
    try std.testing.expect(!bitmap.empty(&map, nbits));

    var rendered: [64]u8 = undefined;
    const len = bitmap.scnprintf(&map, nbits, &rendered);

    var expected: [64]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}-{d}",
        .{ head_start, bits_per_long - 1, bits_per_long + 2, bits_per_long + 4 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..len]);
}

test "string in-place mutation keeps trimmed and compacted boundaries reusable" {
    var source = [_]u8{ ' ', 'a', ' ', 'b', ' ', 'c', ' ', 0, 'x', 'x' };

    const trimmed = string.trimSpaces(source[0..]);
    try std.testing.expectEqualStrings("a b c", trimmed);
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'a', ' ', 'b', ' ', 'c', 0, 0, 'x', 'x' }, source[0..]);

    const compacted = string.removeSpaces(trimmed);
    try std.testing.expectEqualStrings("abc", compacted);
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(compacted, 'b', 'B'));
    try std.testing.expectEqualStrings("aBc", compacted);
    try std.testing.expectEqual(@as(usize, 2), string.strHasPrefix(compacted, "aB"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(compacted, "ab"));
}

test "rbtree cached detach lets a reused node become the new leftmost" {
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
        .{ .key = 7 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.firstCached(&root));

    entries[1].key = 3;
    _ = rbtree.addCached(&entries[1].node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    var order: [4]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 7, 10, 15 }, order[0..count]);
}
