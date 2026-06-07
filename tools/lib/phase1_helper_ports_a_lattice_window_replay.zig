const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn lessByKey(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn collectForward(root: *const rbtree.RootCached, out: []usize) usize {
    var count: usize = 0;
    var current = rbtree.firstCached(root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "lattice window replay connects bitmap gaps to find-bit cursors, strings, and cached rbtree order" {
    const nbits = bits_per_long * 2 + 19;
    const nwords = 3;
    try std.testing.expectEqual(nwords, bitmap.bitsToWords(nbits));

    var base = [_]Word{0} ** 3;
    var diagonal = [_]Word{0} ** 3;
    var window = [_]Word{0} ** 3;
    var holes = [_]Word{0} ** 3;
    var rebuilt = [_]Word{0} ** 3;

    bitmap.setRange(&base, 3, 7);
    bitmap.setRange(&base, bits_per_long - 2, 8);
    bitmap.setRange(&base, bits_per_long + 21, 5);
    bitmap.setRange(&base, bits_per_long * 2 + 9, 4);

    bitmap.setRange(&diagonal, 5, 2);
    bitmap.setRange(&diagonal, bits_per_long + 1, 5);
    bitmap.setRange(&diagonal, bits_per_long + 23, 2);
    bitmap.setRange(&diagonal, bits_per_long * 2 + 10, 2);

    bitmap.setRange(&window, bits_per_long - 4, 14);
    bitmap.setRange(&window, bits_per_long + 20, 9);
    bitmap.setRange(&window, bits_per_long * 2 + 8, 7);

    const has_overlap = bitmap.andBits(&holes, &base, &diagonal, nbits);
    try std.testing.expect(has_overlap);
    try std.testing.expectEqual(@as(usize, 11), bitmap.weight(&holes, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findFirstBit(&holes, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextBit(&holes, nbits, 8));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 11), find_bit.findLastBit(&holes, nbits));

    const has_remainder = bitmap.andNotBits(&rebuilt, &base, &holes, nbits);
    try std.testing.expect(has_remainder);
    try std.testing.expectEqual(@as(usize, 13), bitmap.weight(&rebuilt, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstBit(&rebuilt, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextZeroBit(&rebuilt, nbits, 3));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long - 8), find_bit.findNextClump8(&clump, &rebuilt, nbits, bits_per_long - 5));
    try std.testing.expectEqual(@as(u8, 0xc0), clump);

    var range_buf = [_]u8{0} ** 96;
    const rendered_len = bitmap.scnprintf(&rebuilt, nbits, &range_buf);
    const rendered = range_buf[0..std.mem.indexOfScalar(u8, &range_buf, 0).?];
    try std.testing.expectEqual(rendered.len, rendered_len);
    try std.testing.expectEqualStrings("3-4,7-9,62-64,85-86,89,137,140", rendered);

    var label_buf = [_]u8{0} ** 128;
    _ = try std.fmt.bufPrintZ(&label_buf, "  window:{s}\n", .{rendered});
    const label = string.strim(&label_buf);
    try std.testing.expect(string.strstarts(label, "window:"));
    try std.testing.expect(string.strEndsWith(label, "137,140"));
    try std.testing.expect(string.sysfsStreq(label, "window:3-4,7-9,62-64,85-86,89,137,140"));

    var entries = [_]Entry{
        .{ .key = find_bit.findNextBit(&rebuilt, nbits, 0) },
        .{ .key = find_bit.findNextBit(&rebuilt, nbits, bits_per_long) },
        .{ .key = find_bit.findLastBit(&rebuilt, nbits) },
        .{ .key = find_bit.findNextBit(&rebuilt, nbits, 80) },
    };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.addCached(&entries[0].node, &root, lessByKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[1].node, &root, lessByKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[2].node, &root, lessByKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[3].node, &root, lessByKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    _ = rbtree.eraseCached(&entries[0].node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    var order: [4]usize = undefined;
    const count = collectForward(&root, &order);
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 64, 85, 140 }, order[0..count]);

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.firstCached(&root));
}
