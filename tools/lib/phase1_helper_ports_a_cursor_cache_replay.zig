const std = @import("std");
const testing = std.testing;

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

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry = entryFromNode(lhs);
    const rhs_entry = entryFromNode(rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *align(1) const usize = @ptrCast(key);
    const entry = entryFromNode(node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn nodeKey(node: ?*rbtree.Node) ?usize {
    const found = node orelse return null;
    return entryFromNode(found).key;
}

fn nodeSerial(node: *const rbtree.Node) usize {
    return entryFromNode(node).serial;
}

test "lane06 cursor cache replay aligns bitmap cursors strings and rbtree cache" {
    const nbits = bits_per_long + 12;
    const word_count = bitmap.bitsToWords(nbits);
    try testing.expectEqual(@as(usize, 2), word_count);

    var base = [_]Word{ 0, 0 };
    var overlay = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };

    bitmap.bitmap_set(&base, 1, 3);
    bitmap.bitmap_set(&base, bits_per_long + 2, 3);
    bitmap.bitmap_set(&overlay, 3, 1);
    bitmap.bitmap_set(&overlay, bits_per_long + 5, 1);
    bitmap.bitmap_set(&overlay, bits_per_long + 7, 1);
    bitmap.bitmap_set(&mask, 2, 2);
    bitmap.bitmap_set(&mask, bits_per_long + 5, 3);

    var replaced = [_]Word{ 0, 0 };
    bitmap.bitmap_replace(&replaced, &base, &overlay, &mask, nbits);

    var unioned = [_]Word{ 0, 0 };
    try testing.expectEqual(@as(usize, 8), bitmap.bitmap_weighted_or(&unioned, &replaced, &base, nbits));

    var cache_gap = [_]Word{ 0, 0 };
    try testing.expect(bitmap.bitmap_andnot(&cache_gap, &unioned, &base, nbits));
    try testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&cache_gap, nbits));

    try testing.expectEqual(bits_per_long + 5, find_bit.findFirstBit(&cache_gap, nbits));
    try testing.expectEqual(bits_per_long + 7, find_bit.findNextBit(&cache_gap, nbits, bits_per_long + 6));
    try testing.expectEqual(bits_per_long + 6, find_bit.findNextZeroBit(&unioned, nbits, bits_per_long + 6));
    try testing.expectEqual(@as(usize, 2), find_bit.findFirstAndBit(&unioned, &mask, nbits));
    try testing.expectEqual(bits_per_long + 5, find_bit.findFirstAndNotBit(&unioned, &base, nbits));
    try testing.expectEqual(bits_per_long + 7, find_bit.findLastBit(&unioned, nbits));

    var clump: u8 = 0;
    try testing.expectEqual(bits_per_long, find_bit.findNextClump8(&clump, &cache_gap, nbits, bits_per_long + 5));
    try testing.expectEqual(@as(u8, 0b1010_0000), clump);

    var range_buf: [32]u8 = undefined;
    const range_len = bitmap.bitmap_scnprintf(&cache_gap, nbits, &range_buf);
    var expected_range_buf: [32]u8 = undefined;
    const expected_range = try std.fmt.bufPrint(
        &expected_range_buf,
        "{d},{d}",
        .{ bits_per_long + 5, bits_per_long + 7 },
    );
    try testing.expectEqualStrings(expected_range, range_buf[0..range_len]);

    var padded: [32]u8 = @splat(0xaa);
    try testing.expectEqual(@as(isize, @intCast(range_len)), string.strscpyPad(&padded, range_buf[0..range_len]));
    try testing.expectEqual(@as(u8, 0), padded[range_len]);
    try testing.expectEqual(@as(?usize, null), string.memchrInv(padded[range_len + 1 ..], 0));
    try testing.expectEqual(range_len, string.strreplace(padded[0 .. range_len + 1], ',', '|'));

    var normalized = [_]u8{ ' ', 'c', 'u', 'r', 's', 'o', 'r', ' ', 'c', 'a', 'c', 'h', 'e', 0, 'x' };
    const trimmed = string.strim(&normalized);
    try testing.expectEqualStrings("cursor cache", trimmed);
    const compact = string.removeSpaces(trimmed);
    try testing.expectEqualStrings("cursorcache", compact);
    try testing.expectEqual(@as(usize, 6), string.strHasPrefix(compact, "cursor"));
    try testing.expect(string.strEndsWith(compact, "cache"));

    const haystack = [_][]const u8{
        "fallback",
        "cursorcache\n",
        compact,
    };
    try testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&haystack, "cursorcache"));
    try testing.expectEqual(@as(?usize, 2), string.matchString(&haystack, compact));

    var entries = [_]Entry{
        .{ .key = bits_per_long + 7, .serial = 0 },
        .{ .key = 1, .serial = 1 },
        .{ .key = bits_per_long + 5, .serial = 2 },
        .{ .key = bits_per_long + 7, .serial = 3 },
        .{ .key = bits_per_long + 3, .serial = 4 },
    };
    var replacement = Entry{ .key = bits_per_long + 3, .serial = 9 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try testing.expectEqual(@as(?usize, 1), nodeKey(rbtree.firstCached(&root)));
    try testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    const duplicate_key: usize = bits_per_long + 7;
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, keyCmp);
    var duplicate_serials: [2]usize = undefined;
    var duplicate_count: usize = 0;
    while (iter.next()) |node| {
        duplicate_serials[duplicate_count] = nodeSerial(node);
        duplicate_count += 1;
    }
    try testing.expectEqual(@as(usize, 2), duplicate_count);
    try testing.expectEqualSlices(usize, &[_]usize{ 0, 3 }, duplicate_serials[0..duplicate_count]);

    const promoted = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try testing.expectEqual(bits_per_long + 3, entryFromNode(promoted).key);
    try testing.expectEqual(@as(?usize, bits_per_long + 3), nodeKey(rbtree.firstCached(&root)));

    rbtree.replaceNodeCached(&entries[4].node, &replacement.node, &root);
    try testing.expectEqual(@as(?usize, bits_per_long + 3), nodeKey(rbtree.firstCached(&root)));
    try testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&replacement.node, &root);
    try testing.expect(rbtree.emptyNode(&replacement.node));
    try testing.expectEqual(@as(?usize, bits_per_long + 5), nodeKey(rbtree.firstCached(&root)));

    rbtree.eraseInitCached(&entries[2].node, &root);
    rbtree.eraseInitCached(&entries[0].node, &root);
    rbtree.eraseInitCached(&entries[3].node, &root);
    try testing.expect(rbtree.emptyRoot(&root.root));
    try testing.expect(root.leftmost == null);
}
