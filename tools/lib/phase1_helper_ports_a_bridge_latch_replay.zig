const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

fn setBit(map: []Word, bit: usize) void {
    bitmap.bitmap_set(map, bit, 1);
}

fn keyOf(node: ?*const rbtree.Node) ?u16 {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return entry.key;
}

const Entry = struct {
    key: u16,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

test "phase1 helper ports A bridge latch replay" {
    const nbits = find_bit.bits_per_long * 2 + 11;

    var old = [_]Word{0}**3;
    var new = [_]Word{0}**3;
    var mask = [_]Word{0}**3;
    var merged = [_]Word{0}**3;
    var latch = [_]Word{0}**3;
    var bridge = [_]Word{0}**3;
    var gaps = [_]Word{0}**3;

    inline for (.{ 4, 9, find_bit.bits_per_long + 2, find_bit.bits_per_long + 14, find_bit.bits_per_long * 2 - 2 }) |bit| {
        setBit(&old, bit);
    }
    inline for (.{ 1, 9, find_bit.bits_per_long + 6, find_bit.bits_per_long + 25, find_bit.bits_per_long * 2 + 1 }) |bit| {
        setBit(&new, bit);
    }
    bitmap.bitmap_set(&mask, 0, 16);
    bitmap.bitmap_set(&mask, find_bit.bits_per_long, 32);

    bitmap.bitmap_replace(&merged, &old, &new, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(&merged, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.find_first_bit(&merged, nbits));
    try std.testing.expectEqual(@as(usize, 9), find_bit.find_next_bit(&merged, nbits, 2));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 6), find_bit.find_next_bit(&merged, nbits, 10));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long * 2 - 2), find_bit.find_last_bit(&merged, nbits));

    inline for (.{ 1, find_bit.bits_per_long + 6, find_bit.bits_per_long * 2 - 2 }) |bit| {
        setBit(&latch, bit);
    }
    try std.testing.expect(bitmap.bitmap_and(&bridge, &merged, &latch, nbits));
    try std.testing.expect(bitmap.bitmap_andnot(&gaps, &merged, &latch, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&bridge, &merged, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&bridge, &gaps, nbits) == false);
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&bridge, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&gaps, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.find_first_and_bit(&merged, &latch, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 6), find_bit.find_next_and_bit(&merged, &latch, nbits, 2));
    try std.testing.expectEqual(@as(usize, 9), find_bit.find_first_andnot_bit(&merged, &latch, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_next_clump8(&clump, &merged, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x40), clump);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 24), find_bit.find_next_clump8(&clump, &merged, nbits, find_bit.bits_per_long + 7));
    try std.testing.expectEqual(@as(u8, 0x02), clump);

    var range_buffer = [_]u8{0}**48;
    const rendered_len = bitmap.bitmap_scnprintf(&merged, nbits, &range_buffer);
    try std.testing.expectEqualSlices(u8, "1,9,70,89,126", range_buffer[0..rendered_len]);

    var label_storage = [_]u8{0}**64;
    const raw_label = try std.fmt.bufPrint(&label_storage, "  bridge:{s}\n", .{range_buffer[0..rendered_len]});
    var label = [_]u8{0}**64;
    @memcpy(label[0..raw_label.len], raw_label);
    const trimmed = string.strim(&label);
    try std.testing.expectEqualSlices(u8, "bridge:1,9,70,89,126", trimmed);
    try std.testing.expectEqual(trimmed.len, string.strreplace(trimmed, ':', '='));
    try std.testing.expectEqual(@as(usize, 7), string.str_has_prefix(trimmed, "bridge="));
    try std.testing.expect(string.str_ends_with(trimmed, "126"));

    const exact_matches = [_][]const u8{
        "bridge=1,9,70,89,126",
        "bridge=1,9,70,89,127",
    };
    const newline_matches = [_][]const u8{
        "skip",
        "bridge=1,9,70,89,126\n",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(&exact_matches, trimmed));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&newline_matches, trimmed));

    var padded = [_]u8{0xaa}**24;
    try std.testing.expectEqual(@as(isize, 6), string.strscpy_pad(&padded, "bridge"));
    try std.testing.expectEqual(@as(?usize, null), string.memchr_inv(padded[7..], 0));
    try std.testing.expectEqual(@as(?usize, 0), string.memchr_inv(padded[0..7], 0));

    var entries = [_]Entry{
        .{ .key = @intCast(find_bit.find_first_bit(&merged, nbits)) },
        .{ .key = @intCast(find_bit.find_first_andnot_bit(&merged, &latch, nbits)) },
        .{ .key = @intCast(find_bit.find_first_and_bit(&merged, &latch, nbits)) },
        .{ .key = @intCast(find_bit.find_last_bit(&merged, nbits)) },
    };
    var replacement = Entry{ .key = entries[0].key };
    var new_leftmost = Entry{ .key = 0 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_add_cached(&entries[0].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[1].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[2].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[3].node, &root, less));
    try std.testing.expectEqual(@as(?u16, entries[0].key), keyOf(rbtree.rb_first_cached(&root)));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_erase_cached(&entries[2].node, &root));
    try std.testing.expectEqual(@as(?u16, entries[0].key), keyOf(rbtree.rb_first_cached(&root)));

    rbtree.rb_replace_node_cached(&entries[0].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?u16, replacement.key), keyOf(rbtree.rb_first_cached(&root)));

    try std.testing.expectEqual(@as(?*rbtree.Node, &new_leftmost.node), rbtree.rb_add_cached(&new_leftmost.node, &root, less));
    try std.testing.expectEqual(@as(?u16, new_leftmost.key), keyOf(rbtree.rb_first_cached(&root)));
    rbtree.rb_erase_init_cached(&new_leftmost.node, &root);
    try std.testing.expect(rbtree.emptyNode(&new_leftmost.node));
    try std.testing.expectEqual(@as(?u16, replacement.key), keyOf(rbtree.rb_first_cached(&root)));
}
