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

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn collect(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var current = rbtree.first(root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "lane06 hinge latch replay keeps helper-derived erase order stable" {
    const nbits = 96;
    var old = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var new = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var mask = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var replaced = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var old_only = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var merged = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var toggled = [_]Word{0} ** bitmap.bitsToWords(nbits);

    bitmap.bitmap_set(&old, 2, 4);
    bitmap.bitmap_set(&old, 70, 3);
    bitmap.bitmap_set(&old, 95, 1);
    bitmap.bitmap_set(&new, 4, 5);
    bitmap.bitmap_set(&new, 65, 4);
    bitmap.bitmap_set(&new, 90, 1);
    bitmap.bitmap_set(&mask, 3, 5);
    bitmap.bitmap_set(&mask, 66, 4);
    bitmap.bitmap_set(&mask, 95, 1);

    bitmap.bitmap_replace(&replaced, &old, &new, &mask, nbits);
    const has_old_only = bitmap.bitmap_andnot(&old_only, &old, &new, nbits);
    bitmap.bitmap_or(&merged, &old, &new, nbits);
    bitmap.bitmap_xor(&toggled, &old, &new, nbits);

    try std.testing.expect(has_old_only);
    try std.testing.expectEqual(@as(usize, 11), bitmap.bitmap_weight(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 6), bitmap.bitmap_weight(&old_only, nbits));
    try std.testing.expectEqual(@as(usize, 16), bitmap.bitmap_weight(&merged, nbits));
    try std.testing.expectEqual(@as(usize, 14), bitmap.bitmap_weight(&toggled, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&replaced, &merged, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&replaced, &old_only, nbits));

    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findNextBit(&replaced, nbits, 3));
    try std.testing.expectEqual(@as(usize, 72), find_bit.findLastBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findFirstAndBit(&old, &new, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstAndNotBit(&old, &new, nbits));
    try std.testing.expectEqual(@as(usize, 70), find_bit.findNextAndNotBit(&old, &new, nbits, 4));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findNextZeroBit(&replaced, nbits, 2));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &replaced, nbits));
    try std.testing.expectEqual(@as(u8, 0xf4), clump);
    try std.testing.expectEqual(@as(usize, 64), find_bit.findNextClump8(&clump, &replaced, nbits, 8));
    try std.testing.expectEqual(@as(u8, 0xdc), clump);

    var rendered = [_]u8{0} ** 64;
    const rendered_len = bitmap.bitmap_scnprintf(&replaced, nbits, &rendered);
    const rendered_text = rendered[0..rendered_len];
    try std.testing.expectEqualStrings("2,4-7,66-68,70-72", rendered_text);

    var padded = [_]u8{ ' ', ' ', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ' ', '\n', 0 } ** 1;
    @memcpy(padded[2 .. 2 + rendered_text.len], rendered_text);
    const trimmed = string.strim(&padded);
    try std.testing.expectEqualStrings(rendered_text, trimmed);
    try std.testing.expectEqual(trimmed.len, string.strreplace(trimmed, ',', '|'));
    try std.testing.expect(string.sysfs_streq(trimmed, "2|4-7|66-68|70-72\n"));
    try std.testing.expectEqual(@as(?usize, 1), string.memchr_inv(trimmed, '2'));

    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(&replaced, nbits) },
        .{ .key = find_bit.findNextBit(&replaced, nbits, 3) },
        .{ .key = find_bit.findNextBit(&replaced, nbits, 6) },
        .{ .key = find_bit.findNextAndNotBit(&old, &new, nbits, 4) },
        .{ .key = find_bit.findLastBit(&replaced, nbits) },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var order: [5]usize = undefined;
    var count = collect(&root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 4, 6, 70, 72 }, order[0..count]);

    rbtree.erase(&entries[2].node, &root);
    rbtree.eraseInit(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));

    count = collect(&root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 4, 70, 72 }, order[0..count]);

    var reseed = Entry{ .key = find_bit.findNextClump8(&clump, &replaced, nbits, 8) };
    rbtree.add(&reseed.node, &root, less);
    count = collect(&root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 4, 64, 70, 72 }, order[0..count]);
}
