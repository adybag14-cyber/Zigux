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

fn lessByKeyThenSerial(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn compareKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
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

fn entrySerial(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.serial;
}

fn collectKeys(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var current = rbtree.first(root);
    while (current) |node| : (current = rbtree.next(node)) {
        out[count] = entryKey(node);
        count += 1;
    }
    return count;
}

test "lane06 rim-queue replay carries rim bitmaps through strings and cached rbtree" {
    const nbits: usize = 130;
    const nwords: usize = 3;
    try std.testing.expectEqual(@as(usize, 3), nwords);
    try std.testing.expectEqual(nwords, bitmap.bitsToWords(nbits));

    var base = [_]Word{0} ** nwords;
    bitmap.setRange(&base, 4, 4);
    bitmap.setRange(&base, 60, 6);
    bitmap.setRange(&base, 124, 4);

    var overlay = [_]Word{0} ** nwords;
    bitmap.setRange(&overlay, 2, 3);
    bitmap.setRange(&overlay, 61, 3);
    bitmap.setRange(&overlay, 126, 3);

    var mask = [_]Word{0} ** nwords;
    bitmap.setRange(&mask, 0, 8);
    bitmap.setRange(&mask, 60, 6);
    bitmap.setRange(&mask, 124, 5);

    var rim = [_]Word{0} ** nwords;
    bitmap.bitmap_replace(&rim, &base, &overlay, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 9), bitmap.bitmap_weight(&rim, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&overlay, &mask, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&rim, &base, nbits));

    var inverse = [_]Word{0} ** nwords;
    bitmap.bitmap_complement(&inverse, &rim, nbits);
    try std.testing.expectEqual(@as(usize, nbits - 9), bitmap.bitmap_weight(&inverse, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&rim, &inverse, nbits));

    try std.testing.expectEqual(@as(usize, 2), find_bit.find_first_bit(&rim, nbits));
    try std.testing.expectEqual(@as(usize, 61), find_bit.find_next_bit(&rim, nbits, 5));
    try std.testing.expectEqual(@as(usize, 5), find_bit.find_next_zero_bit(&rim, nbits, 2));
    try std.testing.expectEqual(@as(usize, 4), find_bit.find_next_and_bit(&base, &overlay, nbits, 0));
    try std.testing.expectEqual(@as(usize, 5), find_bit.find_next_andnot_bit(&base, &overlay, nbits, 0));
    try std.testing.expectEqual(@as(usize, 128), find_bit.find_last_bit(&rim, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_next_clump8(&clump, &rim, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0x1c), clump);
    try std.testing.expectEqual(@as(usize, 56), find_bit.find_next_clump8(&clump, &rim, nbits, 60));
    try std.testing.expectEqual(@as(u8, 0xe0), clump);
    try std.testing.expectEqual(@as(usize, 120), find_bit.find_next_clump8(&clump, &rim, nbits, 124));
    try std.testing.expectEqual(@as(u8, 0xc0), clump);
    try std.testing.expectEqual(@as(usize, 128), find_bit.find_next_clump8(&clump, &rim, nbits, 128));
    try std.testing.expectEqual(@as(u8, 0x01), clump);

    var rendered = [_]u8{0} ** 48;
    const rendered_len = bitmap.bitmap_scnprintf(&rim, nbits, &rendered);
    try std.testing.expectEqualSlices(u8, "2-4,61-63,126-128", rendered[0..rendered_len]);
    try std.testing.expectEqual(@as(u8, 0), rendered[rendered_len]);

    var padded = [_]u8{0xdd} ** 48;
    const copied = string.strscpy_pad(&padded, rendered[0 .. rendered_len + 1]);
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), copied);
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix(&padded, "2-4"));
    try std.testing.expect(string.strEndsWith(&padded, "128"));
    try std.testing.expectEqual(@as(?usize, null), string.memchr_inv(padded[rendered_len + 1 ..], 0));

    const labels = [_][]const u8{
        "2-4,61-63\n",
        "2-4,61-63,126-128\n",
        "rim-queue-missing\n",
    };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(labels[0..], padded[0 .. rendered_len + 1]));

    var label = [_]u8{ ' ', 'r', 'i', 'm', ' ', 'q', 'u', 'e', 'u', 'e', ' ', 0 };
    const trimmed = string.strim(&label);
    try std.testing.expectEqualSlices(u8, "rim queue", trimmed);
    const compact = string.remove_spaces(trimmed);
    try std.testing.expectEqualSlices(u8, "rimqueue", compact);
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr(compact, compact.len, 'q'));

    var entries = [_]Entry{
        .{ .key = find_bit.find_first_bit(&rim, nbits), .serial = 0 },
        .{ .key = find_bit.find_next_bit(&rim, nbits, 5), .serial = 1 },
        .{ .key = find_bit.find_next_and_bit(&base, &overlay, nbits, 0), .serial = 2 },
        .{ .key = find_bit.find_last_bit(&rim, nbits), .serial = 3 },
        .{ .key = find_bit.find_next_bit(&rim, nbits, 5), .serial = 4 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, lessByKeyThenSerial);
    }

    try std.testing.expectEqual(@as(usize, 2), entryKey(rbtree.rb_first_cached(&root).?));

    var ordered: [5]usize = undefined;
    const ordered_count = collectKeys(&root.root, &ordered);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 4, 61, 61, 128 }, ordered[0..ordered_count]);

    const duplicate_key: usize = 61;
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, compareKey);
    var duplicate_serials: [2]usize = undefined;
    var duplicate_count: usize = 0;
    while (iter.next()) |node| {
        duplicate_serials[duplicate_count] = entrySerial(node);
        duplicate_count += 1;
    }
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 4 }, duplicate_serials[0..duplicate_count]);

    const promoted = rbtree.rb_erase_cached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 4), entryKey(promoted));
    try std.testing.expectEqual(@as(usize, 4), entryKey(rbtree.rb_first_cached(&root).?));

    rbtree.rb_erase_init_cached(&entries[2].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[2].node));
    try std.testing.expectEqual(@as(usize, 61), entryKey(rbtree.rb_first_cached(&root).?));

    const remaining = collectKeys(&root.root, &ordered);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 61, 61, 128 }, ordered[0..remaining]);
}
