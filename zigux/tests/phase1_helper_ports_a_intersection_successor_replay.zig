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

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
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

test "phase1 helper ports A intersection cursors feed token cleanup and cached successor erase" {
    const nbits = bitmap.bits_per_long + 13;
    var lhs = [_]Word{ 0, 0 };
    var rhs = [_]Word{ 0, 0 };

    bitmap.bitmap_set(&lhs, 3, 4);
    bitmap.bitmap_set(&lhs, bitmap.bits_per_long - 1, 3);
    bitmap.bitmap_set(&lhs, bitmap.bits_per_long + 9, 1);
    bitmap.bitmap_set(&rhs, 5, 1);
    bitmap.bitmap_set(&rhs, bitmap.bits_per_long, 2);
    bitmap.bitmap_set(&rhs, bitmap.bits_per_long + 9, 4);

    var both = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    try std.testing.expect(bitmap.bitmap_and(&both, &lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.bitmap_weight(&both, nbits));

    try std.testing.expectEqual(@as(usize, 5), find_bit.findFirstAndBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long), find_bit.findNextAndBit(&lhs, &rhs, nbits, 6));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 1), find_bit.findNextAndBit(&lhs, &rhs, nbits, bitmap.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 9), find_bit.findNextAndBit(&lhs, &rhs, nbits, bitmap.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&lhs, &rhs, nbits, bitmap.bits_per_long + 10));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&clump, &both, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0b0010_0000), clump);
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long), find_bit.findNextClump8(&clump, &both, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_0011), clump);
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 8), find_bit.findNextClump8(&clump, &both, nbits, bitmap.bits_per_long + 2));
    try std.testing.expectEqual(@as(u8, 0b0000_0010), clump);

    var rendered: [64]u8 = @splat(0xaa);
    const rendered_len = bitmap.bitmap_scnprintf(&both, nbits, &rendered);
    var expected: [48]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(&expected, "5,{d}-{d},{d}", .{
        bitmap.bits_per_long,
        bitmap.bits_per_long + 1,
        bitmap.bits_per_long + 9,
    });
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);

    var token_buf: [80]u8 = @splat(0);
    const written = try std.fmt.bufPrint(&token_buf, "  {s},tail  ", .{rendered[0..rendered_len]});
    token_buf[written.len] = 0;
    const trimmed = string.strim(token_buf[0 .. written.len + 1]);
    try std.testing.expect(string.strstarts(trimmed, "5"));
    try std.testing.expect(string.strEndsWith(trimmed, "tail"));

    const first_comma = string.strnchr(trimmed, trimmed.len, ',') orelse return error.TestUnexpectedResult;
    const second_comma = first_comma + 1 + (string.strnchr(trimmed[first_comma + 1 ..], trimmed.len - first_comma - 1, ',') orelse return error.TestUnexpectedResult);
    const third_comma = second_comma + 1 + (string.strnchr(trimmed[second_comma + 1 ..], trimmed.len - second_comma - 1, ',') orelse return error.TestUnexpectedResult);
    try std.testing.expectEqualStrings("5", trimmed[0..first_comma]);
    try std.testing.expectEqualStrings(expected_text[2 .. expected_text.len - 3], trimmed[first_comma + 1 .. second_comma]);
    try std.testing.expectEqualStrings(expected_text[expected_text.len - 2 .. expected_text.len], trimmed[second_comma + 1 .. third_comma]);
    try std.testing.expectEqualStrings("tail", trimmed[third_comma + 1 ..]);

    var entries = [_]Entry{
        .{ .key = 5, .serial = 0 },
        .{ .key = bitmap.bits_per_long, .serial = 1 },
        .{ .key = bitmap.bits_per_long + 1, .serial = 2 },
        .{ .key = bitmap.bits_per_long + 9, .serial = 3 },
    };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, entryLess);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    const successor = rbtree.rb_erase_cached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[1].node), successor);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    const duplicate_key = entries[2].key;
    const found = rbtree.find(&duplicate_key, &root.root, keyCmp) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(entries[2].key, found_entry.key);

    rbtree.rb_erase_init_cached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.firstCached(&root));

    var remaining: [3]usize = undefined;
    const count = collectKeys(&root.root, &remaining);
    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ bitmap.bits_per_long + 1, bitmap.bits_per_long + 9 }, remaining[0..count]);
}
