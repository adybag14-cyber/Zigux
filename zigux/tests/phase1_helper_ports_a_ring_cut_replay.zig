const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;

const Entry = struct {
    key: usize,
    tag: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index);
}

fn set(map: []Word, bit_index: usize) void {
    map[bit_index / bitmap.bits_per_long] |= bit(bit_index & (bitmap.bits_per_long - 1));
}

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn lessByKey(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry = entryFromNode(lhs);
    const rhs_entry = entryFromNode(rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn compareKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const usize = @ptrCast(@alignCast(key_ptr));
    const entry = entryFromNode(node);
    if (key.* < entry.key) return -1;
    if (key.* > entry.key) return 1;
    return 0;
}

fn collectAndNotCursors(src: []const Word, cut: []const Word, nbits: usize, out: []usize) usize {
    var count: usize = 0;
    var cursor = find_bit.findFirstAndNotBit(src, cut, nbits);
    while (cursor < nbits) {
        out[count] = cursor;
        count += 1;
        cursor = find_bit.findNextAndNotBit(src, cut, nbits, cursor + 1);
    }
    return count;
}

test "ring cut replay connects bitmap cursors to strings and cached rbtree erase" {
    const nbits = bitmap.bits_per_long + 19;
    var ring = [_]Word{0} ** 2;
    var cut = [_]Word{0} ** 2;
    var carved = [_]Word{0} ** 2;

    for ([_]usize{ 2, 3, 4, 9, 10, 11, 12, bitmap.bits_per_long - 1, bitmap.bits_per_long, bitmap.bits_per_long + 1, bitmap.bits_per_long + 8, bitmap.bits_per_long + 9, bitmap.bits_per_long + 18 }) |idx| {
        set(&ring, idx);
    }
    for ([_]usize{ 3, 10, bitmap.bits_per_long, bitmap.bits_per_long + 9, bitmap.bits_per_long + 18 }) |idx| {
        set(&cut, idx);
    }

    try std.testing.expect(bitmap.andNotBits(&carved, &ring, &cut, nbits));
    try std.testing.expectEqual(@as(usize, 8), bitmap.weight(&carved, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstAndNotBit(&ring, &cut, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findNextAndNotBit(&ring, &cut, nbits, 3));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 8), find_bit.findNextAndNotBit(&ring, &cut, nbits, bitmap.bits_per_long + 2));
    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(&ring, &cut, nbits, bitmap.bits_per_long + 10));

    var rendered = [_]u8{0} ** 96;
    const rendered_len = bitmap.scnprintf(&carved, nbits, &rendered);
    const rendered_text = rendered[0..rendered_len];
    try std.testing.expectEqualStrings("2,4,9,11-12,63,65,72", rendered_text);

    var padded = [_]u8{0xcc} ** 96;
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), string.strscpyPad(&padded, rendered_text));
    try std.testing.expectEqual(@as(usize, 2), string.strHasPrefix(&padded, "2,"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&[_][]const u8{ "cut", rendered_text, "keep" }, rendered_text));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&[_][]const u8{ "cut", "2,4,9,11-12,63,65,72\n", "keep" }, rendered_text));

    var cursors = [_]usize{0} ** 12;
    const cursor_count = collectAndNotCursors(&ring, &cut, nbits, &cursors);
    try std.testing.expectEqual(@as(usize, 8), cursor_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 4, 9, 11, 12, 63, 65, 72 }, cursors[0..cursor_count]);

    var entries: [8]Entry = undefined;
    for (cursors[0..cursor_count], 0..) |cursor, idx| {
        entries[idx] = .{ .key = cursor, .tag = idx };
    }

    var root = rbtree.RootCached.init();
    for (entries[0..cursor_count]) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, lessByKey);
    }

    try std.testing.expect(rbtree.firstCached(&root) == &entries[0].node);
    var forward = [_]usize{0} ** 8;
    var idx: usize = 0;
    var node = rbtree.first(&root.root);
    while (node) |current| {
        forward[idx] = entryFromNode(current).key;
        idx += 1;
        node = rbtree.next(current);
    }
    try std.testing.expectEqualSlices(usize, cursors[0..cursor_count], forward[0..idx]);

    var target_key: usize = 11;
    var match_iter = rbtree.matchIterator(&target_key, &root.root, compareKey);
    const matched = match_iter.next() orelse return error.TestExpectedEqual;
    try std.testing.expectEqual(@as(usize, 11), entryFromNode(matched).key);
    try std.testing.expect(match_iter.next() == null);

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expect(rbtree.firstCached(&root) == &entries[1].node);

    target_key = 63;
    const middle = rbtree.find(&target_key, &root.root, compareKey) orelse return error.TestExpectedEqual;
    rbtree.eraseInitCached(middle, &root);
    try std.testing.expect(rbtree.emptyNode(middle));
    try std.testing.expect(rbtree.find(&target_key, &root.root, compareKey) == null);
}
