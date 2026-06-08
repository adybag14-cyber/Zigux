const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;

const Entry = struct {
    key: usize,
    serial: usize,
    node: rbtree.Node = .{},
};

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index & (bitmap.bits_per_long - 1));
}

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const left = entryFromNode(lhs);
    const right = entryFromNode(rhs);
    if (left.key == right.key) {
        return left.serial < right.serial;
    }
    return left.key < right.key;
}

fn cmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const left = entryFromNode(lhs);
    const right = entryFromNode(rhs);
    if (left.key < right.key) {
        return -1;
    }
    if (left.key > right.key) {
        return 1;
    }
    return 0;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry = entryFromNode(node);
    if (wanted.* < entry.key) {
        return -1;
    }
    if (wanted.* > entry.key) {
        return 1;
    }
    return 0;
}

fn keyOf(node: *const rbtree.Node) usize {
    return entryFromNode(node).key;
}

test "lane06 helper ports A helix gate replay" {
    const nbits: usize = 144;
    const nwords = 3;
    try std.testing.expectEqual(nwords, bitmap.bitsToWords(nbits));

    var base = [_]Word{0} ** nwords;
    var mask = [_]Word{0} ** nwords;
    var incoming = [_]Word{0} ** nwords;
    var helix = [_]Word{0} ** nwords;
    var delta = [_]Word{0} ** nwords;

    bitmap.setRange(&base, 3, 6);
    bitmap.setRange(&base, 30, 5);
    bitmap.setRange(&base, 64, 4);
    bitmap.setRange(&base, 96, 5);
    bitmap.setRange(&base, 127, 2);

    bitmap.setRange(&mask, 5, 3);
    bitmap.setRange(&mask, 32, 4);
    bitmap.setRange(&mask, 65, 2);
    bitmap.setRange(&mask, 100, 4);
    bitmap.setRange(&mask, 140, 6);

    bitmap.setRange(&incoming, 7, 5);
    bitmap.setRange(&incoming, 33, 1);
    bitmap.setRange(&incoming, 66, 7);
    bitmap.setRange(&incoming, 90, 4);
    bitmap.setRange(&incoming, 130, 5);
    bitmap.setRange(&incoming, 142, 5);

    bitmap.bitmap_replace(&helix, &base, &incoming, &mask, nbits);

    try std.testing.expectEqual(@as(usize, 18), bitmap.weight(&helix, nbits));
    try std.testing.expect(helix[0] & bit(3) != 0);
    try std.testing.expect(helix[0] & bit(5) == 0);
    try std.testing.expect(helix[2] & bit(142) != 0);
    try std.testing.expect(helix[2] & ~bitmap.lastWordMask(nbits) == 0);
    try std.testing.expect(bitmap.intersects(&helix, &base, nbits));
    try std.testing.expect(!bitmap.equal(&helix, &base, nbits));

    try std.testing.expect(bitmap.andNotBits(&delta, &helix, &base, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&delta, nbits));
    try std.testing.expectEqual(@as(usize, 142), find_bit.findFirstBit(&delta, nbits));
    try std.testing.expectEqual(@as(usize, 143), find_bit.findLastBit(&delta, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&helix, &base, nbits, 144));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &helix, nbits));
    try std.testing.expectEqual(@as(u8, 0b1001_1000), clump);
    try std.testing.expectEqual(@as(usize, 24), find_bit.findNextClump8(&clump, &helix, nbits, 9));
    try std.testing.expectEqual(@as(u8, 0b1100_0000), clump);

    var rendered_buf = [_]u8{0} ** 128;
    const rendered_len = bitmap.scnprintf(&helix, nbits, &rendered_buf);
    const rendered = rendered_buf[0..rendered_len];
    try std.testing.expectEqualStrings("3-4,7-8,30-31,33,64,66-67,96-99,127-128,142-143", rendered);

    var label = [_]u8{0} ** 160;
    _ = try std.fmt.bufPrint(&label, "  {s} \n", .{rendered});
    const trimmed = string.trimSpaces(&label);
    try std.testing.expectEqualStrings(rendered, trimmed);
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(trimmed, "3-4"));

    var padded = [_]u8{0xaa} ** 96;
    try std.testing.expectEqual(@as(isize, @intCast(rendered.len)), string.strscpyPad(&padded, rendered));
    try std.testing.expectEqual(@as(u8, 0), padded[rendered.len]);
    try std.testing.expectEqual(@as(u8, 0), padded[rendered.len + 1]);

    const haystack = [_][]const u8{ "missing", rendered, "142-143" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&haystack, rendered));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&haystack, rendered));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&haystack, "64,66"));

    var entries = [_]Entry{
        .{ .key = 3, .serial = 0 },
        .{ .key = 8, .serial = 1 },
        .{ .key = 30, .serial = 2 },
        .{ .key = 33, .serial = 3 },
        .{ .key = 64, .serial = 4 },
        .{ .key = 67, .serial = 5 },
        .{ .key = 96, .serial = 6 },
        .{ .key = 127, .serial = 7 },
        .{ .key = 142, .serial = 8 },
        .{ .key = 143, .serial = 9 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry_item| {
        try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&entry_item.node, &root, cmpNode));
        try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
    }
    try std.testing.expectEqual(@as(usize, 3), keyOf(rbtree.firstCached(&root).?));

    var duplicate = Entry{ .key = 67, .serial = 99 };
    const duplicate_match = rbtree.findAddCached(&duplicate.node, &root, cmpNode) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 67), keyOf(duplicate_match));

    const wanted: usize = 67;
    var iter = rbtree.matchIterator(&wanted, &root.root, cmpKey);
    const first_match = iter.next() orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 67), keyOf(first_match));
    try std.testing.expect(iter.next() == null);

    var replacement = Entry{ .key = 96, .serial = 42 };
    rbtree.replaceNodeCached(&entries[6].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(usize, 96), keyOf(rbtree.find(&replacement.key, &root.root, cmpKey).?));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    var drained = [_]usize{0} ** entries.len;
    var drained_len: usize = 0;
    while (rbtree.firstCached(&root)) |node| {
        drained[drained_len] = keyOf(node);
        drained_len += 1;
        rbtree.eraseInitCached(node, &root);
        try std.testing.expect(rbtree.emptyNode(node));
        try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
    }

    try std.testing.expectEqual(entries.len, drained_len);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 3, 8, 30, 33, 64, 67, 96, 127, 142, 143 }, &drained);
}
