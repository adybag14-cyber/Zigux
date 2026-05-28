const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap range flips preserve surrounding and tail state" {
    const nbits = bits_per_long * 2 + 9;
    var map = [_]Word{ 0, 0, 0 };

    bitmap.setRange(&map, bits_per_long - 3, 17);
    try std.testing.expectEqual(@as(usize, 17), bitmap.weight(&map, nbits));
    try std.testing.expect(bitmap.intersects(&map, &[_]Word{ 0, 0x1fff, 0 }, nbits));

    bitmap.clearRange(&map, bits_per_long + 2, 8);
    try std.testing.expectEqual(@as(usize, 9), bitmap.weight(&map, nbits));

    const expected = [_]Word{
        bitmap.firstWordMask(bits_per_long - 3),
        (@as(Word, 0b11) | (@as(Word, 0b1111) << 10)),
        0,
    };
    try std.testing.expect(bitmap.equal(&map, &expected, nbits));

    map[2] = ~bitmap.lastWordMask(nbits);
    try std.testing.expect(bitmap.equal(&map, &expected, nbits));
    try std.testing.expect(bitmap.subset(&expected, &map, nbits));

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&map, nbits, &rendered);
    try std.testing.expectEqualStrings("61-65,74-77", rendered[0..rendered_len]);
}

test "find_bit clump8 masks the final aligned byte window" {
    const nbits = bits_per_long + 13;
    const clump_offset = bits_per_long + 8;
    const map = [_]Word{
        0,
        (@as(Word, 1) << 8) | (@as(Word, 1) << 12) | (@as(Word, 1) << 14),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(clump_offset, find_bit.findNextClump8(&clump, &map, nbits, bits_per_long + 6));
    try std.testing.expectEqual(@as(u8, 0b0001_0001), clump);

    clump = 0x5a;
    try std.testing.expectEqual(nbits, find_bit.findNextClump8(&clump, &map, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "string trim replace and prefix suffix helpers share C-string limits" {
    var text = [_]u8{ ' ', '\t', 'a', 'l', 'p', 'h', 'a', '-', 'b', 'e', 't', 'a', ' ', '\n', 0, 'x' };

    const trimmed = string.strim(&text);
    try std.testing.expectEqualStrings("alpha-beta", trimmed);
    try std.testing.expectEqual(@as(u8, 0), text[12]);

    try std.testing.expectEqual(@as(usize, 10), string.strreplace(trimmed, '-', '_'));
    try std.testing.expectEqualStrings("alpha_beta", trimmed);
    try std.testing.expectEqual(@as(usize, 5), string.str_has_prefix(trimmed, "alpha"));
    try std.testing.expect(string.strstarts(trimmed, "alpha"));
    try std.testing.expect(string.strEndsWith(trimmed, "beta"));
    try std.testing.expect(string.str_ends_with(trimmed, "beta"));
    try std.testing.expect(!string.strEndsWith(&text, "x"));
}

test "rbtree cached traversal keeps predecessor links after leftmost erase" {
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
        .{ .key = 20 },
        .{ .key = 10 },
        .{ .key = 30 },
        .{ .key = 25 },
        .{ .key = 40 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[4].node), rbtree.last(&root.root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.prev(&entries[4].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.prev(&entries[2].node));

    const new_leftmost = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), new_leftmost);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(&entries[0].node));

    var reverse: [4]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.last(&root.root);
    while (current) |node| : (current = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        reverse[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 40, 30, 25, 20 }, reverse[0..count]);
}
