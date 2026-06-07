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

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
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

fn appendKey(keys: *[16]usize, count: *usize, key: usize) void {
    if (count.* == 0 or keys.*[count.* - 1] != key) {
        keys.*[count.*] = key;
        count.* += 1;
    }
}

fn drainOrder(root: *const rbtree.RootCached, out: *[16]usize) usize {
    var count: usize = 0;
    var cursor = rbtree.firstCached(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "carry-chain replay keeps bitmap find string and rbtree helpers aligned" {
    const nbits = bitmap.bits_per_long + 12;
    var base = [_]Word{ 0, 0 };
    var carry = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };
    var merged = [_]Word{ 0, 0 };
    var gaps = [_]Word{ 0, 0 };

    bitmap.bitmap_set(&base, bitmap.bits_per_long - 4, 9);
    bitmap.bitmap_set(&base, bitmap.bits_per_long + 9, 1);
    bitmap.bitmap_set(&carry, bitmap.bits_per_long - 1, 5);
    bitmap.bitmap_set(&carry, bitmap.bits_per_long + 6, 3);
    bitmap.bitmap_set(&mask, bitmap.bits_per_long - 2, 7);

    _ = bitmap.bitmap_weighted_or(&merged, &base, &carry, nbits);
    try std.testing.expectEqual(@as(usize, 13), bitmap.bitmap_weight(&merged, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&merged, &mask, nbits));

    try std.testing.expect(bitmap.bitmap_andnot(&gaps, &merged, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 6), bitmap.bitmap_weight(&gaps, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&gaps, &merged, nbits));
    try std.testing.expect(!bitmap.bitmap_subset(&merged, &gaps, nbits));

    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long - 4), find_bit.find_first_bit(&merged, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long - 4), find_bit.find_first_andnot_bit(&merged, &mask, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 6), find_bit.find_next_andnot_bit(&merged, &mask, nbits, bitmap.bits_per_long - 2));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 9), find_bit.find_last_bit(&merged, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 10), find_bit.find_next_zero_bit(&merged, nbits, bitmap.bits_per_long + 9));

    var clump: u8 = 0;
    const clump_start = find_bit.find_next_clump8(&clump, &merged, nbits, bitmap.bits_per_long - 4);
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long - 8), clump_start);
    try std.testing.expectEqual(@as(u8, 0xf0), clump);

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.bitmap_scnprintf(&merged, nbits, &rendered);
    try std.testing.expectEqualStrings("60-68,70-73", rendered[0..rendered_len]);

    var label = [_]u8{ ' ', 'c', 'a', 'r', 'r', 'y', ':', '6', '0', '-', '6', '8', ',', '7', '0', '-', '7', '3', ' ', '\n', 0, 'x' };
    const trimmed = string.strim(label[0..]);
    _ = string.strreplace(trimmed, ',', '|');
    try std.testing.expect(string.strstarts(trimmed, "carry:"));
    try std.testing.expect(string.strEndsWith(trimmed, "70-73"));
    try std.testing.expect(string.sysfs_streq("carry:60-68|70-73\n", trimmed));

    const targets = [_]usize{
        find_bit.find_first_bit(&merged, nbits),
        find_bit.find_next_bit(&merged, nbits, bitmap.bits_per_long),
        find_bit.find_next_andnot_bit(&merged, &mask, nbits, bitmap.bits_per_long - 2),
        find_bit.find_last_bit(&merged, nbits),
    };

    var keys: [16]usize = undefined;
    var key_count: usize = 0;
    for (targets) |target| {
        appendKey(&keys, &key_count, target);
    }
    try std.testing.expectEqualSlices(usize, &[_]usize{ 60, 64, 70, 73 }, keys[0..key_count]);

    var entries: [4]Entry = undefined;
    var tree = rbtree.RootCached.init();
    for (keys[0..key_count], 0..) |key, idx| {
        entries[idx] = .{ .key = key, .serial = idx };
        _ = rbtree.rb_add_cached(&entries[idx].node, &tree, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_first_cached(&tree));

    const lookup_key = @as(usize, 70);
    const found = rbtree.find(&lookup_key, &tree.root, keyCmp) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(usize, 70), found_entry.key);

    var order: [16]usize = undefined;
    try std.testing.expectEqualSlices(usize, keys[0..key_count], order[0..drainOrder(&tree, &order)]);

    rbtree.rb_erase_init_cached(&entries[0].node, &tree);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&tree));

    const promoted = rbtree.rb_erase_cached(&entries[1].node, &tree) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[2].node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.rb_first_cached(&tree));

    try std.testing.expectEqualSlices(usize, &[_]usize{ 70, 73 }, order[0..drainOrder(&tree, &order)]);
}
