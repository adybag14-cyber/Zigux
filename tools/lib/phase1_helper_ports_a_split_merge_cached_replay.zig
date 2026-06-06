const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: usize,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs_node: *const rbtree.Node, rhs_node: *const rbtree.Node) bool {
    const lhs: *const Entry = @fieldParentPtr("node", lhs_node);
    const rhs: *const Entry = @fieldParentPtr("node", rhs_node);
    if (lhs.key != rhs.key) {
        return lhs.key < rhs.key;
    }
    return lhs.serial < rhs.serial;
}

fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn entryKey(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn collectForward(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.first(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        out[count] = entryKey(node);
        count += 1;
    }
    return count;
}

test "helper ports A split replaced bitmap ranges through cached rbtree reseed" {
    const nbits = bits_per_long + 12;
    const high = bits_per_long;

    var old = [_]Word{ 0, (@as(Word, 1) << 15) };
    var new = [_]Word{ 0, (@as(Word, 1) << 14) };
    var mask = [_]Word{ 0, (@as(Word, 1) << 13) };
    var replaced = [_]Word{ 0, 0 };
    var expected = [_]Word{ 0, 0 };

    bitmap.setRange(&old, 1, 1);
    bitmap.setRange(&old, 4, 2);
    bitmap.setRange(&old, high + 2, 1);
    bitmap.setRange(&old, high + 7, 1);
    bitmap.setRange(&old, high + 10, 1);

    bitmap.setRange(&new, 2, 1);
    bitmap.setRange(&new, 5, 1);
    bitmap.setRange(&new, high + 4, 1);
    bitmap.setRange(&new, high + 7, 1);

    bitmap.setRange(&mask, 1, 2);
    bitmap.setRange(&mask, 4, 1);
    bitmap.setRange(&mask, high + 2, 1);
    bitmap.setRange(&mask, high + 4, 1);
    bitmap.setRange(&mask, high + 10, 1);

    bitmap.replace(&replaced, &old, &new, &mask, nbits);
    bitmap.setRange(&expected, 2, 1);
    bitmap.setRange(&expected, 5, 1);
    bitmap.setRange(&expected, high + 4, 1);
    bitmap.setRange(&expected, high + 7, 1);

    try std.testing.expect(bitmap.equal(&replaced, &expected, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextBit(&replaced, nbits, 3));
    try std.testing.expectEqual(@as(usize, high + 4), find_bit.findNextBit(&replaced, nbits, high));
    try std.testing.expectEqual(@as(usize, high + 7), find_bit.findLastBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstAndBit(&replaced, &new, nbits));
    try std.testing.expectEqual(@as(usize, high + 4), find_bit.findNextAndBit(&replaced, &new, nbits, high));
    try std.testing.expectEqual(@as(usize, high + 8), find_bit.findNextZeroBit(&replaced, nbits, high + 8));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &replaced, nbits));
    try std.testing.expectEqual(@as(u8, 0b0010_0100), clump);

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&replaced, nbits, &rendered);
    var expected_rendered: [64]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected_rendered,
        "2,5,{d},{d}",
        .{ high + 4, high + 7 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);

    var copied = [_]u8{0} ** 64;
    try std.testing.expectEqual(rendered_len, string.strlcpy(&copied, rendered[0..rendered_len]));
    try std.testing.expectEqual(@as(usize, 1), string.strHasPrefix(&copied, "2"));
    try std.testing.expect(string.strEndsWith(&copied, expected_text[expected_text.len - 2 ..]));
    _ = string.strreplace(&copied, ',', '|');
    try std.testing.expectEqual(@as(?usize, 1), string.memchrInv(copied[0..rendered_len], '2'));

    var entries = [_]Entry{
        .{ .key = high + 7, .serial = 0 },
        .{ .key = 2, .serial = 1 },
        .{ .key = high + 4, .serial = 2 },
        .{ .key = 5, .serial = 3 },
    };
    var root = rbtree.RootCached.init();
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.addCached(&entries[0].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.addCached(&entries[1].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[2].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[3].node, &root, less));
    try std.testing.expectEqual(@as(usize, 2), entryKey(rbtree.firstCached(&root).?));

    const low_key: usize = 2;
    const low_node = rbtree.find(&low_key, &root.root, keyCmp) orelse return error.TestUnexpectedResult;
    rbtree.eraseInitCached(low_node, &root);
    try std.testing.expect(rbtree.emptyNode(low_node));
    try std.testing.expectEqual(@as(usize, 5), entryKey(rbtree.firstCached(&root).?));

    rbtree.add(&entries[1].node, &root.root, less);
    if (rbtree.first(&root.root)) |first| {
        root.leftmost = first;
    }

    var order: [4]usize = undefined;
    const count = collectForward(&root.root, &order);
    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 5, high + 4, high + 7 }, order[0..count]);
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}

test "helper ports A split complement leaves tail noise out of tree keys" {
    const nbits = bits_per_long + 9;
    const high = bits_per_long;

    var full = [_]Word{ 0, (@as(Word, 1) << 14) };
    var blocked = [_]Word{ 0, (@as(Word, 1) << 12) };
    var complement = [_]Word{ 0, 0 };
    var allowed = [_]Word{ 0, 0 };

    bitmap.setRange(&full, 0, nbits);
    bitmap.setRange(&blocked, 0, nbits);
    bitmap.clearRange(&blocked, 3, 1);
    bitmap.clearRange(&blocked, high + 8, 1);
    bitmap.complement(&complement, &blocked, nbits);
    try std.testing.expect(bitmap.andBits(&allowed, &full, &complement, nbits));

    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&allowed, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstBit(&allowed, nbits));
    try std.testing.expectEqual(@as(usize, high + 8), find_bit.findNextBit(&allowed, nbits, 4));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&allowed, nbits, high + 9));

    var rendered: [32]u8 = undefined;
    const len = bitmap.scnprintf(&allowed, nbits, &rendered);
    var expected_rendered: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(&expected_rendered, "3,{d}", .{high + 8});
    try std.testing.expectEqualStrings(expected_text, rendered[0..len]);

    var entries = [_]Entry{
        .{ .key = high + 8, .serial = 0 },
        .{ .key = 3, .serial = 1 },
    };
    var root = rbtree.RootCached.init();
    _ = rbtree.addCached(&entries[0].node, &root, less);
    _ = rbtree.addCached(&entries[1].node, &root, less);

    var order: [2]usize = undefined;
    const count = collectForward(&root.root, &order);
    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 3, high + 8 }, order[0..count]);
    try std.testing.expectEqual(@as(usize, 3), entryKey(root.leftmost.?));
}
