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

fn rbErasePlain(node: *rbtree.Node, root: *rbtree.Root) void {
    if (@hasDecl(rbtree, "rb_erase")) {
        rbtree.rb_erase(node, root);
    } else {
        rbtree.erase(node, root);
    }
}

fn rbEraseInitPlain(node: *rbtree.Node, root: *rbtree.Root) void {
    if (@hasDecl(rbtree, "rb_erase_init")) {
        rbtree.rb_erase_init(node, root);
    } else {
        rbtree.eraseInit(node, root);
    }
}

fn collectKeys(comptime Entry: type, root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var current = rbtree.rb_first(root);
    while (current) |node| : (current = rbtree.rb_next(node)) {
        out[count] = nodeKey(Entry, node);
        count += 1;
    }
    return count;
}

test "Lane 06 pivot echo keeps helper ports aligned" {
    const nbits = 96;
    var old = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var new = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var mask = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var pivot = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var guard = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var overlap = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var retained = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var echo = [_]Word{0} ** bitmap.bitsToWords(nbits);

    setRange(&old, 3, 4);
    setRange(&old, 20, 3);
    setRange(&old, 65, 4);
    setRange(&old, 90, 2);

    setRange(&new, 1, 2);
    setRange(&new, 21, 4);
    setRange(&new, 64, 3);
    setRange(&new, 88, 8);

    setRange(&mask, 1, 6);
    setRange(&mask, 20, 6);
    setRange(&mask, 64, 5);
    setRange(&mask, 88, 8);

    bitmap.bitmap_replace(&pivot, &old, &new, &mask, nbits);
    try testing.expectEqual(@as(usize, 17), bitmap.bitmap_weight(&pivot, nbits));

    setRange(&guard, 2, 1);
    setRange(&guard, 22, 1);
    setRange(&guard, 64, 1);
    setRange(&guard, 70, 1);
    setRange(&guard, 90, 2);

    try testing.expectEqual(@as(usize, 18), bitmap.bitmap_weighted_or(&echo, &pivot, &guard, nbits));
    try testing.expect(bitmap.bitmap_and(&overlap, &pivot, &guard, nbits));
    try testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(&overlap, nbits));
    try testing.expect(bitmap.bitmap_andnot(&retained, &pivot, &guard, nbits));
    try testing.expectEqual(@as(usize, 12), bitmap.bitmap_weight(&retained, nbits));
    try testing.expect(bitmap.bitmap_subset(&overlap, &pivot, nbits));
    try testing.expect(!bitmap.bitmap_subset(&guard, &pivot, nbits));
    try testing.expect(!bitmap.bitmap_intersects(&retained, &guard, nbits));

    try testing.expectEqual(@as(usize, 1), find_bit.find_first_bit(&retained, nbits));
    try testing.expectEqual(@as(usize, 2), find_bit.find_next_and_bit(&pivot, &guard, nbits, 0));
    try testing.expectEqual(@as(usize, 21), find_bit.find_next_andnot_bit(&pivot, &guard, nbits, 3));
    try testing.expectEqual(@as(usize, 65), find_bit.find_next_bit(&retained, nbits, 25));
    try testing.expectEqual(@as(usize, 0), find_bit.find_first_zero_bit(&pivot, nbits));
    try testing.expectEqual(@as(usize, 95), find_bit.find_last_bit(&retained, nbits));

    var clump: u8 = 0;
    try testing.expectEqual(@as(usize, 0), find_bit.find_next_clump8(&clump, &retained, nbits, 0));
    try testing.expectEqual(@as(u8, 0x02), clump);
    try testing.expectEqual(@as(usize, 64), find_bit.find_next_clump8(&clump, &retained, nbits, 64));
    try testing.expectEqual(@as(u8, 0x06), clump);
    try testing.expectEqual(@as(usize, 88), find_bit.find_next_clump8(&clump, &retained, nbits, 88));
    try testing.expectEqual(@as(u8, 0xf3), clump);

    var rendered_buf: [64]u8 = undefined;
    @memset(&rendered_buf, 0);
    const rendered_len = bitmap.bitmap_scnprintf(&retained, nbits, &rendered_buf);
    const rendered = rendered_buf[0..rendered_len];
    try testing.expectEqualSlices(u8, "1,21,23-24,65-66,88-89,92-95", rendered);

    var decorated = [_]u8{
        ' ', '\t', '1', ',', ' ', '2',  '1', ',', ' ', '2',
        '3', '-',  '2', '4', ',', ' ',  '6', '5', '-', '6',
        '6', ',',  ' ', '8', '8', '-',  '8', '9', ',', ' ',
        '9', '2',  '-', '9', '5', '\n', 0,   0,   0,   0,
    };
    const trimmed = string.strim(&decorated);
    try testing.expectEqualSlices(u8, "1, 21, 23-24, 65-66, 88-89, 92-95", trimmed);
    const compact = string.remove_spaces(trimmed);
    try testing.expectEqualSlices(u8, rendered, compact);

    var copied: [64]u8 = undefined;
    @memset(&copied, 0xff);
    const copied_len_signed = string.strscpy_pad(&copied, compact);
    try testing.expectEqual(@as(isize, @intCast(compact.len)), copied_len_signed);
    const copied_len: usize = @intCast(copied_len_signed);
    try testing.expectEqual(@as(?usize, null), string.memchr_inv(copied[copied_len + 1 ..], 0));

    try testing.expectEqual(@as(?usize, 1), string.strnchr(copied[0..copied_len], 4, ','));
    try testing.expect(string.streq(copied[0..copied_len], rendered));
    const replaced_len = string.strreplace(copied[0..copied_len], ',', ':');
    try testing.expectEqual(copied_len, replaced_len);
    try testing.expectEqualSlices(u8, "1:21:23-24:65-66:88-89:92-95", copied[0..copied_len]);
    try testing.expectEqual(@as(usize, 2), string.str_has_prefix(copied[0..copied_len], "1:"));
    try testing.expect(string.str_ends_with(copied[0..copied_len], "92-95"));

    const sysfs_choices = [_][]const u8{
        "idle",
        "1:21:23-24:65-66:88-89:92-95\n",
        "miss",
    };
    const exact_choices = [_][]const u8{
        "idle",
        "1:21:23-24:65-66:88-89:92-95",
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
        .{ .key = find_bit.find_next_bit(&retained, nbits, 65), .ordinal = 0 },
        .{ .key = find_bit.find_first_bit(&retained, nbits), .ordinal = 0 },
        .{ .key = find_bit.find_next_bit(&retained, nbits, 88), .ordinal = 0 },
        .{ .key = find_bit.find_next_bit(&retained, nbits, 88), .ordinal = 1 },
        .{ .key = find_bit.find_last_bit(&retained, nbits), .ordinal = 0 },
        .{ .key = find_bit.find_next_bit(&retained, nbits, 21), .ordinal = 0 },
    };
    var replacement = Entry{ .key = 21, .ordinal = 9 };
    var cached_root = rbtree.RootCached.init();

    try testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_add_cached(&entries[0].node, &cached_root, less));
    try testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_add_cached(&entries[1].node, &cached_root, less));
    try testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[2].node, &cached_root, less));
    try testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[3].node, &cached_root, less));
    try testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[4].node, &cached_root, less));
    try testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[5].node, &cached_root, less));
    try testing.expectEqual(@as(usize, 1), nodeKey(Entry, rbtree.rb_first_cached(&cached_root).?));

    const duplicate_key: usize = 88;
    var duplicates = rbtree.matchIterator(&duplicate_key, &cached_root.root, cmp_key);
    const first_duplicate = duplicates.next() orelse return error.TestUnexpectedResult;
    const second_duplicate = duplicates.next() orelse return error.TestUnexpectedResult;
    try testing.expectEqual(@as(usize, 88), nodeKey(Entry, first_duplicate));
    try testing.expectEqual(@as(usize, 88), nodeKey(Entry, second_duplicate));
    try testing.expectEqual(@as(?*rbtree.Node, null), duplicates.next());

    rbtree.rb_replace_node_cached(&entries[5].node, &replacement.node, &cached_root);
    try testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.find(&replacement.key, &cached_root.root, cmp_key));
    const promoted = rbtree.rb_erase_cached(&entries[1].node, &cached_root) orelse return error.TestUnexpectedResult;
    try testing.expectEqual(@as(usize, 21), nodeKey(Entry, promoted));
    try testing.expectEqual(@as(usize, 21), nodeKey(Entry, rbtree.rb_first_cached(&cached_root).?));
    rbtree.rb_erase_init_cached(&replacement.node, &cached_root);
    try testing.expect(rbtree.emptyNode(&replacement.node));

    var ordered: [4]usize = undefined;
    const cached_count = collectKeys(Entry, &cached_root.root, &ordered);
    try testing.expectEqual(@as(usize, 4), cached_count);
    try testing.expectEqualSlices(usize, &[_]usize{ 65, 88, 88, 95 }, ordered[0..cached_count]);

    var primary_entries = [_]Entry{
        .{ .key = 1, .ordinal = 0 },
        .{ .key = 21, .ordinal = 0 },
        .{ .key = 65, .ordinal = 0 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 1, .ordinal = 0 },
        .{ .key = 21, .ordinal = 0 },
        .{ .key = 65, .ordinal = 0 },
    };
    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();
    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, less);
        rbtree.add(&alias_entry.node, &alias_root, less);
    }

    rbtree.erase(&primary_entries[1].node, &primary_root);
    rbErasePlain(&alias_entries[1].node, &alias_root);

    var primary_order: [2]usize = undefined;
    var alias_order: [2]usize = undefined;
    const primary_count = collectKeys(Entry, &primary_root, &primary_order);
    const alias_count = collectKeys(Entry, &alias_root, &alias_order);
    try testing.expectEqual(primary_count, alias_count);
    try testing.expectEqualSlices(usize, primary_order[0..primary_count], alias_order[0..alias_count]);
    try testing.expectEqualSlices(usize, &[_]usize{ 1, 65 }, alias_order[0..alias_count]);

    rbtree.eraseInit(&primary_entries[0].node, &primary_root);
    rbEraseInitPlain(&alias_entries[0].node, &alias_root);
    try testing.expect(rbtree.emptyNode(&primary_entries[0].node));
    try testing.expect(rbtree.emptyNode(&alias_entries[0].node));

    const primary_after_count = collectKeys(Entry, &primary_root, &primary_order);
    const alias_after_count = collectKeys(Entry, &alias_root, &alias_order);
    try testing.expectEqual(primary_after_count, alias_after_count);
    try testing.expectEqualSlices(usize, primary_order[0..primary_after_count], alias_order[0..alias_after_count]);
    try testing.expectEqualSlices(usize, &[_]usize{65}, alias_order[0..alias_after_count]);
}
