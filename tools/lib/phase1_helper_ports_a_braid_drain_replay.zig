const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

fn setBit(map: []Word, bit: usize) void {
    map[bit / bits_per_long] |= @as(Word, 1) << @intCast(bit & (bits_per_long - 1));
}

const Entry = struct {
    key: usize,
    id: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn lessEntry(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const left = entryFromNode(lhs);
    const right = entryFromNode(rhs);
    if (left.key == right.key) {
        return left.id < right.id;
    }
    return left.key < right.key;
}

test "lane06 braid drain ties bitmap find-bit string and cached rbtree helpers" {
    const nbits = bits_per_long * 2 + 13;
    const b = bits_per_long;
    const tail = bits_per_long * 2;

    var old = [_]Word{0} ** 3;
    var new = [_]Word{0} ** 3;
    var mask = [_]Word{0} ** 3;
    var replaced = [_]Word{0} ** 3;
    var blocked = [_]Word{0} ** 3;
    var drained = [_]Word{0} ** 3;
    var mirrored = [_]Word{0} ** 3;

    for ([_]usize{ 1, 3, b + 1, b + 9, tail + 4 }) |bit| {
        setBit(&old, bit);
    }
    for ([_]usize{ 2, 3, 5, b + 4, b + 11, tail + 2, tail + 7 }) |bit| {
        setBit(&new, bit);
    }
    bitmap.setRange(&mask, 2, 6);
    bitmap.setRange(&mask, b + 4, 8);
    bitmap.setRange(&mask, tail + 2, 6);

    bitmap.bitmap_replace(&replaced, &old, &new, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 9), bitmap.weight(&replaced, nbits));
    try std.testing.expect(bitmap.subset(&replaced, &replaced, nbits));
    try std.testing.expect(bitmap.intersects(&replaced, &old, nbits));

    for ([_]usize{ 3, b + 9, tail + 7 }) |bit| {
        setBit(&blocked, bit);
    }
    try std.testing.expect(bitmap.andNotBits(&drained, &replaced, &blocked, nbits));
    try std.testing.expectEqual(@as(usize, 7), bitmap.weight(&drained, nbits));

    bitmap.xorBits(&mirrored, &drained, &blocked, nbits);
    try std.testing.expectEqual(@as(usize, 10), bitmap.weight(&mirrored, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstAndNotBit(&replaced, &blocked, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextAndNotBit(&replaced, &blocked, nbits, 3));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(&drained, nbits));
    try std.testing.expectEqual(@as(usize, tail + 2), find_bit.findLastBit(&drained, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&clump, &drained, nbits, 1));
    try std.testing.expectEqual(@as(u8, 0x26), clump);
    try std.testing.expectEqual(@as(usize, b), find_bit.findNextClump8(&clump, &drained, nbits, b + 1));
    try std.testing.expectEqual(@as(u8, 0x12), clump);
    try std.testing.expectEqual(@as(usize, b + 8), find_bit.findNextClump8(&clump, &drained, nbits, b + 5));
    try std.testing.expectEqual(@as(u8, 0x08), clump);

    var rendered_buf: [96]u8 = undefined;
    @memset(&rendered_buf, 0);
    const rendered_len = bitmap.scnprintf(&drained, nbits, &rendered_buf);
    var expected_storage: [64]u8 = undefined;
    const expected = try std.fmt.bufPrint(&expected_storage, "1-2,5,{d},{d},{d},{d}", .{ b + 1, b + 4, b + 11, tail + 2 });
    try std.testing.expectEqualStrings(expected, rendered_buf[0..rendered_len]);

    var token_storage: [128]u8 = undefined;
    @memset(&token_storage, 0);
    const token_len = try std.fmt.bufPrint(&token_storage, "  {s}\n", .{rendered_buf[0..rendered_len]});
    const token = string.strim(token_storage[0..token_len.len]);
    try std.testing.expectEqualStrings(expected, token);
    try std.testing.expect(string.strstarts(token, "1-2"));

    var tail_storage: [24]u8 = undefined;
    const tail_token = try std.fmt.bufPrint(&tail_storage, "{d}", .{tail + 2});
    try std.testing.expect(string.strEndsWith(token, tail_token));

    const scanned_len = string.strreplace(token, ',', '|');
    try std.testing.expectEqual(expected.len, scanned_len);
    try std.testing.expectEqual(@as(?usize, 3), std.mem.indexOfScalar(u8, token, '|'));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv("======", '='));
    try std.testing.expectEqual(@as(?usize, 3), string.memchrInv("===|==", '='));

    var sysfs_storage: [128]u8 = undefined;
    const sysfs_token = try std.fmt.bufPrint(&sysfs_storage, "{s}\n", .{token});
    const options = [_][]const u8{ "cold", token, "hot" };
    try std.testing.expect(string.sysfsStreq(sysfs_token, token));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&options, sysfs_token));

    var entries = [_]Entry{
        .{ .key = b + 1, .id = 0 },
        .{ .key = 1, .id = 1 },
        .{ .key = b + 4, .id = 2 },
        .{ .key = 5, .id = 3 },
        .{ .key = tail + 2, .id = 4 },
        .{ .key = 2, .id = 5 },
        .{ .key = b + 11, .id = 6 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, lessEntry);
    }
    try std.testing.expectEqual(@as(usize, 1), entryFromNode(rbtree.firstCached(&root).?).key);

    var replacement = Entry{ .key = b + 4, .id = 99 };
    rbtree.replaceNodeCached(&entries[2].node, &replacement.node, &root);
    var replaced_seen = false;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry = entryFromNode(node);
        if (entry.key == b + 4) {
            try std.testing.expectEqual(@as(usize, 99), entry.id);
            replaced_seen = true;
        }
    }
    try std.testing.expect(replaced_seen);

    try std.testing.expectEqual(entryFromNode(rbtree.eraseCached(&entries[1].node, &root).?).key, 2);
    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(usize, 2), entryFromNode(rbtree.firstCached(&root).?).key);

    var drained_keys: [5]usize = undefined;
    var drained_count: usize = 0;
    while (rbtree.firstCached(&root)) |node| {
        drained_keys[drained_count] = entryFromNode(node).key;
        drained_count += 1;
        _ = rbtree.eraseCached(node, &root);
    }
    try std.testing.expectEqual(@as(usize, 5), drained_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 5, b + 1, b + 11, tail + 2 }, drained_keys[0..drained_count]);
    try std.testing.expect(rbtree.emptyRoot(&root.root));
}
