const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap weighted-or feeds find-bit scans across a masked tail" {
    const nbits = bits_per_long + 6;
    const lhs = [_]Word{
        (@as(Word, 1) << 2) | (@as(Word, 1) << @intCast(bits_per_long - 1)),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 8),
    };
    const rhs = [_]Word{
        (@as(Word, 1) << 4),
        (@as(Word, 1) << 4) | (@as(Word, 1) << 10),
    };
    var union_bits = [_]Word{ 0, 0 };

    const weight = bitmap.bitmap_weighted_or(&union_bits, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 5), weight);
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&union_bits, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findNextBit(&union_bits, nbits, 3));
    try std.testing.expectEqual(@as(usize, bits_per_long - 1), find_bit.findNextBit(&union_bits, nbits, 5));
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextBit(&union_bits, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextBit(&union_bits, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&union_bits, nbits, bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findLastBit(&union_bits, nbits));
}

test "string strscpyPad keeps truncation and padding boundaries explicit" {
    var padded = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(padded[0..], &[_]u8{ 'h', 'i', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0, 0 }, padded[0..]);

    var alias_padded = [_]u8{ 0xbb, 0xbb, 0xbb, 0xbb };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(alias_padded[0..], "ok"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0 }, alias_padded[0..]);

    var truncated = [_]u8{ 0xcc, 0xcc, 0xcc };
    try std.testing.expect(string.strscpyPad(truncated[0..], "abcd") < 0);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0 }, truncated[0..]);

    var one_byte = [_]u8{0xdd};
    try std.testing.expect(string.strscpyPad(one_byte[0..], "x") < 0);
    try std.testing.expectEqual(@as(u8, 0), one_byte[0]);
}

test "rbtree cached erase-init reseeds leftmost after key reuse" {
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
        .{ .key = 30 },
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 40 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    entries[1].key = 5;
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.addCached(&entries[1].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.firstCached(&root));
}
