const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index & (bits_per_long - 1));
}

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn lessByKeySerial(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry = entryFromNode(lhs);
    const rhs_entry = entryFromNode(rhs);
    if (lhs_entry.key == rhs_entry.key) {
        return lhs_entry.serial < rhs_entry.serial;
    }
    return lhs_entry.key < rhs_entry.key;
}

fn cmpByKey(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry = entryFromNode(lhs);
    const rhs_entry = entryFromNode(rhs);
    if (lhs_entry.key < rhs_entry.key) {
        return -1;
    }
    if (lhs_entry.key > rhs_entry.key) {
        return 1;
    }
    return 0;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry = entryFromNode(node);
    if (wanted.* < entry.key) {
        return -1;
    }
    if (wanted.* > entry.key) {
        return 1;
    }
    return 0;
}

fn expectOrder(root: *const rbtree.RootCached, expected: []const i32) !void {
    var cursor = rbtree.firstCached(root);
    var idx: usize = 0;
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], entryFromNode(node).key);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);
}

test "window token replay links bitmap scans to string tokens and cached rbtree" {
    const nbits = bits_per_long + 23;
    var base = [_]Word{ 0, 0 };
    var overlay = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };
    var selected = [_]Word{ 0, 0 };

    bitmap.setRange(&base, 3, 4);
    bitmap.setRange(&base, 19, 3);
    bitmap.setRange(&base, bits_per_long + 2, 5);
    bitmap.setRange(&base, bits_per_long + 19, 3);
    base[1] |= bit(29);

    bitmap.setRange(&overlay, 4, 2);
    bitmap.setRange(&overlay, 20, 5);
    bitmap.setRange(&overlay, bits_per_long + 4, 3);
    bitmap.setRange(&overlay, bits_per_long + 20, 5);

    bitmap.setRange(&mask, 0, 26);
    bitmap.setRange(&mask, bits_per_long, 23);

    const any_selected = bitmap.andBits(&selected, &base, &mask, nbits);
    try std.testing.expect(any_selected);
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstBit(&selected, nbits));
    try std.testing.expectEqual(@as(usize, 19), find_bit.findNextBit(&selected, nbits, 8));
    try std.testing.expectEqual(@as(usize, bits_per_long + 21), find_bit.findLastBit(&selected, nbits));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextZeroBit(&selected, nbits, 3));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findFirstAndBit(&selected, &overlay, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstAndNotBit(&selected, &overlay, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 19), find_bit.findNextAndNotBit(&selected, &overlay, nbits, bits_per_long + 8));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&clump, &selected, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0b0111_1000), clump);
    try std.testing.expectEqual(@as(usize, 16), find_bit.findNextClump8(&clump, &selected, nbits, 8));
    try std.testing.expectEqual(@as(u8, 0b0011_1000), clump);

    var rendered = [_]u8{0xaa} ** 96;
    const rendered_len = bitmap.scnprintf(&selected, nbits, &rendered);
    try std.testing.expectEqualStrings(
        "3-6,19-21,66-70,83-85",
        rendered[0..rendered_len],
    );

    var token = [_]u8{0} ** 64;
    _ = try std.fmt.bufPrint(&token, "  win:{s}  \n", .{rendered[0..rendered_len]});
    const trimmed = string.strim(&token);
    try std.testing.expectEqualStrings("win:3-6,19-21,66-70,83-85", trimmed);
    try std.testing.expectEqual(@as(?usize, 7), string.strnchr(trimmed, trimmed.len, ','));
    try std.testing.expect(string.strstarts(trimmed, "win:3-6"));
    try std.testing.expect(string.strEndsWith(trimmed, "83-85"));
    try std.testing.expect(string.sysfsStreq(trimmed, "win:3-6,19-21,66-70,83-85\n"));

    const keys = [_]i32{
        @intCast(find_bit.findFirstBit(&selected, nbits)),
        @intCast(find_bit.findNextBit(&selected, nbits, 8)),
        @intCast(find_bit.findFirstAndBit(&selected, &overlay, nbits)),
        @intCast(find_bit.findNextAndNotBit(&selected, &overlay, nbits, bits_per_long + 8)),
    };

    var entries = [_]Entry{
        .{ .key = keys[1], .serial = 1 },
        .{ .key = keys[0], .serial = 0 },
        .{ .key = keys[3], .serial = 3 },
        .{ .key = keys[2], .serial = 2 },
    };
    var duplicate = Entry{ .key = keys[1], .serial = 99 };
    var replacement = Entry{ .key = keys[0] - 1, .serial = 10 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, lessByKeySerial);
    }

    try expectOrder(&root, &[_]i32{ 3, 4, 19, 83 });
    const existing = rbtree.findAddCached(&duplicate.node, &root, cmpByKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(keys[1], entryFromNode(existing).key);

    var duplicate_key = keys[1];
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, cmpKey);
    const first_match = iter.next() orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(keys[1], entryFromNode(first_match).key);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iter.next());

    const promoted = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(keys[2], entryFromNode(promoted).key);
    try std.testing.expect(rbtree.firstCached(&root) == promoted);

    rbtree.replaceNodeCached(&entries[3].node, &replacement.node, &root);
    try std.testing.expect(rbtree.firstCached(&root) == &replacement.node);
    try expectOrder(&root, &[_]i32{ 2, 19, 83 });

    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try expectOrder(&root, &[_]i32{ 19, 83 });
}
