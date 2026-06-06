const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

fn bit(pos: usize) Word {
    return @as(Word, 1) << @intCast(pos & (bitmap.bits_per_long - 1));
}

fn setBit(map: []Word, pos: usize) void {
    map[pos / bitmap.bits_per_long] |= bit(pos);
}

fn hasBit(map: []const Word, pos: usize) bool {
    return (map[pos / bitmap.bits_per_long] & bit(pos)) != 0;
}

test "copy clear tail feeds andnot cursors and string cleanup" {
    const nbits = bitmap.bits_per_long + 10;
    var source = [_]Word{ 0, 0 };
    var blocker = [_]Word{ 0, 0 };

    for ([_]usize{ 2, 3, 4, 5, 6, 7, 12, 13, 62, 63, 64, 65, 66, 67, 68, 72 }) |pos| {
        setBit(&source, pos);
    }
    setBit(&source, nbits + 5);

    for ([_]usize{ 3, 5, 63, 64, 72 }) |pos| {
        setBit(&blocker, pos);
    }

    var copied = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    bitmap.copyClearTail(&copied, &source, nbits);

    try std.testing.expect(hasBit(&copied, 68));
    try std.testing.expect(!hasBit(&copied, 72 + 2));

    var remaining = [_]Word{ 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&remaining, &copied, &blocker, nbits));
    try std.testing.expectEqual(@as(usize, 11), bitmap.weight(&remaining, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstAndNotBit(&copied, &blocker, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findNextAndNotBit(&copied, &blocker, nbits, 3));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findNextZeroBit(&remaining, nbits, 2));
    try std.testing.expectEqual(@as(usize, 68), find_bit.findLastBit(&remaining, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &remaining, nbits));
    try std.testing.expectEqual(@as(u8, 0b1101_0100), clump);

    var rendered_buf: [96]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&remaining, nbits, &rendered_buf);
    try std.testing.expectEqualStrings("2,4,6-7,12-13,62,65-68", rendered_buf[0..rendered_len]);

    var padded: [128]u8 = undefined;
    @memset(&padded, 0);
    const decorated = try std.fmt.bufPrint(&padded, "  {s}\n", .{rendered_buf[0..rendered_len]});
    const trimmed = string.strim(decorated);
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(trimmed, "2,4"));
    try std.testing.expect(string.strEndsWith(trimmed, "65-68"));
    try std.testing.expectEqual(@as(usize, 1), string.memchrInv(trimmed[0..3], '2').?);
    try std.testing.expect(string.sysfsStreq(trimmed, "2,4,6-7,12-13,62,65-68\n"));
    try std.testing.expectEqual(trimmed.len, string.strreplace(trimmed, '-', ':'));
    try std.testing.expectEqualStrings("2,4,6:7,12:13,62,65:68", trimmed);
}

test "cached rbtree detach and reseed follows andnot cursor keys" {
    const Entry = struct {
        key: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    const cmp_key = struct {
        fn compare(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
            const key_value: *const usize = @ptrCast(@alignCast(key_ptr));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (key_value.* < entry.key) return -1;
            if (key_value.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 2 },
        .{ .key = 4 },
        .{ .key = 62 },
        .{ .key = 65 },
        .{ .key = 65 },
        .{ .key = 68 },
    };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(&entries[0].node, rbtree.addCached(&entries[0].node, &root, less).?);
    for (entries[1..]) |*entry| {
        try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entry.node, &root, less));
    }
    try std.testing.expectEqual(&entries[0].node, rbtree.firstCached(&root).?);

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(&entries[1].node, rbtree.firstCached(&root).?);

    entries[0].key = 1;
    try std.testing.expectEqual(&entries[0].node, rbtree.addCached(&entries[0].node, &root, less).?);
    try std.testing.expectEqual(&entries[0].node, rbtree.firstCached(&root).?);

    const duplicate_key: usize = 65;
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, cmp_key);
    var duplicate_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        try std.testing.expectEqual(@as(usize, 65), entry.key);
        duplicate_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), duplicate_count);

    var ordered: [6]usize = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        ordered[count] = entry.key;
        count += 1;
    }
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 4, 62, 65, 65, 68 }, ordered[0..count]);
}
