const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const nbits = bitmap.bits_per_long + 37;
const nwords = bitmap.bitsToWords(nbits);

const Entry = struct {
    node: rbtree.Node = rbtree.Node.init(),
    key: usize,
};

fn setBit(map: []Word, bit: usize) void {
    map[bit / bitmap.bits_per_long] |= @as(Word, 1) << @intCast(bit & (bitmap.bits_per_long - 1));
}

fn hasBit(map: []const Word, bit: usize) bool {
    return (map[bit / bitmap.bits_per_long] & (@as(Word, 1) << @intCast(bit & (bitmap.bits_per_long - 1)))) != 0;
}

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn mutableEntryFromNode(node: *rbtree.Node) *Entry {
    return @fieldParentPtr("node", node);
}

fn lessEntry(a: *const rbtree.Node, b: *const rbtree.Node) bool {
    return entryFromNode(a).key < entryFromNode(b).key;
}

fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const usize = @ptrCast(@alignCast(key_ptr));
    const node_key = entryFromNode(node).key;
    if (key.* < node_key) return -1;
    if (key.* > node_key) return 1;
    return 0;
}

fn collectSetBits(map: []const Word, out: []usize) usize {
    var count: usize = 0;
    var bit = find_bit.findFirstBit(map, nbits);
    while (bit < nbits) : (bit = find_bit.findNextBit(map, nbits, bit + 1)) {
        out[count] = bit;
        count += 1;
    }
    return count;
}

fn expectOrderedDrain(root: *rbtree.RootCached, expected: []const usize) !void {
    for (expected) |key| {
        const node = rbtree.firstCached(root) orelse return error.MissingNode;
        const entry = mutableEntryFromNode(node);
        try std.testing.expectEqual(key, entry.key);
        rbtree.eraseInitCached(&entry.node, root);
        try std.testing.expect(rbtree.emptyNode(&entry.node));
    }
    try std.testing.expect(rbtree.emptyRoot(&root.root));
    try std.testing.expect(root.leftmost == null);
}

test "phase1 helper ports A crown gap replay" {
    var crown: [nwords]Word = [_]Word{0} ** nwords;
    var gaps: [nwords]Word = [_]Word{0} ** nwords;
    var bridge: [nwords]Word = [_]Word{0} ** nwords;
    var clipped: [nwords]Word = [_]Word{0} ** nwords;
    var allowed: [nwords]Word = [_]Word{0} ** nwords;

    bitmap.bitmap_set(&crown, 2, 7);
    bitmap.bitmap_set(&crown, bitmap.bits_per_long - 4, 9);
    bitmap.bitmap_set(&crown, bitmap.bits_per_long + 9, 12);
    bitmap.bitmap_set(&crown, nbits - 5, 5);

    bitmap.bitmap_set(&gaps, 5, 2);
    bitmap.bitmap_set(&gaps, bitmap.bits_per_long + 12, 3);
    bitmap.bitmap_set(&gaps, nbits - 2, 2);

    bitmap.bitmap_set(&bridge, 1, 4);
    bitmap.bitmap_set(&bridge, bitmap.bits_per_long + 7, 6);
    bitmap.bitmap_set(&bridge, nbits - 7, 3);

    try std.testing.expect(bitmap.andNotBits(&clipped, &crown, &gaps, nbits));
    bitmap.orBits(&allowed, &clipped, &bridge, nbits);

    try std.testing.expectEqual(@as(usize, 26), bitmap.weight(&clipped, nbits));
    try std.testing.expectEqual(@as(usize, 32), bitmap.weight(&allowed, nbits));
    try std.testing.expect(bitmap.subset(&clipped, &allowed, nbits));
    try std.testing.expect(bitmap.intersects(&allowed, &bridge, nbits));
    try std.testing.expect(!hasBit(&clipped, bitmap.bits_per_long + 12));
    try std.testing.expect(hasBit(&allowed, bitmap.bits_per_long + 12));
    try std.testing.expect(!hasBit(&allowed, nbits - 1));

    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&allowed, nbits));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextBit(&allowed, nbits, 5));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextZeroBit(&allowed, nbits, 1));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstAndBit(&allowed, &bridge, nbits));
    try std.testing.expectEqual(bitmap.bits_per_long + 8, find_bit.findNextAndBit(&allowed, &bridge, nbits, bitmap.bits_per_long + 8));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findFirstAndNotBit(&allowed, &bridge, nbits));
    try std.testing.expectEqual(nbits - 3, find_bit.findLastBit(&allowed, nbits));

    var clump: u8 = 0;
    const clump_start = find_bit.findNextClump8(&clump, &allowed, nbits, bitmap.bits_per_long + 8);
    try std.testing.expectEqual(bitmap.bits_per_long + 8, clump_start);
    try std.testing.expectEqual(@as(u8, 0x9f), clump);

    var keys: [32]usize = undefined;
    const key_count = collectSetBits(&allowed, &keys);
    try std.testing.expectEqual(bitmap.weight(&allowed, nbits), key_count);

    var label_buf: [96]u8 = undefined;
    const label_len = try std.fmt.bufPrint(&label_buf, "  crown gap first={d} last={d} weight={d}\x00", .{
        keys[0],
        keys[key_count - 1],
        key_count,
    });
    _ = label_len;
    const trimmed = string.strim(&label_buf);
    _ = string.strreplace(trimmed, ' ', '-');
    try std.testing.expect(string.strHasPrefix(trimmed, "crown-gap") != 0);
    try std.testing.expect(string.strEndsWith(trimmed, "weight=32"));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv("ccccc", 'c'));
    try std.testing.expect(string.sysfsStreq("crown-gap\n", "crown-gap"));

    var entries: [32]Entry = undefined;
    var root = rbtree.RootCached.init();
    var idx: usize = key_count;
    while (idx > 0) {
        idx -= 1;
        entries[idx] = .{ .key = keys[idx] };
        _ = rbtree.addCached(&entries[idx].node, &root, lessEntry);
    }

    try std.testing.expectEqual(keys[0], mutableEntryFromNode(rbtree.firstCached(&root).?).key);
    try std.testing.expectEqual(keys[key_count - 1], mutableEntryFromNode(rbtree.last(&root.root).?).key);

    var gap_key: usize = bitmap.bits_per_long + 12;
    const found_gap = rbtree.find(&gap_key, &root.root, cmpKey) orelse return error.MissingGapKey;
    try std.testing.expectEqual(gap_key, mutableEntryFromNode(found_gap).key);

    try expectOrderedDrain(&root, keys[0..key_count]);

    for (0..key_count) |pos| {
        try std.testing.expect(rbtree.emptyNode(&entries[pos].node));
    }
}
