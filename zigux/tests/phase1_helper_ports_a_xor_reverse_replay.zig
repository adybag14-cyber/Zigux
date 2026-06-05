const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: usize,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const usize = @ptrCast(@alignCast(key_ptr));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (key.* < entry.key) return -1;
    if (key.* > entry.key) return 1;
    return 0;
}

fn collectReverse(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.last(root);
    while (cursor) |node| : (cursor = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

fn tokenValue(token: []const u8) !usize {
    return std.fmt.parseUnsigned(usize, token, 10);
}

test "helper ports A xor and reverse traversal replay" {
    const nbits = bits_per_long * 2 + 10;
    const words = 3;
    try std.testing.expectEqual(words, bitmap.bitsToWords(nbits));

    var lhs = [_]Word{0} ** words;
    var rhs = [_]Word{0} ** words;
    var xor_map = [_]Word{0} ** words;
    var weighted_xor = [_]Word{0} ** words;

    bitmap.setRange(&lhs, 0, 1);
    bitmap.setRange(&lhs, 3, 1);
    bitmap.setRange(&lhs, bits_per_long + 1, 1);
    bitmap.setRange(&lhs, bits_per_long * 2 + 4, 1);

    bitmap.setRange(&rhs, 3, 1);
    bitmap.setRange(&rhs, 7, 1);
    bitmap.setRange(&rhs, bits_per_long + 1, 1);
    bitmap.setRange(&rhs, bits_per_long + 8, 1);
    bitmap.setRange(&rhs, bits_per_long * 2 + 4, 1);
    bitmap.setRange(&rhs, bits_per_long * 2 + 8, 1);
    rhs[words - 1] |= @as(Word, 1) << @intCast(bits_per_long - 1);

    bitmap.xorBits(&xor_map, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&xor_map, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weightedXor(&weighted_xor, &lhs, &rhs, nbits));
    try std.testing.expect(bitmap.equal(&xor_map, &weighted_xor, nbits));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstBit(&xor_map, nbits));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextBit(&xor_map, nbits, 1));
    try std.testing.expectEqual(bits_per_long * 2 + 8, find_bit.findLastBit(&xor_map, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findNextZeroBit(&xor_map, nbits, 0));

    var rendered_buffer = [_]u8{0} ** 96;
    const rendered_len = bitmap.scnprintf(&xor_map, nbits, &rendered_buffer);
    const rendered = rendered_buffer[0..rendered_len];

    var label = [_]u8{0} ** 128;
    try std.testing.expectEqual(@as(usize, 4), string.strlcpy(&label, "xor:"));
    @memcpy(label[4 .. 4 + rendered_len], rendered);
    label[4 + rendered_len] = 0;
    _ = string.replaceChar(&label, ',', '|');
    const compact = label[0 .. 4 + rendered_len];
    try std.testing.expect(string.strHasPrefix(compact, "xor:0|7") != 0);

    var padded = [_]u8{0xaa} ** 64;
    try std.testing.expectEqual(@as(isize, @intCast(compact.len)), string.strscpyPad(&padded, compact));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(padded[compact.len + 1 ..], 0));

    var keys: [4]usize = undefined;
    var token_iter = std.mem.splitScalar(u8, compact[4..], '|');
    var key_count: usize = 0;
    while (token_iter.next()) |token| {
        keys[key_count] = try tokenValue(token);
        key_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 4), key_count);

    var entries: [4]Entry = undefined;
    for (keys[0..key_count], 0..) |key, idx| {
        entries[idx] = .{ .key = key, .serial = idx + 1 };
    }

    var root = rbtree.Root.init();
    for (entries[0..key_count]) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var replacement = Entry{ .key = keys[2], .serial = 42 };
    rbtree.replaceNode(&entries[2].node, &replacement.node, &root);
    const found = rbtree.find(&keys[2], &root, cmpKey) orelse return error.ExpectedReplacement;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(usize, 42), found_entry.serial);

    var reverse: [4]usize = undefined;
    var count = collectReverse(&root, &reverse);
    try std.testing.expectEqualSlices(usize, &[_]usize{ keys[3], keys[2], keys[1], keys[0] }, reverse[0..count]);

    rbtree.erase(&entries[3].node, &root);
    count = collectReverse(&root, &reverse);
    try std.testing.expectEqualSlices(usize, &[_]usize{ keys[2], keys[1], keys[0] }, reverse[0..count]);
}
