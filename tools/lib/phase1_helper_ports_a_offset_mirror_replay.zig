const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;

const Entry = struct {
    key: usize,
    tag: []const u8,
    node: rbtree.Node = .{},
};

fn mark(words: []Word, bit: usize) void {
    words[bit / bitmap.bits_per_long] |= @as(Word, 1) << @intCast(bit & (bitmap.bits_per_long - 1));
}

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn lessByKey(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    return entryFromNode(lhs).key < entryFromNode(rhs).key;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry = entryFromNode(node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn expectNodeKey(expected: usize, node: ?*rbtree.Node) !void {
    const actual = node orelse return error.MissingNode;
    try std.testing.expectEqual(expected, entryFromNode(actual).key);
}

test "phase1 helper ports A offset mirror replay" {
    const nbits = bitmap.bits_per_long + 21;
    const words = bitmap.bitsToWords(nbits);

    var old = [_]Word{0} ** 2;
    var new = [_]Word{0} ** 2;
    var mask = [_]Word{0} ** 2;
    var replaced = [_]Word{0} ** 2;
    var mirror = [_]Word{0} ** 2;
    var gap = [_]Word{0} ** 2;

    try std.testing.expectEqual(@as(usize, 2), words);

    for ([_]usize{ 2, 5, 10, bitmap.bits_per_long + 4, bitmap.bits_per_long + 13 }) |bit| mark(&old, bit);
    for ([_]usize{ 3, 5, 11, bitmap.bits_per_long + 1, bitmap.bits_per_long + 6, bitmap.bits_per_long + 19 }) |bit| mark(&new, bit);
    for ([_]usize{ 2, 3, 10, 11, bitmap.bits_per_long + 1, bitmap.bits_per_long + 4, bitmap.bits_per_long + 6, bitmap.bits_per_long + 19, bitmap.bits_per_long + 23 }) |bit| mark(&mask, bit);
    for ([_]usize{ 3, 5, bitmap.bits_per_long + 6, bitmap.bits_per_long + 19 }) |bit| mark(&mirror, bit);

    bitmap.bitmap_replace(&replaced, &old, &new, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 7), bitmap.weight(&replaced, nbits));
    try std.testing.expect(bitmap.intersects(&replaced, &mirror, nbits));
    try std.testing.expect(bitmap.subset(&mirror, &replaced, nbits));
    try std.testing.expect(bitmap.andNotBits(&gap, &replaced, &mirror, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&gap, nbits));

    const first = find_bit.findFirstBit(&replaced, nbits);
    const second = find_bit.findNextBit(&replaced, nbits, first + 1);
    const first_shared = find_bit.findFirstAndBit(&replaced, &mirror, nbits);
    const first_gap = find_bit.findNextAndNotBit(&replaced, &mirror, nbits, 0);
    const first_zero_after_first = find_bit.findNextZeroBit(&replaced, nbits, first);
    const last = find_bit.findLastBit(&replaced, nbits);
    var clump: u8 = 0;
    const low_clump = find_bit.findNextClump8(&clump, &replaced, nbits, 0);
    try std.testing.expectEqual(@as(usize, 0), low_clump);
    try std.testing.expectEqual(@as(u8, 0x28), clump);
    const high_clump = find_bit.findNextClump8(&clump, &replaced, nbits, bitmap.bits_per_long);
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long), high_clump);
    try std.testing.expectEqual(@as(u8, 0x42), clump);

    try std.testing.expectEqual(@as(usize, 3), first);
    try std.testing.expectEqual(@as(usize, 5), second);
    try std.testing.expectEqual(@as(usize, 3), first_shared);
    try std.testing.expectEqual(@as(usize, 11), first_gap);
    try std.testing.expectEqual(@as(usize, 4), first_zero_after_first);
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 19), last);

    var label = [_]u8{0} ** 80;
    _ = try std.fmt.bufPrint(&label, "  lane6 offset {d} mirror {d}  ", .{ first, last });
    const trimmed = string.trimSpaces(&label);
    var expected_label = [_]u8{0} ** 80;
    const expected_trimmed = try std.fmt.bufPrint(&expected_label, "lane6 offset {d} mirror {d}", .{ first, last });
    var expected_sysfs = [_]u8{0} ** 80;
    const expected_sysfs_label = try std.fmt.bufPrint(&expected_sysfs, "lane6 offset {d} mirror {d}\n", .{ first, last });
    var expected_suffix = [_]u8{0} ** 24;
    const mirror_suffix = try std.fmt.bufPrint(&expected_suffix, "mirror {d}", .{last});
    try std.testing.expect(string.strHasPrefix(trimmed, "lane6") != 0);
    try std.testing.expectEqualStrings(expected_trimmed, trimmed);
    try std.testing.expect(string.strEndsWith(trimmed, mirror_suffix));
    try std.testing.expect(string.sysfsStreq(trimmed, expected_sysfs_label));
    _ = string.strreplace(trimmed, ' ', '_');
    try std.testing.expect(string.memchr_inv(trimmed[0..5], 'l') == 1);

    var compact = [_]u8{0} ** 80;
    _ = try std.fmt.bufPrint(&compact, " offset {d} mirror {d} ", .{ first_gap, last });
    const no_spaces = string.removeSpaces(&compact);
    var expected_last = [_]u8{0} ** 24;
    const last_suffix = try std.fmt.bufPrint(&expected_last, "{d}", .{last});
    try std.testing.expect(string.strHasPrefix(no_spaces, "offset") != 0);
    try std.testing.expect(string.strEndsWith(no_spaces, last_suffix));

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = last, .tag = "last" },
        .{ .key = second, .tag = "shared-a" },
        .{ .key = first, .tag = "first" },
        .{ .key = first_gap, .tag = "gap" },
        .{ .key = second, .tag = "shared-b" },
        .{ .key = bitmap.bits_per_long + 6, .tag = "mirror" },
        .{ .key = bitmap.bits_per_long + 13, .tag = "tail-gap" },
    };

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, lessByKey);
    }

    try expectNodeKey(first, rbtree.firstCached(&root));
    var iter = rbtree.matchIterator(&second, &root.root, cmpKey);
    const first_duplicate = entryFromNode(iter.next().?);
    const second_duplicate = entryFromNode(iter.next().?);
    try std.testing.expectEqual(second, first_duplicate.key);
    try std.testing.expectEqual(second, second_duplicate.key);
    try std.testing.expect(iter.next() == null);

    var replacement = Entry{ .key = bitmap.bits_per_long + 6, .tag = "mirror-replaced" };
    rbtree.replaceNodeCached(&entries[5].node, &replacement.node, &root);
    try std.testing.expectEqualStrings("mirror-replaced", entryFromNode(rbtree.find(&replacement.key, &root.root, cmpKey).?).tag);

    try expectNodeKey(second, rbtree.eraseCached(&entries[2].node, &root));
    rbtree.clearNode(&entries[2].node);
    try std.testing.expect(rbtree.emptyNode(&entries[2].node));

    var sorted: [6]usize = undefined;
    var idx: usize = 0;
    var cursor = rbtree.first(&root.root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        sorted[idx] = entryFromNode(node).key;
        idx += 1;
    }
    try std.testing.expectEqualSlices(usize, &.{
        second,
        second,
        first_gap,
        bitmap.bits_per_long + 6,
        bitmap.bits_per_long + 13,
        last,
    }, sorted[0..idx]);

    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
}
