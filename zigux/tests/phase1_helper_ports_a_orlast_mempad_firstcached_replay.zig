const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap weighted or ignores tail noise while preserving visible bits" {
    const nbits = bits_per_long + 11;
    const lhs = [_]Word{
        (@as(Word, 1) << 2),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 14),
    };
    const rhs = [_]Word{
        (@as(Word, 1) << 5),
        (@as(Word, 1) << 10) | (@as(Word, 1) << 17),
    };
    var dst = [_]Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 4), bitmap.weightedOr(&dst, &lhs, &rhs, nbits));

    const expected = [_]Word{
        (@as(Word, 1) << 2) | (@as(Word, 1) << 5),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 10),
    };
    try std.testing.expect(bitmap.equal(&dst, &expected, nbits));
    try std.testing.expect(bitmap.intersects(&dst, &expected, nbits));
    try std.testing.expect(bitmap.subset(&expected, &dst, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&dst, nbits));
}

test "find_bit last and andnot scans clamp the declared tail window" {
    const nbits = bits_per_long + 11;
    const lhs = [_]Word{
        (@as(Word, 1) << 3),
        (@as(Word, 1) << 4) | (@as(Word, 1) << 10) | (@as(Word, 1) << 14),
    };
    const rhs = [_]Word{
        0,
        (@as(Word, 1) << 4) | (@as(Word, 1) << 17),
    };

    try std.testing.expectEqual(bits_per_long + 10, find_bit.findLastBit(&lhs, nbits));
    try std.testing.expectEqual(bits_per_long + 10, find_bit.findNextAndNotBit(&lhs, &rhs, nbits, bits_per_long));
    try std.testing.expectEqual(bits_per_long + 10, find_bit.findNextAndNotBit(&lhs, &rhs, nbits, bits_per_long + 5));
    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(&lhs, &rhs, nbits, bits_per_long + 11));
}

test "string memory padding helpers stop at C-string boundaries" {
    var fixed = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x' };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&fixed, &[_]u8{ 'a', 'b', 0, 'c', 'd' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0, 0, 0, 0, 0, 0 }, &fixed);
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(fixed[2..], 0));

    var spaced = [_]u8{ 'z', ' ', 'i', ' ', 'g', 0, 'u', 'x' };
    const compact = string.removeSpaces(&spaced);
    try std.testing.expectEqualStrings("zig", compact);
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&spaced, "zig"));
    try std.testing.expect(string.strEndsWith(&spaced, "ig"));
}

test "rbtree find add cached rejects duplicates without moving first node" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 20 },
        .{ .key = 10 },
        .{ .key = 30 },
    };
    var duplicate = Entry{ .key = 10 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&entry.node, &root, cmp));
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.findAddCached(&duplicate.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.next(&duplicate.node));

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
}
