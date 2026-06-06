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

fn cmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn entryKey(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

test "gap-derived bitmap cursors reseed cached rbtree order" {
    const nbits = bits_per_long + 6;
    var source = [_]Word{ 0, 0 };
    var blocked = [_]Word{ 0, 0 };
    var gaps = [_]Word{ 0, 0 };

    bitmap.setRange(&source, 1, 3);
    bitmap.setRange(&source, 9, 1);
    bitmap.setRange(&source, bits_per_long + 1, 2);
    bitmap.setRange(&blocked, 1, 1);
    bitmap.setRange(&blocked, bits_per_long + 2, 1);

    try std.testing.expect(bitmap.andNotBits(&gaps, &source, &blocked, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&gaps, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstAndNotBit(&source, &blocked, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findNextAndNotBit(&source, &blocked, nbits, 3));
    try std.testing.expectEqual(@as(usize, 9), find_bit.findNextAndNotBit(&source, &blocked, nbits, 4));
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextAndNotBit(&source, &blocked, nbits, 10));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&source, &blocked, nbits, bits_per_long + 2));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&clump, &gaps, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0b0000_1100), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &gaps, nbits, 4));
    try std.testing.expectEqual(@as(u8, 0b0000_0010), clump);

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&gaps, nbits, &rendered);
    var expected_rendered: [64]u8 = undefined;
    const expected = try std.fmt.bufPrint(&expected_rendered, "2-3,9,{d}", .{bits_per_long + 1});
    try std.testing.expectEqualStrings(expected, rendered[0..rendered_len]);

    var padded: [64]u8 = @splat(0xaa);
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), string.strscpyPad(&padded, rendered[0..rendered_len]));
    try std.testing.expect(string.strHasPrefix(&padded, "2-3") != 0);
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr(&padded, padded.len, ','));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(padded[rendered_len + 1 ..], 0));

    var entries = [_]Entry{
        .{ .key = bits_per_long + 1, .serial = 0 },
        .{ .key = 9, .serial = 1 },
        .{ .key = 3, .serial = 2 },
        .{ .key = 2, .serial = 3 },
    };
    var duplicate = Entry{ .key = 9, .serial = 4 };
    var reseed = Entry{ .key = 1, .serial = 5 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }
    try std.testing.expectEqual(@as(usize, 2), entryKey(rbtree.firstCached(&root).?));

    const existing = rbtree.findAddCached(&duplicate.node, &root, cmpNode) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 9), entryKey(existing));
    try std.testing.expectEqual(@as(usize, 2), entryKey(rbtree.firstCached(&root).?));

    const promoted = rbtree.eraseCached(&entries[3].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 3), entryKey(promoted));
    try std.testing.expectEqual(@as(usize, 3), entryKey(rbtree.firstCached(&root).?));

    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed.node), rbtree.addCached(&reseed.node, &root, less));
    try std.testing.expectEqual(@as(usize, 1), entryKey(rbtree.firstCached(&root).?));

    const wanted = @as(usize, 9);
    var iter = rbtree.matchIterator(&wanted, &root.root, cmpKey);
    const first_match = iter.next() orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 9), entryKey(first_match));
    try std.testing.expect(iter.next() == null);

    var order: [4]usize = undefined;
    var count: usize = 0;
    var cursor = rbtree.first(&root.root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        order[count] = entryKey(node);
        count += 1;
    }
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 3, 9, bits_per_long + 1 }, order[0..count]);
}
