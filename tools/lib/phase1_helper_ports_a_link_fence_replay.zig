const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
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
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "phase1 helper ports A link fence replay" {
    const nbits = 130;
    var old = [_]bitmap.Word{0} ** bitmap.bitsToWords(nbits);
    var new = [_]bitmap.Word{0} ** bitmap.bitsToWords(nbits);
    var mask = [_]bitmap.Word{0} ** bitmap.bitsToWords(nbits);
    var fenced = [_]bitmap.Word{0} ** bitmap.bitsToWords(nbits);
    var inverted = [_]bitmap.Word{0} ** bitmap.bitsToWords(nbits);
    var shared = [_]bitmap.Word{0} ** bitmap.bitsToWords(nbits);
    var outside = [_]bitmap.Word{0} ** bitmap.bitsToWords(nbits);

    bitmap.bitmap_set(&old, 1, 8);
    bitmap.bitmap_set(&old, 42, 1);
    bitmap.bitmap_set(&old, 64, 5);
    bitmap.bitmap_set(&old, 96, 2);
    bitmap.bitmap_set(&old, 124, 3);
    bitmap.bitmap_set(&new, 3, 4);
    bitmap.bitmap_set(&new, 66, 6);
    bitmap.bitmap_set(&new, 120, 8);
    bitmap.bitmap_set(&mask, 0, 10);
    bitmap.bitmap_set(&mask, 63, 11);
    bitmap.bitmap_set(&mask, 119, 10);

    bitmap.bitmap_replace(&fenced, &old, &new, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 21), bitmap.bitmap_weight(&fenced, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&fenced, &mask, nbits));

    bitmap.bitmap_complement(&inverted, &fenced, nbits);
    try std.testing.expect(!bitmap.bitmap_empty(&inverted, 1));
    try std.testing.expect(!bitmap.bitmap_empty(&inverted, nbits));

    _ = bitmap.bitmap_and(&shared, &fenced, &mask, nbits);
    try std.testing.expect(bitmap.bitmap_subset(&shared, &mask, nbits));
    _ = bitmap.bitmap_andnot(&outside, &fenced, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&outside, nbits));

    try std.testing.expectEqual(@as(usize, 3), find_bit.find_first_bit(&fenced, nbits));
    try std.testing.expectEqual(@as(usize, 66), find_bit.find_next_bit(&fenced, nbits, 64));
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_zero_bit(&fenced, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.find_first_and_bit(&fenced, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 42), find_bit.find_first_andnot_bit(&fenced, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 127), find_bit.find_last_bit(&fenced, nbits));

    var clump: u8 = 0xaa;
    const clump_at = find_bit.find_next_clump8(&clump, &fenced, nbits, 64);
    try std.testing.expectEqual(@as(usize, 64), clump_at);
    try std.testing.expectEqual(@as(u8, 0xfc), clump);

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.bitmap_scnprintf(&fenced, nbits, &rendered);
    try std.testing.expectEqualStrings("3-6,42,66-71,96-97,120-127", rendered[0..rendered_len]);

    var padded = [_]u8{0xcc} ** 40;
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), string.strscpyPad(&padded, rendered[0..rendered_len]));
    try std.testing.expectEqual(@as(?usize, null), string.memchr_inv(padded[rendered_len + 1 ..], 0));
    try std.testing.expect(string.strstarts(&padded, "3-6"));
    try std.testing.expect(string.str_ends_with(padded[0..rendered_len], "120-127"));
    try std.testing.expect(string.sysfs_streq("link-fence\n", "link-fence"));

    var spaced = [_]u8{ ' ', 'l', 'i', 'n', 'k', ' ', 'f', 'e', 'n', 'c', 'e', 0 };
    const trimmed = string.strim(&spaced);
    try std.testing.expectEqualStrings("link fence", trimmed);
    const compact = string.remove_spaces(trimmed);
    try std.testing.expectEqualStrings("linkfence", compact);
    try std.testing.expectEqual(@as(usize, 9), string.strreplace(compact, 'f', 'F'));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(&[_][]const u8{ "linkFence", "fallback" }, compact));

    var entries = [_]Entry{
        .{ .key = 66, .serial = 0 },
        .{ .key = 3, .serial = 1 },
        .{ .key = 120, .serial = 2 },
        .{ .key = 66, .serial = 3 },
        .{ .key = 10, .serial = 4 },
    };
    var cached = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &cached, less);
    }

    try std.testing.expectEqual(@as(*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&cached).?);
    const duplicate_key = @as(i32, 66);
    var iter = rbtree.matchIterator(&duplicate_key, &cached.root, keyCmp);
    var duplicate_serials: [2]usize = undefined;
    var duplicate_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        duplicate_serials[duplicate_count] = entry.serial;
        duplicate_count += 1;
    }
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 3 }, duplicate_serials[0..duplicate_count]);

    const promoted = rbtree.rb_erase_cached(&entries[1].node, &cached) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[4].node), promoted);
    try std.testing.expectEqual(promoted, rbtree.rb_first_cached(&cached).?);

    rbtree.eraseInitCached(&entries[4].node, &cached);
    try std.testing.expect(rbtree.emptyNode(&entries[4].node));
    try std.testing.expectEqual(rbtree.first(&cached.root), rbtree.rb_first_cached(&cached));
}
