const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = .{},
};

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn entryCmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const i32 = @ptrCast(@alignCast(key_ptr));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (key.* < entry.key) return -1;
    if (key.* > entry.key) return 1;
    return 0;
}

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn expectKeys(root: *const rbtree.Root, expected: []const i32) !void {
    var cursor = rbtree.first(root);
    var idx: usize = 0;
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        try std.testing.expect(idx < expected.len);
        try std.testing.expectEqual(expected[idx], entryFromNode(node).key);
        idx += 1;
    }
    try std.testing.expectEqual(expected.len, idx);
}

test "tail bridge bitmap and string cursors stay inside declared nbits" {
    const nbits = bits_per_long * 2 + 13;
    var source = [_]Word{0} ** bitmap.bitsToWords(nbits);
    bitmap.setRange(&source, 1, 4);
    bitmap.setRange(&source, bits_per_long - 2, 5);
    bitmap.setRange(&source, bits_per_long + 8, 3);
    bitmap.setRange(&source, bits_per_long * 2 + 10, 2);
    source[source.len - 1] |= @as(Word, 1) << 20;

    var copied = [_]Word{0} ** source.len;
    bitmap.copyClearTail(&copied, &source, nbits);
    try std.testing.expectEqual(@as(Word, 0), copied[copied.len - 1] & ~bitmap.lastWordMask(nbits));
    try std.testing.expectEqual(@as(usize, 14), bitmap.weight(&copied, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&copied, nbits));
    try std.testing.expectEqual(bits_per_long - 2, find_bit.findNextBit(&copied, nbits, 5));
    try std.testing.expectEqual(bits_per_long * 2 + 11, find_bit.findLastBit(&copied, nbits));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&copied, nbits, bits_per_long * 2 + 12));
    try std.testing.expectEqual(@as(u8, 0x07), find_bit.getValue8(&copied, bits_per_long));

    var clump: u8 = 0;
    try std.testing.expectEqual(bits_per_long - 8, find_bit.findNextClump8(&clump, &copied, nbits, bits_per_long - 8));
    try std.testing.expectEqual(@as(u8, 0xc0), clump);
    try std.testing.expectEqual(bits_per_long, find_bit.findNextClump8(&clump, &copied, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x07), clump);

    var rendered = [_]u8{0} ** 96;
    const rendered_len = bitmap.scnprintf(&copied, nbits, &rendered);
    try std.testing.expectEqualStrings("1-4,62-66,72-74,138-139", rendered[0..rendered_len]);

    var padded = [_]u8{ ' ', ' ', '1', '-', '4', ',', '6', '2', '-', '6', '6', '\n', 0, 'x' };
    const trimmed = string.strim(padded[0 .. padded.len - 1]);
    try std.testing.expectEqualStrings("1-4,62-66", trimmed);
    try std.testing.expectEqual(@as(usize, 9), string.replaceChar(trimmed, ',', '|'));
    try std.testing.expectEqualStrings("1-4|62-66", trimmed);
    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix(trimmed, "1-4|"));
    try std.testing.expect(string.sysfsStreq("62-66\n", trimmed[4..]));
    try std.testing.expectEqual(@as(?usize, 3), string.memchrInv("zzz9zz", 'z'));
}

test "tail bridge cursor keys drive cached rbtree duplicate removal" {
    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = 1, .serial = 0 },
        .{ .key = @intCast(bits_per_long - 2), .serial = 1 },
        .{ .key = @intCast(bits_per_long), .serial = 2 },
        .{ .key = @intCast(bits_per_long + 2), .serial = 3 },
        .{ .key = @intCast(bits_per_long + 8), .serial = 4 },
        .{ .key = @intCast(bits_per_long + 8), .serial = 5 },
        .{ .key = @intCast(bits_per_long * 2 + 10), .serial = 6 },
    };

    for (&entries, 0..) |*entry, idx| {
        const inserted_leftmost = rbtree.addCached(&entry.node, &root, entryLess);
        if (idx == 0) {
            try std.testing.expectEqual(@as(?*rbtree.Node, &entry.node), inserted_leftmost);
        } else {
            try std.testing.expectEqual(@as(?*rbtree.Node, null), inserted_leftmost);
        }
    }
    try std.testing.expectEqual(@as(i32, 1), entryFromNode(rbtree.firstCached(&root).?).key);
    try expectKeys(&root.root, &[_]i32{
        1,
        @intCast(bits_per_long - 2),
        @intCast(bits_per_long),
        @intCast(bits_per_long + 2),
        @intCast(bits_per_long + 8),
        @intCast(bits_per_long + 8),
        @intCast(bits_per_long * 2 + 10),
    });

    var duplicate_key: i32 = @intCast(bits_per_long + 8);
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, entryCmpKey);
    const first_duplicate = iter.next() orelse return error.MissingDuplicate;
    const second_duplicate = iter.next() orelse return error.MissingDuplicate;
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iter.next());
    try std.testing.expectEqual(@as(usize, 4), entryFromNode(first_duplicate).serial);
    try std.testing.expectEqual(@as(usize, 5), entryFromNode(second_duplicate).serial);

    const promoted_leftmost = rbtree.eraseCached(&entries[0].node, &root) orelse return error.MissingPromotedLeftmost;
    try std.testing.expectEqual(rbtree.firstCached(&root), promoted_leftmost);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node) == false);
    rbtree.eraseInitCached(&entries[4].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[4].node));
    try std.testing.expectEqual(@as(i32, @intCast(bits_per_long - 2)), entryFromNode(rbtree.firstCached(&root).?).key);
    try expectKeys(&root.root, &[_]i32{
        @intCast(bits_per_long - 2),
        @intCast(bits_per_long),
        @intCast(bits_per_long + 2),
        @intCast(bits_per_long + 8),
        @intCast(bits_per_long * 2 + 10),
    });
}
