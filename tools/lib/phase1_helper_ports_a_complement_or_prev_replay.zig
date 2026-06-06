const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

const Entry = struct {
    key: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn entryFromNodeMut(node: *rbtree.Node) *Entry {
    return @fieldParentPtr("node", node);
}

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    return entryFromNode(lhs).key < entryFromNode(rhs).key;
}

fn expectOrder(root: *const rbtree.RootCached, expected: []const usize) !void {
    var index: usize = 0;
    var current = rbtree.firstCached(root);
    while (current) |node| : (current = rbtree.next(node)) {
        try std.testing.expect(index < expected.len);
        try std.testing.expectEqual(expected[index], entryFromNode(node).key);
        index += 1;
    }
    try std.testing.expectEqual(expected.len, index);
}

test "lane06 complement or prev replay joins helper ports A" {
    const nbits = bitmap.bits_per_long + 24;
    var source = [_]Word{0} ** 2;
    var mask = [_]Word{0} ** 2;
    var complement = [_]Word{0} ** 2;
    var merged = [_]Word{0} ** 2;
    var shared = [_]Word{0} ** 2;

    bitmap.setRange(&source, 2, 5);
    bitmap.setRange(&source, 17, 3);
    bitmap.setRange(&source, bitmap.bits_per_long + 4, 4);
    bitmap.setRange(&source, bitmap.bits_per_long + 16, 2);
    bitmap.setRange(&mask, 0, 9);
    bitmap.setRange(&mask, bitmap.bits_per_long + 2, 8);
    bitmap.setRange(&mask, bitmap.bits_per_long + 17, 2);

    bitmap.complement(&complement, &source, nbits);
    try std.testing.expect(bitmap.intersects(&source, &mask, nbits));
    try std.testing.expect(!bitmap.subset(&source, &mask, nbits));
    try std.testing.expect(bitmap.subset(&shared, &source, nbits));

    const had_shared = bitmap.andBits(&shared, &source, &mask, nbits);
    try std.testing.expect(had_shared);
    try std.testing.expect(bitmap.subset(&shared, &source, nbits));
    try std.testing.expect(bitmap.subset(&shared, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 10), bitmap.weight(&shared, nbits));

    bitmap.orBits(&merged, &shared, &complement, nbits);
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstBit(&merged, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstAndBit(&source, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 17), find_bit.findNextZeroBit(&merged, nbits, 0));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 23), find_bit.findLastBit(&merged, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &merged, nbits));
    try std.testing.expectEqual(@as(u8, 0xff), clump);
    try std.testing.expectEqual(@as(usize, 16), find_bit.findNextClump8(&clump, &merged, nbits, 17));
    try std.testing.expectEqual(@as(u8, 0b1111_0001), clump);

    var token = [_]u8{0} ** 40;
    const written = try std.fmt.bufPrint(&token, "  lane06:{d}:{d}  \x00", .{
        find_bit.findNextZeroBit(&merged, nbits, 0),
        bitmap.weight(&merged, nbits),
    });
    token[written.len] = 0;
    const trimmed = string.strim(&token);
    try std.testing.expectEqual(@as(usize, 7), string.strHasPrefix(trimmed, "lane06:"));
    try std.testing.expect(string.strEndsWith(trimmed, ":84"));
    try std.testing.expectEqual(@as(usize, 1), string.memchrInv(trimmed[0..7], 'l').?);
    try std.testing.expect(string.sysfsStreq("lane06:17:84\n", trimmed));

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = find_bit.findFirstAndBit(&source, &mask, nbits) },
        .{ .key = find_bit.findNextZeroBit(&merged, nbits, 0) },
        .{ .key = find_bit.findLastBit(&shared, nbits) },
        .{ .key = bitmap.weight(&merged, nbits) },
    };

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }
    try expectOrder(&root, &.{ 2, 17, bitmap.bits_per_long + 17, 84 });
    try std.testing.expectEqual(entries[0].key, entryFromNode(rbtree.firstCached(&root).?).key);
    try std.testing.expectEqual(entries[3].key, entryFromNode(rbtree.last(&root.root).?).key);
    try std.testing.expectEqual(entries[2].key, entryFromNode(rbtree.prev(&entries[3].node).?).key);

    var replacement = Entry{ .key = entries[0].key };
    rbtree.replaceNodeCached(&entries[0].node, &replacement.node, &root);
    try std.testing.expectEqual(replacement.key, entryFromNode(rbtree.firstCached(&root).?).key);

    _ = rbtree.eraseCached(&replacement.node, &root);
    rbtree.eraseInitCached(&entries[2].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[2].node));
    try expectOrder(&root, &.{ 17, 84 });

    entries[2].node = rbtree.Node.init();
    _ = rbtree.addCached(&entries[2].node, &root, less);
    try expectOrder(&root, &.{ 17, bitmap.bits_per_long + 17, 84 });
    try std.testing.expectEqual(entries[1].key, entryFromNodeMut(rbtree.firstCached(&root).?).key);
}
