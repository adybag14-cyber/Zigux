const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

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

fn entryKey(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn appendLiteral(buffer: []u8, cursor: *usize, text: []const u8) void {
    std.debug.assert(cursor.* + text.len < buffer.len);
    @memcpy(buffer[cursor.* .. cursor.* + text.len], text);
    cursor.* += text.len;
    buffer[cursor.*] = 0;
}

fn parseCommaSeparatedKeys(text: []const u8, keys: []usize) !usize {
    var count: usize = 0;
    var start: usize = 0;
    while (start < text.len) {
        var end = start;
        while (end < text.len and text[end] != ',') : (end += 1) {}
        keys[count] = try std.fmt.parseUnsigned(usize, text[start..end], 10);
        count += 1;
        start = end + 1;
    }
    return count;
}

test "lane06 sparse stack replay drains and reseeds helper-derived keys" {
    const nbits = bits_per_long * 2 + 5;
    var old = [_]Word{ 0, 0, 0 };
    var new = [_]Word{ 0, 0, 0 };
    var mask = [_]Word{ 0, 0, 0 };
    var selected = [_]Word{ 0, 0, 0 };
    var selected_copy = [_]Word{ 0, 0, 0 };
    var selected_gap = [_]Word{ 0, 0, 0 };

    bitmap.setRange(&old, 2, 3);
    bitmap.setRange(&old, bits_per_long - 2, 4);
    bitmap.setRange(&old, bits_per_long * 2 + 3, 1);

    bitmap.setRange(&new, 4, 2);
    bitmap.setRange(&new, bits_per_long, 1);
    bitmap.setRange(&new, bits_per_long * 2 + 2, 3);

    bitmap.setRange(&mask, 3, 2);
    bitmap.setRange(&mask, bits_per_long - 1, 3);
    bitmap.setRange(&mask, bits_per_long * 2 + 3, 1);

    bitmap.bitmap_replace(&selected, &old, &new, &mask, nbits);
    bitmap.copy(&selected_copy, &selected, nbits);

    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&selected, nbits));
    try std.testing.expect(bitmap.subset(&selected, &selected_copy, nbits));
    try std.testing.expect(bitmap.intersects(&selected, &mask, nbits));
    try std.testing.expect(bitmap.andNotBits(&selected_gap, &selected, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&selected_gap, nbits));

    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&selected, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findNextBit(&selected, nbits, 3));
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextBit(&selected, nbits, bits_per_long - 1));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 3), find_bit.findLastBit(&selected, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextZeroBit(&selected, nbits, bits_per_long));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&clump, &selected, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0b0001_0100), clump);

    var rendered: [96]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&selected, nbits, &rendered);
    const rendered_text = rendered[0..rendered_len];

    var expected: [96]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "2,4,{d},{d},{d}",
        .{ bits_per_long - 2, bits_per_long, bits_per_long * 2 + 3 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered_text);

    var padded = [_]u8{0} ** 128;
    var cursor: usize = 0;
    appendLiteral(&padded, &cursor, "  ");
    appendLiteral(&padded, &cursor, rendered_text);
    appendLiteral(&padded, &cursor, " \n");

    const trimmed = string.strim(&padded);
    try std.testing.expectEqualStrings(rendered_text, trimmed);
    try std.testing.expect(string.strstarts(trimmed, "2"));
    try std.testing.expect(string.strEndsWith(trimmed, expected_text[expected_text.len - 1 ..]));
    try std.testing.expect(string.sysfs_streq(padded[2 .. cursor + 1], rendered_text));

    var keys: [8]usize = undefined;
    const key_count = try parseCommaSeparatedKeys(trimmed, &keys);
    try std.testing.expectEqual(@as(usize, 5), key_count);

    var entries: [8]Entry = undefined;
    for (keys[0..key_count], 0..) |key, idx| {
        entries[idx] = .{ .key = key, .serial = idx };
    }

    var root = rbtree.RootCached.init();
    for (entries[0..key_count]) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    var drained: [8]usize = undefined;
    var drained_count: usize = 0;
    while (rbtree.firstCached(&root)) |node| {
        drained[drained_count] = entryKey(node);
        drained_count += 1;
        rbtree.eraseInitCached(node, &root);
        try std.testing.expect(rbtree.emptyNode(node));
    }
    try std.testing.expectEqualSlices(usize, keys[0..key_count], drained[0..drained_count]);
    try std.testing.expect(root.root.node == null);
    try std.testing.expect(rbtree.firstCached(&root) == null);

    for (entries[0..key_count], 0..) |*entry, idx| {
        entry.key = keys[key_count - 1 - idx] + 1;
        entry.serial = idx;
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(keys[0] + 1, entryKey(rbtree.firstCached(&root).?));
    try std.testing.expectEqual(keys[key_count - 1] + 1, entryKey(rbtree.last(&root.root).?));
    var reverse_cursor = rbtree.last(&root.root);
    var reverse_count: usize = 0;
    while (reverse_cursor) |node| : (reverse_cursor = rbtree.prev(node)) {
        const expected_key = keys[key_count - 1 - reverse_count] + 1;
        try std.testing.expectEqual(expected_key, entryKey(node));
        reverse_count += 1;
    }
    try std.testing.expectEqual(key_count, reverse_count);
}
