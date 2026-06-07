const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn setBit(map: []Word, bit: usize) void {
    bitmap.setRange(map, bit, 1);
}

fn compareEntryNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn compareKeyNode(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn expectCursorOrder(map: []const Word, nbits: usize, expected: []const usize) !void {
    var current = find_bit.findFirstBit(map, nbits);
    var idx: usize = 0;
    while (current < nbits) : (current = find_bit.findNextBit(map, nbits, current + 1)) {
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], current);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);
}

fn expectRbtreeOrder(root: *const rbtree.RootCached, expected: []const usize) !void {
    var current = rbtree.firstCached(root);
    var idx: usize = 0;
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], entry.key);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);
}

test "lane06 ridge walk replay keeps helper ports aligned" {
    const nbits = bits_per_long * 2 + 13;
    var base = [_]Word{ 0, 0, 0 };
    var overlay = [_]Word{ 0, 0, 0 };
    var mask = [_]Word{ 0, 0, 0 };
    var replaced = [_]Word{ 0, 0, 0 };
    var overlap = [_]Word{ 0, 0, 0 };
    var ridge_gap = [_]Word{ 0, 0, 0 };

    bitmap.setRange(&base, 3, 3);
    bitmap.setRange(&base, 20, 2);
    bitmap.setRange(&base, bits_per_long - 3, 6);
    setBit(&base, bits_per_long + 11);
    setBit(&base, nbits + 3);

    bitmap.setRange(&overlay, 5, 5);
    bitmap.setRange(&overlay, bits_per_long + 1, 6);
    bitmap.setRange(&overlay, bits_per_long * 2 + 2, 3);

    bitmap.setRange(&mask, 4, 7);
    bitmap.setRange(&mask, bits_per_long, 6);
    bitmap.setRange(&mask, bits_per_long * 2, 7);

    bitmap.replace(&replaced, &base, &overlay, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 20), bitmap.weight(&replaced, nbits));
    try std.testing.expect(bitmap.andBits(&overlap, &replaced, &overlay, nbits));
    try std.testing.expectEqual(@as(usize, 13), bitmap.weight(&overlap, nbits));
    try std.testing.expect(bitmap.andNotBits(&ridge_gap, &replaced, &overlay, nbits));
    try std.testing.expectEqual(@as(usize, 7), bitmap.weight(&ridge_gap, nbits));
    try std.testing.expect(bitmap.subset(&overlap, &replaced, nbits));
    try std.testing.expect(bitmap.intersects(&ridge_gap, &base, nbits));

    const expected = [_]usize{
        3,
        5,
        6,
        7,
        8,
        9,
        20,
        21,
        bits_per_long - 3,
        bits_per_long - 2,
        bits_per_long - 1,
        bits_per_long + 1,
        bits_per_long + 2,
        bits_per_long + 3,
        bits_per_long + 4,
        bits_per_long + 5,
        bits_per_long + 11,
        bits_per_long * 2 + 2,
        bits_per_long * 2 + 3,
        bits_per_long * 2 + 4,
    };
    try expectCursorOrder(&replaced, nbits, &expected);
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextBit(&replaced, nbits, 4));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findFirstAndBit(&replaced, &overlay, nbits));
    try std.testing.expectEqual(@as(usize, 20), find_bit.findNextAndNotBit(&replaced, &overlay, nbits, 10));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 4), find_bit.findLastBit(&replaced, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 16), find_bit.findNextClump8(&clump, &replaced, nbits, 16));
    try std.testing.expectEqual(@as(u8, 0b0011_0000), clump);

    var rendered_buf: [160]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&replaced, nbits, &rendered_buf);
    var expected_buf: [160]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected_buf,
        "3,5-9,20-21,{d}-{d},{d}-{d},{d},{d}-{d}",
        .{
            bits_per_long - 3,
            bits_per_long - 1,
            bits_per_long + 1,
            bits_per_long + 5,
            bits_per_long + 11,
            bits_per_long * 2 + 2,
            bits_per_long * 2 + 4,
        },
    );
    try std.testing.expectEqualStrings(expected_text, rendered_buf[0..rendered_len]);

    var label_buf: [192]u8 = undefined;
    const label = try std.fmt.bufPrint(&label_buf, "  ridge:{s}:walk\n", .{rendered_buf[0..rendered_len]});
    var mutable_label: [192]u8 = @splat(0);
    @memcpy(mutable_label[0..label.len], label);
    const trimmed = string.strim(&mutable_label);
    try std.testing.expect(string.strstarts(trimmed, "ridge:"));
    try std.testing.expect(string.strEndsWith(trimmed, ":walk"));
    try std.testing.expectEqual(trimmed.len, string.strreplace(trimmed, ',', ';'));
    try std.testing.expect(string.sysfs_streq("ridge\n", "ridge"));
    const haystack = [_][]const u8{ "low", "ridge\n", "walk" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(haystack[0..], "ridge"));
    try std.testing.expectEqual(@as(?usize, 5), string.memchrInv("rrrrrx", 'r'));

    var entries = [_]Entry{
        .{ .key = expected[0] },
        .{ .key = expected[1] },
        .{ .key = expected[6] },
        .{ .key = expected[8] },
        .{ .key = expected[11] },
        .{ .key = expected[16] },
        .{ .key = expected[17] },
    };
    var duplicate = Entry{ .key = expected[11] };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&entry.node, &root, compareEntryNode));
    }
    try std.testing.expectEqual(&entries[4].node, rbtree.findAddCached(&duplicate.node, &root, compareEntryNode).?);
    try expectRbtreeOrder(&root, &[_]usize{ expected[0], expected[1], expected[6], expected[8], expected[11], expected[16], expected[17] });

    const match_key = expected[11];
    var matches = rbtree.matchIterator(&match_key, &root.root, compareKeyNode);
    try std.testing.expectEqual(&entries[4].node, matches.next().?);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), matches.next());

    try std.testing.expectEqual(&entries[1].node, rbtree.eraseCached(&entries[0].node, &root).?);
    rbtree.eraseInitCached(&entries[3].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));
    try expectRbtreeOrder(&root, &[_]usize{ expected[1], expected[6], expected[11], expected[16], expected[17] });
}
