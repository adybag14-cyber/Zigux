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

test "phase1 helper ports A cross span replay" {
    const nbits = bits_per_long * 2 + 12;

    var base = [_]Word{ 0, 0, 0 };
    var patch = [_]Word{ 0, 0, 0 };
    var mask = [_]Word{ 0, 0, 0 };

    bitmap.setRange(&base, 2, 3);
    bitmap.setRange(&base, bits_per_long - 2, 4);
    bitmap.setRange(&base, bits_per_long + 9, 4);
    bitmap.setRange(&base, bits_per_long * 2 + 3, 3);

    bitmap.setRange(&patch, 6, 3);
    bitmap.setRange(&patch, bits_per_long, 3);
    bitmap.setRange(&patch, bits_per_long + 12, 2);
    bitmap.setRange(&patch, bits_per_long * 2 + 7, 3);

    bitmap.setRange(&mask, 4, 5);
    bitmap.setRange(&mask, bits_per_long - 1, 4);
    bitmap.setRange(&mask, bits_per_long + 12, 2);
    bitmap.setRange(&mask, bits_per_long * 2 + 7, 3);

    var crossed = [_]Word{ 0, 0, 0 };
    bitmap.bitmap_replace(&crossed, &base, &patch, &mask, nbits);

    var patch_kept = [_]Word{ 0, 0, 0 };
    var base_kept = [_]Word{ 0, 0, 0 };
    try std.testing.expect(bitmap.andBits(&patch_kept, &patch, &crossed, nbits));
    try std.testing.expect(bitmap.andNotBits(&base_kept, &base, &mask, nbits));
    try std.testing.expect(bitmap.subset(&base_kept, &crossed, nbits));

    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&crossed, nbits));
    try std.testing.expectEqual(@as(usize, 6), find_bit.findNextBit(&crossed, nbits, 4));
    try std.testing.expectEqual(@as(usize, 6), find_bit.findNextAndBit(&patch, &crossed, nbits, 0));
    try std.testing.expectEqual(@as(usize, bits_per_long - 2), find_bit.findNextAndNotBit(&base, &mask, nbits, bits_per_long - 3));
    try std.testing.expectEqual(@as(usize, bits_per_long + 9), find_bit.findNextAndNotBit(&base, &mask, nbits, bits_per_long - 1));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 9), find_bit.findLastBit(&crossed, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&clump, &crossed, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0b1100_1100), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long - 8), find_bit.findNextClump8(&clump, &crossed, nbits, bits_per_long - 3));
    try std.testing.expectEqual(@as(u8, 0b0100_0000), clump);

    var rendered: [128]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&crossed, nbits, &rendered);
    const ranges = rendered[0..rendered_len];
    try std.testing.expectEqualStrings("2-3,6-8,62,64-66,73-77,131-133,135-137", ranges);
    try std.testing.expect(string.strstarts(ranges, "2-3"));
    try std.testing.expect(string.strEndsWith(ranges, "135-137"));

    var label = [_]u8{ ' ', 'c', 'r', 'o', 's', 's', '-', 's', 'p', 'a', 'n', ' ', 0, 'x' };
    const trimmed = string.strim(label[0..]);
    try std.testing.expectEqualStrings("cross-span", trimmed);
    try std.testing.expectEqual(@as(usize, 5), string.strHasPrefix(trimmed, "cross"));
    try std.testing.expect(string.strEndsWith(trimmed, "span"));
    try std.testing.expectEqual(@as(usize, 10), string.strreplace(trimmed, '-', '_'));
    try std.testing.expectEqualStrings("cross_span", trimmed);

    var copied = [_]u8{0xaa} ** 16;
    try std.testing.expectEqual(@as(isize, 10), string.strscpyPad(copied[0..], trimmed));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'c', 'r', 'o', 's', 's', '_', 's', 'p', 'a', 'n', 0, 0, 0 }, copied[0..13]);

    var entries = [_]Entry{
        .{ .key = @intCast(find_bit.findFirstBit(&crossed, nbits)) },
        .{ .key = @intCast(find_bit.findNextAndBit(&patch, &crossed, nbits, 0)) },
        .{ .key = @intCast(find_bit.findNextAndNotBit(&base, &mask, nbits, bits_per_long - 3)) },
        .{ .key = @intCast(find_bit.findLastBit(&crossed, nbits)) },
    };
    var replacement = Entry{ .key = @intCast(find_bit.findNextAndNotBit(&base, &mask, nbits, bits_per_long - 1)) };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, entryLess);
    }

    try std.testing.expectEqual(entries[0].key, entryKey(rbtree.firstCached(&root).?));
    rbtree.replaceNodeCached(&entries[2].node, &replacement.node, &root);

    var order: [4]i32 = undefined;
    var count: usize = 0;
    var cursor = rbtree.first(&root.root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        order[count] = entryKey(node);
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ entries[0].key, entries[1].key, replacement.key, entries[3].key }, order[0..count]);

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(entries[1].key, entryKey(rbtree.firstCached(&root).?));

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(replacement.key, entryKey(rbtree.firstCached(&root).?));
}
