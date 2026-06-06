const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Entry = struct {
    key: usize,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn collectKeys(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.first(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "phase1 ports A plain erase and eraseInit nodes can be reinserted" {
    const nbits = find_bit.bits_per_long + 9;
    var src = [_]bitmap.Word{ 0, 0 };
    var mask = [_]bitmap.Word{ 0, 0 };
    var selected = [_]bitmap.Word{ 0, 0 };

    bitmap.setRange(&src, 3, 3);
    bitmap.setRange(&src, 9, 1);
    bitmap.setRange(&src, find_bit.bits_per_long + 2, 1);
    bitmap.setRange(&src, find_bit.bits_per_long + 6, 1);
    src[1] |= @as(bitmap.Word, 1) << 14;

    bitmap.setRange(&mask, 4, 1);
    bitmap.setRange(&mask, find_bit.bits_per_long + 2, 1);
    try std.testing.expect(bitmap.andNotBits(&selected, &src, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&selected, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstBit(&selected, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextAndNotBit(&src, &mask, nbits, 4));
    try std.testing.expectEqual(find_bit.bits_per_long + 6, find_bit.findLastBit(&selected, nbits));

    var rendered: [48]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&selected, nbits, &rendered);
    const rendered_text = rendered[0..rendered_len];
    try std.testing.expect(string.memchrInv(rendered_text, ' ') != null);

    var padded: [64]u8 = undefined;
    const copied = string.strscpyPad(&padded, rendered_text);
    try std.testing.expect(copied > 0);
    const copied_len: usize = @intCast(copied);
    const prefix_len = @min(2, rendered_text.len);
    try std.testing.expectEqual(prefix_len, string.strHasPrefix(padded[0..], rendered_text[0..prefix_len]));
    try std.testing.expect(std.mem.eql(u8, rendered_text, padded[0..copied_len]));

    var entries = [_]Entry{
        .{ .key = 3, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 9, .serial = 2 },
        .{ .key = find_bit.bits_per_long + 6, .serial = 3 },
        .{ .key = 5, .serial = 4 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var order: [5]usize = undefined;
    var count = collectKeys(&root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 3, 5, 5, 9, find_bit.bits_per_long + 6 }, order[0..count]);

    rbtree.erase(&entries[2].node, &root);
    count = collectKeys(&root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 3, 5, 5, find_bit.bits_per_long + 6 }, order[0..count]);

    rbtree.eraseInit(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    count = collectKeys(&root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 3, 5, find_bit.bits_per_long + 6 }, order[0..count]);

    entries[1].key = find_bit.bits_per_long + 7;
    entries[1].serial = 5;
    rbtree.add(&entries[1].node, &root, less);
    count = collectKeys(&root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 3, 5, find_bit.bits_per_long + 6, find_bit.bits_per_long + 7 }, order[0..count]);
}
