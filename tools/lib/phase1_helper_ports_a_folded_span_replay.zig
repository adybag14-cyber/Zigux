const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const testing = std.testing;
const Word = bitmap.Word;

fn setRange(words: []Word, start: usize, len: usize) void {
    bitmap.bitmap_set(words, start, len);
}

fn nodeKey(comptime Entry: type, node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn keyCompare(comptime Entry: type, key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) {
        return -1;
    }
    if (wanted.* > entry.key) {
        return 1;
    }
    return 0;
}

test "Lane 06 folded span keeps bitmap find string and cached rbtree aligned" {
    const nbits = 128;
    var span = [_]Word{0}**bitmap.bitsToWords(nbits);
    var gate = [_]Word{0}**bitmap.bitsToWords(nbits);
    var folded = [_]Word{0}**bitmap.bitsToWords(nbits);
    var overlap = [_]Word{0}**bitmap.bitsToWords(nbits);
    var retained = [_]Word{0}**bitmap.bitsToWords(nbits);

    setRange(&span, 4, 5);
    setRange(&span, 18, 6);
    setRange(&span, 64, 5);
    setRange(&span, 120, 4);

    setRange(&gate, 6, 4);
    setRange(&gate, 20, 4);
    setRange(&gate, 67, 6);
    setRange(&gate, 124, 3);

    try testing.expectEqual(@as(usize, 28), bitmap.bitmap_weighted_or(&folded, &span, &gate, nbits));
    try testing.expect(bitmap.bitmap_and(&overlap, &span, &gate, nbits));
    try testing.expectEqual(@as(usize, 9), bitmap.bitmap_weight(&overlap, nbits));
    try testing.expect(bitmap.bitmap_andnot(&retained, &folded, &gate, nbits));
    try testing.expectEqual(@as(usize, 11), bitmap.bitmap_weight(&retained, nbits));
    try testing.expect(bitmap.bitmap_subset(&retained, &folded, nbits));
    try testing.expect(!bitmap.bitmap_intersects(&retained, &gate, nbits));

    try testing.expectEqual(@as(usize, 4), find_bit.find_first_bit(&retained, nbits));
    try testing.expectEqual(@as(usize, 6), find_bit.find_next_and_bit(&span, &gate, nbits, 0));
    try testing.expectEqual(@as(usize, 18), find_bit.find_next_bit(&folded, nbits, 10));
    try testing.expectEqual(@as(usize, 120), find_bit.find_next_andnot_bit(&folded, &gate, nbits, 69));
    try testing.expectEqual(@as(usize, 10), find_bit.find_next_zero_bit(&folded, nbits, 4));
    try testing.expectEqual(@as(usize, 123), find_bit.find_last_bit(&retained, nbits));

    var clump: u8 = 0;
    try testing.expectEqual(@as(usize, 0), find_bit.find_next_clump8(&clump, &retained, nbits, 0));
    try testing.expectEqual(@as(u8, 0x30), clump);
    try testing.expectEqual(@as(usize, 64), find_bit.find_next_clump8(&clump, &retained, nbits, 64));
    try testing.expectEqual(@as(u8, 0x07), clump);
    try testing.expectEqual(@as(usize, 120), find_bit.find_next_clump8(&clump, &retained, nbits, 120));
    try testing.expectEqual(@as(u8, 0x0f), clump);

    var rendered_buf: [48]u8 = undefined;
    @memset(&rendered_buf, 0);
    const rendered_len = bitmap.bitmap_scnprintf(&retained, nbits, &rendered_buf);
    const rendered = rendered_buf[0..rendered_len];
    try testing.expectEqualSlices(u8, "4-5,18-19,64-66,120-123", rendered);

    var decorated = [_]u8{
        ' ', '\t', '4', '-', '5', ',', ' ', '1', '8',  '-',
        '1', '9',  ',', ' ', '6', '4', '-', '6', '6',  ',',
        ' ', '1',  '2', '0', '-', '1', '2', '3', '\n', 0,
        0,   0,    0,   0,
    };
    const trimmed = string.strim(&decorated);
    try testing.expectEqualSlices(u8, "4-5, 18-19, 64-66, 120-123", trimmed);
    const compact = string.remove_spaces(trimmed);
    try testing.expectEqualSlices(u8, rendered, compact);

    var copied: [48]u8 = undefined;
    @memset(&copied, 0xff);
    const copied_len_signed = string.strscpy_pad(&copied, compact);
    try testing.expectEqual(@as(isize, @intCast(compact.len)), copied_len_signed);
    const copied_len: usize = @intCast(copied_len_signed);
    try testing.expectEqual(@as(?usize, null), string.memchr_inv(copied[copied_len + 1 ..], 0));

    try testing.expectEqual(@as(?usize, 3), string.strnchr(copied[0..copied_len], 12, ','));
    try testing.expect(string.streq(copied[0..copied_len], rendered));

    const replaced_len = string.strreplace(copied[0..copied_len], ',', '|');
    try testing.expectEqual(copied_len, replaced_len);
    try testing.expectEqualSlices(u8, "4-5|18-19|64-66|120-123", copied[0..copied_len]);
    try testing.expectEqual(@as(usize, 3), string.str_has_prefix(copied[0..copied_len], "4-5"));
    try testing.expect(string.str_ends_with(copied[0..copied_len], "120-123"));

    const sysfs_choices = [_][]const u8{
        "idle",
        "4-5|18-19|64-66|120-123\n",
        "miss",
    };
    const exact_choices = [_][]const u8{
        "idle",
        "4-5|18-19|64-66|120-123",
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
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.ordinal < rhs_entry.ordinal;
        }
    }.compare;
    const cmp_key = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            return keyCompare(Entry, key, node);
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = find_bit.find_next_bit(&retained, nbits, 64), .ordinal = 0 },
        .{ .key = find_bit.find_next_bit(&retained, nbits, 18), .ordinal = 0 },
        .{ .key = find_bit.find_next_bit(&retained, nbits, 120), .ordinal = 0 },
        .{ .key = find_bit.find_next_bit(&retained, nbits, 120), .ordinal = 1 },
        .{ .key = find_bit.find_next_bit(&retained, nbits, 4), .ordinal = 0 },
    };
    var replacement = Entry{ .key = 18, .ordinal = 9 };
    var root = rbtree.RootCached.init();

    try testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_add_cached(&entries[0].node, &root, less));
    try testing.expectEqual(@as(?*rbtree.Node, &entries[4].node), rbtree.rb_add_cached(&entries[4].node, &root, less));
    try testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[1].node, &root, less));
    try testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[2].node, &root, less));
    try testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[3].node, &root, less));
    try testing.expectEqual(@as(usize, 4), nodeKey(Entry, rbtree.rb_first_cached(&root).?));

    const duplicate_key: usize = 120;
    var duplicates = rbtree.matchIterator(&duplicate_key, &root.root, cmp_key);
    const first_duplicate = duplicates.next() orelse return error.TestUnexpectedResult;
    const second_duplicate = duplicates.next() orelse return error.TestUnexpectedResult;
    try testing.expectEqual(@as(usize, 120), nodeKey(Entry, first_duplicate));
    try testing.expectEqual(@as(usize, 120), nodeKey(Entry, second_duplicate));
    try testing.expectEqual(@as(?*rbtree.Node, null), duplicates.next());

    rbtree.rb_replace_node_cached(&entries[1].node, &replacement.node, &root);
    const replacement_key: usize = 18;
    try testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.find(&replacement_key, &root.root, cmp_key));

    const promoted = rbtree.rb_erase_cached(&entries[4].node, &root) orelse return error.TestUnexpectedResult;
    try testing.expectEqual(@as(usize, 18), nodeKey(Entry, promoted));
    try testing.expectEqual(@as(usize, 18), nodeKey(Entry, rbtree.rb_first_cached(&root).?));
    rbtree.rb_erase_init_cached(&replacement.node, &root);
    try testing.expect(rbtree.emptyNode(&replacement.node));

    var ordered: [3]usize = undefined;
    var count: usize = 0;
    var current = rbtree.rb_first(&root.root);
    while (current) |node| : (current = rbtree.rb_next(node)) {
        ordered[count] = nodeKey(Entry, node);
        count += 1;
    }

    try testing.expectEqual(@as(usize, 3), count);
    try testing.expectEqualSlices(usize, &[_]usize{ 64, 120, 120 }, ordered[0..count]);
}
