const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const testing = std.testing;
const Word = bitmap.Word;

fn nodeKey(comptime Entry: type, node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn keyCompare(comptime Entry: type, key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "Lane 06 delta splice keeps helper ports A in lockstep" {
    const nbits = 96;
    var old = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var new = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var mask = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var spliced = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var shared = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var delta = [_]Word{0} ** bitmap.bitsToWords(nbits);

    bitmap.bitmap_set(&old, 1, 5);
    bitmap.bitmap_set(&old, 12, 4);
    bitmap.bitmap_set(&old, 40, 4);
    bitmap.bitmap_set(&old, 70, 3);
    bitmap.bitmap_set(&old, 90, 2);

    bitmap.bitmap_set(&new, 3, 5);
    bitmap.bitmap_set(&new, 14, 5);
    bitmap.bitmap_set(&new, 42, 4);
    bitmap.bitmap_set(&new, 74, 3);
    bitmap.bitmap_set(&new, 88, 7);

    bitmap.bitmap_set(&mask, 3, 4);
    bitmap.bitmap_set(&mask, 14, 4);
    bitmap.bitmap_set(&mask, 42, 3);
    bitmap.bitmap_set(&mask, 74, 2);
    bitmap.bitmap_set(&mask, 90, 5);

    bitmap.bitmap_replace(&spliced, &old, &new, &mask, nbits);
    try testing.expectEqual(@as(usize, 27), bitmap.bitmap_weight(&spliced, nbits));
    try testing.expect(bitmap.bitmap_and(&shared, &spliced, &old, nbits));
    try testing.expectEqual(@as(usize, 18), bitmap.bitmap_weight(&shared, nbits));
    try testing.expect(bitmap.bitmap_andnot(&delta, &spliced, &old, nbits));
    try testing.expectEqual(@as(usize, 9), bitmap.bitmap_weight(&delta, nbits));
    try testing.expect(bitmap.bitmap_subset(&delta, &spliced, nbits));
    try testing.expect(!bitmap.bitmap_intersects(&delta, &old, nbits));

    try testing.expectEqual(@as(usize, 6), find_bit.find_first_bit(&delta, nbits));
    try testing.expectEqual(@as(usize, 40), find_bit.find_next_and_bit(&spliced, &old, nbits, 16));
    try testing.expectEqual(@as(usize, 74), find_bit.find_next_andnot_bit(&spliced, &old, nbits, 45));
    try testing.expectEqual(@as(usize, 7), find_bit.find_next_zero_bit(&spliced, nbits, 1));
    try testing.expectEqual(@as(usize, 94), find_bit.find_last_bit(&delta, nbits));

    var clump: u8 = 0;
    try testing.expectEqual(@as(usize, 0), find_bit.find_next_clump8(&clump, &delta, nbits, 0));
    try testing.expectEqual(@as(u8, 0x40), clump);
    try testing.expectEqual(@as(usize, 40), find_bit.find_next_clump8(&clump, &delta, nbits, 40));
    try testing.expectEqual(@as(u8, 0x10), clump);
    try testing.expectEqual(@as(usize, 72), find_bit.find_next_clump8(&clump, &delta, nbits, 72));
    try testing.expectEqual(@as(u8, 0x0c), clump);
    try testing.expectEqual(@as(usize, 88), find_bit.find_next_clump8(&clump, &delta, nbits, 88));
    try testing.expectEqual(@as(u8, 0x70), clump);

    var rendered_buf: [48]u8 = undefined;
    @memset(&rendered_buf, 0);
    const rendered_len = bitmap.bitmap_scnprintf(&delta, nbits, &rendered_buf);
    const rendered = rendered_buf[0..rendered_len];
    try testing.expectEqualSlices(u8, "6,16-17,44,74-75,92-94", rendered);

    var decorated = [_]u8{
        ' ', '\t', '6', ',', ' ', '1', '6', '-', '1',  '7',
        ',', ' ',  '4', '4', ',', ' ', '7', '4', '-',  '7',
        '5', ',',  ' ', '9', '2', '-', '9', '4', '\n', 0,
        0,   0,
    };
    const trimmed = string.strim(&decorated);
    try testing.expectEqualSlices(u8, "6, 16-17, 44, 74-75, 92-94", trimmed);
    const compact = string.remove_spaces(trimmed);
    try testing.expectEqualSlices(u8, rendered, compact);

    var copied: [48]u8 = undefined;
    @memset(&copied, 0xff);
    const copied_len_signed = string.strscpy_pad(&copied, compact);
    try testing.expectEqual(@as(isize, @intCast(compact.len)), copied_len_signed);
    const copied_len: usize = @intCast(copied_len_signed);
    try testing.expectEqual(@as(?usize, null), string.memchr_inv(copied[copied_len + 1 ..], 0));
    try testing.expectEqual(@as(?usize, 1), string.strnchr(copied[0..copied_len], 8, ','));
    try testing.expect(string.streq(copied[0..copied_len], rendered));

    const replaced_len = string.strreplace(copied[0..copied_len], ',', ';');
    try testing.expectEqual(copied_len, replaced_len);
    try testing.expectEqualSlices(u8, "6;16-17;44;74-75;92-94", copied[0..copied_len]);
    try testing.expectEqual(@as(usize, 4), string.str_has_prefix(copied[0..copied_len], "6;16"));
    try testing.expect(string.str_ends_with(copied[0..copied_len], "92-94"));

    const sysfs_choices = [_][]const u8{
        "idle",
        "6;16-17;44;74-75;92-94\n",
        "miss",
    };
    const exact_choices = [_][]const u8{
        "idle",
        "6;16-17;44;74-75;92-94",
        "miss",
    };
    try testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&sysfs_choices, copied[0..copied_len]));
    try testing.expectEqual(@as(?usize, 1), string.match_string(&exact_choices, copied[0..copied_len]));

    const Entry = struct {
        key: usize,
        ordinal: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };
    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
            return lhs_entry.ordinal < rhs_entry.ordinal;
        }
    }.compare;
    const cmp_key = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            return keyCompare(Entry, key, node);
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = find_bit.find_next_and_bit(&spliced, &old, nbits, 40), .ordinal = 0 },
        .{ .key = find_bit.find_first_bit(&delta, nbits), .ordinal = 0 },
        .{ .key = find_bit.find_next_andnot_bit(&spliced, &old, nbits, 74), .ordinal = 0 },
        .{ .key = find_bit.find_next_bit(&delta, nbits, 92), .ordinal = 0 },
        .{ .key = find_bit.find_next_bit(&delta, nbits, 92), .ordinal = 1 },
    };
    var replacement = Entry{ .key = 16, .ordinal = 7 };
    var root = rbtree.RootCached.init();

    try testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_add_cached(&entries[0].node, &root, less));
    try testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_add_cached(&entries[1].node, &root, less));
    try testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[2].node, &root, less));
    try testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[3].node, &root, less));
    try testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[4].node, &root, less));
    try testing.expectEqual(@as(usize, 6), nodeKey(Entry, rbtree.rb_first_cached(&root).?));

    const duplicate_key: usize = 92;
    var duplicate_iter = rbtree.matchIterator(&duplicate_key, &root.root, cmp_key);
    const duplicate_first = duplicate_iter.next() orelse return error.TestUnexpectedResult;
    const duplicate_second = duplicate_iter.next() orelse return error.TestUnexpectedResult;
    try testing.expectEqual(@as(usize, 92), nodeKey(Entry, duplicate_first));
    try testing.expectEqual(@as(usize, 92), nodeKey(Entry, duplicate_second));
    try testing.expectEqual(@as(?*rbtree.Node, null), duplicate_iter.next());

    rbtree.rb_replace_node_cached(&entries[1].node, &replacement.node, &root);
    const replacement_key: usize = 16;
    try testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.find(&replacement_key, &root.root, cmp_key));

    const promoted = rbtree.rb_erase_cached(&replacement.node, &root) orelse return error.TestUnexpectedResult;
    try testing.expectEqual(@as(usize, 40), nodeKey(Entry, promoted));
    try testing.expectEqual(@as(usize, 40), nodeKey(Entry, rbtree.rb_first_cached(&root).?));

    rbtree.rb_erase_init_cached(&entries[0].node, &root);
    try testing.expect(rbtree.emptyNode(&entries[0].node));

    var ordered: [3]usize = undefined;
    var count: usize = 0;
    var current = rbtree.rb_first(&root.root);
    while (current) |node| : (current = rbtree.rb_next(node)) {
        ordered[count] = nodeKey(Entry, node);
        count += 1;
    }

    try testing.expectEqual(@as(usize, 3), count);
    try testing.expectEqualSlices(usize, &[_]usize{ 74, 92, 92 }, ordered[0..count]);
}
