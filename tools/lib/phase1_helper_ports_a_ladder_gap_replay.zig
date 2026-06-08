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

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn nodeKey(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

test "phase1 helper ports A ladder gap replay" {
    const nbits = bits_per_long + 19;

    var base = [_]Word{ 0, 0 };
    var fill = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };
    var merged = [_]Word{ 0, 0 };
    var old_only = [_]Word{ 0, 0 };

    bitmap.bitmap_set(&base, 2, 4);
    bitmap.bitmap_set(&base, bits_per_long - 1, 3);
    bitmap.bitmap_set(&base, bits_per_long + 11, 2);

    bitmap.bitmap_set(&fill, 4, 6);
    bitmap.bitmap_set(&fill, bits_per_long + 2, 4);
    bitmap.bitmap_set(&fill, bits_per_long + 16, 2);

    bitmap.bitmap_set(&mask, 4, 3);
    bitmap.bitmap_set(&mask, bits_per_long + 2, 2);
    bitmap.bitmap_set(&mask, bits_per_long + 16, 2);

    bitmap.bitmap_replace(&merged, &base, &fill, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 14), bitmap.bitmap_weight(&merged, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&merged, &fill, nbits));
    try std.testing.expect(!bitmap.bitmap_subset(&fill, &merged, nbits));
    try std.testing.expect(!bitmap.bitmap_andnot(&old_only, &base, &merged, nbits));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weight(&old_only, nbits));

    try std.testing.expectEqual(@as(usize, 2), find_bit.find_first_bit(&merged, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.find_next_bit(&merged, nbits, 3));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.find_next_andnot_bit(&merged, &base, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 17), find_bit.find_last_bit(&merged, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_clump8(&clump, &merged, nbits));
    try std.testing.expectEqual(@as(u8, 0b0111_1100), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long + 16), find_bit.find_next_clump8(&clump, &merged, nbits, bits_per_long + 14));
    try std.testing.expectEqual(@as(u8, 0b0000_0011), clump);

    var rendered: [96]u8 = undefined;
    const rendered_len = bitmap.bitmap_scnprintf(&merged, nbits, &rendered);
    try std.testing.expectEqualStrings("2-6,63-67,75-76,80-81", rendered[0..rendered_len]);

    var padded: [40]u8 = @splat(0xaa);
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), string.strscpy_pad(&padded, rendered[0..rendered_len]));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix(&padded, "2-6"));
    try std.testing.expect(string.strEndsWith(&padded, "80-81"));
    const tokens = [_][]const u8{ "2-6", "63-67", "75-76", "80-81" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(tokens[0..], "63-67"));
    try std.testing.expectEqual(@as(?usize, null), string.memchr_inv(padded[rendered_len + 1 ..], 0));

    var entries = [_]Entry{
        .{ .key = find_bit.find_first_bit(&merged, nbits) },
        .{ .key = find_bit.find_next_bit(&merged, nbits, 4) },
        .{ .key = find_bit.find_next_andnot_bit(&merged, &base, nbits, bits_per_long) },
        .{ .key = find_bit.find_last_bit(&merged, nbits) },
    };
    var replacement = Entry{ .key = entries[0].key };
    var reseed = Entry{ .key = 1 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.last(&root.root));

    const lookup_key = entries[2].key;
    const found = rbtree.find(&lookup_key, &root.root, keyCmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(entries[2].key, nodeKey(found));

    rbtree.replaceNodeCached(&entries[0].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    _ = rbtree.addCached(&reseed.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed.node), rbtree.firstCached(&root));

    var order: [4]usize = undefined;
    var count: usize = 0;
    var cursor = rbtree.first(&root.root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        order[count] = nodeKey(node);
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, entries[1].key, entries[2].key, entries[3].key }, order[0..count]);
}
