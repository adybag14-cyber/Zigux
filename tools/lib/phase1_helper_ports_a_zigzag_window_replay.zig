const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: usize,
    tag: u8,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryLess(lhs_node: *const rbtree.Node, rhs_node: *const rbtree.Node) bool {
    const lhs: *const Entry = @fieldParentPtr("node", lhs_node);
    const rhs: *const Entry = @fieldParentPtr("node", rhs_node);
    if (lhs.key != rhs.key) {
        return lhs.key < rhs.key;
    }
    return lhs.tag < rhs.tag;
}

fn entryCmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn collectKeys(root: *const rbtree.RootCached, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.first(&root.root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

fn expectBitmapText(map: []const Word, nbits: usize, expected: []const u8) !void {
    var rendered: [96]u8 = undefined;
    const len = bitmap.scnprintf(map, nbits, &rendered);
    try std.testing.expectEqualStrings(expected, rendered[0..len]);
}

test "phase1 helper ports A zigzag window replay" {
    const nbits = bits_per_long * 2 + 11;
    const tail_noise = (@as(Word, 1) << 15) | (@as(Word, 1) << 19);

    var low = [_]Word{ 0, 0, tail_noise };
    var high = [_]Word{ 0, 0, tail_noise };
    var mask = [_]Word{ 0, 0, 0 };
    var merged = [_]Word{ 0, 0, 0 };
    var replaced = [_]Word{ 0, 0, 0 };
    var complement = [_]Word{ 0, 0, 0 };
    var scratch = [_]Word{ 0, 0, 0 };

    bitmap.setRange(&low, 2, 3);
    bitmap.setRange(&low, 14, 2);
    bitmap.setRange(&low, bits_per_long + 1, 1);
    bitmap.setRange(&low, bits_per_long + 8, 2);

    bitmap.setRange(&high, 5, 1);
    bitmap.setRange(&high, bits_per_long - 1, 3);
    bitmap.setRange(&high, bits_per_long + 6, 4);
    bitmap.setRange(&high, bits_per_long * 2 + 2, 2);

    bitmap.setRange(&mask, 4, 6);
    bitmap.setRange(&mask, bits_per_long + 6, 4);
    bitmap.setRange(&mask, bits_per_long * 2 + 2, 4);

    try std.testing.expectEqual(@as(usize, 8), bitmap.weight(&low, nbits));
    try std.testing.expectEqual(@as(usize, 10), bitmap.weight(&high, nbits));
    try std.testing.expect(bitmap.intersects(&low, &high, nbits));

    const merged_weight = bitmap.weightedOr(&merged, &low, &high, nbits);
    try std.testing.expectEqual(@as(usize, 15), merged_weight);
    try std.testing.expectEqual(@as(usize, 15), bitmap.weight(&merged, nbits));
    try expectBitmapText(&merged, nbits, "2-5,14-15,63-65,70-73,130-131");

    bitmap.replace(&replaced, &low, &high, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 12), bitmap.weight(&replaced, nbits));
    try expectBitmapText(&replaced, nbits, "2-3,5,14-15,65,70-73,130-131");

    try std.testing.expect(bitmap.andNotBits(&scratch, &replaced, &high, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&scratch, nbits));
    try expectBitmapText(&scratch, nbits, "2-3,14-15");

    bitmap.complement(&complement, &replaced, nbits);
    try std.testing.expectEqual(nbits - bitmap.weight(&replaced, nbits), bitmap.weight(&complement, nbits));

    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextBit(&replaced, nbits, 5));
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextZeroBit(&replaced, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 3), find_bit.findLastBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstAndNotBit(&replaced, &high, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextAndBit(&replaced, &high, nbits, bits_per_long));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &replaced, nbits));
    try std.testing.expectEqual(@as(u8, 0b0010_1100), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long + 64), find_bit.findNextClump8(&clump, &replaced, nbits, bits_per_long * 2));
    try std.testing.expectEqual(@as(u8, 0b0000_1100), clump);

    var rendered: [96]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&replaced, nbits, &rendered);
    try std.testing.expectEqual(@as(usize, 4), string.str_has_prefix(rendered[0..rendered_len], "2-3,"));
    try std.testing.expect(string.str_ends_with(rendered[0..rendered_len], "130-131"));

    var spaced = [_]u8{ ' ', ' ', '2', '-', '5', ',', '1', '4', '-', '1', '5', ' ', '\n', 0 };
    try std.testing.expectEqualStrings("2-5,14-15", string.strim(spaced[0..]));

    var dashes = [_]u8{ '2', '-', '5', ',', '1', '4', '-', '1', '5', 0 };
    try std.testing.expectEqual(@as(usize, 9), string.strreplace(dashes[0..], '-', ':'));
    try std.testing.expectEqualStrings("2:5,14:15", dashes[0..9]);
    try std.testing.expect(string.sysfs_streq("zigzag-window\n", "zigzag-window"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(&[_][]const u8{ "2-5", "65", "130-131" }, "2-5"));
    try std.testing.expectEqual(@as(?usize, 3), string.memchr_inv(&[_]u8{ 'z', 'z', 'z', 'x' }, 'z'));

    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(&replaced, nbits), .tag = 0 },
        .{ .key = find_bit.findNextBit(&replaced, nbits, 5), .tag = 1 },
        .{ .key = find_bit.findNextBit(&replaced, nbits, bits_per_long), .tag = 2 },
        .{ .key = find_bit.findLastBit(&replaced, nbits), .tag = 3 },
        .{ .key = find_bit.findNextZeroBit(&replaced, nbits, bits_per_long), .tag = 4 },
    };

    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, entryLess);
    }

    var order: [entries.len]usize = undefined;
    const count = collectKeys(&root, &order);
    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 5, 64, 65, 131 }, order[0..count]);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    const wanted = @as(usize, bits_per_long + 1);
    const found = rbtree.find(&wanted, &root.root, entryCmpKey) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(usize, 2), found_entry.tag);

    const promoted = rbtree.eraseCached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    const promoted_entry: *const Entry = @fieldParentPtr("node", promoted);
    try std.testing.expectEqual(@as(usize, 5), promoted_entry.key);
    try std.testing.expectEqual(@as(?*rbtree.Node, promoted), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&entries[4].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[4].node));

    var after_remove: [entries.len]usize = undefined;
    const after_count = collectKeys(&root, &after_remove);
    try std.testing.expectEqual(@as(usize, 3), after_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 5, 65, 131 }, after_remove[0..after_count]);
}
