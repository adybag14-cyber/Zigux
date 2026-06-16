const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: usize,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn setBit(map: []Word, bit: usize) void {
    map[bit / bits_per_long] |= @as(Word, 1) << @intCast(bit & (bits_per_long - 1));
}

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn keyOf(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn collectKeys(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var current = rbtree.first(root);
    while (current) |node| : (current = rbtree.next(node)) {
        out[count] = keyOf(node);
        count += 1;
    }
    return count;
}

test "masked gap reseed ties helper cursors to cached rbtree state" {
    const nbits = bits_per_long + 12;
    var old = [_]Word{ 0, 0 };
    var new = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };
    var replaced = [_]Word{ 0, 0 };
    var dropped = [_]Word{ 0, 0 };

    setBit(&old, 2);
    setBit(&old, 5);
    setBit(&old, bits_per_long + 1);
    setBit(&old, bits_per_long + 9);

    setBit(&new, 3);
    setBit(&new, 5);
    setBit(&new, bits_per_long + 4);
    setBit(&new, bits_per_long + 10);

    bitmap.bitmap_set(&mask, 2, 3);
    bitmap.bitmap_set(&mask, bits_per_long + 1, 4);
    bitmap.bitmap_replace(&replaced, &old, &new, &mask, nbits);

    try std.testing.expectEqual(@as(usize, 4), bitmap.bitmap_weight(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextBit(&replaced, nbits, 4));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextBit(&replaced, nbits, 6));
    try std.testing.expectEqual(@as(usize, bits_per_long + 9), find_bit.findLastBit(&replaced, nbits));

    try std.testing.expect(bitmap.bitmap_andnot(&dropped, &old, &replaced, nbits));
    const first_gap = find_bit.findFirstBit(&dropped, nbits);
    const second_gap = find_bit.findNextBit(&dropped, nbits, first_gap + 1);
    try std.testing.expectEqual(@as(usize, 2), first_gap);
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), second_gap);
    try std.testing.expectEqual(second_gap, find_bit.findLastBit(&dropped, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &replaced, nbits));
    try std.testing.expectEqual(@as(u8, 0b0010_1000), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextClump8(&clump, &replaced, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0001_0000), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long + 8), find_bit.findNextClump8(&clump, &replaced, nbits, bits_per_long + 5));
    try std.testing.expectEqual(@as(u8, 0b0000_0010), clump);

    var rendered = [_]u8{0}**64;
    const rendered_len = bitmap.bitmap_scnprintf(&replaced, nbits, &rendered);
    var expected_rendered = [_]u8{0}**32;
    const expected = try std.fmt.bufPrint(&expected_rendered, "3,5,{d},{d}", .{ bits_per_long + 4, bits_per_long + 9 });
    try std.testing.expectEqualSlices(u8, expected, rendered[0..rendered_len]);

    var summary = [_]u8{0}**96;
    const written = try std.fmt.bufPrint(&summary, "  gaps={d}:{d}; kept={s}\n", .{ first_gap, second_gap, rendered[0..rendered_len] });
    summary[written.len] = 0;
    const trimmed = string.strim(&summary);
    try std.testing.expectEqual(@as(usize, 4), string.str_has_prefix(trimmed, "gaps"));
    try std.testing.expect(string.str_ends_with(trimmed, rendered[0..rendered_len]));
    try std.testing.expectEqual(@as(?usize, 1), string.memchr_inv(trimmed[0..5], 'g'));

    const choices = [_][]const u8{ "idle", trimmed, "kept=stale\n" };
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&choices, trimmed));
    try std.testing.expectEqual(@as(?usize, 2), string.sysfs_match_string(&choices, "kept=stale"));

    var padded = [_]u8{0xaa}**96;
    try std.testing.expectEqual(@as(isize, @intCast(trimmed.len)), string.strscpy_pad(&padded, trimmed));
    try std.testing.expectEqual(@as(u8, 0), padded[trimmed.len]);
    try std.testing.expectEqual(@as(?usize, null), string.memchr_inv(padded[trimmed.len + 1 ..], 0));

    var entries = [_]Entry{
        .{ .key = second_gap, .serial = 0 },
        .{ .key = first_gap, .serial = 1 },
        .{ .key = find_bit.findFirstBit(&replaced, nbits), .serial = 2 },
        .{ .key = find_bit.findLastBit(&replaced, nbits), .serial = 3 },
    };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, entryLess);
    }

    try std.testing.expectEqual(first_gap, keyOf(rbtree.firstCached(&root) orelse return error.TestUnexpectedResult));
    const promoted = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 3), keyOf(promoted));

    var order: [4]usize = undefined;
    var count = collectKeys(&root.root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 3, second_gap, bits_per_long + 9 }, order[0..count]);

    var reseed = Entry{ .key = first_gap, .serial = 9 };
    const leftmost = rbtree.addCached(&reseed.node, &root, entryLess) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(first_gap, keyOf(leftmost));
    try std.testing.expectEqual(first_gap, keyOf(rbtree.firstCached(&root) orelse return error.TestUnexpectedResult));

    rbtree.eraseInitCached(&reseed.node, &root);
    try std.testing.expect(rbtree.emptyNode(&reseed.node));
    try std.testing.expectEqual(@as(usize, 3), keyOf(rbtree.firstCached(&root) orelse return error.TestUnexpectedResult));

    count = collectKeys(&root.root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 3, second_gap, bits_per_long + 9 }, order[0..count]);
}
