const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

const Entry = struct {
    key: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn keyOf(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn collectForward(root: *const rbtree.RootCached, out: []usize) usize {
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        out[count] = keyOf(node);
        count += 1;
    }
    return count;
}

fn buildSplicedBitmap(out: []Word, mask: []Word) void {
    const nbits = bitmap.bits_per_long + 19;
    var old: [bitmap.bitsToWords(nbits)]Word = @splat(0);
    var new: [bitmap.bitsToWords(nbits)]Word = @splat(0);

    bitmap.setRange(&old, 2, 4);
    bitmap.setRange(&old, 16, 3);
    bitmap.setRange(&old, bitmap.bits_per_long + 6, 7);

    bitmap.setRange(&new, 8, 4);
    bitmap.setRange(&new, 30, 4);
    bitmap.setRange(&new, bitmap.bits_per_long + 15, 12);

    bitmap.setRange(mask, 4, 9);
    bitmap.setRange(mask, bitmap.bits_per_long + 6, 20);
    bitmap.bitmap_replace(out, &old, &new, mask, nbits);
}

test "helper ports A mask splice clamps replacement and and-not scans" {
    const nbits = bitmap.bits_per_long + 19;
    var spliced: [bitmap.bitsToWords(nbits)]Word = @splat(0);
    var mask: [bitmap.bitsToWords(nbits)]Word = @splat(0);
    buildSplicedBitmap(&spliced, &mask);

    try std.testing.expectEqual(@as(usize, 13), bitmap.weight(&spliced, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&spliced, nbits));
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextBit(&spliced, nbits, 4));
    try std.testing.expectEqual(@as(usize, 16), find_bit.findNextAndNotBit(&spliced, &mask, nbits, 4));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 18), find_bit.findLastBit(&spliced, nbits));

    var rendered: [64]u8 = undefined;
    const written = bitmap.scnprintf(&spliced, nbits, &rendered);
    const expected = "2-3,8-11,16-18,79-82";
    try std.testing.expectEqual(expected.len, written);
    try std.testing.expectEqualStrings(expected, rendered[0..written]);

    var copied: [32]u8 = @splat(0xaa);
    try std.testing.expectEqual(@as(isize, expected.len), string.strscpy_pad(&copied, expected));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&copied, written, '-'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&copied, written, 'z'));

    const tokens = [_][]const u8{
        "2-3,8-11,16-18,79-82\n",
        "2-3,8-11,16-18",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&tokens, copied[0..written]));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&tokens, copied[0..written]));
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(&tokens, "2-3,8-11,16-18,79-82\n"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&tokens, "2-3,8-11,16-18"));
}

test "helper ports A spliced keys preserve cached rbtree erase and reinsert order" {
    const nbits = bitmap.bits_per_long + 19;
    var spliced: [bitmap.bitsToWords(nbits)]Word = @splat(0);
    var mask: [bitmap.bitsToWords(nbits)]Word = @splat(0);
    buildSplicedBitmap(&spliced, &mask);

    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(&spliced, nbits) },
        .{ .key = find_bit.findNextBit(&spliced, nbits, 4) },
        .{ .key = find_bit.findNextAndNotBit(&spliced, &mask, nbits, 4) },
        .{ .key = find_bit.findLastBit(&spliced, nbits) },
    };

    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, entryLess);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    var order: [entries.len]usize = undefined;
    var count = collectForward(&root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 8, 16, bitmap.bits_per_long + 18 }, order[0..count]);

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    entries[0].key = bitmap.bits_per_long + 1;
    _ = rbtree.addCached(&entries[0].node, &root, entryLess);

    count = collectForward(&root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 8, 16, bitmap.bits_per_long + 1, bitmap.bits_per_long + 18 }, order[0..count]);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
}
