const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

fn setBit(words: []Word, bit: usize) void {
    words[bit / bits_per_long] |= @as(Word, 1) << @intCast(bit & (bits_per_long - 1));
}

fn expectBit(words: []const Word, bit: usize) !void {
    try std.testing.expect((words[bit / bits_per_long] & (@as(Word, 1) << @intCast(bit & (bits_per_long - 1)))) != 0);
}

const Entry = struct {
    key: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    return entryFromNode(lhs).key < entryFromNode(rhs).key;
}

fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const usize = @ptrCast(@alignCast(key_ptr));
    const node_key = entryFromNode(node).key;
    if (key.* < node_key) return -1;
    if (key.* > node_key) return 1;
    return 0;
}

fn collectForward(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var current = rbtree.first(root);
    while (current) |node| : (current = rbtree.next(node)) {
        out[count] = entryFromNode(node).key;
        count += 1;
    }
    return count;
}

fn nulLen(buf: []const u8) usize {
    return std.mem.indexOfScalar(u8, buf, 0) orelse buf.len;
}

test "phase1 helper ports A mirror carry replay" {
    const nbits = bits_per_long + 38;
    const extended_bits = nbits + 11;
    const nwords = 3;
    try std.testing.expect(nwords >= bitmap.bitsToWords(extended_bits));

    var old: [nwords]Word = undefined;
    var new: [nwords]Word = undefined;
    var mask: [nwords]Word = undefined;
    var replaced: [nwords]Word = undefined;
    var copied: [nwords]Word = undefined;
    var carry: [nwords]Word = undefined;
    var mirrored: [nwords]Word = undefined;
    var dropped_carry: [nwords]Word = undefined;
    @memset(&old, 0);
    @memset(&new, 0);
    @memset(&mask, 0);
    @memset(&replaced, 0);
    @memset(&copied, ~@as(Word, 0));
    @memset(&carry, 0);
    @memset(&mirrored, 0);
    @memset(&dropped_carry, 0);

    for ([_]usize{ 3, 7, bits_per_long, bits_per_long + 8, nbits - 4 }) |bit| setBit(&old, bit);
    for ([_]usize{ 5, 7, bits_per_long + 1, bits_per_long + 16, nbits - 1 }) |bit| setBit(&new, bit);
    for ([_]usize{ 3, 5, bits_per_long, bits_per_long + 1, bits_per_long + 16, nbits - 1 }) |bit| setBit(&mask, bit);
    for ([_]usize{ 12, bits_per_long + 1, bits_per_long + 26 }) |bit| setBit(&carry, bit);

    bitmap.bitmap_replace(&replaced, &old, &new, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 7), bitmap.bitmap_weight(&replaced, nbits));
    for ([_]usize{ 5, 7, bits_per_long + 1, bits_per_long + 8, bits_per_long + 16, nbits - 4, nbits - 1 }) |bit| {
        try expectBit(&replaced, bit);
    }
    try std.testing.expectEqual(@as(usize, extended_bits), find_bit.find_next_bit(&replaced, extended_bits, nbits));

    bitmap.bitmap_copy_and_extend(&copied, &replaced, nbits, extended_bits);
    try std.testing.expectEqual(@as(usize, extended_bits), find_bit.find_next_bit(&copied, extended_bits, nbits));

    bitmap.bitmap_or(&mirrored, &copied, &carry, extended_bits);
    try std.testing.expectEqual(@as(usize, 9), bitmap.bitmap_weight(&mirrored, extended_bits));
    try std.testing.expectEqual(@as(usize, 12), find_bit.find_next_bit(&mirrored, extended_bits, 8));

    try std.testing.expect(bitmap.bitmap_andnot(&dropped_carry, &mirrored, &carry, extended_bits));
    try std.testing.expectEqual(bitmap.bitmap_weight(&copied, extended_bits) - 1, bitmap.bitmap_weight(&dropped_carry, extended_bits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 8), find_bit.find_next_andnot_bit(&mirrored, &carry, extended_bits, bits_per_long + 2));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.find_next_clump8(&clump, &mirrored, extended_bits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_0010), clump);

    var rendered: [96]u8 = undefined;
    @memset(&rendered, 0);
    _ = bitmap.scnprintf(&mirrored, extended_bits, &rendered);
    try std.testing.expectEqualStrings("5,7,12,65,72,80,90,98,101", rendered[0..nulLen(&rendered)]);

    var label = [_]u8{ ' ', 'm', 'i', 'r', 'r', 'o', 'r', '-', 'c', 'a', 'r', 'r', 'y', ' ', 0, 'x' };
    const trimmed = string.strim(&label);
    try std.testing.expectEqualStrings("mirror-carry", trimmed);
    _ = string.strreplace(trimmed, '-', '_');
    try std.testing.expectEqualStrings("mirror_carry", trimmed);
    try std.testing.expectEqual(@as(usize, 6), string.strHasPrefix(trimmed, "mirror"));
    try std.testing.expect(string.strEndsWith(trimmed, "carry"));
    const names = [_][]const u8{ "base", "mirror_carry\n", "tail" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&names, "mirror_carry"));
    try std.testing.expectEqual(@as(?usize, 2), string.matchString(&names, "tail"));

    const keys = [_]usize{ 90, 5, 72, 12, 65, 80, 65, 100, 7, 97 };
    var entries: [keys.len]Entry = undefined;
    var root = rbtree.RootCached.init();
    for (keys, 0..) |key, idx| {
        entries[idx] = .{ .key = key };
        _ = rbtree.addCached(&entries[idx].node, &root, less);
    }

    try std.testing.expectEqual(@as(usize, 5), entryFromNode(rbtree.firstCached(&root).?).key);

    const duplicate_key: usize = 65;
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, cmpKey);
    var duplicate_count: usize = 0;
    while (iter.next()) |node| {
        try std.testing.expectEqual(duplicate_key, entryFromNode(node).key);
        duplicate_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), duplicate_count);

    var replacement = Entry{ .key = 72 };
    const victim = rbtree.find(&replacement.key, &root.root, cmpKey).?;
    rbtree.replaceNodeCached(victim, &replacement.node, &root);

    const leftmost = rbtree.eraseCached(rbtree.firstCached(&root).?, &root).?;
    try std.testing.expectEqual(@as(usize, 7), entryFromNode(leftmost).key);

    var order: [keys.len]usize = undefined;
    const count = collectForward(&root.root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 7, 12, 65, 65, 72, 80, 90, 97, 100 }, order[0..count]);
}
