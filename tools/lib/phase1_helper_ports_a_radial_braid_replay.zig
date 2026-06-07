const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn collectForward(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.first(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "Lane 06 radial braid ties bitmap cursors strings and cached rbtree order" {
    const nbits = bits_per_long + 8;
    var low_band = [_]Word{ 0, 0 };
    var tail_band = [_]Word{ 0, 0 };
    var braided = [_]Word{ 0, 0 };
    var old_only = [_]Word{ 0, 0 };

    bitmap.setRange(&low_band, 1, 4);
    bitmap.setRange(&tail_band, bits_per_long + 3, 2);
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&low_band, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&tail_band, nbits));

    bitmap.orBits(&braided, &low_band, &tail_band, nbits);
    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&braided, nbits));
    try std.testing.expect(bitmap.intersects(&braided, &tail_band, nbits));
    try std.testing.expect(bitmap.subset(&tail_band, &braided, nbits));

    try std.testing.expect(bitmap.andNotBits(&old_only, &braided, &tail_band, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&old_only, nbits));
    try std.testing.expect(!bitmap.intersects(&old_only, &tail_band, nbits));

    const first = find_bit.findFirstBit(&braided, nbits);
    const next_tail = find_bit.findNextBit(&braided, nbits, bits_per_long);
    const last = find_bit.findLastBit(&braided, nbits);
    try std.testing.expectEqual(@as(usize, 1), first);
    try std.testing.expectEqual(bits_per_long + 3, next_tail);
    try std.testing.expectEqual(bits_per_long + 4, last);

    var clump: u8 = 0;
    const clump_offset = find_bit.findFirstClump8(&clump, &braided, nbits);
    try std.testing.expectEqual(@as(usize, 0), clump_offset);
    try std.testing.expectEqual(@as(u8, 0b0001_1110), clump);

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&braided, nbits, &rendered);
    var expected: [64]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(&expected, "1-4,{d}-{d}", .{ bits_per_long + 3, bits_per_long + 4 });
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);

    var label = [_]u8{0} ** 64;
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), string.strscpyPad(&label, rendered[0..rendered_len]));
    _ = string.strreplace(&label, ',', ':');
    try std.testing.expect(string.strstarts(&label, "1-4"));
    try std.testing.expect(string.strEndsWith(&label, expected_text[expected_text.len - 2 ..]));
    try std.testing.expectEqual(@as(?usize, 0), string.memchrInv(label[0..1], 'x'));

    var entries = [_]Entry{
        .{ .key = last },
        .{ .key = first },
        .{ .key = next_tail },
        .{ .key = clump_offset },
    };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    const leftmost = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    const leftmost_entry: *const Entry = @fieldParentPtr("node", leftmost);
    try std.testing.expectEqual(clump_offset, leftmost_entry.key);

    const wanted_tail = next_tail;
    const found_tail = rbtree.find(&wanted_tail, &root.root, cmpKey) orelse return error.TestUnexpectedResult;
    const found_tail_entry: *const Entry = @fieldParentPtr("node", found_tail);
    try std.testing.expectEqual(next_tail, found_tail_entry.key);

    _ = rbtree.eraseCached(&entries[0].node, &root);
    var order: [4]usize = undefined;
    const count = collectForward(&root.root, &order);
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ clump_offset, first, next_tail }, order[0..count]);
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
