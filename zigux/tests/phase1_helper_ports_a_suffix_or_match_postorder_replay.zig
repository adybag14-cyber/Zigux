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
    if (lhs_entry.key == rhs_entry.key) {
        return lhs_entry.serial < rhs_entry.serial;
    }
    return lhs_entry.key < rhs_entry.key;
}

fn cmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    if (lhs_entry.serial < rhs_entry.serial) return -1;
    if (lhs_entry.serial > rhs_entry.serial) return 1;
    return 0;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn collectInorder(root: *const rbtree.Root, out: []i32) usize {
    var count: usize = 0;
    var current = rbtree.first(root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "bitmap replace result feeds OR scans across a tail boundary" {
    const nbits = bitmap.bits_per_long + 11;
    var old = [_]bitmap.Word{ 0, 0 };
    var new = [_]bitmap.Word{ 0, 0 };
    var mask = [_]bitmap.Word{ 0, 0 };
    var dst = [_]bitmap.Word{ 0, 0 };
    var partner = [_]bitmap.Word{ 0, 0 };

    bitmap.setRange(old[0..], 1, 3);
    bitmap.setRange(old[0..], bitmap.bits_per_long - 2, 4);
    bitmap.setRange(new[0..], bitmap.bits_per_long + 5, 3);
    bitmap.setRange(mask[0..], 0, bitmap.bits_per_long + 8);
    bitmap.bitmap_replace(dst[0..], old[0..], new[0..], mask[0..], nbits);

    partner[0] |= @as(bitmap.Word, 1) << 9;
    partner[1] |= @as(bitmap.Word, 1) << 9;
    var merged = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_or(merged[0..], dst[0..], partner[0..], nbits);

    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(dst[0..], 1));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 5), find_bit.findFirstBit(dst[0..], nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 6), find_bit.findNextBit(dst[0..], nbits, bitmap.bits_per_long + 6));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 7), find_bit.findLastBit(dst[0..], nbits));
    try std.testing.expectEqual(@as(usize, 9), find_bit.findNextBit(merged[0..], nbits, 0));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 5), find_bit.findNextBit(merged[0..], nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 9), find_bit.findNextBit(merged[0..], nbits, bitmap.bits_per_long + 8));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(merged[0..], nbits, nbits));

    var clump: u8 = 0xaa;
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long), find_bit.findNextClump8(&clump, dst[0..], nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b1110_0000), clump);
}

test "string suffix and match helpers respect C-string and sysfs boundaries" {
    var token = [_]u8{ ' ', 'a', 'l', 'p', 'h', 'a', '/', 'b', 'e', 't', 'a', '.', 'k', 'o', '\n', 0, 'x', 'x' };
    const trimmed = string.strim(token[0..]);
    try std.testing.expectEqualSlices(u8, "alpha/beta.ko", trimmed);
    try std.testing.expectEqual(@as(usize, 6), string.str_has_prefix(trimmed, "alpha/"));
    try std.testing.expect(string.str_ends_with(trimmed, ".ko"));

    const plain = [_][]const u8{ "alpha", "beta\n", "gamma\x00hidden" };
    try std.testing.expectEqual(@as(?usize, null), string.match_string(plain[0..], "beta"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(plain[0..], "beta"));
    try std.testing.expectEqual(@as(?usize, 2), string.match_string(plain[0..], "gamma"));

    const dirty = [_]u8{ 0, 0, 0, 'x', 0, 0 };
    try std.testing.expectEqual(@as(?usize, 3), string.memchr_inv(dirty[0..], 0));
}

test "rbtree duplicate matches and postorder survive replacement and erase-init" {
    var root = rbtree.Root.init();
    var entries = [_]Entry{
        .{ .key = 5, .serial = 0 },
        .{ .key = 3, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 7, .serial = 3 },
        .{ .key = 5, .serial = 4 },
        .{ .key = 1, .serial = 5 },
    };
    for (&entries) |*entry| {
        try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAdd(&entry.node, &root, cmpNode));
    }

    const wanted: i32 = 5;
    var iterator = rbtree.matchIterator(&wanted, &root, cmpKey);
    const expected_serials = [_]usize{ 0, 2, 4 };
    for (expected_serials) |serial| {
        const node = iterator.next() orelse return error.UnexpectedEndOfTest;
        const entry: *const Entry = @fieldParentPtr("node", node);
        try std.testing.expectEqual(serial, entry.serial);
    }
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iterator.next());

    var replacement = Entry{ .key = 3, .serial = 9 };
    rbtree.replaceNode(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.findFirst(&replacement.key, &root, cmpKey));

    var order: [entries.len]i32 = undefined;
    const count_before_erase = collectInorder(&root, order[0..]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 3, 5, 5, 5, 7 }, order[0..count_before_erase]);

    var postorder_count: usize = 0;
    var current = rbtree.firstPostorder(&root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        postorder_count += 1;
    }
    try std.testing.expectEqual(@as(usize, entries.len), postorder_count);

    rbtree.eraseInit(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));

    const count_after_erase = collectInorder(&root, order[0..]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 5, 5, 5, 7 }, order[0..count_after_erase]);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.find(&replacement.key, &root, cmpKey));
}
