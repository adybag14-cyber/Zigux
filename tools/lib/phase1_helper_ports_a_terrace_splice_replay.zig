const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

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

fn collectKeys(root: *const rbtree.RootCached, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.firstCached(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "phase1 helper ports A terrace splice replay" {
    const nbits = bits_per_long + 13;
    const tail_noise = @as(Word, 1) << 19;
    const old_map = [_]Word{
        (@as(Word, 1) << 2) | (@as(Word, 1) << 6) | (@as(Word, 1) << 11),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 8) | tail_noise,
    };
    const new_map = [_]Word{
        (@as(Word, 1) << 4) | (@as(Word, 1) << 9) | (@as(Word, 1) << 15),
        (@as(Word, 1) << 3) | (@as(Word, 1) << 10) | tail_noise,
    };
    const splice_mask = [_]Word{
        (@as(Word, 1) << 4) | (@as(Word, 1) << 6) | (@as(Word, 1) << 9),
        (@as(Word, 1) << 3) | (@as(Word, 1) << 8) | (@as(Word, 1) << 10) | tail_noise,
    };

    var terrace = [_]Word{ 0, 0 };
    bitmap.bitmap_replace(&terrace, &old_map, &new_map, &splice_mask, nbits);
    try std.testing.expectEqual(@as(usize, 7), bitmap.bitmap_weight(&terrace, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.find_first_bit(&terrace, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.find_next_bit(&terrace, nbits, 3));
    try std.testing.expectEqual(@as(usize, bits_per_long + 10), find_bit.find_last_bit(&terrace, nbits));

    var overlap = [_]Word{ 0, 0 };
    var gap = [_]Word{ 0, 0 };
    try std.testing.expect(bitmap.bitmap_and(&overlap, &terrace, &splice_mask, nbits));
    try std.testing.expect(bitmap.bitmap_andnot(&gap, &terrace, &splice_mask, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.bitmap_weight(&overlap, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&gap, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.find_first_andnot_bit(&terrace, &splice_mask, nbits));
    try std.testing.expectEqual(@as(usize, 11), find_bit.find_next_andnot_bit(&terrace, &splice_mask, nbits, 3));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_next_clump8(&clump, &terrace, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0b0001_0100), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long + 8), find_bit.find_next_clump8(&clump, &terrace, nbits, bits_per_long + 4));
    try std.testing.expectEqual(@as(u8, 0b0000_0100), clump);

    var rendered: [96]u8 = undefined;
    const rendered_len = bitmap.bitmap_scnprintf(&terrace, nbits, &rendered);
    var expected_storage: [96]u8 = undefined;
    const expected = try std.fmt.bufPrint(
        &expected_storage,
        "2,4,9,11,{d},{d},{d}",
        .{ bits_per_long + 1, bits_per_long + 3, bits_per_long + 10 },
    );
    try std.testing.expectEqualStrings(expected, rendered[0..rendered_len]);

    var decorated: [128]u8 = undefined;
    const decorated_text = try std.fmt.bufPrint(&decorated, "  {s}\n", .{rendered[0..rendered_len]});
    decorated[decorated_text.len] = 0;
    const trimmed = string.strim(decorated[0 .. decorated_text.len + 1]);
    try std.testing.expectEqualStrings(expected, trimmed);
    try std.testing.expectEqual(@as(usize, 1), string.str_has_prefix(trimmed, "2"));
    try std.testing.expect(string.str_ends_with(trimmed, expected[expected.len - 2 .. expected.len]));
    _ = string.strreplace(trimmed, ',', ';');
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(&[_][]const u8{ trimmed, "missing" }, trimmed));
    var sysfs_line: [128]u8 = undefined;
    const sysfs_text = try std.fmt.bufPrint(&sysfs_line, "{s}\n", .{trimmed});
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(&[_][]const u8{ sysfs_text, "other" }, trimmed));

    var entries = [_]Entry{
        .{ .key = find_bit.find_first_bit(&terrace, nbits), .serial = 0 },
        .{ .key = find_bit.find_next_bit(&terrace, nbits, 3), .serial = 1 },
        .{ .key = find_bit.find_next_andnot_bit(&terrace, &splice_mask, nbits, 3), .serial = 2 },
        .{ .key = find_bit.find_last_bit(&terrace, nbits), .serial = 3 },
    };
    var replacement = Entry{ .key = bits_per_long + 4, .serial = 4 };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, less);
    }

    var ordered: [4]usize = undefined;
    try std.testing.expectEqual(@as(usize, 4), collectKeys(&root, &ordered));
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 4, 11, bits_per_long + 10 }, &ordered);

    rbtree.rb_replace_node_cached(&entries[2].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(usize, 4), collectKeys(&root, &ordered));
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 4, bits_per_long + 4, bits_per_long + 10 }, &ordered);
    _ = rbtree.rb_erase_cached(&entries[0].node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&root));

    var postorder_count: usize = 0;
    var post = rbtree.rb_first_postorder(&root.root);
    while (post) |node| : (post = rbtree.rb_next_postorder(node)) {
        postorder_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), postorder_count);
}
