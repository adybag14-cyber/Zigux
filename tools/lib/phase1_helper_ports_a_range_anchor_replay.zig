const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

const Entry = struct {
    key: u16,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn keyOf(node: ?*const rbtree.Node) ?u16 {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return entry.key;
}

fn serialOf(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.serial;
}

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
    const wanted: *const u16 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "phase1 helper ports A range anchor replay" {
    const nbits = find_bit.bits_per_long * 2 + 13;
    const count = find_bit.bits_per_long + 10;

    var source = [_]Word{0} ** 3;
    var extended = [_]Word{0xaa55} ** 3;
    var complement = [_]Word{0} ** 3;
    var partner = [_]Word{0} ** 3;
    var weighted_or = [_]Word{0} ** 3;
    var weighted_xor = [_]Word{0} ** 3;
    var shared = [_]Word{0} ** 3;
    var remainder = [_]Word{0} ** 3;

    bitmap.bitmap_set(&source, 2, 4);
    bitmap.bitmap_set(&source, find_bit.bits_per_long - 1, 3);
    bitmap.bitmap_set(&source, find_bit.bits_per_long + 8, 2);
    bitmap.bitmap_set(&source, find_bit.bits_per_long * 2 + 5, 2);

    bitmap.bitmap_copy_and_extend(&extended, &source, count, nbits);
    try std.testing.expectEqual(@as(usize, 9), bitmap.bitmap_weight(&extended, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.find_first_bit(&extended, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long - 1), find_bit.find_next_bit(&extended, nbits, 6));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 8), find_bit.find_next_bit(&extended, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 9), find_bit.find_last_bit(&extended, nbits));

    bitmap.bitmap_complement(&complement, &extended, nbits);
    try std.testing.expectEqual(nbits - 9, bitmap.bitmap_weight(&complement, nbits));
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_bit(&complement, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long * 2 + 12), find_bit.find_last_bit(&complement, nbits));

    bitmap.bitmap_set(&partner, 3, 1);
    bitmap.bitmap_set(&partner, find_bit.bits_per_long + 1, 1);
    bitmap.bitmap_set(&partner, find_bit.bits_per_long + 8, 1);
    bitmap.bitmap_set(&partner, find_bit.bits_per_long * 2 + 10, 1);

    try std.testing.expectEqual(@as(usize, 10), bitmap.bitmap_weighted_or(&weighted_or, &extended, &partner, nbits));
    try std.testing.expectEqual(@as(usize, 7), bitmap.bitmap_weighted_xor(&weighted_xor, &extended, &partner, nbits));
    try std.testing.expect(bitmap.bitmap_and(&shared, &extended, &partner, nbits));
    try std.testing.expect(bitmap.bitmap_andnot(&remainder, &extended, &partner, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&shared, &extended, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&shared, &remainder, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&shared, nbits));
    try std.testing.expectEqual(@as(usize, 6), bitmap.bitmap_weight(&remainder, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.find_first_and_bit(&extended, &partner, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.find_first_andnot_bit(&extended, &partner, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.find_next_andnot_bit(&extended, &partner, nbits, 3));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long * 2 + 10), find_bit.find_last_bit(&weighted_or, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_next_clump8(&clump, &extended, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x03), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 8), find_bit.find_next_clump8(&clump, &extended, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(u8, 0x03), clump);

    var rendered = [_]u8{0} ** 48;
    const rendered_len = bitmap.bitmap_scnprintf(&extended, nbits, &rendered);
    try std.testing.expectEqualSlices(u8, "2-5,63-65,72-73", rendered[0..rendered_len]);

    var label_storage = [_]u8{0} ** 64;
    const raw_label = try std.fmt.bufPrint(&label_storage, "  range:{s}\n", .{rendered[0..rendered_len]});
    var label = [_]u8{0} ** 64;
    @memcpy(label[0..raw_label.len], raw_label);
    const trimmed = string.strim(&label);
    try std.testing.expectEqualSlices(u8, "range:2-5,63-65,72-73", trimmed);
    try std.testing.expectEqual(trimmed.len, string.strreplace(trimmed, ':', '='));
    try std.testing.expectEqual(@as(usize, 6), string.str_has_prefix(trimmed, "range="));
    try std.testing.expect(string.str_ends_with(trimmed, "72-73"));

    const exact_matches = [_][]const u8{
        "range=2-5,63-65,72-73",
        "range=2-5,63-65,72-74",
    };
    const newline_matches = [_][]const u8{
        "range=2-5,63-65,72-73\n",
        "skip",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(&exact_matches, trimmed));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(&newline_matches, trimmed));

    var collapsed = [_]u8{ 'r', 'a', 'n', 'g', 'e', ' ', 'a', 'n', 'c', 'h', 'o', 'r', 0, 'x' };
    const without_spaces = string.remove_spaces(&collapsed);
    try std.testing.expectEqualSlices(u8, "rangeanchor", without_spaces);

    var padded = [_]u8{0xaa} ** 24;
    try std.testing.expectEqual(@as(isize, 6), string.strscpy_pad(&padded, "anchor"));
    try std.testing.expectEqual(@as(?usize, 0), string.memchr_inv(padded[0..7], 0));
    try std.testing.expectEqual(@as(?usize, null), string.memchr_inv(padded[7..], 0));

    var entries = [_]Entry{
        .{ .key = @intCast(find_bit.find_next_bit(&extended, nbits, find_bit.bits_per_long - 1)), .serial = 0 },
        .{ .key = @intCast(find_bit.find_first_bit(&extended, nbits)), .serial = 1 },
        .{ .key = @intCast(find_bit.find_next_bit(&extended, nbits, find_bit.bits_per_long - 1)), .serial = 2 },
        .{ .key = @intCast(find_bit.find_next_bit(&extended, nbits, find_bit.bits_per_long + 2)), .serial = 3 },
        .{ .key = @intCast(find_bit.find_last_bit(&weighted_or, nbits)), .serial = 4 },
    };
    var duplicate_probe = Entry{ .key = entries[3].key, .serial = 9 };
    var replacement = Entry{ .key = entries[1].key, .serial = 10 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_add_cached(&entries[0].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_add_cached(&entries[1].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[2].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[3].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[4].node, &root, less));
    try std.testing.expectEqual(@as(?u16, entries[1].key), keyOf(rbtree.rb_first_cached(&root)));

    const duplicate_existing = rbtree.rb_find_add_cached(&duplicate_probe.node, &root, cmpNode) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(entries[3].key, keyOf(duplicate_existing).?);
    try std.testing.expectEqual(@as(?u16, entries[1].key), keyOf(rbtree.rb_first_cached(&root)));

    const duplicate_key = entries[0].key;
    var iterator = rbtree.matchIterator(&duplicate_key, &root.root, cmpKey);
    var serials: [2]usize = undefined;
    var serial_count: usize = 0;
    while (iterator.next()) |node| {
        serials[serial_count] = serialOf(node);
        serial_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), serial_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2 }, serials[0..serial_count]);

    rbtree.rb_replace_node_cached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?u16, replacement.key), keyOf(rbtree.rb_first_cached(&root)));

    rbtree.rb_erase_init_cached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(?u16, entries[0].key), keyOf(rbtree.rb_first_cached(&root)));
}
