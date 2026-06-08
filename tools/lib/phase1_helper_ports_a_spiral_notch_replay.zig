const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const nbits = 96;
const nwords = bitmap.bitsToWords(nbits);

const Entry = struct {
    key: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn entryCmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn keyCmp(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const usize = @ptrCast(@alignCast(key_ptr));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (key.* < entry.key) return -1;
    if (key.* > entry.key) return 1;
    return 0;
}

fn setBits(map: []Word, bits: []const usize) void {
    bitmap.bitmap_zero(map, nbits);
    for (bits) |bit| {
        bitmap.bitmap_set(map, bit, 1);
    }
}

fn collectForward(root: *const rbtree.RootCached, out: []usize) usize {
    var count: usize = 0;
    var current = rbtree.rb_first_cached(root);
    while (current) |node| : (current = rbtree.rb_next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "lane06 spiral notch replay crosses bitmap find-bit string and cached rbtree" {
    var base: [nwords]Word = undefined;
    var notch: [nwords]Word = undefined;
    var patch: [nwords]Word = undefined;
    var merged: [nwords]Word = undefined;
    var residue: [nwords]Word = undefined;
    var copied: [nwords]Word = undefined;

    setBits(&base, &[_]usize{ 1, 4, 9, 16, 33, 48, 65, 80, 93 });
    setBits(&notch, &[_]usize{ 4, 16, 33, 80 });
    setBits(&patch, &[_]usize{ 2, 6, 16, 34, 49, 66, 94 });

    const changed = bitmap.bitmap_andnot(&residue, &base, &notch, nbits);
    try std.testing.expect(changed);
    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(&residue, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&residue, &notch, nbits));

    bitmap.bitmap_or(&merged, &residue, &patch, nbits);
    try std.testing.expectEqual(@as(usize, 12), bitmap.bitmap_weight(&merged, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&patch, &merged, nbits));

    bitmap.bitmap_copy_clear_tail(&copied, &merged, nbits);
    try std.testing.expect(bitmap.bitmap_equal(&copied, &merged, nbits));

    try std.testing.expectEqual(@as(usize, 1), find_bit.find_first_bit(&merged, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.find_next_bit(&merged, nbits, 2));
    try std.testing.expectEqual(@as(usize, 2), find_bit.find_next_andnot_bit(&merged, &base, nbits, 2));
    try std.testing.expectEqual(@as(usize, 94), find_bit.find_last_bit(&merged, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 48), find_bit.find_next_clump8(&clump, &merged, nbits, 48));
    try std.testing.expectEqual(@as(u8, 0b0000_0011), clump);

    var rendered: [96]u8 = undefined;
    const rendered_len = bitmap.bitmap_scnprintf(&merged, nbits, &rendered);
    try std.testing.expectEqualStrings("1-2,6,9,16,34,48-49,65-66,93-94", rendered[0..rendered_len]);

    var padded: [48]u8 = undefined;
    try std.testing.expectEqual(@as(isize, 31), string.strscpyPad(&padded, rendered[0..rendered_len]));
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&padded, "1-2"));
    try std.testing.expect(string.strEndsWith(&padded, "93-94"));
    try std.testing.expectEqual(@as(usize, 31), string.strreplace(&padded, ',', '|'));
    try std.testing.expect(string.sysfsStreq(padded[0..31], "1-2|6|9|16|34|48-49|65-66|93-94\n"));

    var tree = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = find_bit.find_first_bit(&merged, nbits) },
        .{ .key = find_bit.find_next_andnot_bit(&merged, &base, nbits, 2) },
        .{ .key = find_bit.find_next_bit(&merged, nbits, 48) },
        .{ .key = find_bit.find_last_bit(&merged, nbits) },
    };
    var duplicate = Entry{ .key = 48 };
    var replacement = Entry{ .key = 6 };

    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &tree, entryLess);
    }
    try std.testing.expect(rbtree.rb_find_add_cached(&duplicate.node, &tree, entryCmp) != null);
    try std.testing.expect(rbtree.emptyNode(&duplicate.node) == false);

    const lookup_key: usize = 48;
    const found = rbtree.find(&lookup_key, &tree.root, keyCmp) orelse return error.MissingNode;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(usize, 48), found_entry.key);

    rbtree.rb_replace_node_cached(&entries[1].node, &replacement.node, &tree);
    rbtree.clearNode(&entries[1].node);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(usize, 1), @as(*const Entry, @fieldParentPtr("node", rbtree.rb_first_cached(&tree).?)).key);

    _ = rbtree.rb_erase_cached(&entries[0].node, &tree);
    rbtree.clearNode(&entries[0].node);
    try std.testing.expectEqual(@as(usize, 6), @as(*const Entry, @fieldParentPtr("node", rbtree.rb_first_cached(&tree).?)).key);

    var order: [4]usize = undefined;
    const count = collectForward(&tree, &order);
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 6, 48, 94 }, order[0..count]);

    rbtree.rb_erase_init_cached(&replacement.node, &tree);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(usize, 48), @as(*const Entry, @fieldParentPtr("node", rbtree.rb_first_cached(&tree).?)).key);
}
