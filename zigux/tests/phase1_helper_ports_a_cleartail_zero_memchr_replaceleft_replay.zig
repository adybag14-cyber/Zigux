const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap copy clear tail and clear range ignore hidden tail bits" {
    const nbits = bits_per_long + 9;
    const tail_noise = @as(Word, 1) << 13;
    const visible_tail = @as(Word, 1) << 8;
    const src = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << 7),
        visible_tail | tail_noise,
    };
    var dst = [_]Word{ 0, 0 };

    bitmap.copyClearTail(&dst, &src, nbits);
    try std.testing.expectEqual(@as(Word, 0), dst[1] & tail_noise);
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&dst, nbits));

    bitmap.clearRange(&dst, bits_per_long + 8, 1);
    const expected = [_]Word{ (@as(Word, 1) << 1) | (@as(Word, 1) << 7), 0 };
    try std.testing.expect(bitmap.equal(&dst, &expected, nbits));
    try std.testing.expect(!bitmap.intersects(&dst, &[_]Word{ 0, visible_tail | tail_noise }, nbits));
}

test "find_bit zero and clump scans stop at declared tail" {
    const nbits = bits_per_long + 14;
    const visible_mask = find_bit.lastWordMask(nbits);
    const zero_map = [_]Word{
        ~@as(Word, 0),
        visible_mask & ~(@as(Word, 1) << 7),
    };

    try std.testing.expectEqual(bits_per_long + 7, find_bit.findNextZeroBit(&zero_map, nbits, bits_per_long));
    try std.testing.expectEqual(nbits, find_bit.findNextZeroBit(&zero_map, nbits, bits_per_long + 8));

    const clump_map = [_]Word{
        0,
        (@as(Word, 1) << 9) | (@as(Word, 1) << 13),
    };
    var clump: u8 = 0xff;
    try std.testing.expectEqual(bits_per_long + 8, find_bit.findNextClump8(&clump, &clump_map, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0010_0010), clump);
    try std.testing.expectEqual(nbits, find_bit.findNextClump8(&clump, &clump_map, nbits, bits_per_long + 14));
}

test "string padded copies and dirty-byte scans honor C-string boundaries" {
    var padded = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x' };
    try std.testing.expectEqual(@as(isize, 3), string.strscpyPad(&padded, &[_]u8{ 'z', 'i', 'g', 0, 'u', 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 0, 0, 0, 0, 0 }, &padded);
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(padded[3..], 0));

    var compact = [_]u8{ ' ', 'a', ' ', 'b', 0, ' ', 'c' };
    const compacted = string.removeSpaces(&compact);
    try std.testing.expectEqualStrings("ab", compacted);
    try std.testing.expectEqual(@as(usize, 2), string.replaceChar(&compact, 'b', 'z'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'z', 0, 'b', 0, ' ', 'c' }, &compact);
}

test "rbtree cached replace keeps the leftmost cursor on the replacement" {
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
        .{ .key = 12 },
        .{ .key = 4 },
        .{ .key = 20 },
    };
    var replacement = Entry{ .key = 4 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 12, 20 }, order[0..count]);
}
