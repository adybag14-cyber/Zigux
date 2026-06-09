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

fn collectKeys(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var current = rbtree.first(root);
    while (current) |node| : (current = rbtree.next(node)) {
        out[count] = entryFromNode(node).key;
        count += 1;
    }
    return count;
}

test "lane06 stride halo replay keeps helper ports aligned" {
    const nbits = bits_per_long + 16;
    const word_count = bitmap.bitsToWords(nbits);
    try testing.expectEqual(@as(usize, 2), word_count);

    var base = [_]Word{ 0, 0 };
    var overlay = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };

    bitmap.bitmap_set(&base, 4, 4);
    bitmap.bitmap_set(&base, bits_per_long + 1, 2);
    bitmap.bitmap_set(&base, bits_per_long + 10, 2);

    bitmap.bitmap_set(&overlay, 2, 2);
    bitmap.bitmap_set(&overlay, bits_per_long + 3, 4);
    bitmap.bitmap_set(&overlay, bits_per_long + 12, 1);

    bitmap.bitmap_set(&mask, 2, 6);
    bitmap.bitmap_set(&mask, bits_per_long + 2, 5);
    bitmap.bitmap_set(&mask, bits_per_long + 12, 1);

    var stride = [_]Word{ 0, 0 };
    bitmap.bitmap_replace(&stride, &base, &overlay, &mask, nbits);
    try testing.expectEqual(@as(usize, 10), bitmap.bitmap_weight(&stride, nbits));

    var guard = [_]Word{ 0, 0 };
    bitmap.bitmap_set(&guard, 3, 1);
    bitmap.bitmap_set(&guard, bits_per_long + 4, 1);
    bitmap.bitmap_set(&guard, bits_per_long + 6, 1);
    bitmap.bitmap_set(&guard, bits_per_long + 11, 1);

    var halo = [_]Word{ 0, 0 };
    try testing.expect(bitmap.bitmap_andnot(&halo, &stride, &guard, nbits));
    try testing.expectEqual(@as(usize, 6), bitmap.bitmap_weight(&halo, nbits));
    try testing.expect(bitmap.bitmap_subset(&halo, &stride, nbits));
    try testing.expect(bitmap.bitmap_intersects(&stride, &guard, nbits));

    var shadow = [_]Word{ 0, 0 };
    bitmap.bitmap_set(&shadow, 2, 1);
    bitmap.bitmap_set(&shadow, 5, 1);
    bitmap.bitmap_set(&shadow, bits_per_long + 1, 1);
    bitmap.bitmap_set(&shadow, bits_per_long + 12, 1);

    var toggled = [_]Word{ 0, 0 };
    bitmap.bitmap_xor(&toggled, &halo, &shadow, nbits);
    try testing.expectEqual(@as(usize, 4), bitmap.bitmap_weight(&toggled, nbits));

    try testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&halo, nbits));
    try testing.expectEqual(bits_per_long + 1, find_bit.findNextBit(&halo, nbits, 3));
    try testing.expectEqual(@as(usize, 3), find_bit.findNextAndBit(&stride, &guard, nbits, 0));
    try testing.expectEqual(bits_per_long + 1, find_bit.findNextAndNotBit(&stride, &guard, nbits, 4));
    try testing.expectEqual(@as(usize, 5), find_bit.findNextBit(&toggled, nbits, 4));
    try testing.expectEqual(@as(usize, 4), find_bit.findNextZeroBit(&stride, nbits, 2));
    try testing.expectEqual(bits_per_long + 12, find_bit.findLastBit(&halo, nbits));

    var clump: u8 = 0;
    try testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&clump, &halo, nbits, 0));
    try testing.expectEqual(@as(u8, 0x04), clump);
    try testing.expectEqual(bits_per_long, find_bit.findNextClump8(&clump, &halo, nbits, bits_per_long));
    try testing.expectEqual(@as(u8, 0x2a), clump);
    try testing.expectEqual(bits_per_long + 8, find_bit.findNextClump8(&clump, &halo, nbits, bits_per_long + 8));
    try testing.expectEqual(@as(u8, 0x14), clump);

    var rendered_buf: [48]u8 = undefined;
    const rendered_len = bitmap.bitmap_scnprintf(&halo, nbits, &rendered_buf);
    const rendered = rendered_buf[0..rendered_len];

    var expected_buf: [48]u8 = undefined;
    const expected = try std.fmt.bufPrint(
        &expected_buf,
        "2,{d},{d},{d},{d},{d}",
        .{
            bits_per_long + 1,
            bits_per_long + 3,
            bits_per_long + 5,
            bits_per_long + 10,
            bits_per_long + 12,
        },
    );
    try testing.expectEqualStrings(expected, rendered);

    var decorated_buf: [64]u8 = undefined;
    const decorated = try std.fmt.bufPrint(
        &decorated_buf,
        " \t2, {d}, {d}, {d}, {d}, {d}\n",
        .{
            bits_per_long + 1,
            bits_per_long + 3,
            bits_per_long + 5,
            bits_per_long + 10,
            bits_per_long + 12,
        },
    );
    decorated_buf[decorated.len] = 0;

    const trimmed = string.strim(&decorated_buf);
    const compact = string.removeSpaces(trimmed);
    try testing.expectEqualStrings(rendered, compact);

    var padded: [64]u8 = @splat(0xaa);
    try testing.expectEqual(@as(isize, @intCast(compact.len)), string.strscpyPad(&padded, compact));
    try testing.expectEqual(@as(u8, 0), padded[compact.len]);
    try testing.expectEqual(@as(?usize, null), string.memchrInv(padded[compact.len + 1 ..], 0));
    try testing.expectEqual(@as(?usize, 1), string.strnchr(padded[0..compact.len], 4, ','));
    try testing.expect(string.strstarts(padded[0..compact.len], "2,"));
    try testing.expect(string.strEndsWith(padded[0..compact.len], rendered[rendered.len - 2 ..]));
    try testing.expectEqual(compact.len, string.strreplace(padded[0 .. compact.len + 1], ',', '|'));

    const sysfs_choices = [_][]const u8{
        "idle",
        padded[0..compact.len],
        "miss\n",
    };
    const exact_choices = [_][]const u8{
        "idle",
        rendered,
        padded[0..compact.len],
    };
    try testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs_choices, padded[0..compact.len]));
    try testing.expectEqual(@as(?usize, 1), string.matchString(&exact_choices, rendered));

    var entries = [_]Entry{
        .{ .key = bits_per_long + 5, .serial = 0 },
        .{ .key = 2, .serial = 1 },
        .{ .key = bits_per_long + 12, .serial = 2 },
        .{ .key = bits_per_long + 1, .serial = 3 },
        .{ .key = bits_per_long + 10, .serial = 4 },
        .{ .key = bits_per_long + 3, .serial = 5 },
        .{ .key = bits_per_long + 5, .serial = 6 },
    };
    var replacement = Entry{ .key = bits_per_long + 1, .serial = 9 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try testing.expectEqual(@as(?usize, 2), nodeKey(rbtree.firstCached(&root)));
    try testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    const duplicate_key: usize = bits_per_long + 5;
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, keyCmp);
    const first_duplicate = iter.next() orelse return error.TestUnexpectedResult;
    const second_duplicate = iter.next() orelse return error.TestUnexpectedResult;
    try testing.expectEqual(@as(usize, 0), entryFromNode(first_duplicate).serial);
    try testing.expectEqual(@as(usize, 6), entryFromNode(second_duplicate).serial);
    try testing.expectEqual(@as(?*rbtree.Node, null), iter.next());

    const promoted = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try testing.expectEqual(bits_per_long + 1, entryFromNode(promoted).key);
    try testing.expectEqual(@as(?usize, bits_per_long + 1), nodeKey(rbtree.firstCached(&root)));

    rbtree.replaceNodeCached(&entries[3].node, &replacement.node, &root);
    try testing.expectEqual(@as(?usize, bits_per_long + 1), nodeKey(rbtree.find(&replacement.key, &root.root, keyCmp)));
    try testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&replacement.node, &root);
    try testing.expect(rbtree.emptyNode(&replacement.node));
    try testing.expectEqual(@as(?usize, bits_per_long + 3), nodeKey(rbtree.firstCached(&root)));

    var ordered: [5]usize = undefined;
    const count = collectKeys(&root.root, &ordered);
    try testing.expectEqual(@as(usize, 5), count);
    try testing.expectEqualSlices(
        usize,
        &[_]usize{
            bits_per_long + 3,
            bits_per_long + 5,
            bits_per_long + 5,
            bits_per_long + 10,
            bits_per_long + 12,
        },
        ordered[0..count],
    );

    rbtree.eraseInitCached(&entries[5].node, &root);
    rbtree.eraseInitCached(&entries[0].node, &root);
    rbtree.eraseInitCached(&entries[6].node, &root);
    rbtree.eraseInitCached(&entries[4].node, &root);
    rbtree.eraseInitCached(&entries[2].node, &root);
    try testing.expect(rbtree.emptyRoot(&root.root));
    try testing.expect(root.leftmost == null);
}
