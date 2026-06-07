const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

const Entry = struct {
    key: usize,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs_node: *const rbtree.Node, rhs_node: *const rbtree.Node) bool {
    const lhs: *const Entry = @fieldParentPtr("node", lhs_node);
    const rhs: *const Entry = @fieldParentPtr("node", rhs_node);
    if (lhs.key != rhs.key) {
        return lhs.key < rhs.key;
    }
    return lhs.serial < rhs.serial;
}

fn setBits(map: []Word, bits: []const usize) void {
    for (bits) |bit| {
        bitmap.setRange(map, bit, 1);
    }
}

fn collectForward(root: *const rbtree.RootCached, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.first(&root.root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "phase1 helper ports A wavefront cascade replay" {
    const nbits = bitmap.bits_per_long + 24;
    var front = [_]Word{ 0, 0 };
    var back = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };
    var merged = [_]Word{ 0, 0 };
    var wave = [_]Word{ 0, 0 };
    var carved = [_]Word{ 0, 0 };

    setBits(&front, &[_]usize{ 1, 4, 9, bitmap.bits_per_long + 2, bitmap.bits_per_long + 7 });
    setBits(&back, &[_]usize{ 4, 10, bitmap.bits_per_long + 2, bitmap.bits_per_long + 11, bitmap.bits_per_long + 20 });
    setBits(&mask, &[_]usize{ 4, 9, 10, bitmap.bits_per_long + 2, bitmap.bits_per_long + 7, bitmap.bits_per_long + 11 });

    try std.testing.expectEqual(@as(usize, 8), bitmap.weightedOr(&merged, &front, &back, nbits));
    try std.testing.expect(bitmap.andBits(&wave, &merged, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&wave, nbits));
    var front_only = [_]Word{ 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&front_only, &front, &back, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&front_only, nbits));
    try std.testing.expect(bitmap.andNotBits(&carved, &wave, &front, nbits));

    try std.testing.expectEqual(@as(usize, 4), find_bit.findFirstAndBit(&merged, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 10), find_bit.findNextAndNotBit(&wave, &front, nbits, 5));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 11), find_bit.findNextBit(&carved, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 11), find_bit.findLastBit(&carved, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &wave, nbits, 8));
    try std.testing.expectEqual(@as(u8, 0b0000_0110), clump);

    var rendered: [96]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&wave, nbits, &rendered);
    const rendered_text = rendered[0..rendered_len];
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(rendered_text, "1"));
    try std.testing.expect(string.strEndsWith(rendered_text, "75"));
    try std.testing.expectEqual(@as(?usize, 0), string.strnchr(rendered_text, rendered_text.len, '4'));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv("zzzz", 'z'));

    var trim_buf = [_]u8{ ' ', 'w', 'a', 'v', 'e', ':', '4', ',', '1', '0', ' ', 0 };
    const trimmed = string.strim(trim_buf[0..]);
    try std.testing.expectEqualStrings("wave:4,10", trimmed);
    _ = string.strreplace(trimmed, ',', '|');
    try std.testing.expectEqualStrings("wave:4|10", trimmed);

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = 4, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = bitmap.bits_per_long + 2, .serial = 2 },
        .{ .key = bitmap.bits_per_long + 11, .serial = 3 },
    };
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    _ = rbtree.eraseCached(&entries[0].node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));

    var order: [4]usize = undefined;
    const count = collectForward(&root, &order);
    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ bitmap.bits_per_long + 2, bitmap.bits_per_long + 11 }, order[0..count]);
}
