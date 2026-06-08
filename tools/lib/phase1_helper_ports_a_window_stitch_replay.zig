const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn entryKey(node: *const rbtree.Node) i32 {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

test "phase1 helper ports A window stitch replay" {
    const nbits = bits_per_long * 2 + 9;

    var left = [_]Word{ 0, 0, 0 };
    var right = [_]Word{ 0, 0, 0 };
    var stitch_mask = [_]Word{ 0, 0, 0 };

    bitmap.setRange(&left, bits_per_long - 3, 5);
    bitmap.setRange(&left, bits_per_long + 12, 4);
    bitmap.setRange(&right, 4, 3);
    bitmap.setRange(&right, bits_per_long + 1, 2);
    bitmap.setRange(&right, bits_per_long * 2 + 4, 2);

    bitmap.setRange(&stitch_mask, bits_per_long - 1, 4);
    bitmap.setRange(&stitch_mask, bits_per_long * 2 + 4, 2);

    var stitched = [_]Word{ 0, 0, 0 };
    bitmap.bitmap_replace(&stitched, &left, &right, &stitch_mask, nbits);

    var left_only = [_]Word{ 0, 0, 0 };
    var right_only = [_]Word{ 0, 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&left_only, &left, &stitched, nbits));
    try std.testing.expect(bitmap.andBits(&right_only, &right, &stitched, nbits));

    try std.testing.expectEqual(@as(usize, bits_per_long - 3), find_bit.findFirstBit(&stitched, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long - 2), find_bit.findNextBit(&stitched, nbits, bits_per_long - 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextAndBit(&right, &stitched, nbits, bits_per_long - 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 12), find_bit.findNextAndNotBit(&left, &stitch_mask, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 5), find_bit.findLastBit(&stitched, nbits));

    var clump: u8 = 0;
    const clump_at = find_bit.findNextClump8(&clump, &stitched, nbits, bits_per_long - 3);
    try std.testing.expectEqual(@as(usize, bits_per_long - 8), clump_at);
    try std.testing.expectEqual(@as(u8, 0b0110_0000), clump & 0b1111_0000);

    var rendered: [96]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&stitched, nbits, &rendered);
    const ranges = rendered[0..rendered_len];
    try std.testing.expectEqualStrings("61-62,65-66,76-79,132-133", ranges);
    try std.testing.expect(string.strEndsWith(ranges, "132-133"));

    var label = [_]u8{ ' ', 'w', 'i', 'n', 'd', 'o', 'w', '-', 's', 't', 'i', 't', 'c', 'h', ' ', 0, 'x' };
    const trimmed = string.strim(label[0..]);
    try std.testing.expectEqualStrings("window-stitch", trimmed);
    try std.testing.expect(string.strstarts(trimmed, "window"));
    try std.testing.expect(string.strEndsWith(trimmed, "stitch"));
    try std.testing.expectEqual(@as(usize, 13), string.strreplace(trimmed, '-', '_'));
    try std.testing.expectEqualStrings("window_stitch", trimmed);

    var copied = [_]u8{0} ** 20;
    try std.testing.expectEqual(@as(isize, 13), string.strscpyPad(copied[0..], trimmed));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'w', 'i', 'n', 'd', 'o', 'w', '_', 's', 't', 'i', 't', 'c', 'h', 0, 0 }, copied[0..15]);

    var entries = [_]Entry{
        .{ .key = @intCast(find_bit.findFirstBit(&stitched, nbits)) },
        .{ .key = @intCast(find_bit.findNextAndBit(&right, &stitched, nbits, 0)) },
        .{ .key = @intCast(find_bit.findNextAndNotBit(&left, &stitch_mask, nbits, bits_per_long)) },
        .{ .key = @intCast(find_bit.findLastBit(&stitched, nbits)) },
    };
    var replacement = Entry{ .key = entries[1].key + 1 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, entryLess);
    }
    try std.testing.expectEqual(entries[0].key, entryKey(rbtree.firstCached(&root).?));

    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);

    var order: [4]i32 = undefined;
    var count: usize = 0;
    var cursor = rbtree.first(&root.root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        order[count] = entryKey(node);
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ entries[0].key, replacement.key, entries[2].key, entries[3].key }, order[0..count]);

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(replacement.key, entryKey(rbtree.firstCached(&root).?));
}
